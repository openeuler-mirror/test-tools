"""
断言封装
"""

from .LogUtil import my_log
import json


class AssertUtil:
    def __init__(self):
        self.log = my_log("AssertUtil")

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

    def assert_body(self, body, excepted_body):
        """
        验证返回结果内容相等
        """
        try:
            assert body == excepted_body
            self.log.info("body验证通过，body is %s,except_body is %s" % (body, excepted_body))
            return True
        except:
            self.log.error("body验证失败,body is %s,except_body is %s" % (body, excepted_body))
            raise

    def assert_in_body(self, body, excepted_body):
        """
        验证返回结果是否包含期望的结果
        """
        try:
            body = json.dumps(body)
            assert excepted_body in body
            return True
        except:
            self.log.error("不包含或者body错误，body is %s,excepted_body is %s" % (body, excepted_body))
            raise


