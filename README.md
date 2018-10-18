


# 用法
查看帮助： python douyin_downloader.py --help
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



# 注释



ref: 
1. https://github.com/AppSign/douyin
2. https://github.com/hacksman/spider_world
3. picture_scrapy/picture_downloader.py

todo:
1. 异步下载器： 实现到 util.py 里面即可？
2. 下载 __COMMENT_URL= "https://aweme.snssdk.com/aweme/v1/comment/list/" 的内容
3. 爬取首页视频: feed.py
4. 视频搜索: search.py
5. 视频下载 无水印 downloadVideo.py
6. 拉取指定用户个人信息 userInfo.py
7. 下载该用户所有视频
8. 下载该用户所有视频和音频
9. 下载单个视频
10. 下载单个视频的音频 -- 还不正确待修正，不知道支持不
11. 用户的评论信息
12. 不能每次 get_signed_params 都 getDevice/getToken ，设定时间超时重获取就可以了。 done
13. 为了避免重启时重复下载，对于判断依据存在的视频id就不要重复爬取了。
14. 总是出现 socket.gaierror 这个错误，有必要向 asks 作者反馈一下。


本地调试异步下载器的方法：
1. 准备一个有合适文件的目录（比如 a.jpg/b.mp4/c.txt ），在下面执行 `python -m http.server > server.log &` 打开文件HTTP服务器
2. 使用 `curl -v -N --noproxy -XGET http://127.0.0.1:8000/a.jpg` 或者 `curl -v -N --noproxy -XHEAD http://127.0.0.1:8000/b.mp4` 调试请求。
3. 根据 curl 返回内容调试下载器参数。





当前爬取的日志信息：
2018-10-18 01:33:03,470 - util.py[line:87] - DEBUG: get response from https://api.appsign.vip:2688/douyin/device/new/version/2.7.0 is <Response 200 OK> with body: {"success": true, "data": {"openudid": "dfc790da8c...

2018-10-18 01:33:04,104 - util.py[line:57] - DEBUG: get response from https://api.appsign.vip:2688/token/douyin/version/2.7.0 is <Response 200 OK> with body: {"success": true, "token": "b77a12f892a7490b829a2c...

2018-10-18 01:33:05,013 - util.py[line:111] - DEBUG: post response from https://api.appsign.vip:2688/sign is <Response 200 OK> with body: {"success": true, "data": {"mas": "015cd9aeeea4dc2...

2018-10-18 01:33:05,650 - util_helper.py[line:49] - DEBUG: get response from https://aweme.snssdk.com/aweme/v1/aweme/favorite/ is <Response 200 OK> with body: {"max_cursor": 1538926484000, "aweme_list": [{"ris...

2018-10-18 01:33:06,630 - util.py[line:87] - DEBUG: get response from https://api.appsign.vip:2688/douyin/device/new/version/2.7.0 is <Response 200 OK> with body: {"success": true, "data": {"openudid": "6ffc6b6d19...

2018-10-18 01:33:07,025 - util.py[line:57] - DEBUG: get response from https://api.appsign.vip:2688/token/douyin/version/2.7.0 is <Response 200 OK> with body: {"success": true, "token": "7c1ace6a4da447c49d9db1...

2018-10-18 01:33:08,078 - util.py[line:111] - DEBUG: post response from https://api.appsign.vip:2688/sign is <Response 200 OK> with body: {"success": true, "data": {"mas": "0172e27d9207a4b...

2018-10-18 01:33:08,340 - util_helper.py[line:85] - DEBUG: get response from https://aweme.snssdk.com/aweme/v1/aweme/detail/ is <Response 200 OK> with body: {"status_code": 0, "extra": {"logid": "20181018013...

2018-10-18 01:33:08,342 - util_helper.py[line:89] - INFO: ['http://v6-dy.ixigua.com/video/m/220b166005bbb924e30b63f709f8373a2f7115c97a600003ee63189a5ac/?AWSAccessKeyId=qh0h9TdcEMoS2oPj7aKX&Expires=1539801244&Signature=dO%2FG%2FRn8%2BRJdD%2Bx9RdaEDgmj2G4%3D', 'http://v3-dy.ixigua.com/4895d752afc5bdb59bf7f75df76f1942/5bc7809c/video/m/220b166005bbb924e30b63f709f8373a2f7115c97a600003ee63189a5ac/', 'https://aweme.snssdk.com/aweme/v1/play/?video_id=v0200fa40000beu1iorrm1ndlt7i63v0&line=0&ratio=720p&media_type=4&vr_type=0&test_cdn=None&improve_bitrate=0&h265=1', 'https://api.amemv.com/aweme/v1/play/?video_id=v0200fa40000beu1iorrm1ndlt7i63v0&line=0&ratio=720p&media_type=4&vr_type=0&test_cdn=None&improve_bitrate=0&h265=1', 'https://aweme.snssdk.com/aweme/v1/play/?video_id=v0200fa40000beu1iorrm1ndlt7i63v0&line=1&ratio=720p&media_type=4&vr_type=0&test_cdn=None&improve_bitrate=0&h265=1', 'https://api.amemv.com/aweme/v1/play/?video_id=v0200fa40000beu1iorrm1ndlt7i63v0&line=1&ratio=720p&media_type=4&vr_type=0&test_cdn=None&improve_bitrate=0&h265=1']

2018-10-18 01:33:08,343 - util_helper.py[line:105] - INFO: download video]url=http://v6-dy.ixigua.com/video/m/220b166005bbb924e30b63f709f8373a2f7115c97a600003ee63189a5ac/?AWSAccessKeyId=qh0h9TdcEMoS2oPj7aKX&Expires=1539801244&Signature=dO%2FG%2FRn8%2BRJdD%2Bx9RdaEDgmj2G4%3D ...

2018-10-18 01:33:08,343 - util_helper.py[line:106] - INFO: download music]url=https://p3.pstatp.com/obj/http://p1.pstatp.com/obj/d1a60002269f4bee0240 ...
[Finished in 6.0s]



