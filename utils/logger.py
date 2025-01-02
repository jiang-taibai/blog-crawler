import logging
import os
from datetime import datetime
import threading


# 定义日志颜色类
class LogColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # 蓝色
        'INFO': '\033[92m',  # 绿色
        'WARNING': '\033[93m',  # 黄色
        'ERROR': '\033[91m',  # 红色
        'CRITICAL': '\033[95m',  # 洋红色
    }
    RESET = '\033[0m'

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        log_message = super().format(record)
        return f"{log_color}{log_message}{self.RESET}"


class Logger:
    _instance = None
    _lock = threading.Lock()  # 用于确保线程安全
    _logger = None
    _initialized = False  # 确保只初始化一次

    def __new__(cls, log_file: str = None, console_level: int = logging.INFO, file_level: int = logging.DEBUG):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_file: str = None, console_level: int = logging.INFO, file_level: int = logging.DEBUG):
        if Logger._initialized:  # 如果已经初始化过，则跳过
            return

        with Logger._lock:  # 加锁确保线程安全的初始化
            if Logger._initialized:  # 防止在加锁后多次初始化
                return

            Logger._logger = logging.getLogger("UnifiedLogger")
            Logger._logger.setLevel(logging.DEBUG)  # 设置基础日志级别

            # 控制台输出
            if not Logger._logger.handlers:
                console_handler = logging.StreamHandler()
                console_handler.setLevel(console_level)
                console_format = LogColorFormatter(
                    '%(asctime)s - [%(filename)s:%(lineno)04d] - %(levelname)8s - %(message)s'
                )
                console_handler.setFormatter(console_format)
                Logger._logger.addHandler(console_handler)

                # 文件输出
                if log_file is None:
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    log_dir = os.path.join(current_dir, '..', 'log')
                    os.makedirs(log_dir, exist_ok=True)
                    log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")

                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(file_level)
                file_format = logging.Formatter(
                    '%(asctime)s - [%(filename)s:%(lineno)04d] - %(levelname)8s - %(message)s'
                )
                file_handler.setFormatter(file_format)
                Logger._logger.addHandler(file_handler)

            Logger._initialized = True

    @classmethod
    def get_logger(cls) -> logging.Logger:
        if cls._logger is None:
            cls()  # 调用 __new__ 和 __init__，完成初始化
        return cls._logger


# 提供全局 logger 对象，避免每次调用 get_logger
logger = Logger.get_logger()

# 示例用法
if __name__ == '__main__':
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
