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
    length = random.randint(1, 60)
    characters = string.ascii_letters + string.digits + ''.join(set(string.punctuation) - set("><"))
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


def create_new_name(src_name):
    """生成任意名称+时间戳"""
    new_name = src_name + str(dt_strftime('%H%M%S'))
    return new_name


def generate_random_number(m, n):
    """随机生成一个m~n之间的正整数"""
    random_number = random.randint(m, n)
    return random_number


def generate_content(n):
    """随机生成内容，由1-n之间(n默认为65535)任意个字符和数字组成"""
    length = random.randint(1, n)
    characters = string.ascii_letters + string.digits + ''.join(set(string.punctuation) - set("><"))
    content = ''.join(random.choices(characters, k=length))
    return content


def correct_operation_name(min_len=5, max_len=60) -> str:
    cs = string.ascii_letters + string.digits + '_'
    return ''.join(random.choices(cs, k=random.randint(min_len, max_len)))


def repo_name(length=20):
    """随机生成一个长度在20以内的字符串"""
    characters = string.ascii_letters + string.digits + string.punctuation
    repo = ''.join(random.choices(characters, k=length))
    return repo


def repo_data(length=20):
    length = random.randint(1, 512)
    characters = string.ascii_letters + string.digits + string.punctuation
    data = ''.join(random.choice(characters) for _ in range(length))
    return data


def task_name():
    """随机生成一个长度在32以内的字符串"""
    length = random.randint(1, 17)
    characters = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choices(characters, k=length))
    task_name = 'task' + random_string
    return task_name


def task_desc():
    """随机生成一个长度在150以内的字符串"""
    length = random.randint(1, 147)
    characters = string.ascii_letters + string.digits + string.punctuation
    random_string = ''.join(random.choices(characters, k=length))
    task_desc = 'desc' + random_string
    return task_desc


def test_script_name(length=10):
    characters = string.ascii_letters
    data = ''.join(random.choice(characters) for _ in range(length))
    return data


def test_symbol(length=1):
    """随机生成一个任意长度的纯符号字符串"""
    characters = string.punctuation
    data = ''.join(random.choice(characters) for _ in range(length))
    return data
