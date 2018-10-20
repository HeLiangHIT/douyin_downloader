#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-10-18 00:15:14
# @Author  : He Liang (heianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT

from util import *


class DouyinTool(object):
    def __init__(self, version=APPINFO['version_code']):
        super(DouyinTool, self).__init__()
        self.sign_util = SignUtil(version)

    async def get_main_page(self, user_id, count=6):
        '''爬取主页视频内容内容
        >>> resp = trio.run(DouyinTool().get_main_page, "84834596404")
        >>> print(resp['status_code'])
        0
        '''
        url = "https://aweme.snssdk.com/aweme/v1/feed/"
        feed_param = {
            "ac":           "WIFI",
            "count":        str(count),
            "feed_style":   "0",
            "filter_warn":  "0",
            "filter_warn":  "0",
            "max_cursor":   "0",
            "min_cursor":   "0",
            "pull_type":    "1",
            "type":         "0",
            "volume":       "0.00"
        }
        resp = await self.sign_util.curl(url, feed_param)
        return resp.json() if resp is not None else {"status_code": -1}


    async def search_web(self, keyword, count=12, offset=0):
        '''搜索内容
        >>> resp = trio.run(DouyinTool().search_web, "美女")
        >>> print(resp['status_code'])
        0
        '''
        url = "https://api.amemv.com/aweme/v1/general/search/"
        search_param = {
            "ac":       "WIFI",
            "count":    str(count),
            "keyword":  keyword,
            "offset":   str(offset),
        }
        resp = await self.sign_util.curl(url, search_param)
        return resp.json() if resp is not None else {"status_code": -1}

    async def get_user_info(self, user_id):
        '''获取用户详细信息
        >>> resp = trio.run(DouyinTool().get_user_info, "84834596404")
        >>> print(resp['status_code'])
        0
        '''
        url = "https://aweme.snssdk.com/aweme/v1/user/"
        user_params = {
            "ac": "WIFI",
            "user_id": user_id,
        }
        resp = await self.sign_util.curl(url, user_params)
        return resp.json() if resp is not None else {"status_code": -1}

    async def get_comments(self, aweme_id, cursor=0):
        '''获取视频评论
        >>> comments, _, _ = trio.run(DouyinTool().get_comments, "6610186359145499912", 0)
        >>> print(len(comments) > 0)
        True
        '''
        url = "https://aweme.snssdk.com/aweme/v1/comment/list/"
        comment_params = {
            "count": str(20),
            "cursor": str(cursor),
            "comment_style": '2',
            "aweme_id": aweme_id,
            "digged_cid": "",
        }
        resp = await self.sign_util.curl(url, comment_params)
        comments_res = resp.json() if resp is not None else {"status_code": -1}
        hasmore = comments_res.get("hasmore", False)
        cursor = comments_res.get("cursor", cursor)
        comments = comments_res.get("comments", [])
        # for comment in comments:
        #     real_comment = comment.get("reply_comment")[0] if comment.get("reply_comment") else comment
        #     upvote_count = real_comment.get("digg_count")
        #     comment_item = {
        #         "aweme_id" : aweme_id,
        #         "text": real_comment.get("text", ''),
        #         "upvote_count": upvote_count,
        #         "nick_name": real_comment['user'].get("nickname"),
        #         "user_id": real_comment['user'].get("uid"),
        #     }
        return comments, hasmore, cursor

    async def like_video(self, aweme_id):
        '''喜欢一个视频： 为啥会失败呢？错误码8是什么意思？
        >>> resp = trio.run(DouyinTool().like_video, "6613913455902592259")
        >>> print(resp['status_code'])
        8
        '''
        url = "https://aweme.snssdk.com/aweme/v1/commit/item/digg/"
        like_params = {
            "pass-region": "1",
            "aweme_id": aweme_id,
            "type": 1,
        }
        resp = await self.sign_util.curl(url, like_params, data=like_params, method='POST',
            headers={**IPHONE_HEADER, "sdk-version": "1", "Accept-Encoding": 'br, gzip, deflate'})
        return resp.json() if resp is not None else {"status_code": -1}

    async def _get_follow_list(self, user_id, offset=0):
        '''获取关注列表举例, 参考 'json_demo/follow_list.json'
        >>> follow_list, _, _ = trio.run(DouyinTool()._get_follow_list, "84834596404", 0)
        >>> print(len(follow_list))
        20
        '''
        url = 'https://aweme.snssdk.com/aweme/v1/user/following/list/'
        follow_para = {
            "user_id": user_id,
            "offset": str(offset),
            "count": str(20),
            "source_type": "2",
            "max_time": str(int(time.time())),
            "ac": "WIFI",
        }
        resp = await self.sign_util.curl(url, follow_para)
        if not resp:
            return [], False, offset

        follow_info = resp.json()
        follow_list = follow_info.get('followings', [])
        # hasmore = follow_info.get('has_more', False) # always be true
        hasmore = follow_info.get('total', 0) > (offset + 20)

        return follow_list, hasmore, offset + 20

    async def get_follow_list(self, user_id, offset=0, repeat_func=None):
        '''爬取指定用户的所有关注的用户列表 async for video in get_follow_list(uid): ...
        第二次post返回都是失败， post 缺少什么必要参数呢？'''
        total = 0
        while True:
            follow_list, hasmore, offset = await self._get_follow_list(user_id, offset)
            # print(len(follow_list), hasmore, offset)
            for follow in follow_list:
                uid = follow.get('uid', None)
                nickname = follow.get('nickname', '')
                signature = follow.get('signature', '')
                birthday = follow.get('birthday', '')
                # if uid == '92654947278' or nickname == '已重置':
                #     # 测试发现这个号并没有什么卵用，而且并不是关注的用户
                #     continue
                total += 1
                yield {'user_id':uid, 'nickname':nickname, 'signature':signature, 'birthday':birthday,}
            if not hasmore:
                logging.info(f"get follow list finished, there are total {total} people followed by user_id={user_id}!")
                # raise StopIteration # ref: https://www.jsonthon.org/dev/peps/pep-0479/  or  https://stackoverflow.com/questions/51700960/runtimeerror-generator-raised-stopiteration-everytime-i-try-to-run-app
                return

    async def _get_video_list(self, url, user_id, max_cursor=0):
        '''获取视频列表
        # url = "https://aweme.snssdk.com/aweme/v1/aweme/favorite/" # 用户喜欢的视频
        # url = "https://aweme.snssdk.com/aweme/v1/aweme/post/" # 用户发布的视频
        # 抓取我喜欢的视频列表, 参考 'json_demo/video_list.json'
        >>> video_list, _, _ = trio.run(DouyinTool()._get_video_list, "https://aweme.snssdk.com/aweme/v1/aweme/favorite/", "84834596404", 0)
        >>> print(len(video_list))
        19

        # 抓取我发布的视频列表
        >>> video_list, _, _ = trio.run(DouyinTool()._get_video_list, "https://aweme.snssdk.com/aweme/v1/aweme/post/", "84834596404", 0)
        >>> print(len(video_list))
        0
        '''
        video_params = {
            "count": "21",
            "user_id": user_id,
            "max_cursor": str(max_cursor),
        }
        resp = await self.sign_util.curl(url, video_params)
        if not resp:
            return [], True, max_cursor

        video_resp = resp.json()
        video_list = video_resp.get('aweme_list', [])
        hasmore = video_resp.get('has_more', False)
        max_cursor = video_resp.get('max_cursor', max_cursor)

        return video_list, hasmore, max_cursor

    async def get_favorite_list(self, user_id, max_cursor=0, repeat_func=None):
        '''爬取指定用户的所有喜欢视频列表，返回各个视频要下载需要的所有信息，请使用 async for video in get_favorite_list(uid): ...'''
        total = 0
        while True:
            video_list, hasmore, max_cursor = await self._get_video_list("https://aweme.snssdk.com/aweme/v1/aweme/favorite/", user_id, max_cursor)
            for video in video_list:
                video_item = await self.parse_video_info(video, repeat_func)
                total += 1
                yield video_item
            if not hasmore:
                logging.info(f"get favorite list finished, there are total {total} videos for user_id={user_id}!")
                return

    async def get_post_list(self, user_id, max_cursor=0, repeat_func=None):
        '''爬取指定用户的所有发布视频列表，返回各个视频要下载需要的所有信息，请使用 async for video in get_post_list(uid): ...'''
        total = 0
        while True:
            video_list, hasmore, max_cursor = await self._get_video_list("https://aweme.snssdk.com/aweme/v1/aweme/post/", user_id, max_cursor)
            for video in video_list:
                video_item = await self.parse_video_info(video, repeat_func)
                total += 1
                yield video_item
            if not hasmore:
                logging.info(f"get post list finished, there are total {total} videos for user_id={user_id}!")
                return


    async def _get_video_url(self, aweme_id):
        '''获取视频地址，可以直接使用 asks.get(video_url, verify=False, headers=IPHONE_HEADER, verify=False) 下载视频'''
        url = "https://aweme.snssdk.com/aweme/v1/aweme/detail/"
        video_para = post_data = {'aweme_id': aweme_id}
        resp = await self.sign_util.curl(url, video_para)
        try:
            video_info = resp.json()
            play_addr_raw = video_info['aweme_detail']['video']['play_addr']['url_list']
            # 注意测试发现这个播放列表里前两个链接都是可以用的，下载的时候可以为了保险起见循环下载测试
            return play_addr_raw[0:2]
        except Exception as e:
            logging.error(f"parser video url fail from {trim(resp.text, 200)}!")
            return None

    async def _get_music_url(self, music_id):
        '''获取音频地址，可以直接使用 asks.get(music_url, verify=False, headers=IPHONE_HEADER, verify=False) 下载视频'''
        url = f"https://p3.pstatp.com/obj/{music_id}"
        return url

    async def parse_video_info(self, video, repeat_func=None):
        '''解析视频关键信息
        >>> dy = DouyinTool()
        >>> video_list, _, _ = trio.run(DouyinTool()._get_video_list, "https://aweme.snssdk.com/aweme/v1/aweme/favorite/", "84834596404", 0)
        >>> video = video_list[0]
        >>> video_item = trio.run(dy.parse_video_info, video)
        >>> print(video_item['video_url'][0].startswith("http"))
        True
        >>> print(video_item['video_url'][1].startswith("http"))
        True
        '''
        author_name = video['author'].get("nickname")
        author_uid = video['author'].get('uid')
        video_desc = video.get('desc')
        music_id = video['music']['play_url'].get('uri')
        aweme_id = video.get("aweme_id")

        file_name = "_".join([author_name, author_uid, trim(video_desc, 20, '')])
        name = f"{file_name}.mp4"
        if repeat_func and repeat_func(name):
            video_url = music_url = None # 用于下载器的去重复处理回调函数，当文件已经存在时不用再获取视频地址了，无需下载
        else:
            video_url = await self._get_video_url(aweme_id)
            music_url = await self._get_music_url(music_id)

        download_item = {
            "author_name": author_name,
            "video_desc": video_desc,
            "author_uid": author_uid,
            "music_id": music_id,
            "aweme_id" : aweme_id,
            "video_url" : video_url,
            "music_url" : music_url,
            "name" : name,
        }

        return download_item


