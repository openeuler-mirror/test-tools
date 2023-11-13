import os
from Aops_Api_Auto_Test.utils.YamlUtil import YamlReader

# 1、获取项目基本目录
# 获取当前项目的绝对路径
current = os.path.abspath(__file__)
# print(current)
BASE_DIR = os.path.dirname(os.path.dirname(current))
# print(BASE_DIR)
# 定义config目录路径
_config_path = BASE_DIR + os.sep + "config"
# 定义data目录路径
_data_path = BASE_DIR + os.sep + "test_data"
# 定义conf.yml文件路径
_config_file = _config_path + os.sep + "conf.yaml"
# 定义log文件路径
_log_path = BASE_DIR + os.sep + "logs"
# 定义report目录路径
_report_path = BASE_DIR + os.sep + "report"

def get_config_path():
    return _config_path


def get_config_file():
    return _config_file


def get_log_path():
    return _log_path


def get_data_path():
    return _data_path


def get_report_path():
    return _report_path


class ConfigYaml:
    # 初始yaml读取配置文件
    def __init__(self):
        self.config = YamlReader(get_config_file()).data()

    def get_conf_url(self):
        """
        获取测试的服务的配置信息
        :return:
        """
        return self.config["BASE"]["test"]["url"]

    def get_conf_log(self):
        return self.config["BASE"]["log_level"]

    def get_conf_log_extension(self):
        return self.config["BASE"]["log_extension"]

    def get_db_config_info(self):
        return self.config['db']
