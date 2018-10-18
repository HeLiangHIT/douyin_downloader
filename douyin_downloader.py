#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-10-18 23:38:24
# @Author  : He Liang (heianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT

'''
抖音下载器: 异步下载抖音视频

Usage:
  douyin_downloader.py [--dir=dir] [--concurrency=concurrency] <user> <action>
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
            if downloader.is_file_downloaded(video['name']):
                logging.info(f"{video['name']} is already downloaded!")
                continue
            url = video['video_url'][0] # TODO add list url support
            logging.debug(f"downloading {url} ... ")
            content = await downloader.download_file(url)
            if content is not None:
                await downloader.save_file(video['name'], content)
                logging.info(f"download {video['name']} from {url} succ")
            else:
                logging.error(f"download {video['name']} from {url} FAIL!")


func_dict = {
    "favorite" : get_favorite_list,

}


# 生产-消费 流程 的生产者 _sender
async def generate_videos(_sender, user, action):
    async for video in func_dict[action](user):
        file_name = "_".join([video["author_name"], video["author_uid"], trim(video["video_desc"], 20)])
        video['name'] = f"{file_name}.mp4"
        await _sender.send(video)
    await _sender.send(None)


# 主函数
async def main(user, action, save_dir, concurrency):
    logging.info(f"start download favorite video to {save_dir} with {concurrency} concurrency ...")
    downloader = AsyncDownloader(save_dir)

    async with trio.open_nursery() as nursery:
        _sender, _receiver = trio.open_memory_channel(concurrency) # 并行数量
        nursery.start_soon(generate_videos, _sender, user, action)
        nursery.start_soon(download_videos, _receiver, downloader)

    logging.info("file downloads over!")


if __name__ == '__main__':
    arguments = docopt(__doc__, version="douyin_downloader 0.0.1")
    save_dir = arguments["--dir"] if arguments["--dir"] else _SAVE_DIR # 不会取doc里`*default`的值
    concurrency = int(arguments["--concurrency"])
    user = arguments['<user>']
    if not user.isdigit():
        logging.critical(f"user={user} is illegal!")
    action = arguments['<action>']
    if action not in func_dict.keys():
        logging.critical(f"action={action} is not supported!")
    trio.run(main, user, action, save_dir, concurrency)





