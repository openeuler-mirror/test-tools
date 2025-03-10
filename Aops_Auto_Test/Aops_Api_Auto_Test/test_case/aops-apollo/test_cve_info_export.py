# -- coding: utf-8 --
import os
import pytest
from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.query.aops_zeus import QueryDataBase
from Aops_Api_Auto_Test.test_case.setup import CreateData
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml
from Aops_Api_Auto_Test.api.aops_apollo import ApiApollo

data_file = os.path.join(conf.get_data_path(), "aops-apollo", "cve_info_export.yaml")
log = my_log()


class TestCveInfoExport:

    @staticmethod
    def setup_class():
        log.info("准备测试套依赖数据")
        CreateData().get_cve_and_patch()

    @staticmethod
    def teardown_class():
        log.info("清理当前测试套数据")
        QueryDataBase().delete_host(Yaml(conf.get_common_yaml_path()).data()['host_ip'])
        QueryDataBase().delete_host_group(Yaml(conf.get_common_yaml_path()).data()['host_group_name'])
        Yaml(conf.get_common_yaml_path()).clear_yaml()

    @pytest.mark.parametrize('test_data', Yaml(data_file).data())
    def test_cve_info_export(self, test_data):
        test_data = Yaml(conf.get_common_yaml_path()).replace_yaml(test_data)
        log.info("test_data: {}".format(test_data))
        res = ApiApollo().cve_info_export(test_data["data"])
        assert_res = AssertUtil()
        if type(res["body"]) == dict:
            assert_res.assert_code(res["body"]["code"], test_data["validate"]["code"])
            assert_res.assert_label(res["body"]["label"], test_data["validate"]["label"])
            assert_res.assert_message(res["body"]["message"], test_data["validate"]["message"])
        else:
            assert_res.assert_code(res["code"], test_data["validate"]["code"])
            assert_res.assert_database(test_data["validate"]['sql'], len((res["body"].strip().split('\n')))-1)
