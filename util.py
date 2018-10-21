#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-10-17 22:12:00
# @Author  : He Liang (heianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT

'''
ref1: https://github.com/AppSign/douyin  抖音通信协议 2.9.1版本协议签名
ref2: https://github.com/hacksman/spider_world 抖音爬虫例子
'''

import trio, asks, logging, json, time, os, arrow, socket, random
asks.init('trio')

logging.basicConfig(level=logging.INFO, 
    format='%(asctime)s %(filename)s:%(lineno)d %(threadName)s:%(funcName)s %(levelname)s] %(message)s')
IPHONE_HEADER = {"User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"}
CURL_TIMEOUT = 60
DOWNLOAD_TIMEOUT = 600
RETRIES_TIMES = 5

# 基本配置
_API = "https://api.appsign.vip:2688"
APPINFO = {
    "version_code": "2.7.0",
    "app_version": "2.7.0",
    "channel": "App%20Stroe",
    "app_name": "aweme",
    "build_number": "27014",
    "aid": "1128",
}
'''
APPINFO = {
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

def fname_normalize(name, del_char=' /~!@#$%^&*()\\[]}{|'):
    '''规范化文件名称'''
    for c in del_char:
        name = name.replace(c, '')
    return name


def params2str(params):
    '''拼装请求参数
    >>> print(params2str({'a':1, 'b':1}))
    a=1&b=1
    '''
    return "&".join(["%s=%s" % (k, v) for k, v in params.items()])


def mixString(pwd):
    '''混淆手机号码和密码
    >>> print(mixString('0123456789abcdeefg'))
    35343736313033323d3c6467666160606362
    '''
    return "".join([hex(ord(c) ^ 5)[-2:] for c in pwd])


def user_input(msg, choices=[], default='', retries=3):
    '''用户输入验证'''
    res = input(msg)
    if len(res) == 0:
        return default
    if choices and res not in choices:
        if retries-1 <= 0:
            print("Byebye! Stubborn man!")
            exit(-1)
        print(f'Choose one of {choices}, please!', end=' ')
        return user_input(msg, choices, retries-1)
    return res


class SignUtil(object):
    """抖音签名请求专用"""
    def __init__(self, version=APPINFO['version_code']):
        super(SignUtil, self).__init__()
        self.version = version
        self.sign = {"expired": arrow.Arrow(2000, 1, 1, 0, 0, 0), "common_params": None, "token":None}
        self.s = asks.Session(_API, connections=5)
        
    async def get_token(self):
        '''获取Token: 有效期60分钟
        get https://api.appsign.vip:2688/token/douyin -> 
        {
            "token":"5826aa5b56614ea798ca42d767170e74",
            "success":true
        }
        >>> token = trio.run(SignUtil().get_token) # doctest: +ELLIPSIS
        >>> print(len(token))
        32
        '''
        url = f"{_API}/token/douyin/version/{self.version}" if self.version else f"{_API}/token/douyin"
        resp = await self.s.get(url)
        logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
        return resp.json().get('token', '')

    async def get_device(self):
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
        >>> device = trio.run(SignUtil().get_device) # doctest: +ELLIPSIS
        >>> print(device['device_type'])
        iPhone8,1
        '''
        url = f"{_API}/douyin/device/new/version/{self.version}" if self.version else "{_API}/douyin/device/new"
        resp = await self.s.get(url)
        logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
        return resp.json().get('data', {})

    async def get_sign(self, token, query):
        '''使用拼装参数签名
        post https://api.appsign.vip:2688/sign -->
        {
            "token":"TOKEN",
            "query":"通过参数生成的加签字符串"
        }
        >>> data, res = trio.run(SignUtil().get_sign, 'aaa', {"aaa":"aaa"})
        >>> print(res)
        {'success': False, 'error': 'token is error'}
        '''
        assert isinstance(query, dict)
        url = f"{_API}/sign"
        resp = await self.s.post(url, json={"token": token, "query": params2str(query)})
        logging.debug(f"post response from {url} is {resp} with body: {trim(resp.text)}")
        return resp.json().get('data', {}), resp.json()

    async def get_sign_params(self, force=False):
        '''获取可用的签名参数，由于每次获取后的有效时间是大概60分钟，
        因此此处维护一个带时间戳的字典，如果超过 55min 则重新生成，否则就不重新生成，除非强制刷新'''
        if not force and self.sign['expired'] > arrow.utcnow():
            return self.sign['common_params'], self.sign['token']

        device = await self.get_device()
        common_params = {** device, ** APPINFO}
        token = await self.get_token()
        logging.debug(f"new sign params generated, last time is {self.sign['expired']}")

        self.sign = {
            "expired" : arrow.utcnow().shift(minutes=5), # 实测貌似很快就失效了
            "common_params" : common_params,
            "token" : token
        }
        return self.sign['common_params'], self.sign['token']

    async def get_signed_params(self, params, force = False):
        '''给请求 params 签名'''
        assert isinstance(params, dict)
        common_params, token = await self.get_sign_params(force)
        query_params = {**params, ** common_params}
        signed, _ = await self.get_sign(token, query_params)
        return {**query_params, **signed}

    async def curl(self, url, params, data=None, headers=IPHONE_HEADER, method='GET', retries=2, timeout=CURL_TIMEOUT):
        '''抖音的签名请求函数'''
        if retries <= 0:
            logging.error(f"curl {url} with method={method} failed, return None!")
            return None
        try:
            s_params = await self.get_signed_params(params)
            if method.upper() == 'GET':
                resp = await self.s.get(url, params=s_params, data=data, headers=IPHONE_HEADER, verify=False, timeout=timeout)
            elif method.upper() == 'POST':
                resp = await self.s.post(url, params=s_params, data=data, headers=IPHONE_HEADER, verify=False, timeout=timeout)
            else:
                logging.error(f"undefined method={method} for url={url}")
                return None
            logging.debug(f"curl response from {url} is {resp} with body: {trim(resp.text)}")
            return resp
        except Exception as e:
            logging.warning(f"curl {url} with method={method} failed, retry with new signed params!")
            await self.get_sign_params(True) # force fresh self.sign
            self.s = asks.Session(_API, connections=5) # restart session
            return await self.curl(url, params, data, headers, method, retries-1)


