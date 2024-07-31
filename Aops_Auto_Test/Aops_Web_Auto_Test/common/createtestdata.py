import random
import string

from Aops_Web_Auto_Test.utils.times import dt_strftime


def host_name():
    """生成主机名，host+时间戳"""
    hostname = 'host' + str(dt_strftime('%H%M%S'))
    return hostname


def group():
    """生成主机组名，group+时间戳"""
    groupname = 'group' + str(dt_strftime('%H%M%S'))
    return groupname


def group_desc():
    """生成主机组描述，group+时间戳"""
    length = min(1, 60)

    characters = string.ascii_letters + string.digits + string.punctuation.replace("><", "")
    group_desc = ''.join(random.choices(characters, k=length))
    return group_desc


def host_ip():
    """随机生成一个0.0.0.0-255.255.255.255之间的ip"""
    host_ip = '.'.join(str(random.randint(0, 255)) for _ in range(4))
    return host_ip


def host_port():
    """随机生成一个0~65535 内正整数"""
    port = random.randint(0, 65535)
    return port