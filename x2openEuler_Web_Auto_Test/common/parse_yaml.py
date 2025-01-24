"""
@Time : 2025/1/6 20:33
@Auth : ysc
@File : parse_yaml.py
@IDE  : PyCharm
"""
from string import Template
import yaml
import os


class Yaml:
    def __init__(self, yaml_file):

        if os.path.exists(yaml_file):
            self.yaml_file = yaml_file
        else:
            raise FileNotFoundError("%s 文件不存在" % yaml_file)
        self._data = None
        self._data_all = None

    def data(self):
        if not self._data:
            with open(self.yaml_file, "rb") as f:
                self._data = yaml.safe_load(f)
        return self._data

    def data_all(self):
        if not self._data_all:
            with open(self.yaml_file, "rb") as f:
                self._data_all = list(yaml.safe_load_all(f))
        return self._data_all

    def write_yaml(self, data):
        with open(self.yaml_file, 'a', encoding='utf-8') as f:
            yaml.dump(data=data, stream=f, allow_unicode=True)

    def replace_yaml(self, test_data):
        with open(self.yaml_file, "rb") as f1:
            common_dict = yaml.safe_load(f1)
        yaml_data = yaml.dump(test_data)
        re = Template(yaml_data).substitute(common_dict)
        return yaml.safe_load(stream=re)

    def clear_yaml(self) -> object:
        with open(self.yaml_file, "w", encoding='utf-8') as f:
            f.truncate()
