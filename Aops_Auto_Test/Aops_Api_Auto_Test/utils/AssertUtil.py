"""
断言封装
"""
from .LogUtil import my_log
import re
from .MysqlUtil import ql


class AssertUtil:
    def __init__(self):
        self.log = my_log()

    def assert_code(self, code, excepted_code):
        """
         断言code相等
        """
        try:
            assert int(code) == int(excepted_code)
            self.log.info("code验证通过,code is %s,except_code is %s" % (code, excepted_code))
            return True
        except:
            self.log.error("code error,code is %s,except_code is %s" % (code, excepted_code))
            raise

    def assert_label(self, label, excepted_label):
        """
        断言label相等
        """
        try:
            assert label == excepted_label
            self.log.info("label验证通过，label is %s,except_label is %s" % (label, excepted_label))
            return True
        except:
            self.log.error("label验证失败,body is %s,except_label is %s" % (label, excepted_label))
            raise

    def assert_message(self, message, excepted_message):
        """
        断言label相等
        """
        try:
            assert message == excepted_message
            self.log.info("message验证通过，message is %s,except_message is %s" % (message, excepted_message))
            return True
        except:
            self.log.error("message验证失败,body is %s,except_message is %s" % (message, excepted_message))
            raise

    def assert_in_body(self, body, excepted_body):
        """
        验证返回结果是否包含期望的结果
        """
        try:
            assert excepted_body in body
            return True
        except:
            self.log.error("不包含或者body错误，body is %s,excepted_body is %s" % (body, excepted_body))
            raise

    def assert_str_and_int(self, data1, data2):

        if type(data2) is str and data2.startswith("^"):
            try:
                assert re.findall(data2, str(data1))
                self.log.info("返回数据断言成功,{},{}匹配".format(data1, data2))
            except:
                self.log.error("返回数据断言失败，{},{}不匹配！".format(data1, data2))
                raise
        elif data1 is None:
            try:
                assert data1 == data2
                self.log.info("返回数据断言成功{}， {}相等".format(data1, data2))
            except:
                self.log.error("返回数据断言失败，{}，{}不相等".format(data1, data2))
                raise
        else:
            try:
                assert data1 == data2
                self.log.info("返回数据断言成功{}， {}相等".format(data1, data2))
            except:
                self.log.error("返回数据断言失败，{}，{}不相等".format(data1, data2))
                raise

    def assert_data(self, res_data, except_data):
        """
        断言data相等
        """
        try:
            assert type(res_data) == type(except_data) and len(res_data) == len(except_data)
            self.log.info("{}，{}长度或类型相同".format(res_data, except_data))
            if isinstance(except_data, dict):
                if len(except_data) == 0:
                    self.assert_str_and_int(len(except_data), len(res_data))
                else:
                    for except_key, except_value in except_data.items():
                        res_value = res_data[str(except_key)]
                        if isinstance(except_data, dict) or isinstance(except_data, list):
                            self.assert_data(res_value, except_value)
                        else:
                            self.assert_str_and_int(res_value, except_value)
            elif isinstance(except_data, list):
                if len(except_data) == 0:
                    self.assert_str_and_int(len(except_data), len(res_data))
                else:
                    for i in range(len(except_data)):
                        if isinstance(except_data[i], list) or isinstance(except_data[i], dict):
                            self.assert_data(res_data[i], except_data[i])
                        else:
                            self.assert_str_and_int(res_data[i], except_data[i])
            else:
                self.assert_str_and_int(res_data, except_data)
        except:
            self.log.error("{}，{}长度或类型不相同".format(res_data, except_data))
            raise


    def assert_search(self, res, expect_field):
        """
        断言搜索结果，当前只支持搜索条件的断言
        """
        # 判断列表为空
        if isinstance(expect_field, list) and len(expect_field) == 0:
            try:
                assert res == expect_field
                self.log.info("返回字段断言成功，均为空{}，{}".format(res, expect_field))
            except:
                self.log.error("返回字段断言失败，一个不为空{},{}".format(res, expect_field))
                raise
        else:
            # 校验返回字段是否全
            res_key = res[0].keys()
            for except_field_key in expect_field.keys():
                try:
                    assert except_field_key in res_key
                    self.log.info("返回字段断言成功，{}包含{}".format(res_key, except_field_key))
                except:
                    self.log.error("返回字段断言失败，{}不包含{}".format(res_key, except_field_key))
                    raise
            expect_key = expect_field.keys()
            for key in expect_key:
                if expect_field[key]:
                    for item in res:
                        try:
                            assert expect_field[key] == item[key]
                            self.log.info("搜索条件断言成功，{}, {}".format(expect_field[key], item[key]))
                        except:
                            self.log.info("搜索条件断言成功，{}, {}".format(expect_field[key], item[key]))
                            raise

    def assert_database(self, sql, excepted_result):
        """
        断言数据库
        """
        ql.connect()
        sql_result = ql.fetchall(sql)[0]['count(*)']
        try:
            assert sql_result == excepted_result
            self.log.info(
                "数据库校验通过,数据库查询结果： {}; 期望结果是： {}".format(sql_result, excepted_result))
        except:
            self.log.error(
                "数据库校验失败,数据库查询结果： {}; 期望结果是： {}".format(sql_result, excepted_result))
            raise
