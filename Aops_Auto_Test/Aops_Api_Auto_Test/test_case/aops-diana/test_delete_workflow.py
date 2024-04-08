from config import conf
import os

from utils.MysqlUtil import Mysql
from utils.YamlUtil import YamlReader
import pytest
from config.conf import ConfigYaml
from utils.RequestsUtil import Request
from utils.AssertUtil import AssertUtil
import allure

data_file = os.path.join(conf.get_data_path(), "aops-diana1/workflow", "delete_hold_workflow.yaml")
data_list = YamlReader(data_file).data_all()
# print("test data: ", data_list)

class TestModel:
    @pytest.mark.parametrize('register', data_list)
    def test_get_model(self, register,get_token):
        # print('register: ',register)
        headers = {'Content-Type': 'application/json', 'Access-Token': get_token}
        url = ConfigYaml().get_conf_url() + ":" + register['port'] + register['path']
        print('url: ',url)

        ql = Mysql('172.168.174.157', 'root', 'aops', 3306)
        ql.connect()
        sql = "select workflow_id from workflow where username='fhstest' and status='hold'"
        ql.cursor.execute(sql)
        workflow_id = ql.cursor.fetchone()

        register["data"]['workflow_id'] = workflow_id['workflow_id']
        print('register: ', register)
        data = register["data"]
        case_name = register["case_name"]
        allure.dynamic.title(case_name)
        allure.dynamic.description("请求body==>> %s" % str(data))
        request = Request()
        res = request.delete(url=url, json=data, headers=headers)
        print("res==",res)
        assert_res = AssertUtil()
        assert_res.assert_code(res["body"]["code"], register["except"]["code"])
        assert_res.assert_body(res["body"]["label"], register["except"]["label"])
        assert_res.assert_body(res["body"]["message"], register["except"]["message"])

if __name__ == '__main__':
    pytest.main(["-s", "test_delete_workflow.py", "--alluredir", "./report/result"])