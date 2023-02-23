# _*_ coding: UTF-8 _*_
"""
@project -> file : city-test -> exception_util
@Author          : qinmin.vendor
@Date            : 2023/2/21 11:13
@Desc            : 
"""
from api_case_generate_tools.utils.operation_logging import operationLogging


class baseError(Exception):
    """
    异常基类
    """
    def __init__(self,msg):
        self.msg=msg
        log = operationLogging()
        log.log_main('error', False, self.msg)


class opeartionTypeError(baseError):
    """
    excel操作类型错误
    """
    def __init__(self,msg):
        super(opeartionTypeError,self).__init__(msg=msg)

class sheetNameNotFoundError(baseError):
    """
    未找到sheetname错误
    """

    def __init__(self,msg):
        super(sheetNameNotFoundError,self).__init__(msg=msg)
class customApiEnumTypeError(baseError):
    """
    custom_api_enum_type不匹配错误
    """

    def __init__(self,msg):
        super(customApiEnumTypeError,self).__init__(msg=msg)

class paramsObjTypeError(baseError):
    """
    params_obj_type不匹配错误
    """

    def __init__(self,msg):
        super(paramsObjTypeError,self).__init__(msg=msg)

class excelObjTypeError(baseError):
    """
    params_obj_type不匹配错误
    """

    def __init__(self,msg):
        super(excelObjTypeError,self).__init__(msg=msg)


class paramsTypeEnumError(baseError):
    '''
    数据枚举为空错误
    '''
    def __init__(self,msg):
        super(paramsTypeEnumError,self).__init__(msg=msg)


class objNotCallError(baseError):
    '''对象不可调用错误'''
    def __init__(self,msg):
        super(objNotCallError,self).__init__(msg=msg)

class fileNotFoundError(baseError):
    '''文件没有找到错误'''
    def __init__(self,msg):
        super(fileNotFoundError,self).__init__(msg=msg)