import os
import pytest
from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.MysqlUtil import ql
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml
from Aops_Api_Auto_Test.api.aops_apollo import ApiApollo

data_file = os.path.join(conf.get_data_path(), "aops-apollo", "upload_unaffected_cve.yaml")
log = my_log()


class TestUploadUnaffectedCve:

    @staticmethod
    def setup_class():
        log.info("准备测试套依赖数据")
        ApiApollo()

    @pytest.mark.parametrize('test_data', Yaml(data_file).data())
    def test_upload_unaffected_cve(self, test_data):
        test_data = Yaml(conf.get_common_yaml_path()).replace_yaml(test_data)
        log.info("test_data: {}".format(test_data))
        ql.connect()
        before_count = ql.fetchall("select count(*) from parse_advisory_record")[0]["count(*)"]
        res = ApiApollo().upload_parse_advisory(test_data['data'])
        if res:
            assert_res = AssertUtil()
            assert_res.assert_code(res["body"]["code"], test_data["validate"]["code"])
            assert_res.assert_label(res["body"]["label"], test_data["validate"]["label"])
            assert_res.assert_message(res["body"]["message"], test_data["validate"]["message"])
            if res["body"]["code"] == '200':
                assert_res.assert_database(test_data["validate"]["sql"], before_count + 1)

