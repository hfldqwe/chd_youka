#!/usr/bin/env python
# coding:utf-8
import asyncio
import aiohttp
import json
# import requests
from aiohttp import request
from hashlib import md5

class Chaojiying_Client(object):
    def __init__(self, username, password, soft_id):
        self.username = username
        password =  password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    async def PostPic(self, im, codetype, client):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile':im}
        params.update(files)
        async with client.post(url='http://upload.chaojiying.net/Upload/Processing.php', data=params, headers=self.headers) as response:
            return await response.json()

    # def ReportError(self, im_id):
    #     """
    #     im_id:报错题目的图片ID
    #     """
    #     params = {
    #         'id': im_id,
    #     }
    #     params.update(self.base_params)
    #     r = request("POST",url='http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
    #     return r.json()

if __name__ == '__main__':
    async def main():
        async with aiohttp.ClientSession() as client:
            code = await chaojiying.PostPic(im, '4004', client)
            print(code)
            return code

    chaojiying = Chaojiying_Client(config.code_username, config.code_password, config.code_soft_id)  #用户中心>>软件ID 生成一个替换 96001
    im = open('test.png', 'rb').read()                     #本地图片文件路径 来替换 a.jpg 有时WIN系统须要//

    # asyncio.run(main())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())                 #1902 验证码类型  官方网站>>价格体系 3.4+版 print 后要加()

