# _*_ coding: UTF-8 _*_
"""
@file            : update_metaverse_config
@Author          : qtclm
@Date            : 2023/2/3 11:13
@Desc            :
"""

import json
import os.path
import collections
import os
import re
import sys
from ruamel import yaml
import argparse


class OperationYaml(object):

    def __init__(self, file_path, file_name):
        yaml_path = os.path.join(os.path.dirname(__file__), file_path)
        self.file_path = os.path.join(yaml_path, file_name)

    # 获取所有数据
    def read_data(self, mode='r'):
        """ 读取yaml里面里面的数据"""
        try:
            with open(self.file_path, mode, encoding='utf8') as f:
                # yaml_info = yaml.load(f, Loader=yaml.Loader)
                yaml_info = yaml.round_trip_load(f)
                return yaml_info
        except Exception as error:
            print(f'读取yaml失败，错误如下：{error}')
            return False

    # 更新文件数据
    def write_yaml(self, data, mode='w'):
        """ 往yaml里面写入数据
            yamlFile：yaml文件名
            road_data：要写入的数据
            mode：写入方式： w，覆盖写入， a，追加写入
            将原数据读取出来，如果没有要加入的key，则创建一个，如果有，则执行key下面的数据修改
        """
        old_data = self.read_data()
        new_data = data
        if new_data == {} or new_data == [] or new_data == '':
            print('写入数据为空，跳过写入')
            return None
        if old_data and isinstance(old_data, dict):
            # collections.ChainMap - -将多个映射合并为单个映射
            # 如果有重复的键，那么会采用第一个映射中的所对应的值
            d = dict(collections.ChainMap(new_data, old_data))
            self.write_data(d)
            # 重新赋值给实例，不然数据写入的数据不会生效
        else:
            # 如果old_data为空，直接写入传入的数据
            self.write_data(new_data)

    # 写入数据基础方法
    def write_data(self, data, mode='w'):
        try:
            with open(self.file_path, mode, encoding="utf-8") as f:
                # yaml.dump(road_data, f)  # , Dumper=yaml.RoundTripDumper
                yaml.round_trip_dump(data, f, default_flow_style=False)
                return True
        except Exception as error:
            print(f'yaml文件写入失败，错误如下：\n{error}')
            return False


def get_env_config(env: str, server_http_port=18990):
    '''
    获取环境对应的配置信息
    :param server_grpc_port: 边端设备grpc端口
    :param env:
    :return:
    '''
    if env.strip() not in ('staging', 'demo'):
        raise Exception("不支持的环境类型")
    config_dict = dict()
    server_http_port = server_http_port
    # connection_sdk_port = connection_sdk_port
    config_dict['bucket_name'] = server_http_port
    if env.strip() == 'staging':
        access_key = 'xxx'
        secret_key = 'xxx'
        bucket_name = "xxx"
    elif env.strip() == 'xxx':
        access_key = 'xxx'
        secret_key = 'xxx'
        bucket_name = "xxx"
    else:
        access_key=''
        secret_key=''
        bucket_name=''
    config_dict['access_key'] = access_key
    config_dict['secret_key'] = secret_key
    config_dict['bucket_name'] = bucket_name
    config_dict['server_http_port'] = server_http_port
    # config_dict['connection_sdk_port'] = connection_sdk_port
    return config_dict


def dict_str_to_json_str(dict_str):
    '''将字符串dict转换为可用的json字符串'''
    return str(dict_str).replace("'", '"') \
        .replace("None", 'null').replace('False', 'false').replace(
        'True', 'true'
    )


def open_file_to_json_obj(file_path, file_name):
    '''打开文件并转换为json字符串'''
    with open(os.path.join(file_path, file_name), 'r', encoding='utf-8') as f:
        json_data = f.read()
        json_data = dict_str_to_json_str(json_data)
    json_data = json.loads(json_data)
    return json_data


