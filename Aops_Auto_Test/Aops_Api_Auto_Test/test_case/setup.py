from Aops_Api_Auto_Test.api.aops_zeus import ApiZeus
from Aops_Api_Auto_Test.api.aops_apollo import ApiApollo
from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.config.conf import ConfigYaml
from Aops_Api_Auto_Test.query.aops_zeus import QueryDataBase
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml
log = my_log()


class CreateData:
    def get_group_name(self):
        ApiZeus().register_group({"host_group_name": "api_test_group", "description": "api_test_group"})
        host_group_name = "api_test_group"
       # host_group_name = QueryDataBase().query_group_name("api_test_group")
        Yaml(conf.get_common_yaml_path()).write_yaml({"host_group_name": host_group_name})
        return host_group_name

    def get_host_info(self):
        host_info = {
            "host_name": "api_test_host",
            "host_group_name": self.get_group_name(),
            "host_ip": ConfigYaml().get_host_info(),
            "ssh_port": 22,
            "ssh_user": "root",
            "password": "openEuler12#$",
            "management": True,
            "ssh_pkey": ""
        }
        ApiZeus().register_host(host_info)
        host_id = QueryDataBase().query_host_info(host_info['host_name'])['host_id']
        host_name = host_info['host_name']
        host_ip = host_info['host_ip']
        Yaml(conf.get_common_yaml_path()).write_yaml({"host_id": host_id})
        Yaml(conf.get_common_yaml_path()).write_yaml({"host_ip": host_ip})
        Yaml(conf.get_common_yaml_path()).write_yaml({"host_name": host_name})
        return host_id, host_name, host_ip

    def get_repo_info(self):
        repo_info = {
  "repo_name": "api_test_repo",
  "repo_data": "[aops-update]\nname=update\nbaseurl=https://repo.openeuler.org/openEuler-22.03-LTS/update/$basearch\nenabled=1\ngpgcheck=1\ngpgkey=https://repo.openeuler.org/openEuler-22.03-LTS/OS/$basearch/RPM-GPG-KEY-openEuler"
}
        ApiApollo().import_repo(repo_info)
        repo_id = QueryDataBase().query_repo(repo_info['repo_name'])['repo_id']
        repo_data = QueryDataBase().query_repo(repo_info['repo_name'])['repo_data']
        Yaml(conf.get_common_yaml_path()).write_yaml({"repo_id": repo_id})
        Yaml(conf.get_common_yaml_path()).write_yaml({"repo_name": repo_info['repo_name']})
        Yaml(conf.get_common_yaml_path()).write_yaml({"repo_data": repo_data})

    def generate_repo_set_task(self):
        self.get_repo_info()
        self.get_host_info()
        data = {
                "repo_name": Yaml(conf.get_common_yaml_path()).data()['repo_name'],
                "task_name": "REPO设置任务",
                "description": "为以下1个主机设置Repo：{}".format(Yaml(conf.get_common_yaml_path()).data()['host_name']),
                "info": [
                    {
                        "host_id": Yaml(conf.get_common_yaml_path()).data()['host_id']
                    }
                ]
            }
        res = ApiApollo().generate_repo_set_task(data)
        Yaml(conf.get_common_yaml_path()).write_yaml({"task_id": res["body"]["data"]['task_id']})
        return res

    def get_cve_and_patch(self):
        try:
            host_id = self.get_host_info()[0]
            res = ApiApollo().scan_host({"host_list": [host_id]})
            if res["body"]["code"] == '200':
                while True:
                    status_res = ApiApollo().get_host_status({"host_list": [host_id]})
                    if status_res["body"]["data"]["result"][str(host_id)] == 0:
                        get_host_cve_res = ApiApollo().get_host_cve({"host_id": host_id,"filter": {"fixed": False,"severity": []}})
                        if get_host_cve_res["body"]["code"] == '200' and get_host_cve_res["body"]["data"]["result"] is not None:
                            get_unfix_package = ApiApollo().get_cve_unfixed_packages({"cve_id": get_host_cve_res["body"]["data"]["result"][0]["cve_id"],"host_ids": [host_id]})
                            if get_unfix_package["body"]["code"] == '200':
                                for unfix in get_unfix_package["body"]["data"]:
                                    if unfix["support_way"] == 'coldpatch':
                                        cold_installed_rpm = unfix["installed_rpm"]
                                        cold_available_rpm = unfix["available_rpm"]
                                        cold_fix_way = 'coldpatch'
                                    elif unfix["support_way"] == 'hotpatch':
                                        hot_installed_rpm = unfix["installed_rpm"]
                                        hot_available_rpm = unfix["available_rpm"]
                                        hot_fix_way = 'hotpatch'
                                Yaml(conf.get_common_yaml_path()).write_yaml({"cold_fix_way": cold_fix_way})
                                Yaml(conf.get_common_yaml_path()).write_yaml({"cold_installed_rpm": cold_installed_rpm})
                                Yaml(conf.get_common_yaml_path()).write_yaml({"cold_available_rpm": cold_available_rpm})
                                Yaml(conf.get_common_yaml_path()).write_yaml({"hot_fix_way": hot_fix_way})
                                Yaml(conf.get_common_yaml_path()).write_yaml({"hot_installed_rpm": hot_installed_rpm})
                                Yaml(conf.get_common_yaml_path()).write_yaml({"hot_available_rpm": hot_available_rpm})
                                Yaml(conf.get_common_yaml_path()).write_yaml({"cve_id": get_host_cve_res["body"]["data"]["result"][0]["cve_id"]})
                                break
        except:
            log.error("准备测试数据失败！")

    def generate_cve_fix_task(self):
        self.get_cve_and_patch()
        data = {
            "task_name": "CVE修复任务",
            "description": "修复以下1个CVE：CVE-2023-1068",
            "accepted": True,
            "check_items": [],
            "takeover": True,
            "info": [
                {
                    "cve_id": Yaml(conf.get_common_yaml_path()).data()['cve_id'],
                    "host_info": [
                        {
                            "host_id": Yaml(conf.get_common_yaml_path()).data()['host_id'],
                        }
                    ],
                    "rpms": [
                        {
                            "installed_rpm": Yaml(conf.get_common_yaml_path()).data()['hot_installed_rpm'],
                            "available_rpm": Yaml(conf.get_common_yaml_path()).data()['hot_available_rpm'],
                            "fix_way": Yaml(conf.get_common_yaml_path()).data()['hot_fix_way']
                        },
                        {
                            "installed_rpm": Yaml(conf.get_common_yaml_path()).data()['cold_installed_rpm'],
                            "available_rpm": Yaml(conf.get_common_yaml_path()).data()['cold_available_rpm'],
                            "fix_way": Yaml(conf.get_common_yaml_path()).data()['cold_fix_way']
                        }
                    ]
                }
            ]
        }
        res = ApiApollo().generate_cve_fix_task(data)
        Yaml(conf.get_common_yaml_path()).write_yaml({"cold_fix_way_task_id": res["body"]["data"][0]['task_id']})
        Yaml(conf.get_common_yaml_path()).write_yaml({"hot_fix_way_task_id": res["body"]["data"][1]['task_id']})
        return res













