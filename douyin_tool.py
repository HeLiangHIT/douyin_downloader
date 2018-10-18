#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-10-18 00:15:14
# @Author  : He Liang (heianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT

from util import *



async def get_follow_list(user_id, offset=0, count=20):
    '''获取关注列表举例, 参考 'json_demo/follow_list.py'
    >>> follow_list = trio.run(get_follow_list, "84834596404", "0", "20")
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
    params = await get_signed_params(follow_para)
    resp = await asks.get(url, params=params, verify=False, headers=IPHONE_HEADER)
    logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
    return resp.json()['followings']


async def _get_favorite_list(user_id, max_cursor=0):
    '''抓取我喜欢的视频列表, 参考 'json_demo/video_list.py'
    >>> video_list, _, _ = trio.run(_get_favorite_list, "84834596404", 0)
    >>> print(len(video_list))
    20
    '''
    url = "https://aweme.snssdk.com/aweme/v1/aweme/favorite/" # 用户喜欢的视频
    # url =  https://aweme.snssdk.com/aweme/v1/aweme/post/ # 用户发布的视频
    favorite_para = {
        "count": "21",
        "user_id": user_id,
        "max_cursor": str(max_cursor),
    }
    params = await get_signed_params(favorite_para)
    resp = await asks.get(url, params=params, verify=False, headers=IPHONE_HEADER)
    logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")

    favorite_info = resp.json()
    video_list = favorite_info.get('aweme_list')
    hasmore = favorite_info.get('has_more')
    max_cursor = favorite_info.get('max_cursor')
    
    return video_list, hasmore, max_cursor


async def _get_video_url(aweme_id):
    '''获取视频地址，可以直接使用 asks.get(video_url, headers=IPHONE_HEADER, verify=False) 下载视频'''
    url = "https://aweme.snssdk.com/aweme/v1/aweme/detail/"

    video_para = post_data = {'aweme_id': aweme_id}
    params = await get_signed_params(video_para)
    resp = await asks.get(url, params=params, data=post_data, headers=IPHONE_HEADER, verify=False)
    logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")

    video_info = resp.json()
    play_addr_raw = video_info['aweme_detail']['video']['play_addr']['url_list']
    # 注意测试发现这个播放列表里前两个链接都是可以用的，下载的时候可以为了保险起见循环下载测试
    return play_addr_raw[0:2]


async def _get_music_url(music_id):
    '''获取音频地址，可以直接使用 asks.get(music_url, headers=IPHONE_HEADER, verify=False) 下载视频'''
    url = f"https://p3.pstatp.com/obj/{music_id}"
    return url


async def _parse_video_info(video):
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
    }

    return download_item


async def get_favorite_list(user_id, max_cursor=0):
    '''爬取指定用户的所有喜欢视频列表，返回各个视频要下载需要的所有信息，请使用 async for video in get_favorite_list(uid): ...'''
    total = 0
    while True:
        video_list, hasmore, max_cursor = await _get_favorite_list(user_id, max_cursor)
        for video in video_list:
            video_item = await _parse_video_info(video)
            total += 1
            yield video_item
        if not hasmore:
            logging.info(f"get favorite list finished, there are total {total} videos for user_id={user_id}!")
            raise StopIteration()


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




if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)  # verbose=True shows the output
    logging.info("doctest finished.")
    



