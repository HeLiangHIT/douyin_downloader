#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-10-17 22:12:00
# @Author  : He Liang (heianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT

'''
ref1: https://github.com/AppSign/douyin  抖音通信协议 2.9.1版本协议签名
ref2: https://github.com/hacksman/spider_world 抖音爬虫例子
'''

import trio, asks, logging, json, time, os
asks.init('trio')

logging.basicConfig(level=logging.DEBUG, 
    format='%(asctime)s %(filename)s:%(lineno)d %(threadName)s:%(funcName)s %(levelname)s] %(message)s')

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
IPHONE_HEADER = {"User-Agent": "Aweme/2.8.0 (iPhone; iOS 11.0; Scale/2.00)"}


def trim(text, max_len = 50, suffix = '...'):
    '''为避免打印的日志过长，可以使用该函数裁剪一下'''
    text = text.replace('\n', '')
    return f"{text[:max_len]} {suffix}" if len(text) > max_len else text


async def getToken(version=_APPINFO['version_code']):
    '''获取Token: 有效期60分钟
    get https://api.appsign.vip:2688/token/douyin -> 
    {
        "token":"5826aa5b56614ea798ca42d767170e74",
        "success":true
    }
    >>> token = trio.run(getToken) # doctest: +ELLIPSIS
    >>> print(len(token))
    32
    '''
    url = f"{_API}/token/douyin/version/{version}" if version else f"{_API}/token/douyin"
    resp = await asks.get(url)
    logging.debug(f"get response from {url} is {resp} with body: {trim(resp.text)}")
    return resp.json().get('token', None)


async def getDevice(version=_APPINFO['version_code']):
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
    >>> device = trio.run(getDevice) # doctest: +ELLIPSIS
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


async def getSign(token, query):
    '''使用拼装参数签名
    post https://api.appsign.vip:2688/sign -->
    {
        "token":"TOKEN",
        "query":"通过参数生成的加签字符串"
    }
    >>> data, res = trio.run(getSign, 'aaa', {"aaa":"aaa"})
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


async def _get_sign_params(force = False):
    '''获取可用的签名参数，由于每次获取后的有效时间是大概60分钟，因此'''
    device = await getDevice()
    token = await getToken()
    return {** device, ** _APPINFO}, token


async def get_signed_params(params):
    '''给请求 params 签名'''
    assert isinstance(params, dict)
    common_params, token = await _get_sign_params()
    query_params = {**params, ** common_params}
    signed, _ = await getSign(token, query_params)
    return {**query_params, **signed}



if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False)  # verbose=True shows the output
    logging.info("doctest finished.")





