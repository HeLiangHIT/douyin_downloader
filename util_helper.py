#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-10-18 00:15:14
# @Author  : He Liang (heianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT

from util import *


_SAVE_DIR = "%s/Movies/douyin/" % os.path.expanduser('~') # os.environ['HOME']


async def example_get_follow_list(user_id, offset=0, count=20):
    '''获取关注列表举例, 参考 'json_demo/follow_list.py'
    >>> follow_list = trio.run(example_get_follow_list, "84834596404", "0", "20")
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
    logging.debug(f"get response from {url} is {resp} with body: {avoid_too_long(resp.text)}")
    return resp.json()['followings']


async def example_favorite_url(user_id, max_cursor=0):
    '''抓取我喜欢的视频列表, 参考 'json_demo/video_list.py'
    >>> video_list, _, _ = trio.run(example_favorite_url, "84834596404", 0)
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
    logging.debug(f"get response from {url} is {resp} with body: {avoid_too_long(resp.text)}")

    favorite_info = resp.json()
    video_list = favorite_info.get('aweme_list')
    hasmore = favorite_info.get('has_more')
    max_cursor = favorite_info.get('max_cursor')
    
    return video_list, hasmore, max_cursor


def parse_video_info(video):
    '''解析视频关键信息'''
    author_nick_name = video['author'].get("nickname")
    author_uid = video['author'].get('uid')
    video_desc = video.get('desc')
    music_id = video['music']['play_url'].get('uri')
    aweme_id = video.get("aweme_id")

    download_item = {
        "author_nick_name": author_nick_name,
        "video_desc": video_desc,
        "author_uid": author_uid,
        "music_id": music_id,
        "aweme_id" : aweme_id,
    }

    return download_item


async def get_video_url(aweme_id):
    '''获取视频地址，可以直接使用 asks.get(video_url, headers=IPHONE_HEADER, verify=False) 下载视频'''
    url = "https://aweme.snssdk.com/aweme/v1/aweme/detail/"

    video_para = post_data = {'aweme_id': aweme_id}
    params = await get_signed_params(video_para)
    resp = await asks.get(url, params=params, data=post_data, headers=IPHONE_HEADER, verify=False)
    logging.debug(f"get response from {url} is {resp} with body: {avoid_too_long(resp.text)}")

    video_info = resp.json()
    play_addr_raw = video_info['aweme_detail']['video']['play_addr']['url_list']
    logging.info(play_addr_raw)
    return play_addr_raw[0]


async def get_music_url(music_id):
    '''获取音频地址，可以直接使用 asks.get(music_url, headers=IPHONE_HEADER, verify=False) 下载视频'''
    url = f"https://p3.pstatp.com/obj/{music_id}"
    return url


async def mock_download_video(video_item):
    '''模拟下载器下载视频和音频'''
    # 获取真实下载地址
    video_url = await get_video_url(video_item['aweme_id'])
    music_url = await get_music_url(video_item["music_id"])
    video_name = "_".join([video_item["author_nick_name"], video_item["author_uid"], video_item["video_desc"]])
    # 使用下载器下载视频和音频 ... 此处省略
    logging.info(f"download video]url={video_url} ...")
    logging.info(f"download music]url={music_url} ...")
    is_video_ok = True # async_download(video_url, os.path.join(_SAVE_DIR, "%s.mp4" % video_name))
    if not is_video_ok:
        logging.warn(f"download {video_name}.mp4 FAIL!")
    is_music_ok = True # async_download(music_url, os.path.join(_SAVE_DIR, "%s.mp3" % video_name))
    if not is_music_ok:
        logging.warn(f"download {video_name}.mp4 FAIL!")

    return is_video_ok and is_music_ok




if __name__ == '__main__':
    # import doctest
    # doctest.testmod(verbose=False)  # verbose=True shows the output
    # logging.info("doctest finished.")

    video_list, _, _ = trio.run(example_favorite_url, "84834596404", 0)

    video = video_list[0]
    video_item = parse_video_info(video)
    isok = trio.run(mock_download_video, video_item)


