# -- coding: utf-8 --
import os
import pytest
from Aops_Api_Auto_Test.test_case.setup import CreateData
from Aops_Api_Auto_Test.api.aops_zeus import ApiZeus
from Aops_Api_Auto_Test.query.aops_zeus import QueryDataBase
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml

log = my_log()
data_file = os.path.join(conf.get_data_path(), "aops-zeus", "update_host_info.yaml")


class TestUpdateHostInfo:

    @staticmethod
    def setup_class():
        log.info("准备测试套依赖数据")
        CreateData().get_host_info()

    @staticmethod
    def teardown_class():
        log.info("清理当前测试套数据")
        QueryDataBase().delete_host(Yaml(conf.get_common_yaml_path()).data()['host_ip'])
        QueryDataBase().delete_host_group(Yaml(conf.get_common_yaml_path()).data()['host_group_name'])
        Yaml(conf.get_common_yaml_path()).clear_yaml()

    @pytest.mark.parametrize('test_data', Yaml(data_file).data())
    def test_update_host_info(self, test_data):
        test_data = Yaml(conf.get_common_yaml_path()).replace_yaml(test_data)
        log.info("test_data: {}".format(test_data))
        body_data = test_data['data']
        res = ApiZeus().update_host(body_data)
        assert_res = AssertUtil()
        assert_res.assert_code(res["body"]["code"], test_data["validate"]["code"])
        assert_res.assert_label(res["body"]["label"], test_data["validate"]["label"])
        assert_res.assert_message(res["body"]["message"], test_data["validate"]["message"])
        if res["body"]["code"] == '200':
            assert_res.assert_database(test_data["validate"]['sql'], 1)