async def _get_follow_list_test():
    '''测试 get_follow_list_test 是否正确
    >>> print(trio.run(_get_follow_list_test))
    5
    '''
    total = 0
    async for people in DouyinTool().get_follow_list("84834596404", 0):
        logging.info(f"begin to parser {total}-th {people['nickname']} ... ")
        total += 1
        if total >= 5:
            logging.info("assume we get finished!")
            return total
    return total


async def _get_favorite_list_test():
    '''测试 get_favorite_list_test 是否正确，这里只抓几个做测试
    >>> print(trio.run(_get_favorite_list_test))
    5
    '''
    total = 0
    async for video in DouyinTool().get_favorite_list("84834596404"):
        video_name = "_".join([video["author_name"], video["author_uid"], trim(video["video_desc"], 20, '')])
        logging.info(f"begin download {total}-th {video_name} to ./ ... ")
        total += 1
        if total >= 5:
            logging.info("assume we get finished!")
            return total
    return total


async def _get_post_list_test():
    '''测试 get_post_list_test 是否正确，这里只抓几个做测试
    >>> print(trio.run(_get_post_list_test))
    0
    '''
    total = 0
    async for video in DouyinTool().get_post_list("84834596404"):
        video_name = "_".join([video["author_name"], video["author_uid"], trim(video["video_desc"], 20)])
        logging.info(f"begin download {total}-th {video_name} to ./ ... ")
        total += 1
        if total >= 5:
            logging.info("assume we get finished!")
            return total
    return total


if __name__ == '__main__':
    # import doctest
    # doctest.testmod(verbose=False)  # verbose=True shows the output
    # logging.info("doctest finished.")
    print(trio.run(_get_follow_list_test))