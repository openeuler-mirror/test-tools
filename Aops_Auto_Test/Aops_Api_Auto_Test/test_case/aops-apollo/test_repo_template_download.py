import os
import pytest
from Aops_Api_Auto_Test.config import conf
from Aops_Api_Auto_Test.utils.AssertUtil import AssertUtil
from Aops_Api_Auto_Test.utils.LogUtil import my_log
from Aops_Api_Auto_Test.utils.YamlUtil import Yaml
from Aops_Api_Auto_Test.api.aops_apollo import ApiApollo

data_file = os.path.join(conf.get_data_path(), "aops-apollo", "repo_template_download.yaml")
log = my_log()


class TestDownloadRepoTemplate:

    @staticmethod
    def setup_class():
        log.info("准备测试套依赖数据")
        ApiApollo()

    @pytest.mark.parametrize('test_data', Yaml(data_file).data())
    def test_download_repo_template(self, test_data):
        test_data = Yaml(conf.get_common_yaml_path()).replace_yaml(test_data)
        log.info("test_data: {}".format(test_data))
        res = ApiApollo().download_repo_template()
        log.info("res: {}".format(res))
        text = str.encode(res["body"], 'utf - 8')
        with open("../template.repo", "wb") as f:
            f.write(text)
        assert_res = AssertUtil()
        assert_res.assert_code(res["code"], test_data["validate"]["code"])
        assert_res.assert_in_body(res["body"], test_data["validate"]["data"])