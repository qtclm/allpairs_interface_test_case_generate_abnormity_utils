# _*_ coding: UTF-8 _*_
"""
@file            : exception_util
@Author          : qtclm
@Date            : 2023/2/21 11:13
@Desc            : 
"""
from utils.operation_logging import operationLogging


class baseError(Exception):
    """
    异常基类
    """
    log = operationLogging('exception_log')

    def __init__(self,msg,Reason=None):
        self.msg=msg
        self.log.log_main('error', False, self.msg)
        Exception.__init__(self, msg, Reason)


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

class baseElementTypeError(baseError):
    '''web、ui类型错误'''
    def __init__(self,msg):
        super(baseElementTypeError,self).__init__(msg=msg)


class projectRootPathNotFoundError(baseError):
    '''项目根目录没找到错误'''
    def __init__(self,msg):
        super(projectRootPathNotFoundError,self).__init__(msg=msg)

class encryTypeError(baseError):
    '''加密方式不支持错误'''
    def __init__(self,msg):
        super(encryTypeError,self).__init__(msg=msg)

class objTypeNotIterationError(baseError):
    '''类型不可迭代错误'''
    def __init__(self,msg):
        super(objTypeNotIterationError,self).__init__(msg=msg)

class notFoundRuningDeviceError(baseError):
    '''没有找到正在运行的设备'''
    def __init__(self,msg):
        super(notFoundRuningDeviceError,self).__init__(msg=msg)

class getPackageForApkFileError(baseError):
    '''根据apk文件包名查询包名错误'''
    def __init__(self,msg):
        super(getPackageForApkFileError,self).__init__(msg=msg)

class databaseConnectError(baseError):
    def __init__(self, msg='数据库连接异常,请查看本地MySql服务是否启动！', Reason=None):
        super(databaseConnectError, self).__init__(msg=msg,Reason=Reason)

class sqlExcuteError(baseError):
    def __init__(self, msg='sql执行异常，请检查sql语法是否合法', Reason=None):
        super(sqlExcuteError, self).__init__(msg=msg,Reason=Reason)

class readConfigError(baseError):
    def __init__(self, msg='Config读取初始化失败', Reason=None):
        super(readConfigError, self).__init__(msg=msg,Reason=Reason)


class mailInitializationError(baseError):
    def __init__(self, msg='邮件初始化', Reason=None):
        super(mailInitializationError, self).__init__(msg=msg,Reason=Reason)


class readYamlError(baseError):
    def __init__(self, msg='Yaml读取初始化失败', Reason=None):
        super(readConfigError, self).__init__(msg=msg,Reason=Reason)


class assertionAnomaly(baseError):
    def __init__(self, msg='断言失败', Reason=None):
        super(assertionAnomaly, self).__init__(msg=msg,Reason=Reason)


class readExcelError(baseError):
    def __init__(self, msg='读取Excel失败', Reason=None):
        super(readExcelError, self).__init__(msg=msg,Reason=Reason)


class closeFileError(baseError):
    def __init__(self, msg='关闭文件时发生错误', Reason=None):
        super(closeFileError, self).__init__(msg=msg,Reason=Reason)


class logConfigError(baseError):
    def __init__(self, msg='日志配置初始化错误', Reason=None):
        super(logConfigError, self).__init__(msg=msg,Reason=Reason)


class requestError(baseError):
    def __init__(self, msg='请求时发生错误', Reason=None):
        super(requestError, self).__init__(msg=msg,Reason=Reason)


class statusCodeAbnormal(baseError):
    def __init__(self, msg='状态码异常', Reason=None):
        super(statusCodeAbnormal, self).__init__(msg=msg,Reason=Reason)


class writeResultError(baseError):
    def __init__(self, msg='写入测试结果失败', Reason=None):
        super(writeResultError, self).__init__(msg=msg,Reason=Reason)



class readFileError(baseError):
    def __init__(self, msg='读取文件失败', Reason=None):
        super(readExcelError, self).__init__(msg=msg,Reason=Reason)


class dingTalkConnectError(baseError):
    def __init__(self, msg='钉钉连接异常', Reason=None):
        super(dingTalkConnectError, self).__init__(msg=msg,Reason=Reason)


class jsonFormatError(baseError):
    def __init__(self, msg='JSON格式化输出异常', Reason=None):
        super(jsonFormatError, self).__init__(msg=msg,Reason=Reason)


class shellEnterError(baseError):
    def __init__(self, msg='命令行输入异常',Reason=None):
        super(shellEnterError, self).__init__(msg=msg, Reason=Reason)


class getTestCaseError(baseError):
    def __init__(self, msg='获取测试用例异常',Reason=None):
        super(getTestCaseError, self).__init__(msg=msg, Reason=Reason)


class dataTransformError(baseError):
    def __init__(self, msg='数据转换异常',Reason=None):
        super(dataTransformError, self).__init__(msg=msg, Reason=Reason)

class argsTypeError(baseError):
    def __init__(self, msg='参数类型错误',Reason=None):
        super(argsTypeError, self).__init__(msg=msg, Reason=Reason)

class jsonPathExtractError(baseError):
    def __init__(self, msg='jsonpath提取失败',Reason=None):
        super(jsonPathExtractError, self).__init__(msg=msg, Reason=Reason)


if __name__=="__main__":
    raise getPackageForApkFileError(msg='apk file not found')