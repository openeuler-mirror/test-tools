import os
import pytest
from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.query.aops_zeus import QueryDataBase
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml
from Aops_Api_Auto_Test.api.aops_apollo import ApiApollo
from Aops_Api_Auto_Test.api.aops_zeus import ApiZeus
from Aops_Api_Auto_Test.test_case.setup import CreateData

data_file = os.path.join(conf.get_data_path(), "aops-apollo", "repo_import.yaml")
log = my_log()


class TestRepoImport:

    @staticmethod
    def setup_class():
        log.info("准备测试套依赖数据")
        CreateData().get_cluster_id()
        ApiZeus()

    @staticmethod
    def teardown_class():
        log.info("清理当前测试套数据")
        QueryDataBase().delete_repo(repo_name)
        Yaml(conf.get_common_yaml_path()).clear_yaml()

    @pytest.mark.parametrize('test_data', Yaml(data_file).data())
    def test_repo_import(self, test_data):
        test_data = Yaml(conf.get_common_yaml_path()).replace_yaml(test_data)
        log.info("test_data: {}".format(test_data))
        global repo_name
        repo_name = test_data["data"][Yaml(conf.get_common_yaml_path()).data()['cluster_id']]["repo_name"]
        res = ApiApollo().import_repo(test_data['data'])
        assert_res = AssertUtil()
        assert_res.assert_code(res["body"]["code"], test_data["validate"]["code"])
        assert_res.assert_label(res["body"]["label"], test_data["validate"]["label"])
        assert_res.assert_message(res["body"]["message"], test_data["validate"]["message"])
        if res["body"]["data"][Yaml(conf.get_common_yaml_path()).data()['cluster_id']]["label"] == 'Succeed':
            assert_res.assert_database(test_data["validate"]['sql'], 1)
