# filename : main.py
import aiohttp
import json
from async_spider.youka import Spider
from tornado.web import RequestHandler

from async_spider.youka import get_cookies

spider = Spider()
jar = aiohttp.CookieJar()
client = aiohttp.ClientSession(cookie_jar=jar)

class TestHandler(RequestHandler):
    '''
    一个用于测试的handler
    '''
    def get(self):
        self.write("服务器正常启动")

class BaseHandler(RequestHandler):
    ''' 作为一个基类，写入公共方法 '''
    @property
    async def cookies(self):
        '''
        返回用户的cookies
        :return:
        '''
        if not hasattr(self,"_cookies"):
            username = self.get_argument("username", None)
            password = self.get_argument("password", None)
            self._cookies = await get_cookies(client=client, username=username, password=password)
        return self._cookies


class InfoHandler(BaseHandler):
    ''' 返回个人信息 '''
    async def post(self):
        try:
            data = await spider.info(client=client, cookies=await self.cookies)
            result = {"message":"success","status":200,"data":data}
            self.write(json.dumps(result,ensure_ascii=False))
        except:
            self.write({"message":"false"})

class CurrentRecordHandler(BaseHandler):
    ''' 当前的消费记录 '''
    async def post(self):
        try:
            data = await spider.current_record(client=client, cookies=await self.cookies)
            print(await self.cookies)
            result = {"message":"success","status":200,"data":data}
            self.write(json.dumps(result,ensure_ascii=False))
        except:
            self.write({"message":"false"})


class HistoryRecordHandler(BaseHandler):
    ''' 历史消费记录 '''
    async def post(self):
        '''
        beginTime="2019 02 17", endTime="2019 03 17"
        :return:
        '''
        beginTime = self.get_argument("beginTime")
        endTime = self.get_argument("endTime")

        try:
            data = await spider.history_record(client=client, cookies=await self.cookies, beginTime=beginTime,
                                               endTime=endTime)
            result = {"message":"success","status":200,"data":data}
            self.write(json.dumps(result,ensure_ascii=False))
        except:
            self.write({"message":"false"})