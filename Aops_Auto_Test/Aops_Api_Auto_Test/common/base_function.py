import os
import time
from string import Template
import requests
import yaml

from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.utils.MysqlUtil import ql
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.config.conf import ConfigYaml
from Aops_Api_Auto_Test.utils.RequestsUtil import Request
from Aops_Api_Auto_Test.utils.YamlUtil import YamlReader
common_file = os.path.join(conf.get_data_path(), "common.yaml")


class BaseFun:
    log = my_log()

    def __init__(self,data_yaml):
        self.access_token = None
        self.host_group_name = 'pre_api_test_group1'
        self.host_id = None
        self.host_name = 'pre_api_test_host1'
        self.repo_name = 'pre_api_test_repo1'
        self.set_repo_task_id = None
        self.set_repo_task_name = None
        self.cve_fix_task_id = None
        self.data_yaml = data_yaml

    def get_token(self):
        self.log.info("----Start get token----")
        url = ConfigYaml().get_conf_url() + ':80/api/manage/account/login'
        data = {
            "username": "admin",
            "password": "changeme"
        }
        res = requests.post(url=url, json=data)
        body = res.json()
        res_data = dict()
        res_data["body"] = body
        token_access = res_data["body"]["data"]['token']
        self.log.info("Start get token: {}".format(token_access))
        self.access_token = token_access
        YamlReader(common_file).write_yaml({"token": token_access})
        return token_access

    def register_group(self):
        self.log.info("Start register group")
        headers = {'Content-Type': 'application/json', 'Access-Token': self.access_token}
        url = ConfigYaml().get_conf_url() + ":11111/manage/host/group/add"
        data = {
            "host_group_name": self.host_group_name,
            "description": "api_group1"
        }
        request = Request()
        request.post(url=url, json=data, headers=headers)
        sql = "select host_group_name from host_group where host_group_name='{}'".format(self.host_group_name)
        ql.connect()
        mysql_result = ql.fetchall(sql)
        self.log.info("Get host_group_name: {}".format(mysql_result))
        YamlReader(common_file).write_yaml({"host_group_name": self.host_group_name})

    def register_host(self, host_ip):
        self.log.info("Start register host")
        headers = {'Content-Type': 'application/json', 'Access-Token': self.access_token}
        url = ConfigYaml().get_conf_url() + ":11111/manage/host/add"
        data = {
            "host_name": self.host_name,
            "host_group_name": self.host_group_name,
            "host_ip": host_ip,
            "ssh_port": 22,
            "ssh_user": "root",
            "password": "openEuler12#$",
            "management": True
        }
        self.log.info("注册主机信息： {}".format(data))
        request = Request()
        try:
            aa = request.post(url=url, json=data, headers=headers)
            self.log.info("Get response: {}".format(aa))
        except:
            self.log.info("请求失败")
            raise
        sql = "select host_id, host_name, host_ip from host where host_name='{}'".format(self.host_name)
        ql.connect()
        mysql_result = ql.fetchall(sql)
        self.log.info("Get host_info: {}".format(mysql_result))
        self.host_id = mysql_result[0]['host_id']
        YamlReader(common_file).write_yaml({"host_id": self.host_id})
        YamlReader(common_file).write_yaml({"host_name": self.host_name})
        YamlReader(common_file).write_yaml({"host_ip": host_ip})

    def import_repo(self):
        self.log.info("Start import repo")
        headers = {'Content-Type': 'application/json', 'Access-Token': self.access_token}
        print('headers:', headers)
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/repo/import"
        data = {
            "repo_name": self.repo_name,
            "repo_data": "[aops-update]\n"
                         "name=update\n"
                         "baseurl=https://repo.openeuler.org/openEuler-22.03-LTS-SP1/update/$basearch/\n"
                         "enabled=1\n"
                         "gpgcheck=1\n"
                         "gpgkey=https://repo.openeuler.org/openEuler-22.03-LTS-SP1/OS/$basearch/RPM-GPG-KEY-openEuler\n"
        }
        request = Request()
        request.post(url=url, json=data, headers=headers)
        sql = "select repo_name from repo where repo_name='{}'".format(self.repo_name)
        ql.connect()
        mysql_result = ql.fetchall(sql)[0]
        self.log.info("Get repo: {}".format(mysql_result))
        self.repo_name = mysql_result['repo_name']
        YamlReader(common_file).write_yaml({"repo_name": self.repo_name})

    def create_set_repo_task(self):
        self.log.info("Start create a set_repo task")
        headers = {'Content-Type': 'application/json', 'Access-Token': self.access_token}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/repo/generate"
        data = {
            "repo_name": self.repo_name,
            "task_name": "pre_api_REPO设置任务",
            "description": "设置repo",
            "info": [
                {
                    "host_id": self.host_id,
                    "host_name": self.host_name,
                    "host_ip": self.host_ip
                }
            ]
        }
        self.log.info("create_repo_task: {}".format(data))
        request = Request()
        res = request.post(url=url, json=data, headers=headers)
        self.log.info("create_repo_task返回值: {}".format(res))
        sql = "select task_id as set_repo_task_id, task_name as set_repo_task_name from vul_task where task_name='pre_api_REPO设置任务'"
        ql.connect()
        mysql_result = ql.fetchall(sql)
        self.log.info("Get set_repo task info: {}".format(mysql_result))
        self.set_repo_task_id = mysql_result[0]['set_repo_task_id']
        self.set_repo_task_name = mysql_result[0]['set_repo_task_name']
        YamlReader(common_file).write_yaml({"set_repo_task_name": self.set_repo_task_name})
        YamlReader(common_file).write_yaml({"set_repo_task_id": self.set_repo_task_id})

    def execute_set_repo_task(self):
        self.log.info("Start execute set_repo task")
        headers = {'Content-Type': 'application/json', 'Access-Token': self.access_token}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/execute"
        data = {
            "task_id": self.set_repo_task_id
        }
        self.log.info("repo_data: {}".format(data))
        request = Request()
        res = request.post(url=url, json=data, headers=headers)
        time.sleep(10)
        self.log.info("res: {}".format(res))
        self.log.info("Execute set_repo task end!")

    def execute_cve_scan_task(self):
        self.log.info("Start execute cve scan task")
        data = {
            "host_list": [
                self.host_id
            ]
        }
        headers = {'Content-Type': 'application/json', 'Access-Token': self.access_token}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/host/scan"
        request = Request()
        request.post(url=url, json=data, headers=headers)
        self.log.info(time.sleep(20))
        self.log.info("Execute cve scan task end!")

    def create_cve_fix_task(self):
        self.log.info("Start create fix_cve task")
        data = {
  "task_name": "pre_api_CVE修复任务",
  "description": "修复以下1个CVE：CVE-2023-3331",
  "auto_reboot": False,
  "accepted": False,
  "info": [
    {
      "cve_id": "CVE-2023-3331",
      "host_info": [
        {
          "host_id": self.host_id,
          "host_ip": self.host_ip,
          "host_name": self.host_name,
          "hotpatch": False
        }
      ],
      "reboot": False
    }
  ]
}
        self.log.info("create cve_fix data: {}".format(data) )
        headers = {'Content-Type': 'application/json', 'Access-Token': self.access_token}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/cve/generate"
        request = Request()
        res = request.post(url=url, json=data, headers=headers)
        self.log.info("create cve_fix result: {}".format(res) )
        task_id = res['body']['data']['task_id']
        self.log.info("Get fix_cve task_id: {}".format(task_id))
        self.cve_fix_task_id = task_id
        YamlReader(common_file).write_yaml({"cve_fix_task_id": self.cve_fix_task_id})

    def execute_cve_fix_task(self):
        self.log.info("Start execute fix_cve task")
        data = {
            "task_id": self.cve_fix_task_id
        }
        headers = {'Content-Type': 'application/json', 'Access-Token': self.access_token}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/execute"
        request = Request()
        request.post(url=url, json=data, headers=headers)
        time.sleep(10)
        self.log.info("Execute cve_fix task end!")

    def yaml_replace(self):
        # self.get_token()
        # self.register_group()
        # self.register_host()
        # # self.import_repo()
        # # self.create_set_repo_task()
        # # self.execute_set_repo_task()
        # # self.execute_cve_scan_task()
        # # self.create_cve_fix_task()
        # # self.execute_cve_fix_task()
        with open(common_file, "rb") as f1:
            common_dict = yaml.safe_load(f1)
        with open(self.data_yaml, encoding='utf-8') as f:
            re = Template(f.read()).substitute(common_dict)
            return yaml.safe_load(stream=re)

    def clear_data(self):
        self.log.info("清理所有测试数据")
        delete_host = "delete from host where host_id='{}'".format(self.host_id)
        delete_group = "delete from host_group where host_group_name='{}'".format(self.host_group_name)
        delete_set_repo_task = "delete from vul_task where task_name='pre_api_REPO设置任务'"
        delete_cve_fix_task = "delete from vul_task where task_name='pre_api_CVE修复任务'"
        delete_repo = "delete from repo where repo_name='{}'".format(self.repo_name)
        ql.connect()
        ql.exec(delete_host)
        self.log.info("删除host: {}".format(self.host_id))
        ql.exec(delete_group)
        self.log.info("删除主机组: {}".format(self.host_group_name))
        ql.exec(delete_set_repo_task)
        self.log.info("删除设置repo任务: pre_api_REPO设置任务")
        ql.exec(delete_cve_fix_task)
        self.log.info("删除修复cve任务: pre_api_CVE修复任务")
        ql.exec(delete_repo)
        self.log.info("删除repo: {}".format(self.repo_name))
        self.log.info("数据清理完成")








