# -- coding: utf-8 --
import os
import pytest
from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml
from Aops_Api_Auto_Test.api.aops_diana import ApiDiana

data_file = os.path.join(conf.get_data_path(), "aops-diana", "get_app_detail.yaml")
log = my_log()


class TestGetAppDetail:

    @staticmethod
    def setup_class():
        log.info("准备测试套依赖数据")
        ApiDiana()

    @staticmethod
    def teardown_class():
        log.info("清理当前测试套数据")
        Yaml(conf.get_common_yaml_path()).clear_yaml()

    @pytest.mark.parametrize('test_data', Yaml(data_file).data())
    def test_get_app_detail(self, test_data):
        test_data = Yaml(conf.get_common_yaml_path()).replace_yaml(test_data)
        log.info("test_data: {}".format(test_data))
        res = ApiDiana().get_app_detail(test_data["data"])
        assert_res = AssertUtil()
        assert_res.assert_code(res["body"]["code"], test_data["validate"]["code"])
        assert_res.assert_label(res["body"]["label"], test_data["validate"]["label"])
        assert_res.assert_message(res["body"]["message"], test_data["validate"]["message"])
        if res["body"]["code"] == 200:
            assert_res.assert_data(res["body"]["data"], test_data["validate"]["data"])