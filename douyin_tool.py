#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-10-18 00:15:14
# @Author  : He Liang (heianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT

from util import *



async def get_main_page(user_id, count=6):
    '''爬取主页视频内容内容
    >>> resp = trio.run(get_main_page, "84834596404")
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
    try:
        params = await get_signed_params(feed_param)
        resp = await asks.get(url, params=params, headers=IPHONE_HEADER)
        logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
    except Exception as e:
        logging.error(f"get follow list fail from {url}]err=%s" % e)
        return {"status_code": -1}
    return resp.json()


async def search_web(keyword, count=12, offset=0):
    '''搜索内容
    >>> resp = trio.run(search_web, "美女")
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
    try:
        params = await get_signed_params(search_param)
        resp = await asks.get(url, params=params, headers=IPHONE_HEADER)
        logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
    except Exception as e:
        logging.error(f"search from {url}]err=%s" % e)
        return {"status_code": -1}
    return resp.json()


async def get_user_info(user_id):
    '''搜索内容
    >>> resp = trio.run(get_user_info, "84834596404")
    >>> print(resp['status_code'])
    0
    '''
    url = "https://aweme.snssdk.com/aweme/v1/user/"
    feed_param = {
        "ac": "WIFI",
        "user_id": user_id,
    }
    try:
        params = await get_signed_params(feed_param)
        resp = await asks.get(url, params=params, headers=IPHONE_HEADER)
        logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
    except Exception as e:
        logging.error(f"search from {url}]err=%s" % e)
        return {"status_code": -1}
    return resp.json()



async def _get_follow_list(user_id, offset=0, count=20):
    '''获取关注列表举例, 参考 'json_demo/follow_list.py'
    >>> follow_list, _, _ = trio.run(_get_follow_list, "84834596404", 0, 20)
    >>> print(len(follow_list))
    20
    '''
    url = 'https://aweme.snssdk.com/aweme/v1/user/following/list/'
    follow_para = {
        "user_id": user_id,
        "offset": str(offset),
        "count": str(count),
        "source_type": "2",
        "max_time": int(time.time()),
        "ac": "WIFI",
    }
    try:
        params = await get_signed_params(follow_para)
        resp = await asks.get(url, params=params, verify=False, headers=IPHONE_HEADER)
        logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
    except Exception as e:
        logging.error(f"get follow list fail from {url}]err=%s" % e)
        return [], False, offset

    follow_info = resp.json()
    follow_list = follow_info.get('followings', [])
    hasmore = follow_info.get('has_more', False)
    # hasmore = follow_info.get('total', 0) > (offset + count)
    
    return follow_list, hasmore, offset + count

async def get_follow_list(user_id, offset=0, repeat_func=None):
    '''爬取指定用户的所有关注的用户列表 async for video in get_follow_list(uid): ...
    第二次post返回都是失败， post 缺少什么必要参数呢？'''
    total = 0
    while True:
        follow_list, hasmore, offset = await _get_follow_list(user_id, offset, count=20)
        for follow in follow_list:
            user_id = follow.get('uid', None)
            nickname = follow.get('nickname', '')
            signature = follow.get('signature', '')
            birthday = follow.get('birthday', '')
            total += 1
            yield {'user_id':user_id, 'nickname':nickname, 'signature':signature, 'birthday':birthday,}
        if not hasmore:
            logging.info(f"get follow list finished, there are total {total} people followed by user_id={user_id}!")
            # raise StopIteration # ref: https://www.python.org/dev/peps/pep-0479/  or  https://stackoverflow.com/questions/51700960/runtimeerror-generator-raised-stopiteration-everytime-i-try-to-run-app
            return

async def _get_follow_list_test():
    '''测试 get_follow_list_test 是否正确
    >>> print(trio.run(_get_follow_list_test))
    20
    '''
    total = 0
    async for people in get_follow_list("84834596404", 20):
        logging.info(f"begin to get video_list of {people} ... ")
        total += 1
    return total


async def _get_video_list(url, user_id, max_cursor=0):
    '''获取视频列表
    # url = "https://aweme.snssdk.com/aweme/v1/aweme/favorite/" # 用户喜欢的视频
    # url = "https://aweme.snssdk.com/aweme/v1/aweme/post/" # 用户发布的视频
    '''
    favorite_para = {
        "count": "21",
        "user_id": user_id,
        "max_cursor": str(max_cursor),
    }
    try:
        params = await get_signed_params(favorite_para)
        resp = await asks.get(url, params=params, verify=False, headers=IPHONE_HEADER)
        logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
    except (socket.gaierror, ) as e:
        logging.error(f"get video list fail from {url}]err=%s" % e)
        return [], True, max_cursor

    favorite_info = resp.json()
    video_list = favorite_info.get('aweme_list', [])
    hasmore = favorite_info.get('has_more', False)
    max_cursor = favorite_info.get('max_cursor', max_cursor)
    
    return video_list, hasmore, max_cursor


