# _*_ coding: UTF-8 _*_
"""
@file            : other_util
@Author          : qtclm
@Date            : 2023/1/29 19:44
@Desc            :
"""

import ast
import base64
import hashlib
import json
import os
import re
import traceback
from collections.abc import Iterable
import sys
from urllib.parse import urljoin, urlparse, urlunparse
from posixpath import normpath
from Crypto.Cipher import AES
from typing import Any, Union
import importlib
import platform
from utils.exception_util import *
from utils.__init__ import get_project_rootpath


class otherUtil(object):
    system_type = platform.system()
    project_rootpath = get_project_rootpath()

    @classmethod
    def recursion_remove_char(cls, str_in: object, space_chars: object, remove_type: object = 2) -> object:
        '''
        Args:
            str_in:
            space_char: 需要被移除的字符
            remove_type: 移除类型，0：去除字符串左边的字符,1：去除右边的字符，2：去除左右两边的字符
        Returns:
        '''
        '''递归去除字符串中首尾特定的字符'''

        def recursion_remove_char_main(str_in_obj, space_char_obj, remove_type_obj):
            if not space_char_obj:
                return str_in_obj
            if not str_in_obj:
                return str_in_obj
            if not isinstance(str_in_obj, str):
                str_in_obj = str(str_in_obj)
            if remove_type_obj == 0:
                if str_in_obj[:len(space_char_obj)] != space_char_obj:
                    return str_in_obj
                return recursion_remove_char_main(str_in_obj=str_in_obj[len(space_char_obj):],
                                                  space_char_obj=space_char_obj, remove_type_obj=remove_type_obj)
            elif remove_type_obj == 1:
                if str_in_obj[-len(space_char_obj):] != space_char_obj:
                    return str_in_obj
                return recursion_remove_char_main(str_in_obj=str_in_obj[:-len(space_char_obj)],
                                                  space_char_obj=space_char_obj, remove_type_obj=remove_type_obj)
            else:
                str_in_obj = recursion_remove_char_main(str_in_obj=str_in_obj, space_char_obj=space_char_obj,
                                                        remove_type_obj=0)
                str_in_obj = recursion_remove_char_main(str_in_obj=str_in_obj, space_char_obj=space_char_obj,
                                                        remove_type_obj=1)
                return str_in_obj

        if isinstance(space_chars, str):
            space_chars = [space_chars]
        for i in space_chars:
            str_in = recursion_remove_char_main(str_in_obj=str_in, space_char_obj=i, remove_type_obj=remove_type)
        return str_in

    @classmethod
    def isevaluatable(cls, str_in, is_dynamic_import_module=False, is_ast_eval=True):
        '''判断字符是否可被eval,安全的做法'''
        try:
            str_in = str(str_in)
            if is_dynamic_import_module:
                str_in = cls.recursion_remove_char(str_in=str_in, space_chars='.')
                module_name, import_result_dict = cls.dynamic_import_module(module_name=str_in)
                if import_result_dict:
                    if __name__ == "__main__":  # 当前模块调用才更新
                        globals().update(import_result_dict)
                    return True
            ast.literal_eval(str_in) if is_ast_eval else eval(str_in)
            return True
        except:
            # traceback.print_exc()
            return False

    @classmethod
    def isevaluatable_unsafety(cls, str_in, is_dynamic_import_module=False):
        '''判断字符是否可被eval,不安全的做法'''
        return cls.isevaluatable(str_in=str_in, is_dynamic_import_module=is_dynamic_import_module, is_ast_eval=False)

    def str_output_case(self, str_in):
        if not isinstance(str_in, str):
            str_in = str(str_in)
        out_str_tuple = (str_in, str_in.lower(), str_in.upper(), str_in.capitalize())
        return out_str_tuple

    def standard_str(self, str_in, **kwargs):
        # '''将带有time关键字的参数放到字符串末尾，并去除参数sign'''
        if not str_in:
            return str_in
        time_key = kwargs['time_key'] if kwargs.get('time_key') else 'time'
        sign_key = kwargs['sign_key'] if kwargs.get('sign_key') else 'sign'
        spilt_key = kwargs['spilt_key'] if kwargs.get('spilt_key') else '\n'
        space_one = kwargs['space_one'] if kwargs.get('space_one') else '='
        str_in_split = str_in.split(spilt_key)
        str_in_split = [i for i in str_in_split if i]
        # '''过滤参数中带有time、sign（根据实际情况修改）得参数'''
        str_in_split_time = [i for i in str_in_split if i.startswith(f'{time_key}{space_one}')]
        str_in_split_sign = [i for i in str_in_split if i.startswith(f'{sign_key}{space_one}')]
        [str_in_split.remove(i) for i in str_in_split_time]
        [str_in_split.remove(i) for i in str_in_split_sign]
        str_in_split.extend(str_in_split_time)
        str_in_split.extend(str_in_split_sign)
        str_out = spilt_key.join(str_in_split)
        return str_out

    def str_to_dict(self, str_in, space_one=':', space_two='\n', is_params_sort=False, **kwargs):
        # '''将str转换为dict输出'''
        if not str_in:
            return {}
        if is_params_sort:
            str_in = self.standard_str(str_in, spilt_key=space_two, space_one=space_one, **kwargs)
        str_in_split = [i.strip() for i in str_in.split(space_two) if i.strip()]
        str_in_dict_keys = [i[:i.find(space_one)].strip() for i in str_in_split]
        str_in_dict_values = [
            eval(i[i.find(space_one) + 1:].strip()) if self.isevaluatable(i[i.find(space_one) + 1:].strip())
            else i[i.find(space_one) + 1:].strip() for i in str_in_split]
        str_in_dict = dict(zip(str_in_dict_keys, str_in_dict_values))
        return str_in_dict

    def dict_to_str(self, dict_in, space_one='=', space_two='&'):
        # 将dict转换为str
        if isinstance(dict_in, dict) and dict_in:
            str_out = ''
            for k, v in dict_in.items():
                str_out += '{}{}{}{}'.format(k, space_one, v, space_two)
            return self.recursion_remove_char(str_in=str_out, space_chars=space_two, remove_type=1)
        return ''

    # 对字典进行排序
    def sorted_dict(self, dict_in):
        if isinstance(dict_in, dict):
            __dict = dict(sorted(dict_in.items(), key=lambda x: x[0]))  # 对字典进行排序
            return __dict
        return None

    def request_data_to_str_postman(self, str_in, space_one=':', space_two='\n'):
        # ''' 一个用于指定输出的postman的方法，去除空格'''
        str_dict = self.str_to_dict(str_in)
        str_out = self.dict_to_str(str_dict, space_one=space_one, space_two=space_two)
        return str_out

    @classmethod
    def encry_main(cls, str_in, encry_type='md5', upper=False, encoding='utf-8'):
        # '''生成md5加密字符串'''
        try:
            str_out = eval(f"hashlib.{encry_type}()")  # 采用md5加密
            str_out.update(str(str_in).encode(encoding=encoding))
            if upper:
                return str_out.hexdigest().upper()
            return str_out.hexdigest()
        except:
            raise encryTypeError(f"不支持的加密方式：,目前支持的加密方式:{hashlib.algorithms_guaranteed}")

    @classmethod
    def encry_aes(cls, data_in, password):
        import os
        from passlib.utils.pbkdf2 import pbkdf2
        def encryptWithPbkdf2(data_in, password):
            interations = 1024
            keyLen = 32
            saltLen = 64
            ivLen = 12
            if isinstance(data_in, dict):
                data_in = json.dumps(data_in)
            salt = os.urandom(saltLen)
            iv = os.urandom(ivLen)
            # key=pbkdf2(secret=password, salt=salt, rounds=interations, keylen=keyLen, prf=digest)
            key = pbkdf2(secret=password, salt=salt, rounds=interations, keylen=keyLen)
            cryptor = AES.new(key, AES.MODE_GCM, iv)
            encrypt_data = cryptor.encrypt(data_in.encode('utf-8'))
            base64_encrypt_data = base64.b64encode(encrypt_data)
            utf8_data = base64_encrypt_data.decode('utf-8')  # base64转换位utf8
            return utf8_data

        enctry_result = encryptWithPbkdf2(data_in=data_in, password=password)
        return enctry_result

    def url_join(self, base, url):
        # 针对url进行拼接
        url_join = urljoin(base, url)
        url_array = urlparse(url_join)
        path = normpath(url_array[2])
        return urlunparse(
            (url_array.scheme, url_array.netloc, path, url_array.params, url_array.query, url_array.fragment))

    def generate_file_lineStr(self, join_str='\t', *args):
        # 生成文件行字符串，传入数组，分割符，完成字符串组装
        generate_str = ''
        for i in args:
            generate_str += str(i) + str(join_str)
        return generate_str.strip()

    def assert_to_pyobject(self, str_in):
        # 将断言中的true/false/null，转换为python对象
        str_dict = self.str_to_dict(str_in)
        src_value_list = ['true', 'false', 'null']
        target_values_list = [True, False, None]
        for str_dict_key in str_dict:
            for index, src_value in enumerate(src_value_list):
                if str_dict[str_dict_key] == src_value:
                    str_dict[str_dict_key] = target_values_list[index]
        return str_dict

    def pyobject_to_json_str(self, str_in, src_value_list=[], target_values_list=[]):
        '''将py对象转换为json_str'''
        if not isinstance(str_in, str):
            return str_in
        src_value_list = ['True', 'False', 'None', '"'] if not src_value_list else src_value_list
        target_values_list = ['true', 'false', 'null', "'"] if not target_values_list else target_values_list
        for index, src_value in enumerate(src_value_list):
            str_in = str_in.replace(src_value, target_values_list[index])
        return str_in

    def json_str_to_pyobject(self, str_in, is_eval=True):
        # 将json_str中的true/false/null，转换为python对象
        src_value_list = [' ', 'true', 'false', 'null', '<NULL>']
        target_values_list = ['', 'True', 'False', 'None', 'None']
        str_in = self.pyobject_to_json_str(str_in=str_in, src_value_list=src_value_list,
                                           target_values_list=target_values_list)
        if is_eval:
            # 处理多个引号的字符
            json_pyobj = eval(str_in) if self.isevaluatable(str_in) else str_in
            if isinstance(json_pyobj, dict):
                for i in json_pyobj:
                    json_pyobj[i] = eval(json_pyobj[i]) if self.isevaluatable(json_pyobj[i]) else json_pyobj[i]
            return json_pyobj
        return str_in

    def check_filename(self, file_name, ignore_chars: (list, tuple, set) = [],
                       priority_matching_chars: (list, tuple, set) = []):
        '''
        校验文件名称的方法，在 windows 中文件名不能包含('\','/','*','?','<','>','|') 字符
        Args:
            ignore_chars: 不需要被替换的字符集合，范围中chars
            priority_matching_chars: 优先被匹配的字符集合，如果不为空，直接使用此集合定义的字符即进行替换

        Returns:
        '''
        if priority_matching_chars:
            for i in priority_matching_chars:
                file_name = file_name.replace(i, '')
            return file_name
        chars = ['\\', '\/', '*', '?', '<', '>', '|', '\n', '\b', '\f', '\t', '\r', '-', ' ', '.', ':', '[', ']']
        chars = [i for i in chars if i not in ignore_chars]
        for i in chars:
            file_name = file_name.replace(i, '')
        return file_name

    def is_contains_chinese(self, strs):
        '''检测字符是否包含中文'''
        for _char in strs:
            if '\u4e00' <= _char <= '\u9fa5':
                return True
        return False

    def recursion_dir_all_dir(self, path, filter_conditions=[]):
        '''
        :param path: 遍历项目下所有的python包目录，以便添加到sys.path
        '''
        dir_list = []
        if not filter_conditions:
            filter_conditions = ['.', '.git', '.idea', '.pytest_cache', '__pycache__']
        for dir_path, dirs, files in os.walk(path):
            dirs = [i for i in dirs if i not in filter_conditions]  # 过滤非必要的目录
            for dir in dirs:
                dir_path_obj = os.path.join(dir_path, dir)
                dir_path_obj_files = os.listdir(dir_path_obj)
                if "__init__.py" in dir_path_obj_files:
                    dir_list.append(dir_path_obj)
        return dir_list

    def recursion_dir_all_file(self, path, file_size_filter=1024 * 10 * 8):
        '''
        :param path: 获取目录及子目录下的所有文件
        '''
        file_list = []
        for dir_path, dirs, files in os.walk(path):
            for file in files:
                file_size = os.stat(os.path.join(dir_path, file)).st_size
                if file_size >= file_size_filter:  # 过滤掉小于10kb的数据
                    file_list.append(os.path.join(dir_path, file))
        return file_list

    def build_str_obj(self, obj: Any, join_blank=True):
        '''输出自带引号的str'''
        if obj and isinstance(obj, str):
            if obj[0] in ('"', '{') and obj[-1] in ('"', '}'):
                obj = "'" + obj + "'"
            else:
                obj = '"' + obj + '"'
            if join_blank:
                obj = ' ' + obj + ' '
        return obj

    @classmethod
    def class_type_repr_dispose(cls, str_in):
        '''将函数repr方法返回的字符处理为eval可识别的字符'''
        str_in = str(str_in).strip()
        str_in_match = re.search('^(\[|<)\S+', str_in)
        if str_in_match:
            str_in = cls.recursion_remove_char(str_in=str_in_match.group(),
                                               space_chars=('[', '<', '"', "'", ' ', '>', '"', "'", ']'),
                                               remove_type=2)
        return str_in

    @classmethod
    def class_type_module_dispose(cls, str_in):
        '''返回eval可识别的类型字符'''
        str_in = str(str_in).strip()
        str_in_match = re.search('[\'"]{0,}<(class|module)\s{1}\S+>[\'"]{0,}', str_in)
        if str_in_match:
            str_in = cls.recursion_remove_char(str_in=str_in,
                                               space_chars=('"', "'", '<class', '<module', ' ', '>', '"', "'"),
                                               remove_type=2)
        else:
            str_in = cls.class_type_repr_dispose(str_in=str_in)
        return str_in

    @classmethod
    def dynamic_import_module(cls, module_name):
        '''动态导入模块'''

        def get_import_result(module_name):
            if isinstance(module_name, (list, tuple, set, dict)):
                module_name = '.'.join([str(i) for i in module_name])
            try:
                meta_class = importlib.import_module(module_name)  # 导入的就是需要导入的那个metaclass
                importlib.reload(meta_class)
                return {module_name: meta_class}
            except (ModuleNotFoundError, BaseException):
                return {}

        def dynamic_import_module_main(package_module):
            if not isinstance(package_module, (list, tuple, set)):
                package_module_split = package_module.split('.')
            else:
                package_module_split = package_module
            import_module_result_dict = {}
            if len(package_module_split) > 1:
                import_module_name = '.'.join(package_module_split[:-1])
                import_module_dict = get_import_result(module_name=import_module_name)
                if import_module_dict:
                    func_module = package_module_split[-1]
                    meta_class = import_module_dict[import_module_name]
                    if hasattr(meta_class, func_module):
                        func_obj = getattr(meta_class, func_module)
                        import_module_result_dict[func_module] = func_obj
            else:
                import_module_dict = get_import_result(module_name=package_module_split[0])
                if import_module_dict:
                    import_module_result_dict.update(import_module_dict)
            return import_module_result_dict

        module_name = cls.class_type_module_dispose(module_name)
        module_name_split = module_name.split('.')
        import_result_dict = {}
        for index, i in enumerate(module_name_split):
            import_result_dict.update(dynamic_import_module_main(package_module=module_name_split[:index + 1]))
        return module_name, import_result_dict

    @classmethod
    def compare_list_polishing(cls, list1: Iterable, list2: Iterable, polishing_str=None) -> (list, tuple):
        # 比较两个list的长度，长度的list用None(polishing_str)补足
        if not (isinstance(list1, Iterable) or isinstance(list2, Iterable)):
            raise objTypeNotIterationError(msg="list1/list2必须是可迭代类型")
        l_con = len(list1)
        l_pr = len(list2)
        if l_con != l_pr:
            l_difference = l_con - l_pr
            _list = []
            if l_difference < 0:
                _list.extend(list1)
                for i in range(abs(l_difference)):
                    _list.append(polishing_str)
                return _list, list2
            else:
                _list.extend(list2)
                for i in range(abs(l_difference)):
                    _list.append(polishing_str)
                return list1, _list
        return list1, list2

    @classmethod
    def check_file_path_is_exits(cls, file_name, type=1):
        '''
        检查文件或者目录是否存在，如果不存在则自动创建
        :param file_name: 文件名称或者目录名称
        :param type: 0:文件夹 1:文件
        :return:
        '''
        if not os.path.exists(file_name):  # 判断文件是否存在
            if type == 0:
                print('文件夹不存在，开始创建:"%s"' % (file_name))
                os.makedirs(file_name)
            if type == 1:
                print('文件不存在，开始创建:"%s"' % (file_name))
                with open(file_name, 'w') as file:  # 创建文件
                    file.close()
            print('"%s"已创建' % (file_name))

    @classmethod
    def get_system_line_break(cls):
        '''根据操作系统类型，返回不同的换行符'''
        if cls.system_type == "Windows":
            line_break = '\r\n'
        elif cls.system_type == "Linux":
            line_break = '\n'
        else:
            line_break = '\r'
        return line_break

    @classmethod
    def dict_parse_generator(cls, params, pre=None):
        def dict_parse_generator_main(params, pre):
            '''递归解析json，如果key为对应的值是list且list中的元素不是dict，则不返回'''
            pre = pre[:] if pre else []  # 纪录value对应的key信息
            if params and isinstance(params, list):
                if isinstance(params[0], dict):
                    params = params[0]

            if isinstance(params, dict):
                for key, value in params.items():
                    if isinstance(value, dict):
                        if len(value) > 0:
                            for d in cls.dict_parse_generator(value, pre + [key]):
                                yield d
                        else:
                            yield pre + [key, '{}']
                    elif isinstance(value, (list, tuple)):
                        if len(value) > 0:
                            for index, v in enumerate(value):
                                # 纪录list的下标与key，方便动态提取
                                if isinstance(v, dict):
                                    for d in cls.dict_parse_generator(v, pre + [key, str(index)]):
                                        yield d
                                else:
                                    yield pre + [key, value]
                        else:
                            yield pre + [key, '[]'] if isinstance(value, list) else pre + [key, '()']

                    else:
                        yield pre + [key, value]

        def de_weight(dict_parse_result):
            '''元素去重'''
            dict_parse_result_out = []
            for i in dict_parse_result:
                if i not in dict_parse_result_out:
                    dict_parse_result_out.append(i)
            return dict_parse_result_out

        dict_parse_result = dict_parse_generator_main(params=params, pre=pre)
        return de_weight(dict_parse_result)


