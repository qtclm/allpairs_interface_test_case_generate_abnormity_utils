# _*_ coding: UTF-8 _*_
"""
@project -> file : city-test -> servers_util
@Author          : qinmin.vendor
@Date            : 2023/2/8 19:25
@Desc            : 
"""

import re
import subprocess
import tempfile
import sys
import traceback
import platform
from api_case_generate_tools.utils.operation_logging import operationLogging

system_type=platform.system()
log=operationLogging()

def get_system_line_break():
    '''根据操作系统类型，返回不同的换行符'''
    if system_type == "Windows":
        line_break='\r\n'
    elif system_type == "Linux":
        line_break = '\n'
    else:
        line_break='\r'
    return line_break

def get_pid_for_port(port=4723):
    '''根据端口查询对应的进程id'''
    filter_str='findstr' if system_type=='Windows' else 'grep'
    cmd_find =f'netstat -ano|{filter_str} {port}'
    command_exec_result = excuteCommand(cmd_find)
    port_pid_info = [i for i in command_exec_result if ':{} '.format(port) in i]  # 过滤端口中包含4723的信息，以免造成程序误判
    if port_pid_info:
        pid = re.search('\d+$',port_pid_info[0].strip())
        if pid :
            pid=pid.group()
            # 执行被占用端口的pid
            if int(pid)>0:
                return pid


def kill_port_process(port=4723):
    # 6.根据系统和端口号关闭对应的进程
    # 查找对应端口的pid
    pid = get_pid_for_port(port)
    if not pid:
        return '根据端口未查询到进程占用'
    command=f'taskkill -t -f /pid {pid}' if sys.platform=='Windows' else f'kill -9 {pid}'
    return excuteCommand(command)


# 命令执行封装
def excuteCommand(command,commandType='subPopen',clog_exec=True):
    # clog_exec:windows环境将start字符串拼接在命令前，防止程序运行阻塞，默认为阻塞
    # commandType：指定命令类型
    result = None
    if clog_exec==False and system_type=='Windows':
        command='start {}'.format(command)
    try:
        log_content = f'exec command:\n{command}\ncommand_type:{commandType},clog_exec:{clog_exec}'
        log.log_main('info', False, log_content)
        if commandType not in ('system','popen','subPopen'):
            return result
        if commandType in ('system','popen'):
            exec(f"result=os.{commandType}(command)")
        #Python中使用subprocess执行一系列cmd命令时，偶尔会出现阻塞情况，命令没有继续执行完毕。
        # 解决：1.使用临时文件tempfile扩展缓存区；2.去掉不必要输出，以减少输出量的大小
        elif commandType=='subPopen':
            out_temp = tempfile.SpooledTemporaryFile(max_size=10 * 1000)
            fileno = out_temp.fileno()
            line_break=get_system_line_break()
            stdout=subprocess.PIPE if system_type=='Windows' else fileno
            p = subprocess.Popen(command, shell=True, stdout=stdout,
                                 stderr=subprocess.PIPE)  # stdout=subprocess.PIPE
            result=p.communicate()
            # print("first_exec:",result)
            if isinstance(result,(tuple,list,set)) and result[0]==None and result[1]==b'' :
                result=subprocess.getoutput(command)

            if isinstance(result,str):
                result=result.split(line_break)

            result = [i.decode("utf8", "ignore").strip() if isinstance(i,bytes) else i.strip() for i in result if i]
            if not result:
                return result
            if len(result)>1:
               result=[i.split(line_break)[0] if i.split(line_break) else i for i in result if i]
            else:
                result=[i.split(line_break) for i in result if i][0]
            result = [i for i in result if i]
        return result
    except :
        traceback.print_exc()

if __name__=="__main__":
    test_dir='D:\city-pro-test' if system_type=='Windows' else '/home/qinmin/city-pro-test'
    # command=f'pytest -s -q  {test_dir} --env staging  -k "test_shebei_guanli"  --count 1  --collect-only '
    command=f'pip install airtest==1.2.7'
    commandType = 'subPopen'
    result=excuteCommand(command=command,commandType='subPopen')
    print(result)