def update_container_name(file_path, file_name, container_name):
    '''
    指定容器名称
    :param container_name:
    :param file_path:
    :param file_name:
    :return:
    '''
    if not container_name:
        return
    with open(os.path.join(file_path, file_name), 'r') as f:
        sh_data = f.read()
    container_name_regex = re.search('container_name=.*', sh_data)
    if container_name_regex:
        container_name_match = container_name_regex.group()
        if not container_name_match.endswith(container_name):
            sh_data = sh_data.replace(container_name_match, f"{container_name_match}_{container_name}")
            with open(os.path.join(file_path, file_name), 'w') as f:
                f.write(sh_data)


def update_device_id(file_path, file_name, device_id):
    '''

    :param file_path:
    :param file_name:
    :param device_id:
    :return:
    '''
    if not device_id:
        return
    with open(os.path.join(file_path, file_name), 'r') as f:
        sh_data = f.read()
    device_id_regex = re.search('\s+return.*', sh_data)
    if device_id_regex:
        device_id_match = device_id_regex.group()
        _device_id = device_id_match[device_id_match.find('"') + 1:device_id_match.rfind('"')]
        sh_data = sh_data.replace(_device_id, f"{device_id}")
        with open(os.path.join(file_path, file_name), 'w') as f:
            f.write(sh_data)


def get_metaverse_dir(file_path):
    '''
    获取metaverse目录
    :return:
    '''
    if file_path[-1] == os.sep:
        file_path = file_path[:-1]
    file_path_prefix_index = file_path.rfind(os.sep)
    if file_path_prefix_index not in (-1, len(file_path) - 1):
        metaverse_dir = file_path[:file_path_prefix_index] + os.sep
    else:
        metaverse_dir = ''
    return metaverse_dir


