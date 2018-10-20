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
抖音下载器: 异步下载抖音视频

Usage:
  douyin_downloader.py user action [--dir=dir] [--concurrency=concurrency]
  douyin_downloader.py --version

Options:
  --dir=dir                    select file save dir. * default: '$HOME/Movies/douyin/'
  --concurrency=concurrency    select the concurrency number of downloader. [default: 20]
```


举例：

1. `python douyin_downloader.py 84834596404 favorite`
2. `python douyin_downloader.py --dir=. --concurrency=10 84834596404 favorite`
3. `python douyin_downloader.py 84838778760 favorite`


下载过程和结果展示：

![下载中...](img/downloading.png)
![下载结果](img/result.png)


## TODO

* [ ] 下载 评论 "https://aweme.snssdk.com/aweme/v1/comment/list/" 的内容。
* [ ] 为了避免重复下载，可以将下载过的视频id/用户id保存到redis中防止重复爬一个用户的内容，如果redis中存在视频信息就不要再下载了，如果redis中存在用户信息的话就直接取走了就好了。
* [ ] 抽象 douyin_tool.py 里面的下载函数（通过传递params和url来实现下载即可），地址管理方式（使用字典抽象动作+地址）。
* [ ] 新增下载所有自己关注的账号的视频。
* [ ] 下载点击量超过1w的视频类似的功能。
* [ ] 顺藤摸瓜，爬取自己关注的人发布视频->依次再爬取他们关注的人发布的视频...保存人的信息和视频的信息，然后把整个抖音数据库都扒下来了。注意下载的视频点赞数量需要超过一定比较妥。
* [ ] 融入美女自动识别等功能（可以参考douyinbot工程）。
* [ ] 总是出现 socket.gaierror 这个错误，有必要向 asks 作者反馈一下。
* [ ] s = Session('https://example.org', connections=2)


# 参考

1. https://github.com/AppSign/douyin
2. https://github.com/hacksman/spider_world
3. https://github.com/python-trio/trio
4. https://github.com/theelous3/asks





