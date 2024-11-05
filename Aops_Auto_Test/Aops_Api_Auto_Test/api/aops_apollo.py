import os
import time

from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.config.conf import ConfigYaml, BASE_DIR
from Aops_Api_Auto_Test.utils.RequestsUtil import Request
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml


class ApiApollo:

    def __init__(self):
        self.log = my_log()
        # url = ConfigYaml().get_conf_url() + ':80/api/manage/account/login'
        # new url for 20.03-sp4
        url = ConfigYaml().get_conf_url() + ':80/accounts/login'
        data = {
            "username": ConfigYaml().get_user(),
            "password": ConfigYaml().get_login_password()
        }
        res = Request().post(url=url, json=data)
        token_access = res["body"]["data"]['token']
        self.log.info("Start get token: {}".format(token_access))
        Yaml(conf.get_common_yaml_path()).write_yaml({"token": token_access})

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

    def upload_parse_advisory(self, file_name):
        """
        Upload_parse_advisory
        :return:
        """
        headers = {'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/cve/advisory/upload"
        file_path = os.path.join(BASE_DIR, "test_file", file_name)
        try:
            with open(file_path, 'rb') as file:
                res = Request().post(url=url, files={'file': file}, headers=headers)
                self.log.info("Upload parse advisory result: {}".format(res))
                return res
        except PermissionError:
            self.log.info("PermissionError")

    def upload_unaffected_cve(self, file_name):
        """
        upload_unaffected_cve
        :return:
        """
        headers = {'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/cve/unaffected/upload"
        file_path = os.path.join(BASE_DIR, "test_file", file_name)
        try:
            with open(file_path, 'rb') as file:
                res = Request().post(url=url, files={'file': file}, headers=headers)
                self.log.info("Upload unaffected cve result: {}".format(res))
                return res
        except PermissionError:
            self.log.info("PermissionError")


    def cve_overview(self):
        """
        View the number of CVEs at each leve
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/cve/overview"
        res = Request().get(url=url, params=None, headers=headers)
        self.log.info("Get cve number result: {}".format(res))
        return res

    def cve_info_export(self, data):
        """
        Export cve infos
        :param:
        {
  "host_list": [
    host_id
  ]
}
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/cve/info/export"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Export cve info result: {}".format(res))
        return res


    def import_repo(self, repo_data: dict):
        """
        data: {
            "cluster_id": {
                "repo_name": repo_name
                "repo_data": repo_data
            }
        }

        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        # url = ConfigYaml().get_conf_url() + ":11116/vulnerability/repo/import"
        # 20.03-sp4 new url
        url = ConfigYaml().get_conf_url() + "/distribute/vulnerabilities/repo/import"
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
        self.log.info("Query host list res: {}".format(res))
        return res

    def get_host_detail_info(self, data):
        """
        host_id: 1234

        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/host/info/get"
        res = Request().get(url=url, params=data, headers=headers)
        self.log.info("Get host detail info: {}".format(res))
        return res

    def scan_host(self, data):
        """
        data = {
            "cluster_id":{
                "host_list": [host_id]
            }
        }
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        # url = ConfigYaml().get_conf_url() + ":11116/vulnerability/host/scan"
        url = ConfigYaml().get_conf_url() + "/distribute/vulnerabilities/host/scan"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Scan host result: {}".format(res))
        return res

    def get_host_cve(self, data):
        """
        data = {
  "page": 1,
  "per_page": 10,
  "host_id": host_id,
  "filter": {
    "affected": true,
    "fixed": false,
    "severity": []
  }
}
       :return:

        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        # url = ConfigYaml().get_conf_url() + ":11116/vulnerability/host/cve/get"
        url = ConfigYaml().get_conf_url() + "/vulnerabilities/host/cve/get"
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
        # url = ConfigYaml().get_conf_url() + ":11116/vulnerability/cve/unfixed/packages/get"
        url = ConfigYaml().get_conf_url() + "/vulnerabilities/cve/unfixed/packages/get"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Get cve unfixed package info: {}".format(res))
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

    def get_task_list(self, data):
        """
        data:
        {
  "sort": "create_time",
  "direction": "asc",
  "filter": {
    "task_name": "修复",
    "task_type": [
      "cve fix"
    ]
  },
  "page": 1,
  "per_page": 10
}

        :return
        """

        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/list/get"
        res = Request().post(url=url, params=data, headers=headers)
        self.log.info("Get task list: {}".format(res))
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

    def get_task_progress(self, data):
        """
        data:
        {
  "task_list": [
    "554649d6bf1c11ee84b2525400be8073",
    "61432c14bf1b11ee84b2525400be8073",
  ]
}

        :return
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/progress/get"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Execute task execute progress: {}".format(res))
        return res

    def delete_task(self, data):
        """
        {
  "task_list": [
    "a28c8a08a61111ee84b2525400be8073"
  ]
}

        :return
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/delete"
        res = Request().delete(url=url, json=data, headers=headers)
        self.log.info("Delete task result: {}".format(res))
        return res

    def get_cve_fix_task_result(self, data):
        """
        data:{"task_id": "task_id"}

        :return
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/cve-fix/result/get"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Get cve fix task result: {}".format(res))
        return res

    def generate_repo_set_task(self, data):
        """
        para:
        {
    "cluster_id": {
        "task_name": "REPO设置任务",
        "description": "为以下1个主机设置Repo：host1",
    }

}
        return::

        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        # url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/repo/generate"
        url = ConfigYaml().get_conf_url() + "/distribute/vulnerabilities/task/repo/generate"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Generate repo set task: {}".format(res))
        return res

    def get_repo_set_task_info(self, data):
        """
        para:
        {
  "task_id": "689cd3e2be7711ee84b2525400be8073",
  "filter": {
    "host_name": "host",
    "status": [
      "fail",
      "running",
      "unknown",
      "succeed"
    ]
  },
  "page": 1,
  "per_page": 10
}
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/task/repo/info/get"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Get repo set task info: {}".format(res))
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

    def get_host_status(self, data):
        """
        para:
        {
  "repo_name_list": []
}
        return:

        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        # url = ConfigYaml().get_conf_url() + ":11116/vulnerability/host/status/get"
        url = ConfigYaml().get_conf_url() + "/vulnerabilities/host/status/get"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Get host_status: {}".format(res))
        return res

#     def get_host_cve(self, data):
#         """
#         para:
#         {
#   "host_id": "302",
#   "sort": "cvss_score",
#   "direction": "asc",
#   "filter": {
#     "search_key": "CVE",
#     "affected": true,
#     "severity": [
#       "High"
#     ]
#   },
#   "page": 1,
#   "per_page": 10
# }
#         return:
#
#         """
#         headers = {'Content-Type': 'application/json',
#                    'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
#         url = ConfigYaml().get_conf_url() + ":11116/vulnerability/host/cve/get"
#         res = Request().post(url=url, json=data, headers=headers)
#         self.log.info("Get host_cve: {}".format(res))
#         return res

    def get_cve_host(self, data):
        """
        :param
        {
  "cve_id": "CVE-2023-1068",
  "filter": {
    "fixed": false
  },
  "page": 1,
  "per_page": 10
}
       :return:

        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        # url = ConfigYaml().get_conf_url() + ":11116/vulnerability/cve/host/get"
        url = ConfigYaml().get_conf_url() + "/vulnerabilities/cve/host/get"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Get cve host: {}".format(res))
        return res
		
    def get_cve_list(self, data):
        """
        data:{"task_id": "task_id"}

        :return
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11116/vulnerability/cve/list/get"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Get cve list: {}".format(res))
        return res
