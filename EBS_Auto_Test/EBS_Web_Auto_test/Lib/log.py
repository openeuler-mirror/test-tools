# -*- coding: utf-8 -*-
"""
@Time ： 2023/5/8 0008 19:48
@Auth ： ysc
@File ：log.py
@IDE ：PyCharm
"""
import os
import time
import datetime
import logging
from Config import config as cg


class Log(object):
    def __init__(self):
        self.log_path = os.path.join(cg.ROOT_DIR, 'logs')
        if not os.path.exists(self.log_path): os.mkdir(self.log_path)
        # 生成日志名称
        # 生成日志名称
        self.logName = os.path.join(self.log_path, '%s.log' % time.strftime('%Y-%m-%d-%H-%M-%S'))  # 文件的命名
        # 生成logger
        self.logger = logging.getLogger('ROOT')
        self.logger.setLevel(logging.DEBUG)
        # 创建一个StreamHandler,用于输出到控制台
        stream_handler = logging.StreamHandler()
        self.formatter = logging.Formatter(
            '%(asctime)s - %(filename)s:%(lineno)d - %(module)s:%(funcName)s - %(levelname)s - %(message)s')  # 日志输出格式
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(self.formatter)
        self.logger.addHandler(stream_handler)

        #  创建一个FileHandler，用于写到本地
        fh = logging.FileHandler(filename=self.logName, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

    def get_file_sorted(self):
        """最后修改时间顺序升序排列 os.path.getmtime()->获取文件最后修改时间"""
        dir_list = os.listdir(self.log_path)
        if not dir_list:
            return
        else:
            dir_list = sorted(dir_list, key=lambda x: os.path.getmtime(os.path.join(self.log_path, x)))
            return dir_list

    def TimeStampToTime(self, timestamp):
        """格式化时间"""
        timeStruct = time.localtime(timestamp)
        return str(time.strftime('%Y-%m-%d', timeStruct))

    def handle_logs(self):
        """处理日志过期天数和文件数量"""
        dir_list = [self.log_path]  # 要删除文件的目录名
        for dir in dir_list:
            dirPath = dir  # 拼接删除目录完整路径
            file_list = self.get_file_sorted()  # 返回按修改时间排序的文件list
            if file_list:  # 目录下没有日志文件
                for i in file_list:
                    file_path = os.path.join(dirPath, i)  # 拼接文件的完整路径
                    t_list = self.TimeStampToTime(os.path.getctime(file_path)).split('-')
                    now_list = self.TimeStampToTime(time.time()).split('-')
                    t = datetime.datetime(int(t_list[0]), int(t_list[1]),
                                          int(t_list[2]))  # 将时间转换成datetime.datetime 类型
                    now = datetime.datetime(int(now_list[0]), int(now_list[1]), int(now_list[2]))
                    if (now - t).days > 3:  # 创建时间大于30天的文件删除
                        self.delete_logs(file_path)
                if len(file_list) > 3:  # 限制目录下记录文件数量为30个
                    file_list = file_list[0:-4]
                    for i in file_list:
                        file_path = os.path.join(dirPath, i)
                        print(file_path)
                        self.delete_logs(file_path)

    def delete_logs(self, file_path):
        try:
            os.remove(file_path)
        except PermissionError as e:
            self.logger.warning('删除日志文件失败：{}'.format(e))

    def getLogger(self):
        # 返回logger句柄
        return self.logger

log = Log().getLogger()

if __name__ == "__main__":
    log = Log().getLogger()
    log.info("This is logger class")
    Log().handle_logs()
