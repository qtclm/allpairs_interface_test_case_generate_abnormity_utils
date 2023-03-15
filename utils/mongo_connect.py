# _*_ coding: UTF-8 _*_
"""
@file            : mongo_connect
@Author          : qtclm
@Date            : 2023/1/29 19:44
@Desc            : 自动生成接口测试用例：支持正交实验，等价类，边界值
"""

from utils.mongo_public import operationMongo
from utils.operation_yaml import operationYaml

class Config(object):
    def __init__(self,file_path='config',file_name='config.yaml'):
        config=operationYaml(file_path=file_path,file_name=file_name).read_data()
        self.dataBaseConfig=config['config']

class mongo_tencentcloud(operationMongo,Config):
    def __init__(self):
        Config.__init__(self)
        host=self.dataBaseConfig['tencent_cloud_mongodb']['host']
        user=self.dataBaseConfig['tencent_cloud_mongodb']['user']
        password=self.dataBaseConfig['tencent_cloud_mongodb']['password']
        port=self.dataBaseConfig['tencent_cloud_mongodb']['port']
        db='creeper_test'
        super(mongo_tencentcloud,self).__init__(host=host,user=user,password=password,port=port,db=db)
        # print('链接成功')


if __name__=='__main__':
    # gld=Mongo_gldexp()
    # print(gld.select_all_collection('dwd_gw_order_geo_dtl_i_d_1',{"commercial_id":810016429},{"trade_id":1,'brandId':1}))
    gld_exp=mongo_tencentcloud()
    print(gld_exp.select_all_collection('partnerShopInfo',{"source":-92},{"shopId":0,'brandId':0,"_id":0} ,sort_col=[()]) )
    # Mongo_tencentcloud()