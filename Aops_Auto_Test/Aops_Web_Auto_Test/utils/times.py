# -*- coding:utf-8 -*-
import time
import datetime
from functools import wraps


def timestamp():
    """时间戳"""
    return time.time()


def dt_strftime(fmt="%Y%m", day='', model='next'):
    """
    datetime格式化时间
    :param fmt: %Y%m%d %H%M%S
    :param day: digits
    :param model: previous or next
    """
    if day:
        if model == "next":
            date_time = datetime.datetime.now() + datetime.timedelta(int(day))
        elif model == "previous":
            date_time = datetime.datetime.now() - datetime.timedelta(int(day))
        else:
            raise ValueError("model 参数必须是next或previous")
    else:
        date_time = datetime.datetime.now()
    return date_time.strftime(fmt)


def sleep(seconds=5.0):
    """
    睡眠时间
    """
    time.sleep(seconds)


def running_time(func):
    """函数运行时间"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = timestamp()
        res = func(*args, **kwargs)
        print("校验元素done！用时%.3f秒！" % (timestamp() - start))
        return res

    return wrapper


if __name__ == '__main__':
    print(dt_strftime("%Y%m%d%H%M%S"))