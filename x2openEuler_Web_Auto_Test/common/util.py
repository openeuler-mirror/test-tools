"""
@Time : 2024/10/26 11:04
@Auth : ysc
@File : util.py
@IDE  : PyCharm
"""
import re
import json
import subprocess
import yaml
import common.ssh_cmd as ssh_cmd


x2_cmd = subprocess.run("cat ~/.bashrc | grep x2openEuler= | awk -F '\"' '{print $2}'", shell=True,
                        capture_output=True).stdout.decode("utf-8").strip("\n") + " "


def test_cmd(strs):
    return f"{x2_cmd} {strs}"


def run_cmd(cmd):
    run = subprocess.run(cmd, shell=True, capture_output=True)
    cmd_output = run.stdout.decode("utf-8")
    cmd_return = run.returncode

    pattern = re.compile(r"\"? saved: (.*?)\n")
    cmd_file = pattern.findall(cmd_output)
    if cmd_file:
        cmd_file = cmd_file[0]

    result = {"cmd_output": cmd_output, "cmd_return": cmd_return, "cmd_file": cmd_file}

    return result


def diff_output(cmd_output, expect_result):
    flag = 0
    if expect_result not in cmd_output:
        flag = 1

    return flag


def diff_file():
    pass


def json_to_dict(file_name):
    file_name = file_name[:-4] + "json"
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)


def json2dict(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        return json.load(f)


def get_conf_data(str):
    conf = subprocess.run(f"sysctl {str}", shell=True, capture_output=True).stdout.decode(
            "utf-8").replace(" ", "").strip("\n").split("=")[1]
    return conf


def change_conf_data(cmd):
    exec_cmd = subprocess.run(f"sudo {cmd}", shell=True, capture_output=True)
    if exec_cmd.returncode != 0:
        print(f"Exec exec {cmd} failed")
        return exec_cmd.returncode


def get_filename(path):
    filename = subprocess.run(f"base {path}", shell=True, capture_output=True).stdout.decode("utf-8").strip("\n")
    return filename


def get_dirname(path):
    dirname = subprocess.run(f"base {path}", shell=True, capture_output=True).stdout.decode("utf-8").strip("\n")
    return dirname


def sort_complex_dict(obj, exclude_keys=None, key=None):
    """
    对复杂字典进行排序
    :param obj: 要排序的对象
    :param exclude_keys: 需要剔除的键，不参与排序
    :param key: 用于对自定义对象进行排序的键
    :return: 排序后的对象
    """
    if exclude_keys is None:
        exclude_keys = set()

    if isinstance(obj, dict):
        sorted_obj = {}
        for k in sorted(obj.keys()):
            if k not in exclude_keys:
                sorted_obj[k] = sort_complex_dict(obj[k], exclude_keys, key)
        return sorted_obj
    elif isinstance(obj, list):
        sorted_list = [sort_complex_dict(item, exclude_keys, key) for item in obj]

        # 如果列表中的元素是字典并且指定了排序键，则按照该键进行排序
        if all(isinstance(item, dict) for item in sorted_list) and key is not None:
            return sorted(sorted_list, key=lambda x: x[key])

        # 否则，根据自定义排序函数对列表进行排序，以确保顺序一致
        return sorted(sorted_list, key=lambda x: str(x))
    else:
        return obj


def yaml_to_dict(yaml_file):
    with open(yaml_file, "r", encoding="UTF-8") as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def exec_cmd(node, host_ip, cmd):
    conn = ssh_cmd.SSHClient(host_ip, node["port"], node["user_name"], node["password"], 99999)
    exit_code, output = conn.execute_command(cmd)
    conn.close()
    return exit_code, output


def upload_file(node, host_ip, local_dir="", local_file="", remote_dir=""):
    conn = ssh_cmd.SSHClient(host_ip, node["port"], node["user_name"], node["password"], 99999)
    conn.psftp_put(local_dir=local_dir, local_file=local_file, remote_dir=remote_dir)


def get_kvm_ip(address_res):
    """
    通过vrirsh domifaddr命令返回值获取虚拟机ip
    :param address_res: vrirsh domifaddr命令返回值, str
    :return: 虚拟机ip
    """
    return address_res.strip().split('\n')[-1].split(' ')[-1].split('/')[0]

