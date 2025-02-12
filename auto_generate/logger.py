import os
import logging
import logging.handlers
from datetime import datetime
current_file_path = os.path.abspath(__file__)
current_dir_path = os.path.dirname(current_file_path)
log_dir_path = os.path.join(current_dir_path, 'script_logs')


def setup_logger():
    # 获取当前时间
    current_datetime = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    # 创建日志目录
    os.makedirs(log_dir_path, exist_ok=True)
    # 生成日志文件名
    log_file_name = f'{log_dir_path}/{current_datetime}.log'
    # 创建日志记录器
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # 设置日志级别为 DEBUG

    # 创建文件处理器，每天生成一个日志文件
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file_name, when='midnight', interval=1, backupCount=7, encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)  # 设置文件处理器的日志级别为 DEBUG

    # 创建控制台处理器，用于输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)  # 设置控制台处理器的日志级别为 DEBUG

    # 创建格式器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 将格式器添加到处理器
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
