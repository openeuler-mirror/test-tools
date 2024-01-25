# -- coding: utf-8 --
import os
import pytest
from Aops_Api_Auto_Test.api.aops_apollo import ApiApollo
from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.query.aops_zeus import QueryDataBase
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.MysqlUtil import ql
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml
from Aops_Api_Auto_Test.test_case.setup import CreateData

data_file = os.path.join(conf.get_data_path(), "aops-apollo", "task_cve-rollback_generate.yaml")
log = my_log()
CreateData().generate_cve_fix_task()


class TestGenerateCveRollbackTask:

    @staticmethod
    def teardown_class():
        log.info("清理当前测试套数据")
        QueryDataBase().delete_host(Yaml(conf.get_common_yaml_path()).data()['host_ip'])
        QueryDataBase().delete_host_group(Yaml(conf.get_common_yaml_path()).data()['host_group_name'])
        Yaml(conf.get_common_yaml_path()).clear_yaml()

    @pytest.mark.parametrize('test_data', Yaml(conf.get_common_yaml_path()).replace_yaml(data_file))
    def test_generate_cve_rollback_task(self, test_data):
        log.info("test_data: {}".format(test_data))
        data = test_data["data"]
        ql.connect()
        before_value = ql.fetchall(test_data["validate"]['sql'])[0]['count(*)']
        res = ApiApollo().generate_cve_rollback_task(data)
        assert_res = AssertUtil()
        assert_res.assert_code(res["body"]["code"], test_data["validate"]["code"])
        assert_res.assert_label(res["body"]["label"], test_data["validate"]["label"])
        assert_res.assert_message(res["body"]["message"], test_data["validate"]["message"])
        if res["body"]["code"] == '200':
            assert_res.assert_data(res["body"]["data"], test_data["validate"]["data"])
            assert_res.assert_database(test_data["validate"]['sql'], before_value+1)


