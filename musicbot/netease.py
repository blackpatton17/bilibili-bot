# !/usr/bin/python
# -*- coding:utf-8 -*-
# time: 2022/02/07
# author = 'blackpatton17'


'''
Program: Netease capability

20220207 program init
'''

import aiohttp
import aiofiles
import asyncio
import shutil

import logging
import time, hashlib, urllib.request, re, json
from moviepy.editor import *
import os, sys, threading
from .exceptions import DownloadError, HTTPError, NeteaseError
from .constants import AUDIO_CACHE_PATH

import imageio

imageio.plugins.ffmpeg.download()

log = logging.getLogger(__name__)




async def get_music_metadata(mid):
    start_url = f'http://localhost:3000/song/detail?ids={mid}'

    async with aiohttp.ClientSession() as session:
        async with session.get(start_url) as resp:
            resp_json = await resp.json()
            return resp_json['songs'][0]


# download music
# TODO: support for playlist
async def _down_music(filename, start_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(start_url) as resp:
            if resp.status >= 200 and resp.status < 300:
                resp_json = await resp.json()
                download_url = resp_json["data"][0]["url"]
                # 开始下载
                async with session.get(download_url) as resp:
                    if resp.status >= 200 and resp.status < 300:
                        # 写入本地文件
                        f = await aiofiles.open(os.path.join(AUDIO_CACHE_PATH, r'{}.mp3'.format(filename)), mode='wb')
                        await f.write(await resp.read())
                        await f.close()
                    else:
                        filename = r'{}.mp3'.format(filename)
                        raise DownloadError("Download Fail for %s with status code %s" % (filename, resp.status))
            else:
                raise DownloadError(f"Fetch Download URL for {filename} with status code {resp.status}")

# 下载主入口
# quality: 80, 64, 32, 16
async def download(mid, path=None):
    start_time = time.time()

    data = await get_music_metadata(mid)
    start_url = f'http://localhost:3000/song/url?id={mid}'

    mid_item = data
    log.info(mid_item)

    cid = str(mid_item['id'])
    title = mid_item['name']

    filename = '{}_{}'.format(mid, title)
    if not path:
        path = AUDIO_CACHE_PATH  # 下载目录
    full_video_path = os.path.join(path, filename + '.mp3')

    # 检测视频文件是否已经存在
    if os.path.exists(full_video_path) and os.path.isfile(full_video_path):
        return filename + '.mp3'

    log.info(f'[下载音乐的mid]:{mid}')
    log.info(f'[下载音乐的标题]:{title}')
    log.info(f'[下载音乐至目录]:{path}')
    await _down_music(filename, start_url)

    # 最后合并视频
    log.info(filename)
    end_time = time.time()  # 结束时间
    log.info('下载总耗时%.2f秒,约%.2f分钟' % (end_time - start_time, int(end_time - start_time) / 60))

    return filename + '.mp3'