def update_config(env, file_path, file_name: str, device_type: str,
                  sdk_config: list = ['road'], server_http_port=18990,process_interval=6):
    '''
    agent配置信息变更
    :param server_http_port: 边端设备http端口
    :param env: 环境，支持demo、staging
    :param file_path: 配置文件路径
    :param file_name: 配置文件名称
    :param device_type: rv真实设备，amd64模拟设备
    :param sdk_config: sdk配置 road、collission_image二选一,默认road
    :param process_interval: 图片检测跳帧数，默认为6
    :return:
    '''

    def write_json_to_file(file_path, file_name):
        '''将json字符串写入到文件'''
        with open(os.path.join(file_path, file_name), 'w') as f:
            f.write(json.dumps(json_data, indent=4))

    if device_type.strip() not in ('rv', 'amd64'):
        return "不支持的设备类型，退出更新设备"
    config = get_env_config(env=env, server_http_port=server_http_port)
    access_key = config['access_key']
    secret_key = config['secret_key']
    bucket_name = config['bucket_name']
    server_http_port = int(config['server_http_port'])
    connection_sdk_port = 30043
    if file_name.endswith(".yml"):
        ym = OperationYaml(file_path=file_path, file_name=file_name)
        config_data = ym.read_data()
        if not config_data:
            return ""
        if file_name.strip() in (
                'agent_amd64_standard.yml', 'agent_rv_standard.yml', 'agent_amd64_demo.yml', 'agent_rv_demo.yml'):
            if device_type == 'amd64':
                config_data['server']['grpc_port'] = f":{server_http_port + 110}"
                config_data['server']['http_port'] = f":{server_http_port + 100}"
            config_data['connection']['sdk']['address'] = 'senseauto-city-{}-symphony.sensetime.com'.format(env)
            config_data['connection']['sdk']['port'] = connection_sdk_port
            config_data['connection']['registration'][
                'url'] = 'https://senseauto-city-{}-symphony.sensetime.com/symphony/device-manager/registration/v1/auth/register/device'.format(
                env)
            ym.write_data(config_data)

    elif file_name.endswith('.json'):
        if file_name.strip() in ('pre_registry_rv_standard.json', 'pre_registry.json'):
            # if standard != "standard":
            #     return "非标品，不需要更改此配置"
            json_data = open_file_to_json_obj(file_path=file_path, file_name=file_name)
            json_data['DeviceManagerUpload']['AccessKey'] = access_key
            json_data['DeviceManagerUpload']['SecretKey'] = secret_key
            json_data['DeviceManagerUpload'][
                'HTTPEndpoint'] = 'https://senseauto-device-manager-{}.sensetime.com'.format(env)

            write_json_to_file(file_path=file_path, file_name=file_name)

        elif file_name.strip() in ('registry_rv_standard.json', 'registry_amd64_standard.json', 'registry_rv.json'):
            # if standard != 'standard':
            #     return "非标品，不需要更改此配置"
            json_data = open_file_to_json_obj(file_path=file_path, file_name=file_name)
            if json_data.get('DeviceManagerUpload'):
                json_data['DeviceManagerUpload']['AccessKey'] = access_key
                json_data['DeviceManagerUpload']['SecretKey'] = secret_key
                json_data['DeviceManagerUpload'][
                    'HTTPEndpoint'] = 'https://senseauto-device-manager-{}.sensetime.com'.format(env)
            if json_data.get('SyACfg'):
                json_data['SyACfg'][
                    'BusinessRegistryUrl'] = 'https://senseauto-city-{}-symphony.sensetime.com/symphony/device-manager/registration/v1/auth/register/device'.format(
                    env)
                json_data['SyACfg']['SymphonyAgentService']['GRPCEndpoint'] = "127.0.0.1:{}".format(
                    server_http_port + 110)

            write_json_to_file(file_path=file_path, file_name=file_name)

        elif file_name.strip() in (
                "config_rv_standard.json", 'config_amd64_standard.json', 'config_rv_demo.json','config_amd64_demo.json'):
            json_data = open_file_to_json_obj(file_path=file_path, file_name=file_name)
            json_data['SymphonyAgentService']['GRPCEndpoint'] = "127.0.0.1:{}".format(
                server_http_port + 110)  # 端口与agent里的grpc端口一致
            json_data['DataReturn']['SymphonyUpload']['SymphonyAgentService'][
                'GRPCEndpoint'] = "127.0.0.1:{}".format(server_http_port + 110)  # 端口与agent里的grpc端口一致
            json_data['GRPCEndPoint'] = ":{}".format(server_http_port + 10)  # 端口与agent里的grpc端口一致
            json_data['HTTPEndpoint'] = ":{}".format(server_http_port)  # 端口与agent里的grpc端口一致
            json_data['DataReturn']['BucketName'] = bucket_name
            sdk_config_out = [i.lower() for i in sdk_config if
                              i.lower() in ('road', 'things', 'collision_image', 'collision')]
            sdk_config_dict = dict()
            for i in sdk_config_out:
                if i == 'road':
                    sdk_config_dict[
                        'ROAD'] = "/go/src/gitlab.senseauto.com/sensecity/city-lite/metaverse/examples/sdk_road.json"
                elif i == 'things':
                    sdk_config_dict[
                        'THINGS'] = "/go/src/gitlab.senseauto.com/sensecity/city-lite/metaverse/examples/sdk_things.json"
                elif i in ('collision', 'collision_image'):
                    sdk_config_dict[
                        'COLLISION_IMAGE'] = "/go/src/gitlab.senseauto.com/sensecity/city-lite/metaverse/examples/sdk_collision.json"

            if sdk_config_dict.get('ROAD') and sdk_config_dict.get('THINGS'):
                raise Exception("道路养护与万物检测配置不能同时开启")
            json_data['SdkConfig'] = sdk_config_dict
            write_json_to_file(file_path=file_path, file_name=file_name)

        elif file_name.strip() in (
            "sdk_rv_road.json","sdk_rv_things.json","sdk_things.json",'sdk_road.json' ):
            json_data = open_file_to_json_obj(file_path=file_path, file_name=file_name)
            json_data['process_interval']=process_interval
            write_json_to_file(file_path=file_path, file_name=file_name)





