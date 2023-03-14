# _*_ coding: UTF-8 _*_
"""
@project -> file : city-test -> rr
@Author          : qinmin.vendor
@Date            : 2023/1/29 19:44
@Desc            :
"""

import collections
import json
import os
import traceback
from ruamel import yaml
from utils.other_util import otherUtil
from utils.operation_logging import operationLogging


class operationYaml(object):
    log = operationLogging('yaml_log')

    def __init__(self, file_path, file_name):
        yaml_path = os.path.join(otherUtil.project_rootpath, file_path)
        self.file_path = os.path.join(yaml_path, file_name)

    # 获取所有数据
    def read_data(self, mode='r', out_dict=False):
        """ 读取yaml里面里面的数据"""
        try:
            with open(self.file_path, mode, encoding='utf-8') as f:
                yaml_info = yaml.round_trip_load(f)  # , Loader=yaml.Loader
                if out_dict:
                    yaml_info = json.loads(json.dumps(yaml_info))
                return yaml_info
        except:
            self.log.log_main('error', False, f'读取yaml文件失败,具体错误\n:{traceback.format_exc()}')
            return False

    # 通过key递归获取对应的值
    def readDataForKey(self, key=None, yaml_data=None):
        datas = self.read_data()
        # print(logs().out_varname(datas))
        # for循环字典这一层的所有key值
        if datas:
            if key:
                if yaml_data is None:
                    yaml_data = datas
                else:
                    yaml_data = yaml_data
                # print(yaml_data)
                for i in list(yaml_data.keys()):
                    # 如果当前的key是我们要找的
                    if i == key:
                        return yaml_data[i]
                    # 如果当前的key不是我们找的key，并且是字典类型
                    elif isinstance(yaml_data[i], dict):
                        # 使用递归方法，查找下一层的字典
                        return self.readDataForKey(key, yaml_data[i])
                    else:
                        continue
            else:
                pass
        else:
            return None

    # 只有一层的字典适用
    def readforKey_onetier(self, key=None):
        datas = self.read_data()
        if datas:
            if key:
                for i in datas.keys():
                    if i == key:
                        return datas[i]
                    else:
                        continue
            else:
                return None
        else:
            return None

    # 更新文件数据
    def write_yaml(self, data, mode='w'):
        """ 往yaml里面写入数据
            yamlFile：yaml文件名
            road_data：要写入的数据
            mode：写入方式： w，覆盖写入， a，追加写入
            将原数据读取出来，如果没有要加入的key，则创建一个，如果有，则执行key下面的数据修改
        """
        old_data = self.read_data()
        new_data = data
        if new_data == {} or new_data == [] or new_data == '':
            self.log.log_main('info', False, '写入数据为空，跳过写入')
            return None
        if old_data and isinstance(old_data, dict):
            # collections.ChainMap - -将多个映射合并为单个映射
            # 如果有重复的键，那么会采用第一个映射中的所对应的值
            d = dict(collections.ChainMap(new_data, old_data))
            self.write_data(d)
            # 重新赋值给实例，不然数据写入的数据不会生效
        else:
            # 如果old_data为空，直接写入传入的数据
            self.write_data(new_data)

    # 写入数据基础方法
    def write_data(self, data, mode='w'):
        try:
            with open(self.file_path, mode, encoding="utf-8") as f:
                # yaml.dump(road_data, f, Dumper=yaml.RoundTripDumper)
                yaml.round_trip_dump(data, f, default_style=False)
                return True
        except:
            self.log.log_main('error', False, f'yaml文件写入失败，错误如下：\n{traceback.format_exc()}')

            return False


if __name__ == "__main__":
    ym = operationYaml(file_path='config', file_name='config.yaml')
