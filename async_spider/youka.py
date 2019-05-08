import aiohttp
import asyncio
from lxml import etree
import base64
import logging

from async_spider.config import url,config
from async_spider.chaojiying import Chaojiying_Client
from hfldtools.cookies import Cookies
from hfldtools.other import ReadConfig

jar = aiohttp.CookieJar(unsafe=True)
cookies_manage = Cookies(cookies_type="youka",**ReadConfig(filenames="/home/py/project/chd_youka/async_spider/info.ini").get_dict("redis_236"))

class Parse():
    def parse_index(self,text):
        '''
        用于解析首页
        :param text: 抓取到的文本
        :return: cpatcha_url, 一个由元组构成的列表(元组由两个元素组成 (代号，学校名称))
        '''
        html = etree.HTML(text)
        school = html.xpath("//select[@id='SchoolCode']/option")
        captcha_url = html.xpath("//img[@id='imgCheckCode']/@src")
        return captcha_url[0], [(i.xpath(".//@value")[0],i.xpath(".//text()")[0]) for i in school]

    async def parse_captcha(self, content, client):
        '''
        解析验证码
        :return: <int> or <str> a code
        '''
        chaojiying = Chaojiying_Client(config.code_username, config.code_password, config.code_soft_id)
        code = await chaojiying.PostPic(content, '4004', client)
        return code.get("pic_str")

    def parse(self, text):
        '''
        对于数据(基本信息，消费记录，历史消费情况)基本解析处理
        :param text:
        :return: [('姓名', '董盛'), ('学工号', '2017905714'), ('校园卡余额', '52.64'), ('银行卡号', '6216*********5794'), ('银行卡余额', '0'), ('当前过渡余额', '0.00'), ('上次过渡余额', '0.00'), ('挂失状态', '正常卡'), ('冻结状态', '正常'), ('身份类型', '本科生'), ('部门名称', '2017260101')]
        '''
        html = etree.HTML(text)
        result = html.xpath("//table[@class='mobileT']//tr")
        info = [i.xpath("string(./td[@class='second'])") for i in result]

        # 提取出基本信息之后，进一步进行处理，主要是起到空格
        info = [item.strip() for item in info]
        return info

    def parse_info(self, text):
        '''
        解析出基本信息
        :param text:
        :return:{
            "name":"董盛","student_id":"201790xxxx","over":"52.64","bank_card":"6216*********5794",
            "status":{'挂失状态': '正常卡', '冻结状态': '正常', '身份类型': '本科生'},
        }
        '''
        pass
        info = self.parse(text)
        [name, student_id, over, bank_card],[loss, freeze, identity] = info[0:4], info[7:10]

        return {
            "name":name,"student_id":student_id,"over":over,"bank_card":bank_card,
            "status":{'挂失状态': loss, '冻结状态': freeze, '身份类型': identity},
        }

    def parse_current_record(self, text):
        '''
        解析消费记录
        :param text:
        :return:
        '''
        record = self.parse(text)
        record_orgs = [record[i:i+5] for i in range(0,len(record),5)]
        return [{"time":record_org[0],"place":record_org[1], "cost":record_org[3], "balance":record_org[4], "ykt_id":None} for record_org in record_orgs]


    def parse_history_record(self, text):
        '''
        解析历史消费记录
        :param text:
        :return:
        '''
        return self.parse_current_record(text)

class Prepare():
    def login_data(self,username, password, captcha, schoolcode='xahu', signtype='SynSno'):
        '''
        构造登陆使用的参数
        :return:data
        '''
        data = {
            'CheckCode': captcha,  # 这个字段必须，为验证码字段
            'NextUrl': "",
            'openid': '',
            'Password': base64.b64encode(password.encode('utf-8')).decode(),
            'SchoolCode': schoolcode,
            'SignType': signtype,   # 默认使用学工号进行登陆
            'UserAccount': username,
        }
        return data

    def history_record_data(self, beginTime, endTime):
        '''
        历史消费记录data
        :param beginTime:
        :param endTime:
        :return: data
        '''
        data = {
            "beginTime":beginTime,
            "endTime":endTime,
        }
        return data

class Spider(Parse, Prepare):
    async def get_index(self,client):
        '''
        爬取首页
        :return:self.parse_index(result)
        '''
        async with client.get(url.login_url(), headers=url.headers) as resp:
            result = await resp.text()
            return self.parse_index(result)

    async def captcha(self,client):
        '''
        爬取验证码
        :return:self.parse_captcha(content)
        '''
        captcha_url, _ = await self.get_index(client)
        async with client.get(url.root_url()+captcha_url,headers=url.headers) as resp:
            content = await resp.read()
            code = await self.parse_captcha(content,client)
            return code, resp.cookies

    async def login(self, client, username, password, schoolcode='xahu', signtype='SynSno'):
        '''
        进行登陆
        :return:cookies(如果登陆失败返回None)
        '''
        captcha, cookies = await self.captcha(client)
        data = self.login_data(username, password, captcha, schoolcode=schoolcode, signtype=signtype)
        print(data)
        async with client.post(url.login_url(), headers=url.headers, data=data) as resp:
            result = await resp.json()
            print(result)
            # 判断是否登陆成功
            if result['success'] == True:
                cookies = {key:value.value for key,value in resp.cookies.items()}
                return cookies

    async def info(self, client, cookies):
        '''
        爬取基本信息
        :param client:
        :param cookies: 登陆后的cookies
        :return:
        '''
        async with client.get(url.info_url(), headers=url.headers, cookies=cookies) as resp:
            text = await resp.text()
            return self.parse_info(text)

    async def current_record(self, client, cookies):
        '''
        爬取用户当天消费记录
        :param client:
        :param cookies:
        :return:
        '''
        async with client.get(url.current_record_url(), headers=url.headers, cookies=cookies) as resp:
            text = await resp.text()
            return self.parse_current_record(text)

    async def history_record(self, client, cookies, beginTime, endTime):
        '''
        爬取历史消费
        :param client:
        :param cookies:
        :return:
        '''
        async with client.get(url.history_record_url(), headers=url.headers, cookies=cookies, params=self.history_record_data(beginTime,endTime)) as resp:
            text = await resp.text()
            return self.parse_history_record(text)

async def get_cookies(client, username, password):
    '''
    用于获取cookies以及保存cookies
    :param client: 客户端
    :param username: 账号
    :param password: 密码
    :return: cookies
    '''
    cookies = cookies_manage.get(username)
    spider = Spider()

    for i in range(3):
        ''' 登录失败可以进行三次重试 '''
        if cookies:
            try:
                info = await spider.info(client=client, cookies=cookies)

                # 验证cookies是否有效
                if info.get("student_id") == str(username):
                    cookies_manage.set(username=username,cookies=dict(cookies))
                    return cookies
            except:
                logging.log("cookies过期")
        else:
            cookies = await spider.login(client=client, username=username, password=password)




if __name__ == '__main__':
    spider = Spider()
    parse = Parse()

    username = config.username
    password = config.password

    async def main():
        async with aiohttp.ClientSession(cookie_jar=jar) as client:
            # result = await spider.get_index(client)

            # code = await spider.captcha(client)

            # cookies = await spider.login(client, username=username, password=password)
            cookies = await get_cookies(client,username,password)
            print(cookies)

            info = await spider.info(client, cookies)
            print(info)

            current_record = await spider.current_record(client, cookies)
            print(current_record)

            history_record = await spider.history_record(client, cookies, beginTime="2019 02 17", endTime="2019 03 17")
            print(history_record)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
