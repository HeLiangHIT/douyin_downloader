# douyin_downloader

```univers.flf
                                 88                                     88
                                 88                                     ""
                                 88
                         ,adPPYb,88  ,adPPYba,  88       88 8b       d8 88 8b,dPPYba,
                        a8"    `Y88 a8"     "8a 88       88 `8b     d8' 88 88P'   `"8a
                        8b       88 8b       d8 88       88  `8b   d8'  88 88       88
                        "8a,   ,d88 "8a,   ,a8" "8a,   ,a88   `8b,d8'   88 88       88
                         `"8bbdP"Y8  `"YbbdP"'   `"YbbdP'Y8     Y88'    88 88       88
                                                                d8'
                                                               d8'
         88                                            88                                 88
         88                                            88                                 88
         88                                            88                                 88
 ,adPPYb,88  ,adPPYba,  8b      db      d8 8b,dPPYba,  88  ,adPPYba,  ,adPPYYba,  ,adPPYb,88  ,adPPYba, 8b,dPPYba,
a8"    `Y88 a8"     "8a `8b    d88b    d8' 88P'   `"8a 88 a8"     "8a ""     `Y8 a8"    `Y88 a8P_____88 88P'   "Y8
8b       88 8b       d8  `8b  d8'`8b  d8'  88       88 88 8b       d8 ,adPPPPP88 8b       88 8PP""""""" 88
"8a,   ,d88 "8a,   ,a8"   `8bd8'  `8bd8'   88       88 88 "8a,   ,a8" 88,    ,88 "8a,   ,d88 "8b,   ,aa 88
 `"8bbdP"Y8  `"YbbdP"'      YP      YP     88       88 88  `"YbbdP"'  `"8bbdP"Y8  `"8bbdP"Y8  `"Ybbd8"' 88
```



# 用法

查看帮助： `python douyin_downloader.py --help`

```
抖音下载器: 异步下载抖音视频。 follow 参数用于指定是否是下载关注的用户视频。

Usage:
  douyin_downloader.py [--dir=dir] [--concurrency=concurrency] [--follow=follow] <user> <action> follow
  douyin_downloader.py [--dir=dir] [--concurrency=concurrency] [--follow=follow] <user> <action>
  douyin_downloader.py --version

Options:
  --dir=dir                    select file save dir. * default: '$HOME/Movies/douyin/'
  --concurrency=concurrency    select the concurrency number of downloader. [default: 20]
```


举例：

1. `python douyin_downloader.py 84834596404 favorite` 下载用户 84834596404 喜欢过的视频。
2. `python douyin_downloader.py --dir=. --concurrency=10 84834596404 post` 下载用户 84834596404 上传的视频。
3. `python douyin_downloader.py 84838778760 favorite follow` 下载用户 84838778760 关注的用户喜欢过的视频。


下载过程和结果展示：

![下载中...](img/downloading.png)
![下载结果](img/result.png)


## TODO

* [ ] 从首页依次爬取抖音所有点击量超过1w的视频下载...
* [ ] 顺藤摸瓜，爬取自己关注的人->爬取他们关注的人...把整个抖音数据库都扒下来了，看看有没有用...
* [ ] 融入美女自动识别等功能（可以参考 [Douyin-Bot](https://github.com/wangshub/Douyin-Bot) ）。


# 参考

1. https://github.com/AppSign/douyin
2. https://github.com/hacksman/spider_world
3. https://github.com/python-trio/trio
4. https://github.com/theelous3/asks


欢迎扫码关注作者，获取更多信息哦～另外如果本源码对你有所帮助，可以[点赞以支持作者的持续更新](./img/URgood.jpg)。

<img src="./img/owner.jpg" width = "300" height = "300" alt="关注作者" align=center />