def main(**kwargs):
    file_path, env, sdk_config, server_http_port, container_name, device_id = \
        kwargs['filepath'], kwargs['env'], kwargs['sdkconfig'], kwargs['httpport'], kwargs['containername'], kwargs[
            'deviceid']
    process_interval=kwargs['processinterval']
    sdk_config = sdk_config.split(",")
    metaverse_dir = get_metaverse_dir(file_path=file_path)
    container_name_file_path = metaverse_dir + 'scripts'
    container_name_file_name = 'start-dev.sh'
    # 更新metaverse容器名称
    update_container_name(file_path=container_name_file_path, file_name=container_name_file_name,
                          container_name=container_name)
    # 指定设备名称
    device_id_file_path = metaverse_dir + 'internal/device'
    device_id_file_name = 'device_amd64.go'
    update_device_id(file_path=device_id_file_path, file_name=device_id_file_name, device_id=device_id)
    # 更新配置文件信息
    for pre in ('','_standard'):
        update_config(env, file_path, file_name=f"pre_registry{pre}.json",
                      device_type="amd64", sdk_config=sdk_config,
                      server_http_port=server_http_port,process_interval=process_interval)
    update_config(env, file_path, file_name="registry_rv.json",
                  device_type="rv", sdk_config=sdk_config,
                  server_http_port=server_http_port,process_interval=process_interval)
    for sdk_type in ('road','things'):
        update_config(env, file_path, file_name=f"sdk_rv_{sdk_type}.json",
                      device_type="rv", sdk_config=sdk_config,
                      server_http_port=server_http_port,process_interval=process_interval)
        update_config(env, file_path, file_name=f"sdk_{sdk_type}.json",
                      device_type="amd64", sdk_config=sdk_config,
                      server_http_port=server_http_port,process_interval=process_interval)

    for device_type in ('rv', 'amd64'):
        update_config(env, file_path, file_name="pre_registry_{}_standard.json".format(device_type),
                      device_type=device_type, sdk_config=sdk_config,
                      server_http_port=server_http_port,process_interval=process_interval)
        update_config(env, file_path, file_name="registry_{}_standard.json".format(device_type),
                      device_type=device_type, sdk_config=sdk_config,
                      server_http_port=server_http_port,process_interval=process_interval)
        for standard in ("standard", "demo"):
            update_config(env, file_path, file_name="agent_{}_{}.yml".format(device_type, standard),
                          device_type=device_type, sdk_config=sdk_config,
                          server_http_port=server_http_port,process_interval=process_interval)
            update_config(env, file_path, file_name="config_{}_{}.json".format(device_type, standard),
                          device_type=device_type, sdk_config=sdk_config,
                          server_http_port=server_http_port,process_interval=process_interval)


def command_set(**kwargs):
    '''
    flow_type='standard',git_code_branch="",
     标品、路行通设备命令行操作集封装
    :param git_code_branch: 代码分支
    :param flow_type: 流程类型，目前支持 路行通:lxt、标品：standard
    :return:
    '''
    # print(kwargs)
    #     前置步骤： 1.切换目录到metaverse主目录：/root/go/src;2.撤销本地对配置文件的修改；3.拉取最新代码；3.下载最新模型 make deps
    #      step1 完成配置文件修改
    #      step2 删除设备证书文件 rm -rf deploy/dev_prv_key.pem deploy/ca.pem
    #      step3 启动并进入docker容器 make dev device=cuda11 host=amd64
    #     标品流程
    #      step4 创建symphony目录 mkdir -p ../road_data/symphony
    #      step5 设备注册前置步骤以及设备注册  go run cmd/pre-register/main.go && go run cmd/register/main.go
    #      step6 启动server sh deploy/run_agent_amd64_standard.sh && sh deploy/run_metaverse_standard.sh
    #      step7 输出服务端日志  tail -f metaverse.log
    #     路行通流程
    #      step4 启动server sh deploy/registry_amd64_demo.sh
    flow_type = kwargs['flow_type'] if kwargs.get('flow_type') else 'lxt'
    git_code_branch = kwargs['git_code_branch'] if kwargs.get('git_code_branch') else ''
    metaverse_parent_path=kwargs['metaverse_parent_path'] if kwargs.get('metaverse_parent_path') else ''
    delete_pem=kwargs['delete_pem'] if kwargs.get('delete_pem') else True
    if sys.platform != 'win32':
        metaverse_dir = get_metaverse_dir(file_path=kwargs['file_path'])
        # print(metaverse_dir)
        if git_code_branch:
            os.chdir("{}".format(os.path.join(metaverse_parent_path,metaverse_dir)))
            os.system("git checkout .")
            git_code_branch = git_code_branch.strip() if git_code_branch.strip().startswith(
                "origin") else "origin {}".format(git_code_branch)
            os.system("git pull {}".format(git_code_branch))
            os.system("make deps")
            # 切换到metaverse上层目录
            os.chdir("{}".format(metaverse_parent_path))
        # 更新配置文件
        main(**kwargs)
        print("配置文件更新完成")
        os.chdir("{}".format(os.path.join(metaverse_parent_path, metaverse_dir))) # 切换目录
        if delete_pem:
            os.system("rm -rf deploy/dev_prv_key.pem deploy/ca.pem")
        os.system("make dev device=cuda11 host=amd64")
        # 下面的代码是在docker容器操作，目前无法执行
        if flow_type in ('standard', '标品'):
            os.system("mkdir -p ../road_data/symphony")
            os.system("go run cmd/pre-register/main.go && go run cmd/register/main.go")
            os.system("sh deploy/run_agent_amd64_standard.sh && sh deploy/run_metaverse_standard.sh")
            os.system("tail -f metaverse.log")
        elif flow_type in ('lxt', '路行通', 'luxingtong'):
            os.system("sh deploy/registry_amd64_demo.sh")
        else:
            raise Exception("不支持的流程类型")
    else:
        main(**kwargs)