# 异步下载/保存器
class AsyncDownloader(object):
    def __init__(self, save_dir):
        super(AsyncDownloader, self).__init__()
        self.save_dir = save_dir
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
    async def download_file(self, url, headers=IPHONE_HEADER, timeout=DOWNLOAD_TIMEOUT, res_time=RETRIES_TIMES):
        if res_time <= 0: # 重试超过了次数
            return None
        try:
            _url = random.choice(url) if isinstance(url, list) else url
            res = await asks.get(_url, headers=headers, timeout=timeout, retries=3)
        except (socket.gaierror, trio.BrokenResourceError, trio.TooSlowError, asks.errors.RequestTimeout) as e:
            logging.error("download from %s fail]err=%s!" % (url, e))
            await trio.sleep(random.randint(1, 5)) # for scheduler
            return await self.download_file(url, res_time=res_time-1)

        if res.status_code not in [200, 202]:
            logging.warn(f"download from {url} fail]response={res}")
            await trio.sleep(random.randint(3, 10))
            return await self.download_file(url, res_time=res_time-1)
        return res.content

    def is_file_downloaded(self, name):
        file_path = os.path.join(self.save_dir, fname_normalize(name))
        return os.path.exists(file_path)

    # 异步文件保存
    async def save_file(self, name, content):
        file_path = os.path.join(self.save_dir, fname_normalize(name))
        fd = await trio.open_file(file_path, 'wb')
        await fd.write(content)
        await fd.aclose()




if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)  # verbose=True shows the output
    logging.info("doctest finished.")





