"""
@Time : 2024/7/27 10:35
@Auth : ysc
@File : log.py
@IDE  : PyCharm
"""
import os
import time
import logging
import x2openEuler_Web_Auto_Test.config.config as cg
from datetime import datetime


class Log(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Log, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.log_path = os.path.join(cg.ROOT_DIR, 'logs')
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)

        # 生成日志名称
        self.logName = os.path.join(self.log_path, f'{time.strftime("%Y-%m-%d-%H-%M-%S")}.log')

        # 生成logger
        self.logger = logging.getLogger('ROOT')
        self.logger.setLevel(logging.DEBUG)

        # 创建一个StreamHandler,用于输出到控制台
        stream_handler = logging.StreamHandler()
        self.formatter = logging.Formatter(
            '%(asctime)s - %(filename)s:%(lineno)d - %(module)s:%(funcName)s - %(levelname)s - %(message)s')
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(stream_handler)

        # 创建一个FileHandler，用于写到本地
        fh = logging.FileHandler(filename=self.logName, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        # 初始化时清理过期日志
        self.handle_logs()

    def get_file_sorted(self):
        """最后修改时间顺序升序排列"""
        dir_list = os.listdir(self.log_path)
        if not dir_list:
            return []
        else:
            return sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(self.log_path, x)))

    def handle_logs(self):
        """处理日志过期天数和文件数量"""
        file_list = self.get_file_sorted()  # 返回按修改时间排序的文件list
        if file_list:  # 目录下有日志文件
            for i in file_list:
                file_path = os.path.join(self.log_path, i)
                file_ctime = datetime.fromtimestamp(os.path.getctime(file_path))
                now = datetime.now()
                if (now - file_ctime).days > cg.LOG_RETENTION_DAYS:  # 创建时间大于配置天数的文件删除
                    self.delete_logs(file_path)

            if len(file_list) > cg.MAX_LOG_FILES:  # 限制目录下记录文件数量为配置值
                file_list = file_list[:-cg.MAX_LOG_FILES]
                for i in file_list:
                    file_path = os.path.join(self.log_path, i)
                    self.delete_logs(file_path)

    def delete_logs(self, file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            self.logger.warning(f'删除日志文件失败：{e}')

    def getLogger(self):
        return self.logger


# 要清理时运行main函数，注释下面一行
log = Log().getLogger()

if __name__ == "__main__":
    log.info("This is logger class")
    Log().handle_logs()
