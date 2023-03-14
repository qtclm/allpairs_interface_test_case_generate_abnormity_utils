# _*_ coding: UTF-8 _*_
"""
@project -> file : allpairs_interface_test_case_generate_abnormity_utils -> upload_file
@Author          : qinmin.vendor
@Date            : 2023/3/13 17:11
@Desc            : 
"""
import ast
import os.path
import requests
from requests_toolbelt import MultipartEncoder


def recursion_remove_char(str_in: object, space_chars: object, remove_type: object = 2) -> object:
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


def isevaluatable(str_in,is_ast_eval=True):
    '''判断字符是否可被eval,安全的做法'''
    try:
        str_in = str(str_in)
        ast.literal_eval(str_in) if is_ast_eval else eval(str_in)
        return True
    except:
        # traceback.print_exc()
        return False


def str_to_dict(str_in, space_one=':', space_two='\n', is_params_sort=False, **kwargs):
    # '''将str转换为dict输出'''
    if not str_in:
        return {}
    str_in_split = [i.strip() for i in str_in.split(space_two) if i.strip()]
    str_in_dict_keys = [i[:i.find(space_one)].strip() for i in str_in_split]
    str_in_dict_values = [
        eval(i[i.find(space_one) + 1:].strip()) if isevaluatable(i[i.find(space_one) + 1:].strip())
        else i[i.find(space_one) + 1:].strip() for i in str_in_split]
    str_in_dict = dict(zip(str_in_dict_keys, str_in_dict_values))
    return str_in_dict


def dict_to_str(dict_in, space_one='=', space_two='&'):
    # 将dict转换为str
    if isinstance(dict_in, dict) and dict_in:
        str_out = ''
        for k, v in dict_in.items():
            str_out += '{}{}{}{}'.format(k, space_one, v, space_two)
        return recursion_remove_char(str_in=str_out, space_chars=space_two, remove_type=1)
    return ''

def upload(url,file_name,file_type='image/png',fdKey='fd_3ae0b3fd807b1c'):
    parmas='''docSubject:测试666
fdId:186da38a7207f68635cbd364902b18e4
fdFlowId:181dc9bc3547d559e67102d4d518f19b
fdModelId:1818f7443b838ff6cd9fd8e49cfb96ff
formValues:{'fd_3ae49ceb23d46c':'66'}
docStatus:20
docCreator:{'LoginName':'RPA_002'}
flowParam:{'operationType':'handler_pass','auditNote':'同意'}
attachmentForms[0].fdKey:%s
attachmentForms[0].fdFileName:%s'''%(fdKey,file_name)
    parmas_dict=str_to_dict(parmas,space_one=':',space_two='\n')
    files = {'file': (file_name.split(os.sep)[-1],open(file_name, mode='rb'), file_type)}
    parmas_dict["attachmentForms[0].fdAttachment"]=files
    for i in parmas_dict:
        parmas_dict[i]=str(parmas_dict[i])
    m = MultipartEncoder(
                fields=parmas_dict
            )
    req_headers = {"Content-Type": m.content_type}
    req = requests.post(url=url, data=m, headers=req_headers)
    print(req)

if __name__=="__main__":
    upload(url='http://www.baidu.com', file_name='../../huochetong_auto_test/utils/update_metaverse_config.py')