# _*_ coding: UTF-8 _*_
"""
@project -> file : city-test -> rr
@Author          : qinmin.vendor
@Date            : 2023/1/29 19:44
@Desc            :
"""

import os
from loguru import logger
# 发生Error日志时，发邮件进行警报
from api_case_generate_tools.utils.send_email import sendEmail
from tabulate import tabulate
from api_case_generate_tools.utils.time_util import timeUtil

class operationLogging(object):
    __email = sendEmail()
    __instance=None
    __email_user_list=None
    __log_path=None
    email_sub='日志告警' #邮件标题
    time_util=timeUtil()
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__log_path = cls.log_path()
            cls.__instance=object.__new__(cls)
        return cls.__instance

    @classmethod
    def log_path(self):
        """Get log directory"""
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "log")
        if not os.path.exists(path):
            os.mkdir(path)
        return path


    @classmethod
    def json_log_msg(cls,*log_msg):
        try:
            if not isinstance(log_msg,(tuple,list,set)):
                return log_msg
            log_msg=','.join(log_msg)
        except:
            log_msg=','.join([str(i) for i in log_msg])
        finally:
            return log_msg

    @classmethod
    def log_main(cls,log_level,is_send_email=False,*log_msg):
        '''
        Args:
            log_level:
            *log_msg:
        Returns:
        '''
        # 去除控制台日志
        # logger.remove(handler_id=None)


        log_msg=cls.json_log_msg(*log_msg)
        date=cls.time_util.timestamp_to_string(is_date=True)
        __log_name=os.path.join(cls.__log_path,f"{log_level}_{date}.log")
        logger_conf = {
            "format": '{time:YYYY-MM-DD HH:mm:ss} | {level}   |  {module}:{function}:{line}  process_id:{process} thread_id:{thread}, log_content:{message}',
            # 配置按大小滚动:rotation,  压缩日志:compression, 多进程安全:enqueue=True
            "rotation":"10 MB","compression":"zip","enqueue":True,
            # 错误堆栈
            "backtrace" : True, "diagnose" : True,
            'encoding':'utf-8',
            'level':'INFO', #级别等于或高于info的日志才会记录日志到文件中
        }
        # 添加log_headel,并记录对应的线程
        log_handel=logger.add(__log_name,**logger_conf)
        if log_level not in ('debug','info','warning','error'):
            log_level='info'
        exec(f"logger.{log_level}(log_msg)")
        if is_send_email:
            cls.__email.send_msg(sub=cls.email_sub,msg=log_msg,user_list=cls.__email_user_list)
        # 移除handel，避免重复打印
        logger.remove(log_handel)


    @classmethod
    def log_main_table(cls,log_level,is_send_email=False,tabel_header=[],tabel_data=[],tablefmt='grid'):
        '''打印表格形式的日志,配合tabulate使用:
        https://blog.csdn.net/qq_43901693/article/details/104920856
         tablefmt支持： 'plain', 'simple', 'grid', 'pipe', 'orgtbl', 'rst', 'mediawiki',
    'latex', 'latex_raw', 'latex_booktabs', 'latex_longtable' and tsv 、jira、html'''
        def convert_to_container(obj):
            if not isinstance(obj,(list,tuple,set)):
                return [obj]
            return obj

        tabel_header = convert_to_container(tabel_header)
        tabel_data=convert_to_container(tabel_data)
        log_msg=tabulate(tabular_data=tabel_data,headers=tabel_header,tablefmt=tablefmt)
        log_msg=f'\ntabel_format:{tablefmt}\n{log_msg}'
        cls.log_main(log_level,is_send_email,log_msg)



if __name__=="__main__":
    op_log=operationLogging()
    # op_log.log_main('info',True,'1','2','3',(1,2,34))
    # op_log.log_main('debug',True,'1','2','3',(1,2,34))
    op_log.log_main_table(log_level='info',is_send_email=False,tabel_header=['name','age'],tabel_data=[('xiaoming',12),('xiaobai',13)],tablefmt='html')

