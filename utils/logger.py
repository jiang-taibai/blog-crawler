import logging
import os
from datetime import datetime


class Logger:
    _instance = None
    _logger = None
    _initialized = False  # 确保只初始化一次

    def __new__(cls, log_file: str = None, console_level: int = logging.INFO, file_level: int = logging.DEBUG):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_file: str = None, console_level: int = logging.INFO, file_level: int = logging.DEBUG):
        if Logger._initialized:
            return

        Logger._logger = logging.getLogger("UnifiedLogger")
        Logger._logger.setLevel(logging.DEBUG)  # 设置基础日志级别

        # 控制台输出
        if not Logger._logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(console_level)
            console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
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
            file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_format)
            Logger._logger.addHandler(file_handler)

        Logger._initialized = True

    @classmethod
    def get_logger(cls):
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