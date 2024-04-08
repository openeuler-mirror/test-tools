import os
from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.config.conf import ConfigYaml, BASE_DIR
from Aops_Api_Auto_Test.utils.RequestsUtil import Request
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml


class ApiDiana:

    def __init__(self):
        self.log = my_log()
        url = ConfigYaml().get_conf_url() + ':80/api/manage/account/login'
        data = {
            "username": ConfigYaml().get_user(),
            "password": ConfigYaml().get_login_password()
        }
        res = Request().post(url=url, json=data)
        token_access = res["body"]["data"]['token']
        self.log.info("Start get token: {}".format(token_access))
        Yaml(conf.get_common_yaml_path()).write_yaml({"token": token_access})

    def get_app_detail(self, app_id):
        """
        Check app detail info

        :param app_id: app_id
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11112/check/app"
        res = Request().get(url=url, params=app_id, headers=headers)
        self.log.info("Get application detail: {}".format(res))
        return res

    def query_app_list(self, params):
        """
        Check app detail info

        :param page: 1
        :param per_page: 10
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11112/check/app/list"
        res = Request().get(url=url, params=params, headers=headers)
        self.log.info("Get application list: {}".format(res))
        return res

    def create_workflow(self, data):
        """
        create_workflow

        {
  "workflow_name": "workflow1",
  "description": "workflow1",
  "app_name": "mysql_network",
  "app_id": "mysql_network",
  "input": {
    "domain": "group1",
    "hosts": [
      "1140"
    ]
  }
}
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11112/check/workflow/create"
        res = Request().post(url=url, json=data, headers=headers)
        self.log.info("Create workflow result: {}".format(res))
        return res

    def delete_workflow(self, data):
        """
        delete workflow

        {
          "workflow_id": "0310f66cefcc11eeb242525400be8073"
        }
        :return:
        """
        headers = {'Content-Type': 'application/json',
                   'Access-Token': Yaml(conf.get_common_yaml_path()).data()['token']}
        url = ConfigYaml().get_conf_url() + ":11112/check/workflow"
        res = Request().delete(url=url, json=data, headers=headers)
        self.log.info("Delete workflow result: {}".format(res))
        return res