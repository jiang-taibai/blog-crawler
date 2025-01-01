import logging
import os
from datetime import datetime


class Logger:
    _instance = None
    _logger = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_file: str = None, level: int = logging.INFO):
        if hasattr(self, '_initialized') and self._initialized:
            return

        self._logger = logging.getLogger("UnifiedLogger")
        self._logger.setLevel(level)

        # 防止重复添加 handler
        if not self._logger.handlers:
            # 控制台输出
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(console_format)
            self._logger.addHandler(console_handler)

            # 文件输出
            if log_file is None:
                log_dir = os.path.join(os.getcwd(), 'logs')
                os.makedirs(log_dir, exist_ok=True)
                log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y-%m-%d')}.log")

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_format)
            self._logger.addHandler(file_handler)

        self._initialized = True

    @classmethod
    def get_logger(cls):
        if cls._logger is None:
            cls()
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
