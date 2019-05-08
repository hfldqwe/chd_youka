from configparser import ConfigParser

from hfldtools.other import Settings


class Config(Settings):
    '''
    用来配置爬虫的相关项
    '''
    def __init__(self):
        if not hasattr(self,"config"):
            self.config = True   # 是否进行了配置初始化

            # 获取超级鹰的账号密码和软件id
            config = ConfigParser()
            config.read("/home/py/project/chd_youka/async_spider/info.ini")
            self.code_username=config.get("chaojiying","username")
            self.code_password=config.get("chaojiying", "password")
            self.code_soft_id=config.get("chaojiying", "soft_id")

            settings = dict(
                debug = True,
            )
            super().__init__(**settings)

    def debug_event(self):
        config = ConfigParser()
        config.read("/home/py/project/chd_youka/async_spider/info.ini")
        self.username = config.get("user","username")
        self.password = config.get("user","password")

class Url():
    '''
    用于记录优卡的链接
    '''
    @property
    def headers(self):
        headers = {
            'Host': 'api.xzxyun.com',
            'Connection': 'keep-alive',
            'Accept': '*/*',
            'Origin': 'http://api.xzxyun.com',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://api.xzxyun.com/Account/Login',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        }

        return headers

    def login_url(self):
        '''
        返回登陆的地址，
        :return:
        '''
        return "http://api.xzxyun.com/Account/Login"

    def root_url(self):
        '''
        :return: 优卡根目录
        '''
        return "http://api.xzxyun.com"

    def info_url(self):
        '''
        基本信息
        :return:基本信息目录
        '''
        return "http://api.xzxyun.com/SynCard/Manage/BasicInfo"

    def current_record_url(self):
        '''
        当天消费记录
        :return:
        '''
        return "http://api.xzxyun.com/SynCard/Manage/CurrentDayTrjn"

    def history_record_url(self):
        '''
        指定日期的消费记录查询
        :return:
        '''
        return "http://api.xzxyun.com/SynCard/Manage/TrjnHistory"

config = Config()
url = Url()