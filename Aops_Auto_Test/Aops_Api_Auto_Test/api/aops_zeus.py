from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.config.conf import ConfigYaml
from Aops_Api_Auto_Test.utils.RequestsUtil import Request
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml



class ApiZeus:

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

    def register_group(self, register_group_data: dict):
        """
        Register a host group
        :param register_group_data: "cluster_id": {
                                        "cluster_id": "cluster_id",
                                        "host_group_name": "api_test_group",
                                        "description": "api_test_group"}
        :return: res
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        # url = ConfigYaml().get_conf_url() + ":11111/manage/host/group/add"
        url = ConfigYaml().get_conf_url() + "/distribute/hosts/group"
        res = Request().post(url=url, json=register_group_data, headers=headers)
        return res

    def register_host(self, host_info: dict):
        """
        Register host
        :param host_info: {
            "cluster_id":
                "host_name": "host_name",
                "host_group_name": "host_group_name",
                "host_ip": "host_ip",
                "ssh_port": ssh_port,
                "ssh_user": "ssh_user",
                "password": "password",
                "management": True/False
        }
        :return: res
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        # url = ConfigYaml().get_conf_url() + ":11111/manage/host/add"
        url = ConfigYaml().get_conf_url() + "/distribute/hosts"
        res = Request().post(url=url, json=host_info, headers=headers)
        self.log.info("Get register host result: {}".format(res))
        return res

    def batch_register_host(self, host_list: list):
        """
        Register host
        :param host_list:
        [{
        host_ip: "1.1.1.1"
        ssh_port: 1
        ssh_user: "root"
        password: "openEuler12#$$"
        host_name: "batch_add_host_1"
        host_group_name: "host_group_name"
        management: false
        },
        {
        host_ip: "1.1.1.2"
        ssh_port: 2
        ssh_user: "root"
        password: "openEuler12#$$"
        host_name: "batch_add_host_2"
        host_group_name: "host_group_name"
        management: false}
        ]
        :return: res
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11111/manage/host/add/batch"
        try:
            res = Request().post(url=url, json=host_list, headers=headers)
            self.log.info("Batch register host result: {}".format(res))

        except:
            self.log.error("Batch register host fail!")
            raise
        return res

    def update_host(self, host_info):
        """
        Register host
        :param host_info: {
            "host_name": "host_name",
            "host_group_name": "host_group_name",
            "host_ip": "host_ip",
            "ssh_port": ssh_port,
            "ssh_user": "ssh_user",
            "password": "password",
            "management": True/False
        }
        :return: res
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11111/manage/host/update"
        res = Request().post(url=url, json=host_info, headers=headers)
        self.log.info("Update host result: {}".format(res))
        return res

    def query_host_info(self, host_list):
        """
        Register host
        :param     host_list{[host_id], basic: true}
        :return: res
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11111/manage/host/info/query"
        res = Request().post(url=url, json=host_list, headers=headers)
        self.log.info("Query host info result: {}".format(res))
        return res

    def collect_host_config_info(self, info):
        """

        :param

        {
  "infos": [
    {
      "host_id": "$host_id",
      "config_list": [
        "/etc/gala-gopher/gala-gopher.conf",
        "/etc/yum.repos.d/openEuler.repo"
      ]
    }
  ]
}
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11111/manage/config/collect"
        res = Request().post(url=url, json=info, headers=headers)
        self.log.info("Collect host config info: {}".format(res))
        return res

    def download_template(self):
        """
        Download batch user template
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11111/manage/host/file/template"
        res = Request().get(url=url, params=None, headers=headers)
        self.log.info("Download template result: {}".format(res))
        return res

    def set_plugin_status(self, data):
        """
        :param
        {
  "host_id": "684",
  "plugins": {
    "gala-gopher": "inactive"
  }
}
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11111/manage/agent/plugin/set"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Set plugin status: {}".format(res))
        return res

    def set_metric_status(self, data):
        """
        :param
        {
  "host_id": "698",
  "plugins": {
    "gala-gopher": {
      "example": "off"
    }
  }
}
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11111/manage/agent/metric/set"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Set metric status: {}".format(res))
        return res

    def get_host_scene(self, data):
        """
        :param:
        host_id=698
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11111/manage/host/scene/get"
        res = Request().get(url=url, params=data, headers=headers)
        self.log.info("Get host scene: {}".format(res))
        return res
