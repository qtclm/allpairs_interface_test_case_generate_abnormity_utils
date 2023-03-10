# _*_ coding: UTF-8 _*_
"""
@file            : wrapper_util
@Author          : qtclm
@Date            : 2023/1/28 11:05
@Desc            : 
"""

import re
import sys
import time
import functools
import traceback
import requests.models
from utils.operation_logging import operationLogging
from utils.data_util import dataUtil

# 注意事项：装饰器不能装饰classmethod
log=operationLogging('wrapper_log')
data_util=dataUtil()


def logger_wrapper(log_level,module_obj=None,class_obj=None,is_send_email=False):
    def logger_wrapper_main(func):
        @functools.wraps(func) #防止函数原信息被改变
        def wrapper(*args,**kwargs):
            log_content=f' func_obj:{func.__name__}'
            if module_obj:
                log_content = f' module_obj:{module_obj},' + log_content
            if class_obj and class_obj!='<module>':
                log_content = f' class_obj:{class_obj},' + log_content
            log.log_main(log_level,is_send_email,f' start call {log_content}, call params: {func.__code__.co_varnames}')
            exec_result=func(*args,**kwargs)
            log.log_main(log_level,is_send_email,f' end call {log_content},call result: {exec_result}')
            return exec_result
        return wrapper
    return logger_wrapper_main

def exec_time_wrapper(round_num:int,module_obj=None,class_obj=None,is_send_email=False):
   def exec_time_wrapper_main(func):
       @functools.wraps(func) #防止函数原信息被改变
       def wrapper(*args, **kwargs):
           s_time = time.perf_counter()
           # 需要定义一个值来接收函数的返回值，否则函数return是无效的
           exec_result=func(*args, **kwargs)
           e_time=time.perf_counter()
           log_content = f' func_obj:{func.__name__} 执行耗时,{round(e_time - s_time, round_num)}s'
           if module_obj:
               log_content = f' module_obj:{module_obj},' + log_content
           if class_obj and class_obj != '<module>':
               log_content = f' class_obj:{class_obj},' + log_content
           log.log_main('info', is_send_email, log_content)
           return exec_result
       return wrapper

   return exec_time_wrapper_main

def phone_validation_check_wapper(func):
    '''手机号验证装饰器'''
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        is_all_match = all([re.search('1[345789][0-9]{9}$', str(i)) for i in args])
        if not is_all_match :
            raise Exception('输入的手机号格式不合法')
        func(*args,**kwargs)
    return wrapper

def email_validation_check_wapper(func):
    '''邮箱格式验证装饰器'''
    @functools.wraps(func)
    def wrapper(*args,**kwargs):
        is_all_match=all([ re.search('\S+@\S+\.com$',str(i)) for i in args])
        if not is_all_match :
            raise Exception('输入的邮箱格式不合法')
        func(*args,**kwargs)
    return wrapper

