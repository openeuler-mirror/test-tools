# -- coding: utf-8 --
from Aops_Api_Auto_Test.common.base_function import BaseFun
from Aops_Api_Auto_Test.config import conf
import os
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.MysqlUtil import ql
import pytest
from Aops_Api_Auto_Test.config.conf import ConfigYaml
from Aops_Api_Auto_Test.utils.RequestsUtil import Request
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
import allure

data_file = os.path.join(conf.get_data_path(), "aops-zeus", "batch_register_host.yaml")
log = my_log()
base_data = BaseFun(data_file)
base_data.get_token()
base_data.register_group()


class TestBatchAddHost:

    @staticmethod
    def teardown_method():
        log.info("删除已添加的主机")
        delete_batch_host = "delete from host where host_name like 'batch%'"
        ql.exec(delete_batch_host)

    @staticmethod
    def teardown_class():
        base_data.clear_data()
        
    @pytest.mark.parametrize('test_data', base_data.yaml_replace())
    def test_batch_add_user(self, test_data):
        log.info("test_data: {}".format(test_data))
        headers = {'Content-Type': 'application/json', 'Access-Token': test_data['token']}
        url = ConfigYaml().get_conf_url() + ":" + test_data["port"] + test_data["path"]
        data = test_data["data"]
        case_name = test_data["case_name"]
        allure.dynamic.title(case_name)
        request = Request()
        res = request.post(url=url, json=data, headers=headers)
        log.info("res: {}".format(res))
        assert_res = AssertUtil()
        assert_res.assert_code(res["body"]["code"], test_data["except"]["code"])
        assert_res.assert_body(res["body"]["label"], test_data["except"]["label"])
        assert_res.assert_body(res["body"]["message"], test_data["except"]["message"])
        if res["body"]["code"] == '200':
            try:
                assert len(ql.fetchall(test_data['sql'])) == len(data['host_list'])
                log.info("数据库校验通过,数据库查询结果： {}".format(ql.fetchall(test_data['sql'])))
            except:
                log.error("数据库校验失败,数据库查询结果： {}".format(ql.fetchall(test_data['sql'])))
