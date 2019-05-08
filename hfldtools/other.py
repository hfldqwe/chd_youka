from configparser import ConfigParser

class Single():
    ''' 单例模式 '''
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,"_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

class Settings(Single):
    ''' 配置类 '''
    def __init__(self,*args,**kwargs):
        self.set(**kwargs)
        if hasattr(self,"debug") and self.debug:
            self.debug_event()

    def set(self,**kwargs):
        ''' 设置属性 '''
        for key,value in kwargs.items():
            setattr(self,key,value)

    def debug_event(self):
        '''
        一个虚拟方法，开启debug必须实现的一个方法
        :return:
        '''
        raise ArithmeticError("没有找到debug_event这个属性")

class ReadConfig():
    '''
    用于读取配置
    '''
    def __init__(self, filenames):
        '''
        :param filenames: 可以是单个文件，也可以是包含多个文件名的列表
        '''
        self.config = ConfigParser()
        self.config.read(filenames=filenames)

    def get_all_dict(self):
        '''
        所有的配置，由两层字典组成。
        :return: a OrderedDict {section_1:{option_1:value_1,...}...}
        '''
        return self.config._sections

    def get_dict(self, section):
        '''
        将一个节点（section）中所有参数读取成一个字典
        :param section: 节点名称
        :return: a OrderedDict {option_1 : value_1, option_2 : value_2...}
        '''
        return self.config._sections.get(section)

    def get_value(self, section, option):
        '''
        读取一个具体的参数
        :return: a str value
        '''
        return self.config.get(section=section, option=option)

    def dict_covert_object(self, config_dict):
        '''
        将字典转化成一个配置实例的属性
        :param config_dict: 包含配置的字典
        :return: config_object
        '''
        config_object = object()
        for k, v in config_dict.items():
            setattr(config_object, k, v)
        return config_object

    def get_object(self, section):
        '''
        类似get_dict，只不过是以一个实例的形式返回，对应的配置在实例的属性中
        使用的方式：
            ```
            config = ReadConfig(filename)
            info = config.get_object(section)
            print(info.option)
            ```
        :param section: 节点的名称
        :return: config_object
        '''
        return self.dict_covert_object(self.get_dict(section=section))

if __name__ == '__main__':
    config = ReadConfig("/home/py/project/chd_youka/async_spider/info.ini")
    params = config.get_dict("redis_236")
    print(params.items())
    print(params)