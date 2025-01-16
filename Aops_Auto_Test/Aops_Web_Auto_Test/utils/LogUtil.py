import logging
from Aops_Web_Auto_Test.config.conf import cm
import datetime
from Aops_Web_Auto_Test.utils.times import dt_strftime
import os


log_l = {
    "info": logging.INFO,
    "debug": logging.DEBUG,
    "warning": logging.WARNING,
    "error": logging.ERROR
}


class Logger:

    def __init__(self, log_path, log_name, log_level):
        self.log_path = log_path
        self.log_name = log_name
        self.log_level = log_level

        self.logger = logging.getLogger(self.log_name)
        self.logger.setLevel(log_l[self.log_level])
        if not self.logger.handlers:
            fh_stream = logging.StreamHandler()
            fh_stream.setLevel(log_l[self.log_level])
            formatter = logging.Formatter('%(asctime)s %(pathname)s %(lineno)s %(levelname)s %(message)s')
            fh_stream.setFormatter(formatter)

            fh_file = logging.FileHandler(self.log_name)
            fh_file.setLevel(log_l[self.log_level])
            fh_file.setFormatter(formatter)
            self.logger.addHandler(fh_stream)
            self.logger.addHandler(fh_file)


log_path = cm.LOG_PATH
current_time = datetime.datetime.now().strftime("%Y-%m-%d")
logname = os.path.join(log_path, '%s.log' % dt_strftime('%Y-%m-%d-%H-%M-%S'))


def my_log():
    return Logger(log_path=log_path, log_name=logname, log_level="info").logger


if __name__ == '__main__':
    my_log().debug("this is debug")