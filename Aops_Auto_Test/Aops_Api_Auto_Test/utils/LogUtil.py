import logging
from Aops_Api_Auto_Test.config import conf
import datetime, os

from Aops_Api_Auto_Test.config.conf import ConfigYaml

log_l = {
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "warning": logging.WARNING,
    "error": logging.ERROR
}

class Logger:

    def __init__(self, log_file, log_name, log_level):
        self.log_file = log_file  # 扩展名 配置文件
        self.log_name = log_name
        self.log_level = log_level

        self.logger = logging.getLogger(self.log_name)
        self.logger.setLevel(log_l[self.log_level])
        if not self.logger.handlers:
            fh_stream = logging.StreamHandler()
            fh_stream.setLevel(log_l[self.log_level])
            formatter = logging.Formatter('%(asctime)s %(pathname)s %(lineno)s %(levelname)s %(message)s')
            fh_stream.setFormatter(formatter)
            fh_file = logging.FileHandler(self.log_file)
            fh_file.setLevel(log_l[self.log_level])
            fh_file.setFormatter(formatter)
            self.logger.addHandler(fh_stream)
            self.logger.addHandler(fh_file)


log_path = conf.get_log_path()
current_time = datetime.datetime.now().strftime("%Y-%m-%d")
log_extension = conf.ConfigYaml().get_conf_log_extension()
logfile = os.path.join(log_path, current_time + log_extension)
loglevel = ConfigYaml().get_conf_log()


def my_log(log_name=__file__):
    return Logger(log_file=logfile, log_name=log_name, log_level=loglevel).logger


if __name__ == '__main__':
    my_log().debug("this is debug")
