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
data_file = os.path.join(conf.get_data_path(), "aops-apollo", "repo_delete.yaml")
log = my_log()


class TestDeleteRepo:

    @staticmethod
    def setup_class():
        log.info("准备测试套依赖数据")
        CreateData().get_repo_info()

    @staticmethod
    def teardown_class():
        log.info("清理当前测试套数据")
        QueryDataBase().delete_repo(Yaml(conf.get_common_yaml_path()).data()['repo_name'])
        Yaml(conf.get_common_yaml_path()).clear_yaml()

    @pytest.mark.parametrize('test_data', Yaml(data_file).data())
    def test_delete_repo(self, test_data):
        test_data = Yaml(conf.get_common_yaml_path()).replace_yaml(test_data)
        log.info("test_data: {}".format(test_data))
        res = ApiApollo().delete_repo(test_data['data'])
        assert_res = AssertUtil()
        assert_res.assert_code(res["body"]["code"], test_data["validate"]["code"])
        assert_res.assert_label(res["body"]["label"], test_data["validate"]["label"])
        assert_res.assert_message(res["body"]["message"], test_data["validate"]["message"])
        if res["body"]["code"] == '200' and 'sql' in test_data["validate"]:
            assert_res.assert_database(test_data["validate"]['sql'], 0)
