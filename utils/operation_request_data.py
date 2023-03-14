# -*- coding: utf-8 -*-
"""
__author__ = qtclm
File Name：     DataUtil
date：          2020/8/12 16:10
"""
from utils.data_util import dataUtil


class operationRequestData(dataUtil):
    def __init__(self):
        super(operationRequestData,self).__init__()

    # dependkey生成
    def depend_key_generate(self, str_in, join_str=''):
        if not isinstance(str_in, dict):
            str_dict = self.str_to_dict(str_in)
        else:
            str_dict = str_in
        if str_dict:
            out_list = [str(join_str) + str(i) for i in str_dict.keys()]
            return out_list
        else:
            return None

    # 将dependfield替换至请求数据，输出dict
    def depend_filed_to_request_data(self, depend_filed, str_in):
        # '''将str_in输出的dict中的key批量替换为denpend_filedkey的值'''
        # print(self.log.out_varname(denpend_filed))
        if isinstance(depend_filed, dict):
            str_in_dict = self.str_to_dict(str_in)
            # '''完成参数替换'''
            str_in_dict.update(depend_filed)
            return str_in_dict
        return None

    # 将替换完成的请求数据，转换为str并输出
    def request_data_depend(self, depend_filed, str_in, space_one=':', space_two='\n'):
        '''数据依赖请求专用，输入依赖字段信息，输出处理完成的字符串'''
        str_dict = self.depend_filed_to_request_data(depend_filed, str_in)
        str_out = self.str_to_dict(str_dict, space_one, space_two)
        return str_out

    # '''常规字符处理，用于处理chrome复制出来的表单数据，输出k1=v1&k2=v2... '''
    def request_data_general(self, str_in, space_one='=', space_two='&'):
        # 将str转换为dict输出
        str_dict = self.str_to_dict(str_in)
        if str_dict:
            str_out = self.str_to_dict(str_dict, space_one, space_two)
            return str_out.encode()
        else:
            return None

    # 最终输出得请求数据，此方法输出str
    def request_to_str(self, str_in, space_one='=', space_two='&'):
        out_str = self.str_to_dict(str_in,space_one=space_one,space_two=space_two)
        return out_str

    def request_to_dict(self, str_in, space_one='=', space_two='&'):
        requests_dict = self.str_to_dict(str_in,space_one=space_one,space_two=space_two)
        return requests_dict

    # ''' 一个用于指定输出的方法，一般不使用'''
    def request_data_custom(self, str_in, str_custom='=>', space_two='\n'):
        str_dict = self.str_to_dict(str_in)
        str_out = self.str_to_dict(str_dict, space_one=str_custom, space_two=space_two)
        return str_out

    # '''批量生成数组格式的数据'''
    def create_batch_data(self, str_in, list_in):
        str_dict = self.str_to_dict(str_in)
        array_str = '[0]'
        array_list = [i for i in str_dict.keys() if array_str in i]
        if array_list:
            array_key = array_list[0]
        else:
            return None
        for index, value in enumerate(list_in):
            _dict_key = '{}{}{}'.format(array_key[:-2], index, array_key[-1])
            str_dict[_dict_key] = value
        out_str = self.str_to_dict(str_dict)
        return out_str.encode()

    # 输入tuple（1.file字段：例如：file，head，具体以系统定义为准，2.文件绝对路径）,输出需要得files对象，用于文件上传
    def out_join_files(self, tuple_in, mode='rb'):
        # 输出files示例
        #  files = {'file': ('git.docx', open('C:/Users/Acer/Downloads/git.docx', 'rb'))}
        if not isinstance(tuple_in, (tuple, list)) and len(tuple_in) == 2:
            print('类型不是tuple或者list，或长度不标准')
            return None
        else:
            tuple_field, tuple_filepath = tuple_in
            file_index = tuple_filepath.rfind('/')
            if file_index == '-1':
                file_index = tuple_filepath.rfind('\\')
                if not file_index == -1:
                    filename = tuple_filepath[file_index + 1:]
                else:
                    filename = 'git(默认值).docx'
                    tuple_filepath = 'C:/Users/Acer/Downloads/git.docx'
            else:
                filename = tuple_filepath[file_index + 1:]
            files = {tuple_field: (filename, open(tuple_filepath, mode))}
            return files

if __name__ == "__main__":
    pass
