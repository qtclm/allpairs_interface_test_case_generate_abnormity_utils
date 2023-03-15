# _*_ coding: UTF-8 _*_
"""
@file            : servers_util
@Author          : qtclm
@Date            : 2023/2/8 19:25
@Desc            : 
"""

import re
import subprocess
import tempfile
import traceback
import platform
from utils.operation_logging import operationLogging

system_type = platform.system()
log = operationLogging('servers_util')


def get_system_line_break():
    '''根据操作系统类型，返回不同的换行符'''
    if system_type == "Windows":
        line_break = '\r\n'
    elif system_type == "Linux":
        line_break = '\n'
    else:
        line_break = '\r'
    return line_break

def get_system_filter_break():
    '''根据操作系统类型，返回不同的文本过滤字符'''
    if system_type == "Windows":
        filter_break = 'findstr'
    else:
        filter_break = 'grep'
    return filter_break

def get_system_kill_pid_break():
    '''根据操作系统类型，返回不同的进程kill字符'''
    if system_type == "Windows":
        kill_pid_break = 'taskkill -f -pid'
    else:
        kill_pid_break = 'kill -9'
    return kill_pid_break


def get_pid_for_port(port=4723):
    '''根据端口查询对应的进程id'''
    filter_str = get_system_filter_break()
    cmd_find = f'netstat -ano|{filter_str} {port}'
    command_exec_result = excute_command(cmd_find)
    port_pid_info = [i for i in command_exec_result if ':{} '.format(port) in i]  # 过滤端口中包含4723的信息，以免造成程序误判
    if port_pid_info:
        pid = re.search('\d+$', port_pid_info[0].strip())
        return pid if pid and int(pid.group()) else None


def kill_port_process(port=4723):
    # 6.根据系统和端口号关闭对应的进程
    # 查找对应端口的pid
    pid = get_pid_for_port(port)
    if not pid:
        return '根据端口未查询到进程占用'
    command = f'{get_system_kill_pid_break()} {pid}'
    return excute_command(command)


# 命令执行封装
def excute_command(command, command_type='subPopen', clog_exec=True):
    # clog_exec:windows环境将start字符串拼接在命令前，防止程序运行阻塞，默认为阻塞
    # command_type：指定命令类型
    result = None
    if clog_exec == False:
        if system_type == 'Windows':
            command = f'start {command}'
        else:
            command=f'nohup {command} &'

    try:
        # log_content = f'exec command:\n{command}\ncommand_type:{command_type},clog_exec:{clog_exec}'
        # log.log_main('info', False, log_content)
        # print(command)
        if command_type not in ('system', 'popen', 'subPopen'):
            return result
        if command_type in ('system', 'popen'):
            exec(f"result=os.{command_type}(command)")
        # Python中使用subprocess执行一系列cmd命令时，偶尔会出现阻塞情况，命令没有继续执行完毕。
        # 解决：1.使用临时文件tempfile扩展缓存区；2.去掉不必要输出，以减少输出量的大小
        elif command_type == 'subPopen':
            out_temp = tempfile.SpooledTemporaryFile(max_size=10 * 1000)
            fileno = out_temp.fileno()
            line_break = get_system_line_break()
            stdout = subprocess.PIPE if system_type == 'Windows' else fileno
            p = subprocess.Popen(command, shell=True, stdout=stdout,
                                 stderr=subprocess.PIPE)  # stdout=subprocess.PIPE
            result = p.communicate()
            # print("first_exec:",result)
            if isinstance(result, (tuple, list, set)) and result[0] == None and result[1] == b'':
                result = subprocess.getoutput(command)

            if isinstance(result, str):
                result = result.split(line_break)

            result = [i.decode("utf8", "ignore").strip() if isinstance(i, bytes) else i.strip() for i in result if i]
            if not result:
                return result
            if len(result) > 1:
                result = [i.split(line_break)[0] if i.split(line_break) else i for i in result if i]
            else:
                result = [i.split(line_break) for i in result if i][0]
            result = [i for i in result if i]
        return result
    except:
        traceback.print_exc()


if __name__ == "__main__":
    test_dir = 'D:\city-pro-test' if system_type == 'Windows' else '/home/qinmin/city-pro-test'
    # command=f'pytest -s -q  {test_dir} --env staging  -k "test_shebei_guanli"  --count 1  --collect-only '
    command = f'pip install airtest==1.2.7'
    commandType = 'subPopen'
    result = excute_command(command=command, clog_exec=True)
    print(result)
