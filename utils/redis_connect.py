# _*_ coding: UTF-8 _*_
"""
@project -> file : city-test -> rr
@Author          : qinmin.vendor
@Date            : 2023/1/29 19:44
@Desc            :
"""


from utils.redis_public import operationRedis
from utils.operation_yaml import operationYaml

class Config(object):
    def __init__(self,file_path='config',file_name='config.yaml'):
        config=operationYaml(file_path=file_path,file_name=file_name).read_data()
        self.dataBaseConfig=config['config']

class redis_qa(operationRedis,Config):
    def __init__(self):
        Config.__init__(self)
        tencent_cloud_redis=self.dataBaseConfig['redis_conf']
        tencent_cloud_redis['db'] = 0
        super(redis_qa,self).__init__(**tencent_cloud_redis)



if __name__=="__main__":
    # re=Redis_tencentcloud()
    # print(re.hash_getvalues('py'))
    pass

