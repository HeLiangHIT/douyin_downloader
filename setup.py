#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-10-21 10:29:28
# @Author  : He Liang (heianghit@foxmail.com)
# @Link    : https://github.com/HeLiangHIT


from setuptools import setup
import codecs, os

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()

setup(
    name='douyin_downloader', #pypi中的名称，pip或者easy_install安装时使用的名称
    version='1.0.1',
    py_modules=['util', 'douyin_tool', 'douyin_downloader'], # 需要打包的 Python 单文件列表
    url='https://github.com/HeLiangHIT/douyin_downloader',
    license='GPLv3',
    author='He Liang',
    author_email='heianghit@foxmail.com',
    keywords="douyin trio",
    install_requires=[ # 需要安装的依赖
        'arrow>=0.12.1',
        'asks>=2.2.0',
        'trio>=0.9.0',
    ],
    # packages = [], # 需要处理的包目录

    description='The douyin video downloader',
    long_description=read('README.md'),
    # 添加这个选项，在 windows 下Python目录的 scripts 下生成exe文件，注意：模块与函数之间是冒号:
    entry_points={'console_scripts': [
        'douyin_downloader = douyin_downloader:cmd_run',
    ]},
    # 此项需要，否则卸载时报windows error
    zip_safe=False,

    classifiers=[ # 程序的所属分类列表
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
    ],
    extras_require={},
)