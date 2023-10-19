# -- coding: utf-8 --
from Aops_Api_Auto_Test.common.base_function import BaseFun
from Aops_Api_Auto_Test.config import conf
import os
from Aops_Api_Auto_Test.utils.LogUtil import my_log
import pytest
from Aops_Api_Auto_Test.config.conf import ConfigYaml
from Aops_Api_Auto_Test.utils.RequestsUtil import Request
import allure

data_file = os.path.join(conf.get_data_path(), "aops-zeus", "template_download.yaml")
base_data = BaseFun(data_file)
base_data.get_token()
log = my_log()


class TestDownloadTemplate:

    @staticmethod
    def teardown_class():
        base_data.clear_data()
        
    @pytest.mark.parametrize('test_data', base_data.yaml_replace())
    def test_download_template(self, test_data):
        log.info("test_data: {}".format(test_data))
        headers = {'Content-Type': 'application/json', 'Access-Token': test_data['token']}
        url = ConfigYaml().get_conf_url() + ":" + test_data["port"] + test_data["path"]
        case_name = test_data["case_name"]
        allure.dynamic.title(case_name)
        request = Request()
        res = request.get(url=url,params=None,headers=headers)
        log.info("res: {}".format(res))
        text = str.encode(res["body"], 'utf - 8')
        try:
            with open("../template.csv", "wb") as f:
                f.write(text)
            assert "host_ip,ssh_port,ssh_user,password,host_name,host_group_name,management" in res["body"]
            log.info("下载文件成功！")
        except:
            log.error("下载文件失败！")
