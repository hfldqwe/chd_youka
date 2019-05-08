import redis

from hfldtools.other import Single
from collections.abc import MutableMapping

class BaseRedis(Single):
    '''
    BaseRedis只会调用一次，防止多次进行连接浪费资源
    :param info: 一个包含配置的字典或者类
    '''
    def __init__(self, host='localhost', port=6379,
                 db=0, password=None, socket_timeout=None,
                 socket_connect_timeout=None,
                 socket_keepalive=None, socket_keepalive_options=None,
                 connection_pool=None, unix_socket_path=None,
                 encoding='utf-8', encoding_errors='strict',
                 charset=None, errors=None,
                 decode_responses=False, retry_on_timeout=False,
                 ssl=False, ssl_keyfile=None, ssl_certfile=None,
                 ssl_cert_reqs='required', ssl_ca_certs=None,
                 max_connections=None, expire=None,**kwargs):
        if not hasattr(self,"red"):
            self.red = redis.Redis(host=host, port=port,
                 db=db, password=password, socket_timeout=socket_timeout,
                 socket_connect_timeout=socket_connect_timeout,
                 socket_keepalive=socket_keepalive, socket_keepalive_options=socket_keepalive_options,
                 connection_pool=connection_pool, unix_socket_path=unix_socket_path,
                 encoding=encoding, encoding_errors=encoding_errors,
                 charset=charset, errors=errors,
                 decode_responses=decode_responses, retry_on_timeout=retry_on_timeout,
                 ssl=ssl, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile,
                 ssl_cert_reqs=ssl_cert_reqs, ssl_ca_certs=ssl_ca_certs,
                 max_connections=max_connections)

            if expire:
                # 用于指定全局时间
                self.expire = expire

    def set_cookies(self,username,cookies, expire=None):
        ''' 建立cookies '''
        self.red.hmset(username,cookies)

        # 如果没有单独指定expire（过期时间），那么使用全局设置
        expire = expire if expire else self.expire
        if expire:
            self.red.expire(username,expire)

    def get_cookies(self,username):
        ''' 获取cookies '''
        raw_cookies = self.red.hgetall(username)
        if raw_cookies:
            return raw_cookies

class Cookies(BaseRedis):
    def __init__(self, *, cookies_type="unnamed", **info_dict):
        '''
        :param info_dict: 含有redis初始化的信息的字典或者类
        :param cookies_type: cookies的类型或者标记（主要为了防止redis中不同的键重名覆盖）
        '''
        if not isinstance(info_dict, MutableMapping):
            info_dict = info_dict.__dict__
        self.cookies_type = cookies_type
        super(Cookies, self).__init__(**info_dict)

    def set(self, username, cookies, expire=None):
        '''
        将cookies存储在redis中
        :param username: 用户的账号
        :param cookies: 用户的cookies
        :return: None
        '''
        username = str(username) + "_" + self.cookies_type
        self.set_cookies(username=username, cookies=cookies ,expire=expire)

    def get(self,username, cookies_type=None):
        '''
        根据参数，对应的cookies,类型为dict,如果没有返回None
        :param username: cookies的名称
        :param cookies_type: cookies的类型或者标记（主要为了防止redis中不同的键重名覆盖）
        :return: cookies
        '''
        if cookies_type:
            username = str(username)+"_"+cookies_type
        else:
            username = str(username) + "_" + self.cookies_type
        return self.get_cookies(username=username)

if __name__ == '__main__':
    from hfldtools.other import ReadConfig
    config = ReadConfig("/home/py/project/chd_youka/async_spider/info.ini")
    cookies = Cookies(cookies_type="youka" ,**config.get_dict("redis_236"))
    cookies = cookies.get("2017905714",cookies_type="youka")
    print(cookies)
    print(type(cookies))
    # cookies.set("2017905714",cookies={"a":1})