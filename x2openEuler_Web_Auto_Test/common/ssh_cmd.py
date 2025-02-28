"""
@Time : 2024/7/27 10:33
@Auth : ysc
@File : ssh_cmd.py
@IDE  : PyCharm
功能：
    1.实现连接/断开服务器
    2.向服务器发送命令
    3.适用于服务器重启场景的重连
    4.上传/下载文件
"""
import os
import re
import sys
import stat
import subprocess
import paramiko
from x2openEuler_Web_Auto_Test.common.log import log
import x2openEuler_Web_Auto_Test.config.config as cg
from x2openEuler_Web_Auto_Test.config.config import get_config


class SSHClient(object):
    def __init__(self, hostname, port=22, username="root", password=None, timeout=None):
        """
        初始化SSH客户端并连接到远程服务器
        :param hostname: 主机名
        :param port: 端口号
        :param username: 用户
        :param password: 密码
        :param timeout: ssh超时时长 Defaults to None
        """
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.client = None
        self.sftp = None
        self.connect()

    def connect(self):
        """ 连接到远程服务器 """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(self.hostname, self.port, self.username, self.password, timeout=self.timeout)
            self.sftp = self.client.open_sftp()
            log.info(f"{self.hostname}:{self.port} Connected to the server successfully.")
        except (
                paramiko.ssh_exception.NoValidConnectionsError,
                paramiko.ssh_exception.AuthenticationException,
        ) as e:
            log.error("Failed to connect the remote machine:%s." % self.hostname)
            log.error(e)
            return cg.Error_CODE

    def execute_command(self, command):
        """ 在远程服务器上执行命令并返回结果 """
        if self.client == cg.Error_CODE:
            return cg.Error_CODE, ""
        stdin, stdout, stderr = self.client.exec_command(command)
        exitcode = stdout.channel.recv_exit_status()

        if exitcode == 0:
            output = stdout.read().decode("utf-8").strip('\n')
        else:
            output = stderr.read().decode("utf-8").strip("\n")

        return exitcode, output

    def close(self):
        """ 关闭SSH连接 """
        if self.client:
            self.client.close()
            log.info(f"{self.hostname}:{self.port} Connection closed.")
            self.client = None
        else:
            log.info("No connection to close.")

    def get_remote_file(self, sftp, remote_dir, remote_file=None):
        """
            获取对端文件
        :param sftp: 和对端建立连接
        :param remote_dir: 远端需要传输文件所在目录
        :param remote_file: 远端需要传输的文件，default to None.
        :return: [list] 文件列表
        """
        all_file = list()

        remote_dir = remote_dir.rstrip('/')

        dir_files = sftp.listdir_attr(remote_dir)
        for d_f in dir_files:
            if remote_file is not None and re.match(remote_file, d_f.filename) is None:
                continue

            _name = remote_dir + "/" + d_f.filename
            if stat.S_ISDIR(d_f.st_mode):
                all_file.extend(self.get_remote_file(sftp, _name))
            else:
                all_file.append(_name)

        return all_file

    def psftp_get(self, remote_dir, remote_file="", local_dir=os.getcwd()):
        self.connect()
        if self.client == cg.Error_CODE:
            sys.exit(cg.Error_CODE)

        if self.execute_command("test -d" + remote_dir)[0]:
            log.error("remote dir:%s does not exist" % remote_dir)
            self.client.close()
            sys.exit(1)

        all_file = list()

        if remote_file == "":
            all_file = self.get_remote_file(self.sftp, remote_dir)
        else:
            if self.execute_command("test -f " + os.path.join(remote_dir, remote_file))[0]:
                log.error("remote file:%s does not exist" % remote_file)
                self.client.close()
                sys.exit(1)

            all_file = self.get_remote_file(self.sftp, remote_dir, remote_file)

        local_dir = os.path.normpath(local_dir)
        remote_dir = os.path.normpath(remote_dir)

        for f in all_file:
            if remote_file == "":
                storage_dir = remote_dir.split("/")[-1]
                storage_path = os.path.join(
                    local_dir, storage_dir + os.path.dirname(f[len(remote_dir):])
                )
                if not os.path.exists(storage_path):
                    os.makedirs(storage_path)
                self.sftp.get(f, os.path.join(storage_path, f.split("/")[-1]))
            else:
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)
                self.sftp.get(f, os.path.join(local_dir, f.split("/")[-1]))
                log.info("start to get file:%s......" % f)

        self.close()

    def get_local_file(self, local_dir, local_file=None):
        """获取本地文件列表

        Args:
            local_dir ([str]): 本地文件所在的目录
            local_file ([str], optional): 本地需要传输的文件. Defaults to None.

        Returns:
            [list]: 文件列表
        """
        all_file = list()

        local_dir = local_dir.rstrip("/")

        dir_files = os.listdir(local_dir)
        for d_f in dir_files:
            if local_file is not None and re.match(local_file, d_f) is None:
                continue

            _name = local_dir + "/" + d_f
            if os.path.isdir(_name):
                all_file.extend(self.get_local_file(_name))
            else:
                all_file.append(_name)

        return all_file

    def psftp_put(self, local_dir=os.getcwd(), local_file="", remote_dir=""):
        """将本地文件传输到远端

       Args:
           conn ([class]): 和远端建立连接
           local_dir ([str]): 本地文件所在的目录
           local_file ([str], optional): 本地需要传输的文件. Defaults to None.
           remote_dir (str, optional): 远端存放文件的目录. Defaults to 根目录.
        """
        self.connect()
        if self.client == cg.Error_CODE:
            sys.exit(cg.Error_CODE)

        if subprocess.getstatusoutput("test -d " + local_dir)[0]:
            log.error("local dir:%s does not exist" % local_dir)
            self.close()
            sys.exit(1)

        if local_file == "":
            all_file = self.get_local_file(local_dir)
        else:
            if subprocess.getstatusoutput("test -f " + os.path.join(local_dir, local_file))[0]:
                log.error("local file:%s does not exist" % local_file)
                self.close()
                sys.exit(1)
            all_file = self.get_local_file(local_dir, local_file)

        if remote_dir == "":
            remote_dir = self.execute_command("pwd")[1]

        local_dir = os.path.normpath(local_dir)
        remote_dir = os.path.normpath(remote_dir)

        for f in all_file:
            if local_file == "":
                storage_dir = local_dir.split("/")[-1]
                storage_path = os.path.join(
                    remote_dir, storage_dir + os.path.dirname(f[len(local_dir):])
                )
                if self.execute_command("test -d " + storage_path)[0]:
                    self.execute_command("mkdir -p " + storage_path)
                self.sftp.put(f, os.path.join(storage_path, f.split("/")[-1]))
            else:
                if self.execute_command("test -d " + remote_dir)[0]:
                    self.execute_command("mkdir -p " + remote_dir)
            self.sftp.put(f, os.path.join(remote_dir, f.split("/")[-1]))
            log.info("start to put file:%s......" % f)

        self.close()


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="manual to this scripts")
    # parser.add_argument("--cmd", type=str, default=None, required=True)
    # parser.add_argument("--ip", type=str, default=None)
    # parser.add_argument("--user", type=str, default="root")
    # parser.add_argument("--password", type=str, default=None)
    # parser.add_argument("--port", type=int, default=22)
    # parser.add_argument("--timeout", type=int, default=None)
    # args = parser.parse_args()
    host = get_config().get('host')
    host_ip = host.get('host_name')
    ssh = SSHClient(hostname=host.get('host_name'), port=host.get('port'), username=host.get('username'),
                    password=host.get('password'))

    _code, stdout = ssh.execute_command("ccentos.sh 82 test_ysc_centos82_01")
    print(stdout)
    _code_, address_res = ssh.execute_command("virsh domifaddr test_ysc_centos82_01")
    node_ip = address_res.strip().split('\n')[-1].split(' ')[-1].split('/')[0]
    print(node_ip)
    _, des_res = ssh.execute_command("virsh destroy test_ysc_centos82_01")
    print(des_res)
    _, del_res = ssh.execute_command(f"virsh undefine --nvram test_ysc_centos82_01")
    print(del_res)