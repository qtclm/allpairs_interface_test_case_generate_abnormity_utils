# _*_ coding: UTF-8 _*_
"""
@project -> file : city-test -> rr
@Author          : qinmin.vendor
@Date            : 2023/1/29 19:44
@Desc            : 自动生成接口测试用例：支持正交实验，等价类，边界值
"""

import sys
import time

sys.path.append('../../')
from api_case_generate_tools.utils.mysql_public import operationMysql
from api_case_generate_tools.utils.operation_yaml import operationYaml
import pymysql

class Config(object):
    def __init__(self,env='qa'):
        if not env in('qa','dev'):
            raise Exception("不支持的环境配置")
        config=operationYaml().read_data()
        self.dataBaseConfig=config['config'][env]

class mysql_qa(operationMysql,Config):
    def __init__(self,db_name='hope_saas_bms'):
        Config.__init__(self)
        tencent_cloud_mysql_conf=self.dataBaseConfig['mysql_conf_qa']
        tencent_cloud_mysql_conf['db'] = db_name
        tencent_cloud_mysql_conf["cursorclass"]=pymysql.cursors.DictCursor
        # print(tencent_cloud_mysql_conf)
        super().__init__(**tencent_cloud_mysql_conf)

class mysql_reg(operationMysql,Config):
    def __init__(self,db_name='hope_saas_bms'):
        Config.__init__(self)
        tencent_cloud_mysql_conf=self.dataBaseConfig['mysql_conf_reg']
        tencent_cloud_mysql_conf['db'] = db_name
        tencent_cloud_mysql_conf["cursorclass"]=pymysql.cursors.DictCursor
        super().__init__(**tencent_cloud_mysql_conf)


class mysql_prod(operationMysql,Config):
    def __init__(self):
        Config.__init__(self)
        tencent_cloud_mysql_conf=self.dataBaseConfig['mysql_conf_prod']
        tencent_cloud_mysql_conf['db'] = 'hope_saas_oms'
        tencent_cloud_mysql_conf["cursorclass"]=pymysql.cursors.DictCursor
        super().__init__(**tencent_cloud_mysql_conf)

class mysql_prod_bms(operationMysql,Config):
    def __init__(self):
        Config.__init__(self)
        tencent_cloud_mysql_conf=self.dataBaseConfig['mysql_conf_prod_bms']
        tencent_cloud_mysql_conf['db'] = 'hope_saas_bms'
        tencent_cloud_mysql_conf["cursorclass"]=pymysql.cursors.DictCursor
        # print(tencent_cloud_mysql_conf)
        super().__init__(**tencent_cloud_mysql_conf)

if __name__=="__main__":
    pd=mysql_qa(db_name='hope_saas_audit')

    start_time=time.time()
    sql_str=''' INSERT INTO `hope_saas_audit`.`aud_shipping_order_audit_process_detail`( `shipping_order_process_no`,`shipping_order_no`, `shipping_status`, `weight`, `volumn`, `quantity`, `value`, `unit`, `create_time`, `update_time`, `create_user`, `update_user`, `user_id`, `del_flag`, `tenant_code`, `back_reason`, `back_explain`, `status`, `back_status`, `signing_time`, `vehicle_owner_ship`, `original_value`, `plan_original_value`, `plan_value`, `reassignment_type`, `estimate_detail`, `dispatch_person`, `contract_code`)
VALUES ( 'ASOP20220706_%s','test_20220706_%s', 4, 30.0000, 30.0000, 30.0000, 700.0000, NULL, '2020-04-22 16:30:54', '2021-06-11 22:25:10', '超级用户', '秦敏', 'T10', 1, 'YLGYS20042100000000002', '3232', NULL, 3, 1, '2020-04-22 16:30:54', NULL, 0.00000, 0.00000, 0.00000, 'NORMAL', '{}', '', '') ; '''
    list1=[(i,i) for i in range(1000)]
    pd.sql_batch(sql_select=sql_str,data_list=list1)
    print(f"执行耗时：{time.time()-start_time}")
