#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-10-17 22:12:00
# @Author  : He Liang (heianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT

'''
ref1: https://github.com/AppSign/douyin  抖音通信协议 2.9.1版本协议签名
ref2: https://github.com/hacksman/spider_world 抖音爬虫例子
'''

import trio, asks, logging, json, time, os, arrow
asks.init('trio')

logging.basicConfig(level=logging.INFO, 
    format='%(asctime)s %(filename)s:%(lineno)d %(threadName)s:%(funcName)s %(levelname)s] %(message)s')
IPHONE_HEADER = {"User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"}
DOWNLOAD_TIMEOUT = 600
RETRIES_TIMES = 5

# 基本配置
_API = "https://api.appsign.vip:2688"
_APPINFO = {
    "version_code": "2.7.0",
    "app_version": "2.7.0",
    "channel": "App%20Stroe",
    "app_name": "aweme",
    "build_number": "27014",
    "aid": "1128",
}
'''
_APPINFO = {
    "version_code": "2.9.1",
    "app_version": "2.9.1",
    "channel": "App Stroe",
    "app_name": "aweme",
    "build_number": "29101",
    "aid": "1128",
}
'''


def trim(text, max_len = 50, suffix = '...'):
    '''为避免打印的日志过长，可以使用该函数裁剪一下'''
    text = text.replace('\n', '')
    return f"{text[:max_len]} {suffix}" if len(text) > max_len else text


async def get_token(version=_APPINFO['version_code']):
    '''获取Token: 有效期60分钟
    get https://api.appsign.vip:2688/token/douyin -> 
    {
        "token":"5826aa5b56614ea798ca42d767170e74",
        "success":true
    }
    >>> token = trio.run(get_token) # doctest: +ELLIPSIS
    >>> print(len(token))
    32
    '''
    url = f"{_API}/token/douyin/version/{version}" if version else f"{_API}/token/douyin"
    resp = await asks.get(url)
    logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
    return resp.json().get('token', None)


async def get_device(version=_APPINFO['version_code']):
    '''获取新的设备信息:有效期60分钟永久
    get https://api.appsign.vip:2688/douyin/device/new ->
    {
        "data":{
            "os_api":"23",
            "screen_width":"1334",
            "vid":"39******-ABCD-DA1D-C2C5-******995D7",
            "os_version":"11.0",
            "new_user":1,
            "install_id":4286******3,
            "iid":***********,
            "idfa":"95******-87D6-F152-04F1-88B******418",
            "device_type":"iPhone8.1",
            "device_platform":"iphone",
            "openudid":"b9f9a7c2c9******45c9aafec7b******24cc6",
            "device_id":57000******
        },
        "success":true
    }
    >>> device = trio.run(get_device) # doctest: +ELLIPSIS
    >>> print(device['device_type'])
    iPhone8,1
    '''
    url = f"{_API}/douyin/device/new/version/{version}" if version else "{_API}/douyin/device/new"
    resp = await asks.get(url)
    logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
    return resp.json().get('data', None)


def params2str(params):
    '''拼装请求参数
    >>> print(params2str({'a':1, 'b':1}))
    a=1&b=1
    '''
    return "&".join(["%s=%s" % (k, v) for k, v in params.items()])


async def get_sign(token, query):
    '''使用拼装参数签名
    post https://api.appsign.vip:2688/sign -->
    {
        "token":"TOKEN",
        "query":"通过参数生成的加签字符串"
    }
    >>> data, res = trio.run(get_sign, 'aaa', {"aaa":"aaa"})
    >>> print(res)
    {'success': False, 'error': 'token is error'}
    '''
    assert isinstance(query, dict)
    url = f"{_API}/sign"
    resp = await asks.post(url, json={"token": token, "query": params2str(query)})
    logging.debug(f"post response from {url} is {resp} with body: {trim(resp.text)}")
    return resp.json().get('data', None), resp.json()


def mixString(pwd):
    '''混淆手机号码和密码
    >>> print(mixString('0123456789abcdeefg'))
    35343736313033323d3c6467666160606362
    '''
    return "".join([hex(ord(c) ^ 5)[-2:] for c in pwd])


_available = {"expired": arrow.Arrow(2000, 1, 1, 0, 0, 0), "common_params": None, "token":None}
async def _get_sign_params(force = False):
    '''获取可用的签名参数，由于每次获取后的有效时间是大概60分钟，
    因此此处维护一个带时间戳的字典，如果超过 55min 则重新生成，否则就不重新生成，除非强制刷新'''
    global _available
    if not force and _available['expired'] > arrow.utcnow():
        return _available['common_params'], _available['token']

    device = await get_device()
    common_params = {** device, ** _APPINFO}
    token = await get_token()
    logging.debug(f"new sign params generated, last time is {_available['expired']}")

    _available = {
        "expired" : arrow.utcnow().shift(minutes=55),
        "common_params" : common_params,
        "token" : token
    }
    return _available['common_params'], _available['token']


async def get_signed_params(params):
    '''给请求 params 签名'''
    assert isinstance(params, dict)
    common_params, token = await _get_sign_params()
    query_params = {**params, ** common_params}
    signed, _ = await get_sign(token, query_params)
    return {**query_params, **signed}



# 异步下载/保存器
class AsyncDownloader(object):
    def __init__(self, save_dir):
        super(AsyncDownloader, self).__init__()
        self.save_dir = save_dir
        os.system("mkdir -p %s" % save_dir)
        
    async def download_file(self, url, headers=IPHONE_HEADER, timeout=DOWNLOAD_TIMEOUT, res_time=RETRIES_TIMES):
        if res_time <= 0: # 重试超过了次数
            return None
        try:
            res = await asks.get(url, headers=headers, timeout=timeout, retries=3)
        except (trio.BrokenResourceError, trio.TooSlowError, asks.errors.RequestTimeout) as e:
            logging.error("download from %s fail]err=%s!" % (url, e))
            await trio.sleep(random.randint(1, 5)) # for scheduler
            return await self.download_file(url, referer, res_time-1)
        
        if res.status_code not in [200, 202]:
            logging.warn(f"download from {url} fail]response={res}")
            await trio.sleep(random.randint(3, 10))
            return await self.download_file(url, referer, res_time-1)
        return res.content

    def is_file_downloaded(self, name):
        file_path = os.path.join(self.save_dir, name)
        return os.path.exists(file_path)

    # 异步文件保存
    async def save_file(self, name, content):
        file_path = os.path.join(self.save_dir, name)
        fd = await trio.open_file(file_path, 'wb')
        await fd.write(content)
        await fd.aclose()




if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)  # verbose=True shows the output
    logging.info("doctest finished.")





