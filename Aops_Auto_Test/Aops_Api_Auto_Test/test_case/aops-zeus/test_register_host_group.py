# -- coding: utf-8 --
from Aops_Api_Auto_Test.api.aops_zeus import ApiZeus
from Aops_Api_Auto_Test.config import conf
import os

from Aops_Api_Auto_Test.query.aops_zeus import QueryDataBase
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.MysqlUtil import ql
import pytest
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml
from Aops_Api_Auto_Test.test_case.setup import CreateData

data_file = os.path.join(conf.get_data_path(), "aops-zeus", "register_host_group.yaml")
log = my_log()


class TestRegisterGroup:
    @staticmethod
    def setup_class():
        log.info("准备测试套数据")
        ApiZeus()
        CreateData().get_cluster_id()

    @staticmethod
    def teardown_method():
        log.info("测试数据清理：删除已注册的主机组")
        QueryDataBase().delete_host_group(group_name)

    @staticmethod
    def teardown_class():
        log.info("清理当前测试套数据")
        Yaml(conf.get_common_yaml_path()).clear_yaml()

    @pytest.mark.parametrize('test_data', Yaml(data_file).data())
    def test_register_group(self, test_data):
        test_data = Yaml(conf.get_common_yaml_path()).replace_yaml(test_data)
        log.info("test_data: {}".format(test_data))
        data = test_data["data"]
        log.info("test_data: {}".format(data))
        global group_name
        res = ApiZeus().register_group(data)
        log.info("res: {}".format(res))
        assert_res = AssertUtil()
        assert_res.assert_code(res["body"]["code"], test_data["validate"]["code"])
        assert_res.assert_data(res["body"]["data"], test_data["validate"]["data"])
        assert_res.assert_label(res["body"]["label"], test_data["validate"]["label"])
        assert_res.assert_message(res["body"]["message"], test_data["validate"]["message"])
        if res["body"]["data"][Yaml(conf.get_common_yaml_path()).data()['cluster_id']]["label"] == 'Succeed':
            assert_res.assert_database(test_data["validate"]['sql'], 1)
            group_name = data[Yaml(conf.get_common_yaml_path()).data()['cluster_id']]['host_group_name']