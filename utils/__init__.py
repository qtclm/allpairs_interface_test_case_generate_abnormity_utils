import os
import sys
from typing import Union

default_match_paths=['.git','config','utils']


def get_project_rootpath(match_paths: Union[list, set, tuple] = None):
    """
    获取项目根目录。此函数的能力体现在，不论当前module被import到任何位置，都可以正确获取项目根目录
    :return:
    """
    path = os.getcwd()
    if sys.platform == 'win32':
        root_path = path[:path.find(':\\') + 2]
    else:
        root_path = os.path.altsep
    while path != root_path:
        # PyCharm项目中，'.idea'是必然存在的，且名称唯一
        # match_paths=['.idea','utils','handle','config']
        if not match_paths:
            match_paths = default_match_paths
        is_match = all([i in os.listdir(path) for i in match_paths])
        if is_match:
            return path
        path = os.path.dirname(path)
    if not path:
        raise Exception('项目根目录未找到,请调整math_paths参数')