if __name__ == "__main__":
    print("请传入需要更新的配置文件目录、环境以及sdk配置、http端口、容器名称、设备id、流程类型、代码分支：\n"
          "第一个参数为配置文件所在目录（默认当前目录下examples）；\n"
          "第二个参数为环境（默认demo）：支持staging、demo；\n"
          "第三个参数为sdk配置（默认为road）。多个sdk配置使用,分割；\n"
          "第四个参数为http端口，指定后可方便复制多套环境使用；\n"
          "第五个参数为container_name\n"
          "第六个参数为device_id\n"
          "第七个参数为流程类型，支持路行通：传入'lxt','路行通','luxingtong'；标品：传入：'standard','标品',默认为标品\n"
          "第八个参数为需要拉取的代码分支，传入后将会拉取对应分支的最新代码以及更新至最新的模型,默认为空即不触发拉取代码\n"
          "第九个参数为检测跳帧数量")
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', '-F', type=str,
                        default="examples", help='配置文件所在目录')
    parser.add_argument('--env', '-E', type=str,
                        default="staging", help='环境：支持demo、staging，默认staging')
    parser.add_argument('--sdkconfig', '-S', type=str,
                        default="road,things", help='sdk配置，默认为road,things')
    parser.add_argument('--httpport', '-H', type=int,
                        default=19080, help='边端http端口，默认为19080')
    parser.add_argument('--containername', '-C', type=str,
                        default="19080", help='指定容器后缀名称，避免复制多条环境时误杀掉之前的容器进程')
    parser.add_argument('--deviceid', '-D', type=str,
                        default="", help='自定义设备id，默认为空，即不修改设备id')
    parser.add_argument('--flowtype', '-FL', type=str,
                        default="",
                        help="流程类型，支持路行通：传入'lxt','路行通','luxingtong'；标品：传入：'standard','标品',默认为标品")
    parser.add_argument('--gitcodebranch', '-G', type=str,
                        default="",
                        help="需要拉取的代码分支，传入后将会拉取对应分支的最新代码以及更新至最新的模型,默认为空即不触发拉取代码")
    parser.add_argument('--metaverseparentpath', '-MP', type=str,
                        default="/root/go/src",
                        help="metaverse的父级目录")
    parser.add_argument('--processinterval', '-PI', type=int,
                        default=6,
                        help="sdk检测跳帧数量")
    parser.add_argument('--deletepem', '-DP', type=bool,
                        default=True,
                        help="是否删除设备证书文件")
    args = parser.parse_args()
    command_set(**args.__dict__)
