# -- coding: utf-8 --
from Aops_Api_Auto_Test.common.base_function import BaseFun
from Aops_Api_Auto_Test.config import conf
import os
import pytest
from Aops_Api_Auto_Test.config.conf import ConfigYaml
from Aops_Api_Auto_Test.utils.RequestsUtil import Request
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.MysqlUtil import ql

data_file = os.path.join(conf.get_data_path(), "aops-zeus", "update_host_info.yaml")
base_data = BaseFun(data_file)
base_data.get_token()
base_data.register_group()
base_data.register_host("1.1.1.1")
log = my_log()


class TestUpdateHostInfo:

    @staticmethod
    def teardown_class():
        base_data.clear_data()

    @pytest.mark.parametrize('test_data', base_data.yaml_replace())
    def test_update_host_info(self, test_data):
        headers = {'Content-Type': 'application/json', 'Access-Token': test_data['token']}
        url = ConfigYaml().get_conf_url() + ":" + test_data["port"] + test_data["path"]
        data = test_data["data"]
        request = Request()
        res = request.post(url=url, json=data, headers=headers)
        log.info("res: {}".format(res))
        assert_res = AssertUtil()
        assert_res.assert_code(res["body"]["code"], test_data["except"]["code"])
        assert_res.assert_body(res["body"]["label"], test_data["except"]["label"])
        assert_res.assert_body(res["body"]["message"], test_data["except"]["message"])
        if res["body"]["code"] == '200':
            try:
                assert len(ql.fetchall(test_data['sql'])) == 1
                log.info("数据库校验通过,数据库查询结果： {}".format(ql.fetchall(test_data['sql'])))
            except:
                log.error("数据库校验失败,数据库查询结果： {}".format(ql.fetchall(test_data['sql'])))

