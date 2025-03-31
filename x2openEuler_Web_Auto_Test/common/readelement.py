"""
@Time : 2024/12/13 15:07
@Auth : ysc
@File : readelement.py
@IDE  : PyCharm
"""
import os
import yaml
import x2openEuler_Web_Auto_Test.config.config as cg


class Element(object):
    """获取元素"""

    def __init__(self, name):
        self.file_name = '%s.yaml' % name
        self.element_path = os.path.join(cg.ELEMENT_PATH, self.file_name)
        if not os.path.exists(self.element_path):
            raise FileNotFoundError("%s 文件不存在！" % self.element_path)
        with open(self.element_path, encoding='utf-8') as f:
            self.data = yaml.safe_load(f)

    def __getitem__(self, item):
        """获取属性"""
        data = self.data.get(item)
        if data:
            name, value = data.split('==')
            return name, value
        raise ArithmeticError("{}中不存在关键字：{}".format(self.file_name, item))
