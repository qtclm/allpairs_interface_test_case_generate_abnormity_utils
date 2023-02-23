# _*_ coding: UTF-8 _*_
"""
@project -> file : city-test -> swagger_api_parse_backup
@Author          : qinmin.vendor
@Date            : 2023/1/12 17:55
@Desc            :
"""

import copy
import json
import os.path
import sys
from utils.operation_datas import operationExcel
from utils.request_main import requestMain
from utils.data_util import dataUtil
#将汉字转换拼音： https://blog.csdn.net/weixin_42464956/article/details/110927073
from xpinyin import Pinyin
from utils.wrapper_util import exec_time_wrapper


class swaggerApiParse():
    url='http://10.4.196.168:31621/v2/api-docs'
    # url='https://10.165.61.58:30443/matrix/v2x-device/v1/v2/api-docs'
    requst=requestMain()
    _data=dataUtil()
    _pinyin=Pinyin()

    excel_path=os.path.join(_data.get_project_rootpath(),"test_data","interface")
    excel_name=f'api{"-".join(url.split("/")[3:])}.xlsx'



    api_data=requst.request_main(url=url,method='get',data=None,headers=None).json()
    api = api_data['paths']  # 取swagger文件内容中的path，文件中path是键名
    api_uri_list = []  # 创建接口地址空列表
    api_method_list = []  # 创建请求方式空列表
    api_name_list = []  # 创建接口描述空列表
    api_params_path_list = []
    api_params_path_list_descs = []
    api_params_body_list = []
    api_params_body_list_descs = []
    # 定义响应相关内容
    api_response_key='200'
    api_response_body_list = []
    api_response_body_list_descs = []
    api_uri=""
    # 定义接口参数描述中各个类型的默认值
    api_params_ref_result_properties_type_default={
        "int":0,"integer":0, "number":0,"float":0.0,"double":0.0,
        "null":None,"object":dict(),"set":set(),"string":"","array":[],
        "bool":False,"boolean":False,
    }

    @classmethod
    @exec_time_wrapper(round_num=10,module_obj=__file__,class_obj=sys._getframe().f_code.co_name,is_send_email=True)
    def get_info_info(cls):
        '''解析api数据'''
        def dispose_api_params_desc_result(api_params,api_params_ref_result,api_data):
            '''处理请求参数中的key，转为jsonpath提取数据并返回'''
            def replece_key(api_params_ref_json_path,api_data,split_symbol='.'):
                '''处理引用为标准的jsonpath，并替换原dict key'''
                if api_params_ref_json_path.startswith('$.'):
                    api_params_ref_json_path_split = api_params_ref_json_path.split(split_symbol)
                    if api_params_ref_json_path_split[1] in api_data.keys():
                        keys=list(api_data[api_params_ref_json_path_split[1]].keys())
                        if api_params_ref_json_path_split[2] in keys:
                            target_no_special_key=api_params_ref_json_path_split[2].replace("«", "").replace("»","").replace(',','')
                            if " " in api_params_ref_json_path_split[2]:
                                target_no_special_key=target_no_special_key.split(" ")[0]

                            if cls._data.is_contains_chinese(api_params_ref_json_path_split[2]):
                                result = cls._pinyin.get_pinyin(api_params_ref_json_path_split[2])
                                result = result.replace('-', '') if result else result
                                api_data[api_params_ref_json_path_split[1]][result]=api_data[api_params_ref_json_path_split[1]][api_params_ref_json_path_split[2]]
                                api_params_ref_json_path_split[2]=result
                            ## 定义去除特殊字符后的目标key
                            if not api_data[api_params_ref_json_path_split[1]].\
                                    get(target_no_special_key):
                                api_data[api_params_ref_json_path_split[1]][target_no_special_key] = \
                                    api_data[api_params_ref_json_path_split[1]][api_params_ref_json_path_split[2]]
                                del api_data[api_params_ref_json_path_split[1]][api_params_ref_json_path_split[2]]

                return api_data

            api_params_ref_is_array=False #标识接口参数是否为array
            if not api_params:
                return "描述key为空",api_params_ref_result,api_params_ref_is_array
            '''解析请求参数为json数据的接口'''
            api_params_ref = api_params
            # params专用
            if api_params.get("schema"):
                if api_params.get("schema").get("$ref"):
                    api_params_ref=api_params['schema']['$ref']

            # response专用
            elif api_params.get("data"):
                if api_params.get("data").get("$ref"):
                    api_params_ref=api_params['data']['$ref']

            elif api_params.get("$ref"):
                api_params_ref = api_params['$ref']

            # '''解析请求参数格式为非json的数据，例如：array[object]'''
            if not str(api_params_ref).startswith('#'):
                # print("api_params_ref:",api_params_ref)
                api_params_ref_type = {}
                if api_params.get("schema"):
                    if api_params.get("schema").get("type"):
                        api_params_ref_type = api_params['schema']['type']

                elif api_params.get("data"):
                    if api_params.get("data").get("type"):
                        api_params_ref_type = api_params['data']['type']

                if api_params_ref_type:
                    if api_params_ref_type in cls.api_params_ref_result_properties_type_default.keys():
                        api_params_ref = api_params['schema']['items']['$ref'] if api_params.get(
                            'schema') and api_params.get('schema').get('items') and \
                            api_params.get('schema').get('items').get('$ref') else api_params
                        if api_params_ref_type == 'array':
                            api_params_ref_is_array = True
                else:
                    api_params_ref_type = api_params['type'] if api_params.get('type') and api_params.get(
                        'items') else {}

                    if api_params_ref_type:
                        if api_params_ref_type in cls.api_params_ref_result_properties_type_default.keys():
                            api_params_ref = api_params['items']['$ref'] if api_params.get(
                                'items') and api_params.get('items').get('$ref') else api_params
                            if api_params_ref_type == 'array':
                                api_params_ref_is_array = True


            api_params_ref_json_path = str(api_params_ref).replace('#', '$').replace('/', '.')
            if " " in api_params_ref_json_path:
                api_data=replece_key(api_params_ref_json_path=api_params_ref_json_path,api_data=api_data)
                api_params_ref_json_path_all = api_params_ref_json_path.split(' ')
                api_params_ref_json_path = api_params_ref_json_path_all[0]
            elif "«" in api_params_ref_json_path or "»" in api_params_ref_json_path:
                api_data=replece_key(api_params_ref_json_path=api_params_ref_json_path,api_data=api_data)
                api_params_ref_json_path=api_params_ref_json_path.replace("«","").replace("»","").replace(',','')
            api_params_ref_json_path_is_contains_chinese=cls._data.is_contains_chinese(api_params_ref_json_path)
            if api_params_ref_json_path_is_contains_chinese:
                api_data=replece_key(api_params_ref_json_path=api_params_ref_json_path,api_data=api_data)
                api_params_ref_json_path = cls._pinyin.get_pinyin(api_params_ref_json_path)
                api_params_ref_json_path = api_params_ref_json_path.replace('-', '') if api_params_ref_json_path else api_params_ref_json_path

            if api_params_ref_json_path.startswith("$."):
                api_params_ref_result = cls._data.json_path_parse_public(json_obj=api_data, json_path=api_params_ref_json_path)
            api_params_ref_result = api_params_ref_result[0] if api_params_ref_result and len(api_params_ref_result)==1 else api_params_ref_result
            return api_params_ref,api_params_ref_result,api_params_ref_is_array

        def api_params_desc_convert_to_params(api_params_ref_result:dict,api_data:dict):
            '''将接口示例对象转换为可用的请求参数'''
            def recursion_get_api_child_parms(properties_key, api_params_ref_result):
                '''递归解析子节点参数信息'''
                api_params_ref, api_params_ref_result, api_params_ref_is_array = dispose_api_params_desc_result(
                    api_params=api_params_ref_result_properties[i],
                    api_params_ref_result=api_params_ref_result, api_data=api_data)
                # api_params_ref没有#时，代表不再有json参数嵌套，不在调用
                if str(api_params_ref).startswith("#/"):
                    api_params = api_params_desc_convert_to_params(api_params_ref_result=api_params_ref_result,
                                                                   api_data=cls.api_data)
                    properties_child_dict = {properties_key: api_params}
                    return api_params_ref_is_array,properties_child_dict
                return False,{}
            _api_params_ref_result_properties_dict = dict()
            if (not api_params_ref_result) or isinstance(api_params_ref_result,str) :
                return _api_params_ref_result_properties_dict

            api_params_ref_result_format=api_params_ref_result['type'] if api_params_ref_result.get('type') else api_params_ref_result
            if api_params_ref_result_format=='object':
                api_params_ref_result_properties=api_params_ref_result['properties'] if api_params_ref_result.get('properties') else {}
                for i in api_params_ref_result_properties:
                    # print("api_params_ref_result_properties[i]:",api_params_ref_result_properties[i])
                    if isinstance(api_params_ref_result_properties[i],dict) and \
                        (api_params_ref_result_properties[i].get('items')
                         and api_params_ref_result_properties[i].get('items').get("$ref") ) \
                        or api_params_ref_result_properties[i].get("$ref")\
                        or (api_params_ref_result_properties[i].get("schema") and api_params_ref_result_properties[i].get("schema").get('$ref')):
                        # print("开始递归处理")
                        api_params_ref_is_array,properties_child_dict=recursion_get_api_child_parms(properties_key=i,api_params_ref_result=api_params_ref_result)
                        if api_params_ref_is_array:
                            for cd in properties_child_dict:
                                if not isinstance(properties_child_dict[cd],(list,tuple,set)):
                                    properties_child_dict[cd]=[properties_child_dict[cd]]

                        _api_params_ref_result_properties_dict.update(properties_child_dict)
                    else:
                        api_params_ref_result_properties_type=api_params_ref_result_properties[i]['type'] if \
                            api_params_ref_result_properties[i].get('type') else 'string'
                        # 如果存在参数示例，则使用参数示例代替定义的默认值
                        api_params_ref_result_properties_example=api_params_ref_result_properties[i]['example'] if \
                            api_params_ref_result_properties[i].get('example') else None
                        if api_params_ref_result_properties_example:
                            if isinstance(api_params_ref_result_properties_example, str):
                                api_params_ref_result_properties_example = api_params_ref_result_properties_example.replace(
                                    '"', '').replace("'", '').replace(' ','')
                                if api_params_ref_result_properties_example.startswith('[') and api_params_ref_result_properties_example.endswith(']'):
                                    api_params_ref_result_properties_example=api_params_ref_result_properties_example[1:-1].split(',')
                                # print("api_params_ref_result_properties_example:",api_params_ref_result_properties_example)
                            _api_params_ref_result_properties_dict[i]=api_params_ref_result_properties_example
                        else:
                            _api_params_ref_result_properties_dict[i]=\
                            cls.api_params_ref_result_properties_type_default[api_params_ref_result_properties_type]
                # print(_api_params_ref_result_properties_dict)
                return _api_params_ref_result_properties_dict

        def dispost_output_api_params(api_params,api_params_type,api_params_ref_result):
            '''api_params_type跟据输出最终需要的api_params'''
            if not api_params:
                return "描述key为空",[],{}
            __api_params=copy.deepcopy(api_params)
            if api_params_type!='response':
                api_params=[i for i in api_params if api_params_type in i.values()]
            if api_params_type in ('body','response'):
                if api_params:
                    if isinstance(api_params,list):
                        api_params=api_params[0]
                    else:
                        api_params=api_params
                else:
                    api_params={}
                '''处理body参数'''
                api_params_ref,api_params_ref_result,api_params_ref_is_array=dispose_api_params_desc_result(
                    api_params=api_params,api_params_ref_result=api_params_ref_result,api_data=cls.api_data)
                # #将api参数转换为最终需要的格式
                api_params_out=api_params_desc_convert_to_params(api_params_ref_result=api_params_ref_result,api_data=cls.api_data)
                if api_params_ref_is_array and ( not isinstance(api_params_out,(list,tuple))):
                    api_params_out=[api_params_out]
                return api_params_ref,api_params_ref_result,api_params_out
            elif api_params_type in ('path','query'):
                '''处理path参数'''
                api_params_ref="参数为path的请求没有描述key（不存在外部引用）"
                if not api_params:
                    if api_params_type=='path':
                        api_params_type='query'
                    elif api_params_type=='query':
                        api_params_type='path'
                    api_params = [i for i in __api_params if api_params_type in i.values()]
                api_params_ref_result=api_params
                api_params_out=dict()
                for api_param_dict in api_params:
                    params_type=api_param_dict['type'] if api_param_dict.get('type') else 'string'
                    params_filed=api_param_dict['name'] if api_param_dict.get('name') else None
                    if params_filed :
                        api_params_out[params_filed]=cls.api_params_ref_result_properties_type_default[params_type]
                return api_params_ref,api_params_ref_result,api_params_out


        for path in cls.api.keys():  # 循环取key
            values = cls.api[path]  # 根据key获取值
            cls.api_uri=path
            api_params_ref_result = "描述结果为空"  # 保存请求示例中的额外嵌套的信息
            api_response_ref_result = "响应结果为空"  # 保存请求示例中的额外嵌套的信息
            # if path=='/v1/collector/find-aggregate':
            # if path=='/v1/maintenance/map/breakage-list':
            for i in values.keys():
                cls.api_uri_list.append(path)  # 将path写入接口地址列表中
                api_method = i  # 获取请求方式，文件中请求方式是key
                cls.api_method_list.append(api_method)  # 将method写入请求方式列表中
                tags = values[api_method]['tags'][0]  # 获取接口分类
                # # 抓取参数与body
                api_params=values[api_method]['parameters'] if values[api_method].get('parameters') else {}
                api_params_ref_path,api_params_ref_result_path,api_params_path=dispost_output_api_params(
                    api_params=api_params,api_params_type='path',api_params_ref_result=api_params_ref_result)
                api_params_ref_body,api_params_ref_result_body,api_params_body=dispost_output_api_params(
                    api_params=api_params,api_params_type='body',api_params_ref_result=api_params_ref_result)
                cls.api_params_path_list_descs.append(f"{api_params_ref_path}:->>{json.dumps(api_params_ref_result_path,ensure_ascii=False)}")
                cls.api_params_path_list.append(json.dumps(api_params_path,ensure_ascii=False))
                cls.api_params_body_list_descs.append(f"{api_params_ref_body}:->>{json.dumps(api_params_ref_result_body,ensure_ascii=False)}")
                cls.api_params_body_list.append(json.dumps(api_params_body,ensure_ascii=False))
                # 抓取响应
                api_response=values[api_method]['responses'][cls.api_response_key] if values[api_method].get('responses') and \
                    values[api_method]['responses'].get(cls.api_response_key) else {}
                api_response_ref,api_response_ref_result,api_response=dispost_output_api_params(
                    api_params=api_response,api_params_type='response',api_params_ref_result=api_response_ref_result)
                if isinstance(api_response,list):
                    api_response=api_response[0]
                cls.api_response_body_list_descs.append(f"{api_response_ref}:->>{json.dumps(api_response_ref_result,ensure_ascii=False)}")
                cls.api_response_body_list.append(json.dumps(api_response,ensure_ascii=False))

                # 拼接api_name
                summary = values[api_method]['summary']  # 获取接口描述
                cls.api_name_list.append(tags + '_' + summary)

    @classmethod
    def rm_old_file(cls):
        '''删除旧数据，避免数据写入重复'''
        if os.path.isfile(f'{os.path.join(cls.excel_path,cls.excel_name)}'):
            print(f'删除文件:{os.path.join(cls.excel_path,cls.excel_name)}')
            os.remove(f'{os.path.join(cls.excel_path,cls.excel_name)}') #删除文件
            ## shutil.rmtree('./') #删除文件夹及子目录下的所有文件
    @classmethod
    def write_data_to_excel(cls):
        '''将api信息写入到excel'''
        op_ex = operationExcel(excel_path=cls.excel_path, excel_name=cls.excel_name,is_read=False,data_only=True)
        # 写入excel首行
        first_line=['case','uri','method','params_path','params_path_desc','params_body','params_body_desc','response_body','response_body_desc','skip']
        op_ex.write_values(first_line)
        # # 写入api信息到excel
        for i in range(len(cls.api_uri_list)):  # 将接口path循环写入第一列
            api_infos=[cls.api_name_list[i],cls.api_uri_list[i],
                       cls.api_method_list[i],cls.api_params_path_list[i],
                       cls.api_params_path_list_descs[i],cls.api_params_body_list[i],
                        cls.api_params_body_list_descs[i],cls.api_response_body_list[i],
                       cls.api_response_body_list_descs[i],0]
            op_ex.write_values(api_infos)
        op_ex.save_workbook(cls.excel_name)     # 保存文件

    @classmethod
    @exec_time_wrapper(round_num=10,module_obj=__file__,class_obj=sys._getframe().f_code.co_name,is_send_email=True)
    def main(cls):
        cls.get_info_info()
        cls.rm_old_file()
        cls.write_data_to_excel()


if __name__=="__main__":
    sa=swaggerApiParse()
    sa.main()
    # print(sa.api_params_body_list)