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

    def replace_yaml(self, target_yaml):
        with open(self.yamlf, "rb") as f1:
            common_dict = yaml.safe_load(f1)
        with open(target_yaml, encoding='utf-8') as f2:
            re = Template(f2.read()).substitute(common_dict)
            return yaml.safe_load(stream=re)

    def clear_yaml(self):
        with open(self.yamlf, "w", encoding='utf-8') as f:
            f.truncate()
