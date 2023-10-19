import yaml
import os


class YamlReader:
    def __init__(self, yamlf):
        if os.path.exists(yamlf):
            self.yamlf = yamlf
        else:
            raise FileNotFoundError("%s 文件不存在"%yamlf)
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
        with open(self.yamlf, 'a', encoding='utf-8') as f:
            yaml.dump(data=data, stream=f, allow_unicode=True)