async def _get_favorite_list(user_id, max_cursor=0):
    '''抓取我喜欢的视频列表, 参考 'json_demo/video_list.py'
    >>> video_list, _, _ = trio.run(_get_favorite_list, "84834596404", 0)
    >>> print(len(video_list))
    19
    '''
    return await _get_video_list("https://aweme.snssdk.com/aweme/v1/aweme/favorite/", user_id, max_cursor)


async def _get_post_list(user_id, max_cursor=0):
    '''抓取我发布的视频列表, 参考 'json_demo/video_list.py'
    >>> video_list, _, _ = trio.run(_get_post_list, "84834596404", 0)
    >>> print(len(video_list))
    0
    '''
    return await _get_video_list("https://aweme.snssdk.com/aweme/v1/aweme/post/", user_id, max_cursor)


async def _get_video_url(aweme_id):
    '''获取视频地址，可以直接使用 asks.get(video_url, headers=IPHONE_HEADER, verify=False) 下载视频'''
    url = "https://aweme.snssdk.com/aweme/v1/aweme/detail/"
    video_para = post_data = {'aweme_id': aweme_id}
    try:
        params = await get_signed_params(video_para)
        resp = await asks.get(url, params=params, data=post_data, headers=IPHONE_HEADER, verify=False)
        logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
        video_info = resp.json()
        play_addr_raw = video_info['aweme_detail']['video']['play_addr']['url_list']
        # 注意测试发现这个播放列表里前两个链接都是可以用的，下载的时候可以为了保险起见循环下载测试
        return play_addr_raw[0:2]
    except Exception as e:
        logging.error(f"get vido info failed!")
        return None

async def _get_music_url(music_id):
    '''获取音频地址，可以直接使用 asks.get(music_url, headers=IPHONE_HEADER, verify=False) 下载视频'''
    url = f"https://p3.pstatp.com/obj/{music_id}"
    return url

async def _parse_video_info(video, repeat_func=None):
    '''解析视频关键信息
    >>> video_list, _, _ = trio.run(_get_favorite_list, "84834596404", 0)
    >>> video = video_list[0]
    >>> video_item = trio.run(_parse_video_info, video)
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
        video_url = await _get_video_url(aweme_id)
        music_url = await _get_music_url(music_id)

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


async def get_favorite_list(user_id, max_cursor=0, repeat_func=None):
    '''爬取指定用户的所有喜欢视频列表，返回各个视频要下载需要的所有信息，请使用 async for video in get_favorite_list(uid): ...'''
    total = 0
    while True:
        video_list, hasmore, max_cursor = await _get_favorite_list(user_id, max_cursor)
        for video in video_list:
            video_item = await _parse_video_info(video, repeat_func)
            total += 1
            yield video_item
        if not hasmore:
            logging.info(f"get favorite list finished, there are total {total} videos for user_id={user_id}!")
            return

async def _get_favorite_list_test():
    '''测试 get_favorite_list_test 是否正确，这里只抓几个做测试
    >>> print(trio.run(_get_favorite_list_test))
    5
    '''
    total = 0
    async for video in get_favorite_list("84834596404"):
        video_name = "_".join([video["author_name"], video["author_uid"], trim(video["video_desc"], 20)])
        logging.info(f"begin download {video_name} to ./ ... ")
        total += 1
        if total >= 5:
            logging.info("assume we get finished!")
            return total
    return total


async def get_post_list(user_id, max_cursor=0, repeat_func=None):
    '''爬取指定用户的所有发布视频列表，返回各个视频要下载需要的所有信息，请使用 async for video in get_post_list(uid): ...'''
    total = 0
    while True:
        video_list, hasmore, max_cursor = await _get_post_list(user_id, max_cursor)
        for video in video_list:
            video_item = await _parse_video_info(video, repeat_func)
            total += 1
            yield video_item
        if not hasmore:
            logging.info(f"get post list finished, there are total {total} videos for user_id={user_id}!")
            return

async def _get_post_list_test():
    '''测试 get_post_list_test 是否正确，这里只抓几个做测试
    >>> print(trio.run(_get_post_list_test))
    0
    '''
    total = 0
    async for video in get_post_list("84834596404"):
        video_name = "_".join([video["author_name"], video["author_uid"], trim(video["video_desc"], 20)])
        logging.info(f"begin download {video_name} to ./ ... ")
        total += 1
        if total >= 5:
            logging.info("assume we get finished!")
            return total
    return total


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)  # verbose=True shows the output
    logging.info("doctest finished.")

