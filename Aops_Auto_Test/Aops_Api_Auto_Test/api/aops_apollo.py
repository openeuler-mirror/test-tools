import time

from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.config.conf import ConfigYaml
from Aops_Api_Auto_Test.utils.RequestsUtil import Request
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml
from Aops_Api_Auto_Test.api.aops_zeus import ApiZeus


class ApiApollo(ApiZeus):
    log = my_log()

    def download_repo_template(self):
        """
        Download repo template
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/repo/template/get"
        res = Request().get(url=url, params=None, headers=headers)
        self.log.info("Download template result: {}".format(res))
        return res

    def import_repo(self, repo_data: dict):
        """
        data:
            "repo_name": repo_name
            "repo_data": repo_data

        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/repo/import"
        res = Request().post(url=url, json=repo_data, headers=headers)
        self.log.info("Import repo result: {}".format(res))
        return res

    def get_repo(self, repo_name_list):
        """
        "repo_name_list": []

        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/repo/get"
        res = Request().post(url=url, json=repo_name_list, headers=headers)
        self.log.info("Get repo result: {}".format(res))
        return res

    def delete_repo(self, repo_name_list):
        """
        "repo_name_list": []

        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/repo/delete"
        res = Request().delete(url=url, json=repo_name_list, headers=headers)
        self.log.info("Delete repo result: {}".format(res))
        return res

    def query_host_list(self, data):
        """
        "filter": {}

        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/host/list/get"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("res: {}".format(res))
        return res

    def scan_host(self, data):
        """
        data = {
            "host_list": [host_id]
        }
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/host/scan"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info(time.sleep(20))
        self.log.info("Scan host result: {}".format(res))
        return res

    def get_host_cve(self, data):
        """
        data = {
  "host_id": host_id,
  "filter": {
    "fixed": false,
    "severity": []
  }
}
       :return:

        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/host/cve/get"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Get host cve info: {}".format(res))
        return res

    def get_cve_unfixed_packages(self, data):
        """
        data = {
"cve_id": "CVE-2023-1070",
"host_ids": [
"16"
]
}
       :return:

        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/cve/unfixed/packages/get"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Get cve unfixed package info: {}".format(res))
        return res

    def generate_cve_fix_task(self, data):
        """
        para:
        {
    "task_name": "CVE修复任务",
    "description": "修复以下1个CVE：CVE-2023-3332",
    "check_items": ["network"],
    "accepted": false,
    "takeover": true,
    "info": [
            {
                "cve_id": "CVE-2023-3332",
                // rpms为空的时候,表示选中该CVE,默认执行策略,有热补丁执行热补丁,没有则执行冷补丁
                "rpms":[
                    {
                        "installed_rpm":"pkg1",
                        "available_rpm": "pkg1-1",
                        "fix_way":"hotpatch"
                    }
                ],
                "host_info": [
                    {
                        "host_id": 1,
                        "host_ip": "172.168.50.127",
                        "host_name": "50.127oe2203sp2-x86"
                    }
                ],
            }
     ]
}
            :return
            """

        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/cve-fix/generate"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Generate cve fix result: {}".format(res))
        return res

    def get_task_info(self, data):
        """
        data:
        {
    "task_id": "task_id"}

        :return
        """

        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/info/get"
        res = Request().get(url=url, params=data, headers=headers)
        self.log.info("Get task info: {}".format(res))
        return res

    def execute_task(self, data):
        """
        data:{"task_id": "task_id"}

        :return
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/execute"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Execute task result: {}".format(res))
        return res

    def get_cve_fix_task_result(self, data):
        """
        data:{"task_id": "task_id"}

        :return
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/cve-fix/result/get"
        time.sleep(60)
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Get cve fix task result: {}".format(res))
        return res

    def generate_cve_rollback_task(self, data):
        """
        para:
        {
              "fix_task_id": "cc5c7a8eaf6011ee84b2525400be8073"
        }
        return::

        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/cve-rollback/generate"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Generate cve rollback task: {}".format(res))
        return res

    def generate_hotpatch_deactivate_task(self, data):
        """
        para:
        {
    "task_name": "cve inactive-patch",
    "info": [
        {
            "host_id": "id1",
            "cves": [
                {
                    "cve_id": "cve1"
                }
            ]
        }
    ]
}
        return::

        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/cve-rollback/generate"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Generate hotpatch deactivate task: {}".format(res))
        return res

    def get_cve_fix_task_info(self, data):
        """
        para:
        {
            "task_id": "1f9166f08e5b11eea1985254008925db",
  	        "direction":"asc/desc",
            "filter": {
      	        "status":"running/succeed/fail/unknown"
        },
        "page": 1,
        "per_page": 10
        }
        return:

        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/cve-fix/info/get"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Get cve fix task info: {}".format(res))
        return res