@exec_time_wrapper(round_num=10)
def retry_wrapper(retry_num,retry_condition,retry_condition_judge:str='==',retry_sleep_time:(int,float)=1,module_obj=None,class_obj=None,is_send_email=False):
    '''
    Args:
        retry_num: 重试次数
        retry_condition: 触发重试的条件
        retry_condition_judge: 重试条件的判断值,可以是：==、not in、in、!=、括号里面的字符只支持相同类型的比较（>= <= > < %=)
        module_obj: 模块对象
        class_obj: 类对象
        is_send_email: 是否触发发送邮件
    Returns:
    '''
    if not isinstance(retry_condition_judge,str):
        raise Exception("retry_condition_judge(重试判断条件)必须是str类型")
    if not isinstance(retry_sleep_time,(int,float)):
        raise Exception("retry_sleep_time(重试等待时间)必须是int、float类型")

    judge_retry_condition_type=retry_condition_judge.lower().strip()
    group_response_status='result_status_match'
    group_response_content='result_content_match'
    py_builtin_types = (str,type(None),int, float, list, set, tuple, dict, bool, bytes, type) #定义python内置类型，用于判断

    def retry_wrapper_main(func):
        @functools.wraps(func) #防止函数原信息被改变
        def wrapper(*args,**kwargs):
            def retry_func(judge_condition_statement,retry_condition_str,judge_retry_condition_type,group_type):
                '''函数重试逻辑'''
                func_exec_result=None
                for i in range(retry_num):
                    # 重试等待时间随重试次数增加而增加
                    log.log_main('info',False,f"retry前等待:{retry_sleep_time+i}s")
                    time.sleep(retry_sleep_time+i)
                    func_exec_result=func(*args,**kwargs)
                    judge_condition_statement=judge_condition_statement_dispose(group_type=group_type,judge_retry_condition_type=judge_retry_condition_type,
                                               judge_condition_statement=judge_condition_statement,exec_result=func_exec_result,retry_condition_str=retry_condition_str)

                    log.log_main('info',False,f"retry_第{i+1}次:{judge_condition_statement}")
                    if eval(judge_condition_statement):
                        log.log_main('info', is_send_email, f' {log_content},请求重试成功,重试次数为:{i + 1}')
                        # print("func_exec_result:",func_exec_result)
                        return func_exec_result

                log.log_main('error', is_send_email, f' {log_content},请求重试失败,返回函数最新执行结果')
                return func_exec_result

            def check_retry_condition_judge_and_return_group(judge_retry_condition_type,exec_result,legal_chars):
                '''校验重试判断条件字符合法性'''
                if not judge_retry_condition_type in legal_chars:
                    log_content = f'judge_retry_condition_type只能是:{legal_chars}中的任意一个字符'
                    log.log_main('error', is_send_email, log_content)
                    raise Exception(log_content)

                '''校验重试判断条件in not in时重试条件的数据类型是否合法'''
                if judge_retry_condition_type in ('in', 'not in'):
                    if (not isinstance(retry_condition, (list, set, tuple, dict))):
                        log_content = f'judge_retry_condition_type为in或者not in时,retry_condition必须可迭代'
                        log.log_main('error', is_send_email, log_content)
                        raise Exception(log_content)

                elif judge_retry_condition_type in ('<','>','>=','<='):
                    if ( isinstance(exec_result,py_builtin_types))  and  (type(exec_result)!=type(retry_condition)):
                        log_content = f'judge_retry_condition_type为(<,>,>=,<=)时,retry_condition与exec_result的类型必须一致'
                        log.log_main('error', is_send_email, log_content)
                        raise Exception(log_content)
                elif judge_retry_condition_type=='size':
                    if not isinstance(retry_condition,(int,float)):
                        log_content = f'judge_retry_condition_type为size时,retry_condition类型必须为int、float'
                        log.log_main('error', is_send_email, log_content)
                        raise Exception(log_content)


                if judge_retry_condition_type in ('==','!=', '>=', '<=', '>', '<', 'in','not in'):
                    return group_response_status
                return group_response_content

            def retry_condition_and_exec_result_dispose(retry_condition,exec_result):
                '''处理重试条件与函数执行结果'''
                def response_dispose(response,attribute='status_code'):
                    '''如果类型是response且包含特定属性，返回属性'''
                    if isinstance(response,requests.models.Response):
                        is_status_code = hasattr(response, attribute)
                        args_obj_str = eval(f'int(response.{attribute})') if is_status_code else response
                        return args_obj_str
                    return response

                def class_repr_obj_type_dispose(exec_result):
                    '''返回可被eval的数据类型'''
                    args_obj_str, import_module_dict = data_util.dynamic_import_module(module_name=exec_result)
                    if import_module_dict:
                        globals().update(import_module_dict)
                        if all([i in import_module_dict.keys() for i in args_obj_str.split('.')]):
                            args_obj_str = eval(args_obj_str)
                        else:
                            args_obj_str = data_util.build_str_obj(args_obj)
                    else:
                        args_obj_str = eval(exec_result) if \
                            data_util.isevaluatable_unsafety(exec_result, is_dynamic_import_module=False) \
                            else data_util.build_str_obj(exec_result)
                    return args_obj_str

                def retry_condition_and_exec_result_dispose_main(args_obj):
                    if not isinstance(args_obj,py_builtin_types):
                        return args_obj
                    args_obj_str=args_obj
                    if isinstance(args_obj_str, str):
                        args_obj_str=class_repr_obj_type_dispose(args_obj_str)
                    return args_obj_str

                retry_condition = retry_condition_and_exec_result_dispose_main(retry_condition)
                exec_result=retry_condition_and_exec_result_dispose_main(exec_result)


                # 处理retry条件为http状态响应码
                if isinstance(exec_result,requests.models.Response) \
                        and isinstance(retry_condition,(int,list,tuple,set,dict)):
                    exec_result=response_dispose(exec_result)


                # '''处理重试条件类型与函数执行结果类型不一致任意一方是类型的字符串形式的情况'''
                if type(retry_condition)!=type(exec_result):
                    if (not isinstance(retry_condition,py_builtin_types)) \
                        and (not isinstance(retry_condition,type)):
                            retry_condition=type(retry_condition)

                    if (not isinstance(exec_result,py_builtin_types)) \
                        and  (not isinstance(exec_result, type)):
                            exec_result = type(exec_result)

                    if isinstance(retry_condition, py_builtin_types) or isinstance(exec_result,py_builtin_types):
                        retry_condition = f' {retry_condition} '
                        exec_result = f' {exec_result} '

                    retry_condition_type_module_str=data_util.class_type_module_dispose(retry_condition) if not data_util.isevaluatable_unsafety(retry_condition) else retry_condition
                    exec_result_type_module_str=data_util.class_type_module_dispose(exec_result) if not data_util.isevaluatable_unsafety(exec_result) else exec_result
                    if  str(retry_condition)!=retry_condition_type_module_str:
                        retry_condition = data_util.build_str_obj(retry_condition_type_module_str)
                    if  str(exec_result)!=exec_result_type_module_str:
                        exec_result=data_util.build_str_obj(exec_result_type_module_str)

                elif type(retry_condition)==type(exec_result):
                    '''如果类型相同，直接比较值'''
                    if data_util.isevaluatable_unsafety(retry_condition) and data_util.isevaluatable_unsafety(exec_result):
                        retry_condition = f' {retry_condition} '
                        exec_result = f' {exec_result} '
                    else:
                        retry_condition= [ str(i) for i in retry_condition]
                        exec_result= [ str(i) for i in exec_result]

                else:
                    exec_result = type(exec_result) if type(exec_result) != type else exec_result
                    retry_condition = type(retry_condition) if type(
                        retry_condition) != type else retry_condition
                    retry_condition = data_util.build_str_obj(f'{retry_condition}')
                    exec_result = data_util.build_str_obj(f'{exec_result}')

                return retry_condition,exec_result

            def judge_condition_statement_dispose(group_type:str,judge_retry_condition_type:str,judge_condition_statement:str,
                                                  exec_result,retry_condition_str:str):
                '''根据重试判断条件、重试判断类型，处理为最终需要的重试判断语句'''

                # '''用于函数执行结果为type的情况(例如：requests.request的执行结果是requests.models.Response)'''
                if group_type==group_response_status:
                    retry_condition_str, exec_result = retry_condition_and_exec_result_dispose(retry_condition,exec_result)
                    judge_condition_statement = f"{exec_result}{judge_retry_condition_type}{retry_condition_str}"
                # '''用于函数结果是str、dict、bytes的情况（常规情况下建议使用此方式）'''
                elif group_type==group_response_content:
                    if judge_retry_condition_type == 'json_path':
                        exec_result = data_util.json_path_parse_public(json_path=retry_condition, json_obj=exec_result)
                        judge_condition_statement = f"{exec_result}"

                    elif judge_retry_condition_type == 'regex':
                        exec_result_match = re.search(retry_condition_str, str(exec_result))
                        if exec_result_match:
                            exec_result=exec_result_match.group()
                            exec_result=exec_result if data_util.isevaluatable_unsafety(exec_result) else data_util.build_str_obj(exec_result)
                        else:
                            exec_result = None
                        judge_condition_statement = f'{exec_result}'

                    elif judge_retry_condition_type == 'size':
                        exec_result_size = len(str(exec_result).encode('utf-8')) if not \
                            isinstance(exec_result,bytes) else len(exec_result)
                        retry_condition_str = int(retry_condition_str)
                        judge_condition_statement = f'{exec_result_size} >= {retry_condition_str}'
                return f'{judge_condition_statement}'

            log_content=f'func_obj:{func.__name__}'
            if module_obj:
                log_content = f' module_obj:{module_obj},' + log_content
            if class_obj and class_obj!='<module>':
                log_content = f' class_obj:{class_obj},' + log_content
            legal_chars=('==','!=', '>=', '<=', '>', '<', 'in','not in','json_path','regex','size')
            '''检查重试判断条件是否合法'''
            exec_result=func(*args,**kwargs)
            # print("exec_result:",exec_result)
            group_type=check_retry_condition_judge_and_return_group(judge_retry_condition_type=judge_retry_condition_type,exec_result=exec_result,legal_chars=legal_chars)
            judge_condition_statement="True"
            retry_condition_str=retry_condition
            judge_condition_statement = judge_condition_statement_dispose(group_type=group_type,judge_retry_condition_type=judge_retry_condition_type,
                                          judge_condition_statement=judge_condition_statement,exec_result=exec_result,retry_condition_str=retry_condition_str)
            try:
                if eval("not "+judge_condition_statement):
                    log.log_main('info',False,f'before: {judge_condition_statement}')
                    exec_result=retry_func(judge_condition_statement=judge_condition_statement,retry_condition_str=retry_condition_str,group_type=group_type,
                               judge_retry_condition_type=judge_retry_condition_type)
            except:
                log_content='exec_result与retry_condition类型不一致时只能使用==、!=,退出重试并返回函数原始执行结果,具体异常信息:\n'
                log.log_main('error', is_send_email, log_content+traceback.format_exc())
            finally:
                return exec_result
        return wrapper
    return retry_wrapper_main

class demo():
    num=0

    @retry_wrapper(retry_num=3,retry_condition=0,retry_condition_judge='==')
    # @logger_wrapper(log_level='info')
    def demo1(self,*args,**kwargs):

        obj=int(time.time())
        print(obj)
        return obj
        # self.num += 1
        # if self.num==4:
            # return 10
        # return self.num
        # return {'data':self.num}

    @classmethod
    def demo2(cls):
        print(cls.num)

    # @retry_wrapper(retry_num=3,retry_condition='$..swagger',retry_condition_judge='json_path')
    # @retry_wrapper(retry_num=3,retry_condition='\w+',retry_condition_judge='regex')
    @retry_wrapper(retry_num=3,retry_condition=10,retry_condition_judge='size')
    def demo3(self):
        import requests
        # req=requests.get(url='http://www.baidu.com')
        req=requests.get(url='http://10.4.196.168:31621/v2/api-docs')
        return req.json()
        # return req.text


if __name__=="__main__":
    # print(demo().demo1(1, 2))
    print(666,demo().demo1())
