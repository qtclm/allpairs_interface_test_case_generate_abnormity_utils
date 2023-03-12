# _*_ coding: UTF-8 _*_
"""
@project -> file : city-test -> rr
@Author          : qinmin.vendor
@Date            : 2023/1/29 19:44
@Desc            : 自动生成接口测试用例：支持正交实验，等价类，边界值
"""

import copy
import json
import os
import random
import re
import shutil
import sys
from collections import OrderedDict
from inspect import isfunction
from allpairspy import AllPairs
from utils.operation_datas import operationExcel
import math
from utils.operation_yaml import operationYaml
from utils.time_util import timeUtil
from utils.wrapper_util import exec_time_wrapper
from utils.exception_util import *
from faker import Faker
from utils.operation_logging import operationLogging
'''faker使用教程：https://blog.csdn.net/qq_42412061/article/details/122997802'''



class autoGenrateApiCaseAllpairspy(object):

    time_util = timeUtil()
    log=operationLogging()
    project_root_path=time_util.get_project_rootpath(match_paths=['config','utils'])
    config_file_path = os.path.join(project_root_path, 'config')
    config_file_name = 'allpairs_config.yaml'
    yaml_obj = operationYaml(path=config_file_path, file_path=config_file_name)
    config_data=yaml_obj.read_data(out_dict=True)

    '''初始化excel相关配置'''
    config_data_excel=config_data['excel_config'] #excel相关配置
    read_excel_case_field_desc = config_data_excel['read_excel_case_field_desc']
    # 数据处理前的case表头，写入excel中最终会删除params_path,且params_body替换为params && response_body替换为expected
    write_excel_case_field_desc = config_data_excel['write_excel_case_field_desc']
    # 定义excle分批保存条数，避免一次性写入太多数据造成数据丢失
    batch_save_num=config_data_excel['batch_save_num']
    # 存放case_info（基于api对应的模块）是否写入首行数据,此参数无需重置
    write_case_info_first_line_sheet_names = []


    '''初始化api相关配置'''
    config_data_api=config_data['api_config'] #api相关配置
    # 断言追加http状态响应码
    expected_extra_info=config_data_api['expected_extra_info']
    # 定义不需要生成正交测试用例的接口集合
    black_api_set=config_data_api['black_api_set']
    case_name_identifying=config_data_api['case_name_identifying']
    # 用户自定义接口枚举参数
    custom_api_enum_data=config_data_api['custom_api_enum_data']
    CONST_TYPE_ENUM={}
    CONST_TYPE_ENUM_COPY={}
    is_array = False  # 判断参数传入的参数是不是list
    params_key_list = []  # 判断参数的key对应的value是不是list类型，如果是，就将key存进此对象
    extra_cases = [] #存放额外的case,请求参数中的key嵌套json的情况
    extra_cases_hash_lists=[] #存放extra_cases元素的hash值，增加程序判断的效率
    key_is_object_convert_list=[] #将json[key]-> object 转换为 json[key]-> list[object]

    '''初始化公用相关配置'''
    config_data_common=config_data['common_config'] #公用相关配置
    # 是否删除旧的excel文件
    is_rm_ord_file=config_data_common['is_rm_ord_file']
    file_path = os.path.join(project_root_path, config_data_common['file_path'])
    swagger_file_path = os.path.join(project_root_path, config_data_common['swagger_file_path'])
    if not os.path.exists(file_path):
        os.makedirs(swagger_file_path)
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    excel_name_params_field_detail_file_name = config_data_common['excel_name_params_field_detail_file_name']
    excel_name_params_obj_file_name = config_data_common['excel_name_params_obj_file_name']
    excel_name_swagger_api_data_file_name = config_data_common['excel_name_swagger_api_data_file_name']
    already_generate_api_file_name=config_data_common['already_generate_api_file_name']
    already_generate_api_file_params_details_file_name=os.path.splitext(excel_name_params_field_detail_file_name)[0]+'_'+already_generate_api_file_name
    already_generate_api_file_params_obj_file_name=os.path.splitext(excel_name_params_obj_file_name)[0]+'_'+already_generate_api_file_name


    @classmethod
    # @exec_time_wrapper(round_num=10,module_obj=__file__,class_obj=sys._getframe().f_code.co_name,is_send_email=False)
    def init_enum_data(cls):
        '''初始化各个类型所需数据,优先使用用户传递的数据'''
        '''定义默认数据'''
        fake = Faker(locale="zh_cn")  # 指定语言为中文
        CONST_MAX_STRING_LENGTH = 100
        CONST_MIN_STRING_LENGTH = 1
        # 生成字符串相关的数据
        # special_chars是否包含特殊字符;digits是否包含数字;upper_case是否包含大写字母,lower_case是否包含小写字母
        special_character = fake.password(length=8, special_chars=True, digits=False, upper_case=False,
                                          lower_case=False)  # 生成随机特殊字符
        random_str = fake.paragraph()  # 生成随机字符
        random_str_max = random_str * math.ceil(CONST_MAX_STRING_LENGTH / len(random_str))
        phone_number = fake.phone_number()  # 生成随机电话号码

        # 生成时间相关的数据
        random_date = fake.date(pattern="%Y-%m-%d", end_datetime=None)  # 生成随机日期
        random_start_datetime = cls.time_util.adjust_time(num=-30)
        random_end_datetime = cls.time_util.adjust_time(num=0)
        random_start_timestamp_millisecond = cls.time_util.adjust_time(num=-30, is_timestamp=True, millisecond=True)
        random_end_timestamp_millisecond = cls.time_util.adjust_time(num=0, is_timestamp=True, millisecond=True)
        random_start_timestamp = cls.time_util.adjust_time(num=-30, is_timestamp=True, millisecond=False)
        random_end_timestamp = cls.time_util.adjust_time(num=0, is_timestamp=True, millisecond=False)

        # 生成int与float相关的数据
        random_int = random.randint(1, 100)
        random_float = round(random.random(), 6) + random_int  # 生成随机字符
        random_int_max = str(random_int) * math.ceil(CONST_MAX_STRING_LENGTH / len(str(random_int)))
        random_float_max = str(str(random_float) *
                               math.ceil(CONST_MAX_STRING_LENGTH / len(str(random_float).replace('.', '')))). \
                               replace('.', '') + "." + str(random_int)

        STRING_ENUM = ["", None, random_str, special_character,
                       random_str_max[:CONST_MAX_STRING_LENGTH], random_str[:CONST_MIN_STRING_LENGTH],
                       random_start_datetime, random_end_datetime, random_date]

        INT_FLOAT_ENUM = [0, None, special_character, random_int, random_float,
                          int(random_int_max[:CONST_MAX_STRING_LENGTH]), phone_number,
                          int(str(random_int)[:CONST_MIN_STRING_LENGTH]),
                          int(random_float_max[:CONST_MAX_STRING_LENGTH]),
                          int(str(random_float)[:CONST_MIN_STRING_LENGTH]), random_start_timestamp,
                          random_start_timestamp_millisecond, random_end_timestamp, random_end_timestamp_millisecond]
        LIST_ENUM = [[], None, [{}], [random_int], [random_str]]
        BOOL_ENUM = [None, False, True, "true", "false"]
        OBJECT_ENUM = [None, {}]
        NULL_ENUM = [None, "null"]


        # 定义接口字段生成的类型与枚举
        cls.CONST_TYPE_ENUM = {
            "str": STRING_ENUM,"string": STRING_ENUM,
            "int": INT_FLOAT_ENUM,"integer": INT_FLOAT_ENUM,"number": INT_FLOAT_ENUM,
            "None": NULL_ENUM,"null": NULL_ENUM,
            'bool': BOOL_ENUM,"boolean": BOOL_ENUM,
            'object': OBJECT_ENUM,'dict': OBJECT_ENUM,"list": LIST_ENUM,'array': LIST_ENUM,
        }

        cls.CONST_TYPE_ENUM_COPY = copy.deepcopy(cls.CONST_TYPE_ENUM)


    @classmethod
    def __custom_valid_combination(cls,row):
        """
        自定义过滤条件，返回false的条件不会出现在组合中
        """
        n = len(row)
        if n > 1:
            if row[0] in (None,'',""):
                return False
        return True


    # 指定：自定义过滤函数
    all_pairs_filter_func=__custom_valid_combination
    if not (isfunction(all_pairs_filter_func) or isinstance(all_pairs_filter_func,(classmethod,staticmethod))) :
        raise objNotCallError(msg=f"all_pairs_filter_func对象必须是一个方法:{all_pairs_filter_func}")


    @classmethod
    def read_all_cases_data(cls):
        if not os.path.exists(os.path.join(cls.swagger_file_path,cls.excel_name_swagger_api_data_file_name)):
            if os.path.exists(os.path.join(cls.project_root_path,cls.excel_name_swagger_api_data_file_name)):
                cls.log.log_main('info',False,'swagger文件目录未找到swagger文件,复制项目下的swagger文件到swagger文件目录')
                shutil.copyfile(src=os.path.join(cls.project_root_path,cls.excel_name_swagger_api_data_file_name),dst=os.path.join(cls.swagger_file_path,cls.excel_name_swagger_api_data_file_name))
            else:
                raise fileNotFoundError(msg='swagger_api_files不存在,请检查文件名是否填写错误,或者执行swagger_api_parse脚本生成swagger文件')
        cases_data_obj=operationExcel(file_path=cls.swagger_file_path,file_name=cls.excel_name_swagger_api_data_file_name,opeartion_type='read',data_only=True)
        lines=cases_data_obj.get_lines()
        case_list=[]
        for line_num in range(lines):
            values=cases_data_obj.get_row_values(line_num+1)
            if values[0]:
                out_values=[]
                for index,i in enumerate(cls.read_excel_case_field_desc):
                    if line_num!=0 and index==cls.write_excel_case_field_desc['response_body']:
                        expected_info=json.loads(values[cls.read_excel_case_field_desc[i]])
                        expected_info.update(cls.expected_extra_info)
                        expected_info['api_response_code']=expected_info['code'] if expected_info.get('code') else 0
                        expected_info['code']=expected_info.pop('http_status_code')
                        values[cls.read_excel_case_field_desc[i]]=json.dumps(expected_info,ensure_ascii=False)
                    out_values.append(values[cls.read_excel_case_field_desc[i]])
                case_list.append(out_values)
        return case_list


    @classmethod
    def get_params_field_type(cls,params_field_value):
        '''根据字段内容输出字段的type'''
        if str(params_field_value).startswith('{') and str(params_field_value).endswith("}"):
            _type = 'dict' or 'object'
        elif str(params_field_value).startswith('[') and str(params_field_value).endswith(']'):
            _type = 'list' or 'array'
        elif isinstance(params_field_value,(int,float)):
            _type = 'int' or 'number'
        elif str(params_field_value) in ("true", 'false', 'True', 'False'):
            _type = 'bool' or 'boolean'
        elif str(params_field_value) in ('None', 'null', 'nil'):
            _type = 'None' or 'null'
        else:
            _type = 'str' or 'string'
        return _type

    @classmethod
    def replace_params_values(cls, params_info, params_type_enum=None):
        '''替换参数所有key的内容,params_type_enum:定义的数据类型枚举，默认为init初始化的数据枚举'''
        if params_type_enum is None:
            params_type_enum = {}
        parse_params_info = cls.time_util.dict_parse_generator(params_info)
        # print("parse_params_info",parse_params_info)
        for i in range(len(parse_params_info)):
            # if parse_params_info[i]:
            params_key = parse_params_info[i][:-1]
            # 组装json提取表达式
            params_extract_str = "']['".join(params_key)
            params_extract_str = "['" + params_extract_str + "']"
            params_extract_str_re = re.search("\['\d+'\]", params_extract_str)
            if params_extract_str_re:
                # 去除list索引下标的字符串，处理为eval能够识别的int字符串
                params_extract_str_re = params_extract_str_re.group()
                params_extract_str = params_extract_str.replace(
                    params_extract_str_re,params_extract_str_re.replace("'", '').replace('"',""))
            # 获取key内容
            params_field_value = eval(f"params_info{params_extract_str}")
            params_type = cls.get_params_field_type(params_field_value=params_field_value)
            if not (params_type_enum and params_type in params_type_enum.keys()):
                # 如果key在传入的枚举数据范围内则直接使用,否则使用默认定义的枚举数据
                params_type_enum=cls.CONST_TYPE_ENUM
                if not params_type_enum:
                    raise paramsTypeEnumError(msg="params_type_enum为空,请执行init_enum_data方法初始化默认枚举数据")
            # print("params_type_enum:",params_type_enum)
            # # 将不为空得参数值且不在枚举定义范围内的数据添加到枚举定义中，避免影响原有数据且用于完善参数覆盖情况
            if params_field_value and (params_field_value not in params_type_enum[params_type]):
                params_type_enum[params_type].append(params_field_value)
            # 动态执行代码：替换key的内容
            exec(f"params_info{params_extract_str}={params_type_enum[params_type]}")

        return params_info


    @classmethod
    def json_is_list_object_to_object(cls,params_info):
        '''将json[key]=list->object设置为object,方便构建oreded_dict对象'''
        if params_info and isinstance(params_info, list) and isinstance(params_info[0],dict):
            params_info = params_info[0]
            if not cls.is_array:
                cls.is_array = True
        return params_info

    @classmethod
    def json_key_is_object_to_list_object(cls,params_info):
        '''#将json[key]-> object 转换为json[key]-> list[object]，由于allpairs无法解析，所以这里手动进行转换'''
        for i in params_info:
            if isinstance(params_info[i], dict):
                cls.key_is_object_convert_list.append(i)
                params_info[i] = [params_info[i]]
        return params_info

    @classmethod
    def api_prams_convert(cls, params_info):
        '''根据参数与参数类型转换为预期定义的数据类型定义的枚举'''

        def append_params_key_is_object_to_params_key_list(params_info):
            '''追加参数key对应的值是object类型的key到指定list中'''
            for i in params_info:
                if isinstance(params_info[i],list) and isinstance(params_info[i][0],dict)\
                        and (i not in cls.params_key_list):
                    cls.params_key_list.append(i)

        if not params_info:
            return params_info
        params_info=cls.json_is_list_object_to_object(params_info=params_info)
        params_info=cls.json_key_is_object_to_list_object(params_info=params_info)
        params_info=cls.replace_params_values(params_info=params_info)
        append_params_key_is_object_to_params_key_list(params_info)
        return params_info

    @classmethod
    def parse_uri_params_path_query(cls,uri: str, params_path: dict):
        '''解析url中的params_path与params_query参数'''
        if not params_path:
            return {},{}
        uri_split = uri.split('/')
        uri_params = [i for i in uri_split if i.startswith('{') and i.endswith('}')]
        params_path_keys = list(params_path.keys())
        uri_params_path_dict = {}  # 存储：uri中的参数是key的情况
        uri_params_query_dict = {}  # 存储：uri中的参数不是key的情况，代表是query参数
        for params_path_key in params_path_keys:
            if "{" + params_path_key + "}" in uri_params:
                uri_params_path_dict[params_path_key]=params_path[params_path_key]
            else:
                uri_params_query_dict[params_path_key]=params_path[params_path_key]
        return uri_params_path_dict,uri_params_query_dict

    @classmethod
    def join_request_uri(cls,uri,path_dict,query_dict):
        def out_path_replace_uri(uri,dict_obj):
            '''uri拼接替换后的path参数'''
            if dict_obj:
                for i in dict_obj:
                    uri = uri.replace("{" + i + "}",str(dict_obj[i]) )
                return uri
            return uri
        def out_query_replace_uri(uri,dict_obj):
            '''uri拼接替换后的query参数'''
            if dict_obj:
                uri += "?"
                for i in dict_obj:
                    uri += f"{i}={str(dict_obj[i])}&"
                uri = uri[:-1] if uri[-1] == "&" else uri
            return uri

        if not (path_dict or query_dict):
            return uri
        uri=out_path_replace_uri(uri=uri,dict_obj=path_dict)
        uri=out_query_replace_uri(uri=uri,dict_obj=query_dict)
        uri = cls.time_util.pyobject_to_json_str(uri)
        return uri

    @classmethod
    def out_target_case(cls,src_obj_index, params_all_obj):
        '''根据index返回符合条件的case'''
        if not params_all_obj:
            return {}
        _l = len(params_all_obj) - 1
        if src_obj_index > _l:
            target_case = params_all_obj[random.randint(0, _l)]
        else:
            target_case = params_all_obj[src_obj_index]
        return target_case

    @classmethod
    def append_params_key_is_object_to_extra_cases(cls, case_params_key_obj, params_keys, extra_cases,
                                                  filter_func, cases_obj=[], is_append_extra_cases=True, params_key=""):
        '''将params[key]->object的value添加到extra_cases'''
        if not isinstance(case_params_key_obj, OrderedDict):
            case_params_key_obj = OrderedDict(case_params_key_obj)
        case_params_key_results = list(
            AllPairs(case_params_key_obj, filter_func=filter_func))
        for case_params_key in case_params_key_results:
            case = cls.dispose_allpairs_obj_str_to_dict(case_str=str(case_params_key),
                                                         params_keys=params_keys,
                                                         extra_cases=extra_cases, filter_func=filter_func)
            if is_append_extra_cases:
                cases_obj = {params_key: case}

                hash_case_obj = cls.time_util.encry_main(str(cases_obj), encry_type='md5')
                if not hash_case_obj in cls.extra_cases_hash_lists:
                    cls.extra_cases_hash_lists.append(hash_case_obj)
                    extra_cases.append(cases_obj)
            else:
                cases_obj.append(case)

    @classmethod
    def dispose_allpairs_obj_str_to_dict(cls, case_str: str, params_keys, extra_cases, filter_func):
        '''AllPairs对象转换为str，并最终处理为dict输出：并过滤掉参数key为object的key，存入extra_cases对象'''

        def match_params_key_not_object(match_expression, case_str, space_comma):
            '''
            Args:
                match_expression: 正则表达式
                case_str: 需要被匹配的请求参数字符
                is_match_object: 定义类型区分是否走object匹配
            Returns:
            '''
            case_params_key_re = re.search(match_expression, case_str)
            # print("case_params_key_re:",case_params_key_re)
            if not case_params_key_re:
                return None
            case_params_key_result = case_params_key_re.group()
            # print("case_params_key_result:",case_params_key_result)
            return cls.time_util.recursion_remove_char(str_in=case_params_key_result, space_chars=space_comma, remove_type=1)

        def match_params_key_object(case_params_key_result, params_key, space_one, space_comma, extra_cases,
                                    filter_func):
            '''处理dict[key]->object专用'''
            if not case_params_key_result.startswith("{}{}".format(params_key, space_one) + "{"):
                return case_params_key_result

            case_params_key_result_dict_str = case_params_key_result[len(params_key) + len(space_one):]
            if case_params_key_result.endswith("}" + space_comma):
                case_params_key_result_dict_str = case_params_key_result_dict_str[:-1]
            case_params_key_result_dict = eval(case_params_key_result_dict_str) if \
                cls.time_util.isevaluatable(case_params_key_result_dict_str) else case_params_key_result_dict_str

            '''将params[key]->object的value添加到extra_cases'''
            cls.append_params_key_is_object_to_extra_cases(case_params_key_obj=case_params_key_result_dict,
                                                           params_keys=list(case_params_key_result_dict.keys()),
                                                           extra_cases=extra_cases, filter_func=filter_func,
                                                           cases_obj=[], is_append_extra_cases=True,
                                                           params_key=params_key)

        def match_params_key_object_main(match_expression, case_str, params_key, index, space_one, space_comma,
                                         extra_cases, filter_func, is_match_object=True):
            '''完成处理dict[key]->object的主程序'''
            if index < len(params_keys) - 1:
                match_expression = f"{params_key}{space_one}.+,\s+{params_keys[index + 1]}"
            case_params_key_result = match_params_key_not_object(match_expression=match_expression, case_str=case_str,
                                                                 space_comma=space_comma)
            if index < len(params_keys) - 1:
                case_params_key_result = case_params_key_result[:case_params_key_result.rfind(space_comma) + 1]
            case_params_key_result = cls.time_util.recursion_remove_char(str_in=case_params_key_result, space_chars=space_comma,
                                                                remove_type=1)
            # 将key对应的值为object类型的key与值添加到cls.extra_cases
            if is_match_object:
                return match_params_key_object(case_params_key_result=case_params_key_result, params_key=params_key,
                                               space_one=space_one, space_comma=space_comma, extra_cases=extra_cases,
                                               filter_func=filter_func)
            return case_params_key_result

        def merge_params_dict(params_keys, case_str, extra_cases, filter_func, space_one='=', space_two='\n',
                              space_comma=','):
            '''将将参数中所有的key与value转换为dict并合并为一个dict，
            key对应的value为object时进行特殊处理（目前只支持key>json>key>not_json,即不支持三层及以上的json嵌套）'''
            all_params_dict = {}
            for index, params_key in enumerate(params_keys):
                '''常规模式匹配字符，即key为不是最后一个且key对应的值不是object'''
                match_expression_rule = f"{params_key}{space_one}\S+{space_comma}"
                case_params_key_result = match_params_key_not_object(match_expression=match_expression_rule,
                                                                     case_str=case_str, space_comma=space_comma)
                if case_params_key_result:
                    if case_params_key_result.startswith(
                            f'{params_key}{space_one}['):  # and case_params_key_result.endswith(']')
                        '''特殊处理：key对应的值为list且元素为string的情况'''
                        match_expression_list_or_str = f"{params_key}{space_one}\S+{space_comma}"
                        case_params_key_result = match_params_key_object_main(
                            match_expression=match_expression_list_or_str, case_str=case_str,
                            params_key=params_key, index=index, space_one=space_one,
                            space_comma=space_comma, extra_cases=extra_cases, filter_func=filter_func,
                            is_match_object=False)

                else:
                    '''处理key对应的值为object的情况'''
                    match_expression_object = f"{params_key}{space_one}.+"
                    case_params_key_result = match_params_key_object_main(
                        match_expression=match_expression_object, case_str=case_str,
                        params_key=params_key, index=index, space_one=space_one,
                        space_comma=space_comma, extra_cases=extra_cases, filter_func=filter_func, is_match_object=True)

                params_key_dict = cls.time_util.str_to_dict(str_in=case_params_key_result, space_one=space_one,
                                                   space_two=space_two)
                all_params_dict.update(params_key_dict)

            return all_params_dict

        if case_str.startswith("Pairs(") and case_str.endswith(")"):
            case_str = case_str[len("Pairs("):-1]
        all_params_dict = merge_params_dict(params_keys=params_keys, case_str=case_str, space_one='=', space_two='\n',
                                            extra_cases=extra_cases, filter_func=filter_func, space_comma=',')
        return all_params_dict

    @classmethod
    def generate_all_cases(cls, ordered_dict_obj,params_info):

        def convert_allpairs_cases_to_cases(params_keys,ordered_dict_obj,cases_obj):
            '''将allparis输出的case字符串转换为dict输出'''
            if len(params_keys)>=2:
                cls.append_params_key_is_object_to_extra_cases(case_params_key_obj=ordered_dict_obj,
                    params_keys=params_keys,extra_cases=cls.extra_cases,filter_func=cls.all_pairs_filter_func,
                    cases_obj=cases_obj,is_append_extra_cases=False,params_key="")
            else:
                '''params只有一个key时,直接组装字典输出（allpairs这种情况处理会输出空）'''
                cases = ordered_dict_obj
                for case in cases:
                    for case_key in cases[case]:
                        cases_obj.append({case: case_key})

        def append_extra_case_to_case(cases_obj,extra_cases,params_key_list):
            # 将extra_case数据追加到参数中
            for index,out_case in enumerate(cases_obj):
                for params_key in params_key_list:
                    update_cases=[i for i in extra_cases for o in i if o == params_key]
                    extra_case=cls.out_target_case(src_obj_index=index,params_all_obj=update_cases)
                    out_case.update(extra_case)

        def return_out_cases(params_info,ordered_dict_obj):
            '''输出最终转换完成的测试用例集合'''
            params_info=params_info[0] if isinstance(params_info,list) else params_info
            params_keys=[i for i in ordered_dict_obj] #以ordered_dict_obj的参数key作为匹配key
            out_cases = []
            '''将allparis输出的case字符串转换为dict输出'''
            convert_allpairs_cases_to_cases(params_keys=params_keys,ordered_dict_obj=ordered_dict_obj,cases_obj=out_cases)
            '''将extra_case数据追加到参数中'''
            append_extra_case_to_case(cases_obj=out_cases,extra_cases=cls.extra_cases,params_key_list=cls.params_key_list)
            return out_cases

        if not (params_info or ordered_dict_obj):
            return []
        return return_out_cases(params_info=params_info,ordered_dict_obj=ordered_dict_obj)

    @classmethod
    def rm_old_file(cls, file_path='./', file_name=''):
        if os.path.exists(os.path.join(file_path, file_name)):
            os.remove(os.path.join(file_path, file_name))

    @classmethod
    def reset_params_key_list_and_extra_cases(cls):
        '''每个api的参数不同，在写入后需要调用此方法重置，避免元素被重复使用'''
        cls.params_key_list=[]
        cls.time_util.extra_cases=[]
        cls.extra_cases_hash_lists=[]
        cls.key_is_object_convert_list=[]
        # 还原默认的枚举定义，避免数据一直递增
        cls.CONST_TYPE_ENUM=cls.CONST_TYPE_ENUM_COPY
        cls.is_array=False

    @classmethod
    def write_first_line(cls,ex_obj,sheet_name,ex_obj_data_case_names,case_info_first_line):
        if cls.is_rm_ord_file or (not ex_obj_data_case_names):
            if not sheet_name in cls.write_case_info_first_line_sheet_names:
                ex_obj.write_values(case_info_first_line)
                cls.write_case_info_first_line_sheet_names.append(sheet_name)

    @classmethod
    def merge_parmas_valid_key_to_ordered_dict(cls,ordered_dict_obj, params_obj):
        '''获取最终需要的key,并输出未orderd_dict对象
        过滤掉不在范围内的key,并补充不在范围内的key'''
        params_obj=cls.json_is_list_object_to_object(params_info=params_obj)
        params_obj_keys = [i for i in ordered_dict_obj if i in params_obj]  # 过滤用户自定义参数key在params_obj中的数据
        params_obj_outside_the_range_keys = [i for i in params_obj if
                                             i not in params_obj_keys]  # 获取用户自定义key在params_obj中不存在的key
        ordered_dict_obj_new = dict(zip(params_obj_keys, [ordered_dict_obj[i] for i in params_obj_keys]))
        params_obj_outside_the_range_dict = dict(
            zip(params_obj_outside_the_range_keys, [params_obj[i] for i in params_obj_outside_the_range_keys]))
        ordered_dict_obj_new.update(
            cls.replace_params_values(params_info=params_obj_outside_the_range_dict, params_type_enum=None))
        return ordered_dict_obj_new

    @classmethod
    def build_ordered_dict_and_all_cases(cls,custom_api_enum_data,uri,params_obj,params_obj_type):
        '''params_obj_type:用于区分path、body'''
        #'''构建生成ordered_dict对象并输出所有测试用例'''
        custom_api_enum_type = custom_api_enum_data['custom_api_enum_type'] if custom_api_enum_data.get(
            'custom_api_enum_type') else 'params_value_type'
        if custom_api_enum_type not in ('params_key', 'params_value_type'):
            raise customApiEnumTypeError(
                msg=f'params_value_type预期:params_key、params_value_type,实际:{custom_api_enum_type}')
        if not params_obj_type in ('path','body'):
            raise paramsObjTypeError(msg=f'params_obj_type预期:path、body,实际:{params_obj_type}')

        if params_obj_type=='path':
            if custom_api_enum_data.get(params_obj_type) :
                if custom_api_enum_type == 'params_key':
                    uri_params_path_dict, uri_params_query_dict = cls.parse_uri_params_path_query(
                        uri=uri, params_path=custom_api_enum_data[params_obj_type])
                    ordered_dict_obj_path = cls.merge_parmas_valid_key_to_ordered_dict(
                        ordered_dict_obj=custom_api_enum_data[params_obj_type], params_obj=params_obj)
                    ordered_dict_obj_query = uri_params_query_dict
                else:
                    uri_params_path_dict, uri_params_query_dict = cls.parse_uri_params_path_query(
                        uri=uri, params_path=params_obj)
                    ordered_dict_obj_path = cls.replace_params_values(params_info=uri_params_path_dict,
                                                                      params_type_enum=custom_api_enum_data[params_obj_type])
                    ordered_dict_obj_query = cls.replace_params_values(params_info=uri_params_query_dict,
                                                                       params_type_enum=custom_api_enum_data[params_obj_type])
            else:
                uri_params_path_dict, uri_params_query_dict = cls.parse_uri_params_path_query(
                    uri=uri, params_path=params_obj)
                ordered_dict_obj_path = cls.api_prams_convert(uri_params_path_dict)
                ordered_dict_obj_query = cls.api_prams_convert(uri_params_query_dict)

            # 输出path与body所有的正交测试用例
            params_all_path = cls.generate_all_cases(ordered_dict_obj_path, uri_params_path_dict)
            params_all_query = cls.generate_all_cases(ordered_dict_obj_query, uri_params_query_dict)
            return params_all_path, params_all_query

        elif params_obj_type=='body':
            if custom_api_enum_data.get(params_obj_type):
                if custom_api_enum_type == 'params_key':
                    ordered_dict_obj_body = cls.merge_parmas_valid_key_to_ordered_dict(
                        ordered_dict_obj=custom_api_enum_data[params_obj_type], params_obj=params_obj)

                else:
                    ordered_dict_obj_body = cls.replace_params_values(params_info=params_obj,
                                                                      params_type_enum=custom_api_enum_data[params_obj_type])

            else:
                ordered_dict_obj_body = cls.api_prams_convert(params_obj)

            # print("ordered_dict_obj_body:",ordered_dict_obj_body)
            params_all_body = cls.generate_all_cases(ordered_dict_obj_body, params_obj)
            return params_all_body

    @classmethod
    def batch_save_excel(cls,index,ex_obj):
        '''分批保存excel数据，避免一次性保存过多数据导致数据丢失(openpyxl库本身的问题)'''
        if index > 0 and index % cls.batch_save_num == 0:
            ex_obj.save_workbook()

    @classmethod
    def delete_default_sheet_and_save(cls,ex_obj):
        # 删除load_workbook默认创建的sheet,并保存excel
        ex_obj.delete_sheet(sheet_name=ex_obj.sheet_name)
        ex_obj.save_workbook()
        # 执行完重置此参数，避免首行数据不写入的问题
        cls.write_case_info_first_line_sheet_names=[]

    @classmethod
    def check_excel_obj(cls,ex_obj=None,is_params_detail=False):
        if ex_obj is None:
            if is_params_detail:
                excel_name = cls.excel_name_params_field_detail_file_name
                already_generate_api_file_name=cls.already_generate_api_file_params_details_file_name
            else:
                excel_name = cls.excel_name_params_obj_file_name
                already_generate_api_file_name=cls.already_generate_api_file_params_obj_file_name
            if cls.is_rm_ord_file:
                #删除已经生成的接口用例文件
                cls.rm_old_file(file_path=cls.file_path, file_name=excel_name)
                #删除已经生成的历史接口文件
                cls.rm_old_file(file_path=cls.file_path,file_name=already_generate_api_file_name)

            ex_obj = operationExcel(file_path=cls.file_path, file_name=excel_name,data_only=False,opeartion_type='read_write')
        if not isinstance(ex_obj,operationExcel):
            raise excelObjTypeError(msg=f"传入的对象预期是:{type(operationExcel)},实际为:{type(ex_obj)}")
        return ex_obj

    @classmethod
    def write_pre_dispose(cls,uri,params_path,params_body,**kwargs):
        '''写入excel数据的前置处理,分别生成：path、query、body的所有用例'''
        uri_copy=copy.deepcopy(uri)
        # 优先使用用户自定义的数据
        custom_api_enum_data=kwargs if kwargs and isinstance(kwargs,dict) else {}
        params_all_path,params_all_query=cls.build_ordered_dict_and_all_cases(
            custom_api_enum_data=custom_api_enum_data,uri=uri_copy,params_obj=params_path,params_obj_type='path')
        params_all_body=cls.build_ordered_dict_and_all_cases(
            custom_api_enum_data=custom_api_enum_data,uri=uri_copy,params_obj=params_body,params_obj_type='body')
        return params_all_path,params_all_query,params_all_body

    @classmethod
    def write_already_generate_api_file(cls,is_params_details,api_list):
        if is_params_details:
            file_name=cls.already_generate_api_file_params_details_file_name
        else:
            file_name=cls.already_generate_api_file_params_obj_file_name
        with open(os.path.join(cls.file_path,file_name),'w',encoding='utf-8') as f:
            f.write(str(api_list))

    @classmethod
    def read_already_generate_api_file(cls,is_params_details):
        if is_params_details:
            file_name=cls.already_generate_api_file_params_details_file_name
        else:
            file_name=cls.already_generate_api_file_params_obj_file_name
        try:
            with open(os.path.join(cls.file_path,file_name),'r',encoding='utf-8') as f:
                api_list=f.read()
                api_list_out=eval(api_list) if cls.time_util.isevaluatable_unsafety(str_in=api_list,is_dynamic_import_module=False) else api_list
            return api_list_out
        except:
            cls.write_already_generate_api_file(is_params_details=is_params_details,api_list=[])
            return cls.read_already_generate_api_file(is_params_details=is_params_details)

    @classmethod
    def black_api_skip_case_generate(cls,uri):
        '''黑名单接口跳过生成用例'''
        if uri in cls.black_api_set:
            cls.log.log_main('info', False, f'uri:{uri}在定义的黑名单接口集合中，跳过生成测试用例')
            return True
        return False

    @classmethod
    def create_sheet_and_refresh_switch_sheet(cls,case_info_copy,ex_obj):
        '''创建sheet并切换到对应sheet'''
        # 根据case模块名称创建sheet，并切换到对应的sheet
        sheet_name = case_info_copy[cls.write_excel_case_field_desc['case']].split('_')[0]
        sheet_name = cls.time_util.check_filename(sheet_name,priority_matching_chars=[':', '/', '\\', '?', '*', '[', ']'])
        if not sheet_name in ex_obj.get_all_sheet_name():
            ex_obj.create_sheet(sheet_name, is_save=True)
        ex_obj.data = ex_obj.get_data_for_sheet_name(sheet_name)
        return sheet_name,ex_obj.data

    @classmethod
    def exist_case_skip_case_generate(cls,case_name,uri,api_file_info):
        '''跳过生成之前已经生成过用例的接口'''
        if case_name in api_file_info:
            cls.log.log_main('info', False,f'uri:{uri}已经生成了测试用例(跳过生成),如果需要重新生成:\n'
                           f'请在excel中删除对应的测试用例或者设置is_rm_ord_excel_file参数为true(重新生成整个测试用例文件)')
            return True
        return False

    @classmethod
    def write_params_filed_detail_to_excel(cls, case_info,params_path,params_body,ex_obj:operationExcel=None,**kwargs):
        '''将参数字段明细写入到excel'''
        def write_cases_data_main(params_all,params_type,ex_obj):
            # 写入excel首行数据(表头)
            if not params_all:
                return False
            case_info_desc_pre=f'{case_name}(接口名称){uri}(接口路径),{method}(请求方式)'
            first_line = list(params_all[0].keys())
            first_line.insert(0,case_info_desc_pre)
            ex_obj.write_values([f'{case_info_desc_pre},生成的{params_type}参数详细信息如下'])
            ex_obj.write_values(first_line)
            for case in params_all:
                # 写入首行数据
                for case_key in case:
                    # 如果key存在与list中，说明参数是list,将object转换为array
                    if case_key in cls.params_key_list:
                        case[case_key] = [case[case_key]]
                    case[case_key]=str(case[case_key])
                # 将接口名称加入首列，方便过滤
                wirte_case_info=list(case.values())
                wirte_case_info.insert(0,case_info_desc_pre)
                ex_obj.write_values(wirte_case_info)

        # 检查ex_obj，如果合法则返回，如果不合法，则触发异常
        ex_obj=cls.check_excel_obj(ex_obj=ex_obj,is_params_detail=True)
        ex_obj_cp=copy.deepcopy(ex_obj)
        uri = case_info[cls.write_excel_case_field_desc['uri']]
        method = case_info[cls.write_excel_case_field_desc['method']]
        case_name = case_info[cls.write_excel_case_field_desc['case']]
        custom_api_enum_data = kwargs if kwargs and isinstance(kwargs, dict) else {}
        # 优先使用用户自定义的数据
        params_all_path, params_all_query, params_all_body = cls.write_pre_dispose(
            uri=uri,params_path=params_path, params_body=params_body, **custom_api_enum_data)


        # 分别写入数据：path、query、body
        write_cases_data_main(params_all=params_all_path,params_type='path',ex_obj=ex_obj)
        write_cases_data_main(params_all=params_all_query,params_type='query',ex_obj=ex_obj)
        write_cases_data_main(params_all=params_all_body,params_type='body',ex_obj=ex_obj)

        # 重置参数状态
        cls.reset_params_key_list_and_extra_cases()
        if ex_obj_cp is None:
            ex_obj.write_values(list(params_all_path[0].keys()))
            ex_obj.write_values(list(params_all_query[0].keys()))
            ex_obj.write_values(list(params_all_body[0].keys()))
            ex_obj.save_workbook()

    @classmethod
    def write_cases_obj_to_excel(cls, case_info, params_path,params_body,ex_obj:operationExcel=None,**kwargs):
        def write_cases_data_main(case_info,params_all_cases,is_body=False):
            '''
            将生成完毕的测试用例写入到excel，基础方法（将测试用例明细写入到excel）
            Args:
                case_info: 原始的测试用例信息
                params_all_cases: 使用正交生成后的所有测试用例集合
                is_body: 用于区分请求参数是否是body，如果不是bodu，则设置params_bodu为{},因为path与query类型不需要body请求，参数直接拼接到url上了
            Returns:
            '''
            for index, case in enumerate(params_all_cases):
                # print("params_all_cases:",id(params_all_cases))
                path_dict = cls.out_target_case(src_obj_index=index,
                                                params_all_obj=params_all_path) if params_all_path else {}
                query_dict = cls.out_target_case(src_obj_index=index,
                                                 params_all_obj=params_all_query) if params_all_query else {}
                # 拼接uri
                uri = cls.join_request_uri(uri=uri_copy, path_dict=path_dict, query_dict=query_dict)
                case_name = case_info[cls.write_excel_case_field_desc['case']]
                # 拼接测试用例名称
                if cls.case_name_identifying in case_name:
                    case_name = case_name[:case_name.find(cls.case_name_identifying)]
                case_name = case_name + cls.case_name_identifying + '-' + str(index + 1)
                case_info[cls.write_excel_case_field_desc['case']] = case_name
                case_info[cls.write_excel_case_field_desc['uri']] = uri
                for case_key in case:
                    # 如果key存在与list中，说明参数是list,将object转换为array
                    if (case_key in cls.params_key_list) and (case_key not in cls.key_is_object_convert_list) :
                        case[case_key] = [case[case_key]]
                # 判断最外层的参数是不是list，是list,将object转换为array
                if cls.is_array:
                    case_info[cls.write_excel_case_field_desc['params_body']] = json.dumps([case], ensure_ascii=False)
                else:
                    case_info[cls.write_excel_case_field_desc['params_body']] = json.dumps(case, ensure_ascii=False)
                if not is_body:
                    # 从params_body中删除params_path&params_query对应的key
                    case_info[cls.write_excel_case_field_desc['params_body']] = json.dumps({})
                case_info_copy=copy.deepcopy(case_info)
                case_info_copy.pop(cls.write_excel_case_field_desc['params_path'])
                ex_obj.write_values(case_info_copy)
        # 检查ex_obj，如果合法则返回，如果不合法，则触发异常
        ex_obj=cls.check_excel_obj(ex_obj=ex_obj,is_params_detail=False)
        uri=case_info[cls.write_excel_case_field_desc['uri']]
        uri_copy=copy.deepcopy(uri)
        # 优先使用用户自定义的数据
        custom_api_enum_data=kwargs if kwargs and isinstance(kwargs,dict) else {}
        params_all_path,params_all_query,params_all_body=cls.write_pre_dispose(
            uri=uri,params_path=params_path,params_body=params_body,**custom_api_enum_data)

        # 分别写入数据：path、query、body
        if params_all_body:
            write_cases_data_main(case_info=case_info,params_all_cases=params_all_body,is_body=True)
        elif params_all_path:
            write_cases_data_main(case_info=case_info, params_all_cases=params_all_path, is_body=False)
        elif params_all_query:
            write_cases_data_main(case_info=case_info, params_all_cases=params_all_query, is_body=False)

        # 重置参数状态
        cls.reset_params_key_list_and_extra_cases()

    @classmethod
    @exec_time_wrapper(round_num=10,module_obj=__file__,class_obj=sys._getframe().f_code.co_name,is_send_email=True)
    def batch_write_params_filed_detail_to_excel(cls,case_list=None):
        if case_list is None:
            case_list=cls.read_all_cases_data()

        ex_obj=cls.check_excel_obj(ex_obj=None,is_params_detail=True)
        # 初始化数据
        cls.init_enum_data()
        already_generate_api_list=[]
        old_already_generate_api_list=cls.read_already_generate_api_file(is_params_details=True)
        for index,params in enumerate(case_list[1:]):
            # params是一个可变类型，程序执行中共用了此对象，这里需要传一个深拷贝对象给他，避免执行过程中params被替换
            params_copy=copy.deepcopy(params)
            uri=params_copy[cls.write_excel_case_field_desc['uri']]
            case_name=params_copy[cls.write_excel_case_field_desc['case']]
            already_generate_api_list.append(case_name)
            # 黑名单接口list跳过生成用例
            url_is_black=cls.black_api_skip_case_generate(uri=uri)
            if url_is_black:
                continue
            case_is_generate = cls.exist_case_skip_case_generate(
                case_name=case_name, uri=uri, api_file_info=old_already_generate_api_list)
            if case_is_generate:
                continue

            # if uri in (
            #     '/v1/collector/find-aggregate'
            # ):
            method=params_copy[cls.write_excel_case_field_desc['method']]
            params_body=params_copy[cls.write_excel_case_field_desc['params_body']]
            params_path=params_copy[cls.write_excel_case_field_desc['params_path']]
            sheet_name, ex_obj.data=cls.create_sheet_and_refresh_switch_sheet(case_info_copy=params_copy,ex_obj=ex_obj)
            # 写入excel首行数据(表头)
            cls.write_first_line(ex_obj=ex_obj,ex_obj_data_case_names=old_already_generate_api_list,
                                     sheet_name=sheet_name,case_info_first_line=[f"{sheet_name}模块所有接口生成的接口参数(包含:path、query、body)明细如下"])
            params_path=json.loads(params_path) if not isinstance(params_path,dict) else params_path
            params_body=json.loads(params_body) if not isinstance(params_body,dict) else params_body
            if params_body in ({}, [], [{}], None) and params_path in ({}, [], [{}], None):
                default_value_pre=f'{case_name}(接口名称),{uri}(接口路径),{method}(请求方式),'
                for default_value in ['path参数为空','query参数为空','body参数为空']:
                    ex_obj.write_values([default_value_pre+default_value])
            else:
                if cls.custom_api_enum_data.get(uri):
                    custom_api_enum_data_kwargs = cls.custom_api_enum_data[uri]
                else:
                    custom_api_enum_data_kwargs = {}
                cls.write_params_filed_detail_to_excel(case_info=params_copy,params_path=params_path,params_body=params_body,ex_obj=ex_obj,**custom_api_enum_data_kwargs)

            # 分批保存excel数据
            cls.batch_save_excel(index=index,ex_obj=ex_obj)

        # 将api集合写入到文件
        cls.write_already_generate_api_file(is_params_details=True,api_list=already_generate_api_list)
        # 删除默认创建的sheet
        cls.delete_default_sheet_and_save(ex_obj=ex_obj)


    @classmethod
    @exec_time_wrapper(round_num=10,module_obj=__file__,class_obj=sys._getframe().f_code.co_name,is_send_email=True)
    def batch_write_cases_obj_to_excel(cls,case_info=None,case_list=None):
        if case_list is None:
            case_list=cls.read_all_cases_data()
        if isinstance(case_list, dict):
            case_list = [case_list]
        case_info_first_line=case_info
        if case_info is None:
            case_info_first_line=list(cls.write_excel_case_field_desc.keys())
            # 删除params_path, 且params_body替换为params & & response_body替换为expected
            case_info_first_line[cls.write_excel_case_field_desc['params_body']]='params'
            case_info_first_line[cls.write_excel_case_field_desc['response_body']]='expected'
            case_info_first_line.pop(cls.write_excel_case_field_desc['params_path'])

        ex_obj=cls.check_excel_obj(ex_obj=None,is_params_detail=False)
        # 初始化数据
        cls.init_enum_data()
        already_generate_api_list=[]
        old_already_generate_api_list=cls.read_already_generate_api_file(is_params_details=False)
        for index,case in enumerate(case_list[1:]):
            # params是一个可变类型，程序执行中共用了此对象，这里需要传一个深拷贝对象给他，避免执行过程中params被替换
            case_info_copy=copy.deepcopy(case)
            uri=case_info_copy[cls.write_excel_case_field_desc['uri']]
            case_name = case_info_copy[cls.write_excel_case_field_desc['case']]
            already_generate_api_list.append(case_name)
            # 黑名单接口list跳过生成用例
            url_is_black = cls.black_api_skip_case_generate(uri=uri)
            if url_is_black:
                continue
            case_is_generate = cls.exist_case_skip_case_generate(
                                case_name=case_name,uri=uri,api_file_info=old_already_generate_api_list)
            if case_is_generate:
                 continue
           # if uri in (
                # '/v1/collector/find-aggregate'
                #'/v1/devices/gateway/call'
           # ):
            params_body=case_info_copy[cls.write_excel_case_field_desc['params_body']]
            params_path=case_info_copy[cls.write_excel_case_field_desc['params_path']]
            sheet_name, ex_obj.data=cls.create_sheet_and_refresh_switch_sheet(case_info_copy=case_info_copy,ex_obj=ex_obj)
                # 写入excel首行数据(表头)
            cls.write_first_line(ex_obj=ex_obj,ex_obj_data_case_names=old_already_generate_api_list,
                                     sheet_name=sheet_name,case_info_first_line=case_info_first_line)

            params_path = json.loads(params_path) if not isinstance(params_path, dict) else params_path
            params_body = json.loads(params_body) if not isinstance(params_body, dict) else params_body
            if params_body in ({},[],[{}],None) and params_path in ({},[],[{}],None) :
                case_info_copy[cls.write_excel_case_field_desc['params_body']]=json.dumps(params_body)
                case_info_copy[cls.write_excel_case_field_desc['params_path']] = json.dumps(params_path)
                case_info_copy.pop(cls.write_excel_case_field_desc['params_path'])
                ex_obj.write_values(case_info_copy)
            else:
                if cls.custom_api_enum_data.get(uri):
                    custom_api_enum_data_kwargs=cls.custom_api_enum_data[uri]
                else:
                    custom_api_enum_data_kwargs = {}
                cls.write_cases_obj_to_excel(case_info=case_info_copy,params_path=params_path,params_body=params_body,ex_obj=ex_obj,**custom_api_enum_data_kwargs)

            # 分批保存excel数据
            cls.batch_save_excel(index=index,ex_obj=ex_obj)
        # 将api集合写入到文件
        cls.write_already_generate_api_file(is_params_details=False,api_list=already_generate_api_list)
        # 删除默认创建的sheet并保存退出
        cls.delete_default_sheet_and_save(ex_obj=ex_obj)


