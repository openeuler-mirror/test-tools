import json
from string import Template
import yaml
import os


class Yaml:
    def __init__(self, yamlf):

        if os.path.exists(yamlf):
            self.yamlf = yamlf
        else:
            raise FileNotFoundError("%s 文件不存在" % yamlf)
        self._data = None
        self._data_all = None

    def data(self):
        if not self._data:
            with open(self.yamlf, "rb") as f:
                self._data = yaml.safe_load(f)
        return self._data

    def data_all(self):
        if not self._data_all:
            with open(self.yamlf, "rb") as f:
                self._data_all = list(yaml.safe_load_all(f))
        return self._data_all

    def write_yaml(self, data):
        with open(self.yamlf, 'a') as f:
            yaml.dump(data=data, stream=f, allow_unicode=True)

    def replace_yaml(self, test_data):
        with open(self.yamlf, "rb") as f1:
            common_dict = yaml.safe_load(f1)
        yaml_data = yaml.dump(test_data)
        re = Template(yaml_data).substitute(common_dict)
        return yaml.safe_load(stream=re)

    def clear_yaml(self):
        with open(self.yamlf, "w", encoding='utf-8') as f:
            f.truncate()

    def generate_data(self, test_data):
        print("--------------------")
        print(type(test_data), test_data)
        print("--------------------")
        if isinstance(test_data, dict):
            for value in test_data.values():
                print("--------------------")
                print(type(value), value)
                print("--------------------")
                if isinstance(value, dict) or isinstance(value, list):
                    self.generate_data(value)
                else:
                    if value.startswith("$"):
                        value = self.yamlf["value"]
        elif isinstance(test_data, list):
            for value in test_data:
                if isinstance(value, list) or isinstance(value, dict):
                    self.generate_data(value)
                else:
                    if value.startswith("$"):
                        value = self.yamlf["item"]
        return test_data
