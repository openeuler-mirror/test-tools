# -- coding: utf-8 --
from Aops_Api_Auto_Test.common.base_function import BaseFun
from Aops_Api_Auto_Test.config import conf
import os
from Aops_Api_Auto_Test.utils.MysqlUtil import ql
from Aops_Api_Auto_Test.utils.YamlUtil import YamlReader
import pytest
from Aops_Api_Auto_Test.config.conf import ConfigYaml
from Aops_Api_Auto_Test.utils.RequestsUtil import Request
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.utils.LogUtil import my_log

data_file = os.path.join(conf.get_data_path(), "aops-zeus", "register_host.yaml")
common_file = os.path.join(conf.get_data_path(), "common.yaml")
data_list = YamlReader(data_file).data_all()
base_data = BaseFun(data_file)
base_data.get_token()
base_data.register_group()
log = my_log()


class TestRegister:

    @staticmethod
    def teardown_method():
        log.info("开始清理当前测试用例数据")
        delete_batch_host = "delete from host where host_name='{}'".format(host_name)
        ql.connect()
        ql.exec(delete_batch_host)

    @staticmethod
    def teardown_class():
        base_data.clear_data()

    @pytest.mark.parametrize('test_data', base_data.yaml_replace())
    def test_register_host(self, test_data):
        headers = {'Content-Type': 'application/json', 'Access-Token': test_data['token']}
        url = ConfigYaml().get_conf_url() + ":" + test_data["port"] + test_data["path"]
        data = test_data["data"]
        global host_name
        host_name = data['host_name']
        request = Request()
        res = request.post(url=url, json=data, headers=headers)
        assert_res = AssertUtil()
        assert_res.assert_code(res["body"]["code"], test_data["except"]["code"])
        assert_res.assert_body(res["body"]["label"], test_data["except"]["label"])
        assert_res.assert_body(res["body"]["message"], test_data["except"]["message"])
        if res["body"]["code"] == '200':
            ql.connect()
            try:
                assert len(ql.fetchall(test_data['sql'])) == 1
                log.info("数据库校验通过,数据库查询结果： {}".format(ql.fetchall(test_data['sql'])))
            except:
                log.error("数据库校验失败,数据库查询结果： {}".format(ql.fetchall(test_data['sql'])))