if __name__ == "__main__":
    params = {"account": "demo", "pwd": "crmeb.com", "key": "533721295cb06314f4bcaacebc28e3bd", "code": "nbcw",
              "wxCode": "", 'userinfo': {}, 'age': 0, 'is_vip': False, 'ext': None,
              'orders': [{"order": "asc", "fileds": []}], 'orders2': [{"order2": "asc", "fileds2": []}],
              "price2":0.05,"ip":""}
    #
    auto_case = autoGenrateApiCaseAllpairspy()
    # print(auto_case.read_all_cases_data())
    # print(auto_case.read_all_cases_data())
    # # 读取case数据
    # print(auto_case.read_all_cases_data())
    # auto_case.batch_write_cases_obj_to_excel()
    # auto_case.join_uri_params_path('/v1/stakes/section/{sectionId}/number/{stakeSerialNumber}',{"sectionId": 0, "stakeSerialNumber": "","test":123})
    # 单个写入
    # auto_case.write_params_filed_detail_to_excel(params)
    # auto_case.write_cases_obj_to_excel(case_info, params=params_array)
    # 批量写入
    auto_case.batch_write_params_filed_detail_to_excel(case_list=None)
    # # print("case_info:before",case_info)
    auto_case.batch_write_cases_obj_to_excel(case_info=None,case_list=None)
    # # print("case_info:after",case_info)
    # # params_info={'company_name': '', 'device_sn': '', 'extra_info': '', 'password': '', 'product_name': '', 'registry_id': '', 'soft_version': '', 'username': ''}
    # # auto_case.init_enum_data()
    # # print(auto_case.replace_params_values(params_info=params_info, params_type_enum=None))


