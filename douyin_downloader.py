#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-10-18 23:38:24
# @Author  : He Liang (heianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT

'''
抖音下载器: 异步下载抖音视频。 follow 参数用于指定是否是下载关注的用户视频。

Usage:
  douyin_downloader.py [--dir=dir] [--concurrency=concurrency] [--follow=follow] <user> <action> follow
  douyin_downloader.py [--dir=dir] [--concurrency=concurrency] [--follow=follow] <user> <action>
  douyin_downloader.py --version

Options:
  --dir=dir                    select file save dir. * default: '$HOME/Movies/douyin/'
  --concurrency=concurrency    select the concurrency number of downloader. [default: 20]
'''

from douyin_tool import *
from docopt import docopt

# 默认配置参数
_SAVE_DIR = "%s/Movies/douyin/" % os.path.expanduser('~') # os.environ['HOME']


# 生产-消费 流程 的消费者 _receiver
async def download_videos(_receiver, downloader):
    while True:
        async for video in _receiver:
            # video = await _receiver.receive() # may get repeated tail
            if video is None:
                return # 结束下载
            url = video['video_url']
            if downloader.is_file_downloaded(video['name']) or url is None:
                logging.info(f"{video['name']} is already downloaded or expired!")
                continue
            
            logging.debug(f"downloading {url} ... ")
            content = await downloader.download_file(url)
            if content is not None:
                await downloader.save_file(video['name'], content)
                logging.info(f"download {video['name']} from {url} succ")
            else:
                logging.error(f"download {video['name']} from {url} FAIL!")


# 生产-消费 流程 的生产者 _sender
async def generate_videos(_sender, func_dict, user, action, repeat_func):
    '''根据用户选择调用指定函数'''
    async for video in func_dict[action](user, repeat_func=repeat_func):
        await _sender.send(video)
    await _sender.send(None)


# 爬取单个用户的视频
async def crawler_user_video(user, func_dict, action, save_dir, concurrency):
    '''下载指定用户指定的'''
    logging.info(f"start download {user}'s favorite video to {save_dir} with {concurrency} concurrency ...")
    downloader = AsyncDownloader(f"{save_dir}/{user}/{action}")

    async with trio.open_nursery() as nursery:
        _sender, _receiver = trio.open_memory_channel(concurrency) # 并行数量
        nursery.start_soon(generate_videos, _sender, func_dict, user, action, downloader.is_file_downloaded)
        nursery.start_soon(download_videos, _receiver, downloader)

    logging.info(f"video for user with user_id={user} downloads finished!")


# 主函数
async def main(user, action, follow, save_dir, concurrency):
    dy = DouyinTool()
    func_dict = {
        "favorite" : dy.get_favorite_list,
        "post" : dy.get_post_list,
    }

    if action not in func_dict.keys():
        logging.critical(f"action={action} is not supported!")
    if not user.isdigit():
        logging.critical(f"user={user} is illegal!")

    if follow:
        user_ids = set()
        async for people in dy.get_follow_list(user):
            user_ids.add(people['user_id'])
        logging.info(f"there are {len(user_ids)} followed users need for crawler, let's begin!")
        for _user in user_ids:
            await crawler_user_video(_user, func_dict, action, save_dir, concurrency)
    else:
        await crawler_user_video(user, func_dict, action, save_dir, concurrency)

    logging.info("all videos are downloaded! congratulations!!!")


def cmd_run():
    '''命令行输入参数'''
    user = user_input("Input user_id:")
    _action = user_input("Choose action[1.favorite, 2.post] *default 1:", ['1', '2'], '1')
    action = ('favorite', 'post')[int(_action) - 1]
    _follow = user_input("Do you want to follow user? [yes/no] *default no:", ['yes', 'no'], 'no')
    follow = _follow == 'yes'
    save_dir = user_input(f"Input video save dir *default {_SAVE_DIR}:", [], _SAVE_DIR)
    concurrency = 20
    print(f"begin to download {'following of ' if follow else ''}{user}'s {action} video to {save_dir} ... ")

    trio.run(main, user, action, follow, save_dir, concurrency)


if __name__ == '__main__':
    arguments = docopt(__doc__, version="douyin_downloader 0.0.1")
    save_dir = arguments["--dir"] if arguments["--dir"] else _SAVE_DIR # 不会取doc里`*default`的值
    concurrency = int(arguments["--concurrency"])
    user = arguments['<user>']
    action = arguments['<action>']
    follow = arguments['follow'] # True if set, else False
    trio.run(main, user, action, follow, save_dir, concurrency)





