# -- coding: utf-8 --
from Aops_Api_Auto_Test.api.aops_zeus import ApiZeus
from Aops_Api_Auto_Test.config import conf
import os

from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.utils.LogUtil import my_log
import pytest
from Aops_Api_Auto_Test.test_case.setup import CreateData

from Aops_Api_Auto_Test.utils.YamlUtil import Yaml

data_file = os.path.join(conf.get_data_path(), "aops-zeus", "template_download.yaml")
CreateData()
log = my_log()


class TestDownloadTemplate:

    @staticmethod
    def teardown_class():
        log.info("清理当前测试套数据")
        Yaml(conf.get_common_yaml_path()).clear_yaml()

    @pytest.mark.parametrize('test_data', Yaml(conf.get_common_yaml_path()).replace_yaml(data_file))
    def test_download_template(self, test_data):
        log.info("test_data: {}".format(test_data))
        res = ApiZeus().download_template()
        log.info("res: {}".format(res))
        text = str.encode(res["body"], 'utf - 8')
        with open("../template.csv", "wb") as f:
            f.write(text)
        assert "host_ip,ssh_port,ssh_user,password,ssh_pkey,host_name,host_group_name,management" in res["body"]
        assert_res = AssertUtil()
        assert_res.assert_code(res["code"], test_data["validate"]["code"])
