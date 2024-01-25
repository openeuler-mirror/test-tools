import os
import pytest
from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.query.aops_zeus import QueryDataBase
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml
from Aops_Api_Auto_Test.api.aops_apollo import ApiApollo

data_file = os.path.join(conf.get_data_path(), "aops-apollo", "repo_import.yaml")
ApiApollo()
log = my_log()

class TestRepoImport:

    @staticmethod
    def teardown_class():
        log.info("清理当前测试套数据")
        QueryDataBase().delete_repo(repo_name)
        Yaml(conf.get_common_yaml_path()).clear_yaml()

    @pytest.mark.parametrize('test_data', Yaml(conf.get_common_yaml_path()).replace_yaml(data_file))
    def test_repo_import(self, test_data):
        log.info("test_data: {}".format(test_data))
        global repo_name
        repo_name = test_data["data"]["repo_name"]
        res = ApiApollo().import_repo(test_data['data'])
        assert_res = AssertUtil()
        assert_res.assert_code(res["body"]["code"], test_data["validate"]["code"])
        assert_res.assert_label(res["body"]["label"], test_data["validate"]["label"])
        assert_res.assert_message(res["body"]["message"], test_data["validate"]["message"])
        if res["body"]["code"] == '200':
            assert_res.assert_database(test_data["validate"]['sql'], 1)