if __name__ == "__main__":
    ot = otherUtil()
    # # dict1=[{'k1':'v1','k2':[1,2,3],'k3':{"k3-1":"v3-1","k3-2":[4,5]},'k4':[{"k4-1":"v4-1"},{"k4-2":"v4-2"}]}]
    # dict1 = {'company_name': '', 'device_sn': '', 'extra_info': '', 'password': '', 'product_name': '',
    #          'registry_id': '', 'soft_version': '', 'username': ''}
    print(globals())
    # dispose_str=ot.class_type_module_dispose(str_in='<selenium.webdriver.remote.webelement.WebElement (session="d6853d3d-f510-400c-8e91-24d40eb5bdf4", element="fc7e4501-40be-4ca3-a7f6-e0871cebdcf9")>')
    # dispose_str2=ot.class_type_module_dispose(str_in='[<selenium.webdriver.remote.webelement.WebElement (session="d6853d3d-f510-400c-8e91-24d40eb5bdf4", element="fc7e4501-40be-4ca3-a7f6-e0871cebdcf9")>]')
    # dispose_str3=ot.class_type_module_dispose(str_in="<class 'selenium.webdriver.remote.webelement.WebElement'>")
    # print(dispose_str)
    # print(dispose_str2)
    # print(dispose_str3)
    # reuslt=ot.recursion_remove_char(str_in='<selenium.webdriver.remote.webelement.WebElement (session="f59b9fcc-0f4a-4eda-8211-156c2732bba3", element="2edc97a7-8918-4c6e-911e-3f16e432a38f")>',space_chars=('<'),remove_type=2)
    # print(reuslt)
