import json
import os
import threading
from json import JSONEncoder

from utils.logger import logger


class Config:
    """
    单例模式配置类，负责加载和提供系统配置。
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Config, cls).__new__(cls)
                    cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.default_config = None
        self.additional_config = None
        self.load_system_config()
        self.__initialized = True

    def _deep_merge(self, source: dict, destination: dict) -> dict:
        """递归地合并两个字典，以最大化保留所有配置"""
        for key, value in source.items():
            if isinstance(value, dict) and key in destination and isinstance(destination[key], dict):
                destination[key] = self._deep_merge(value, destination[key])
            else:
                destination[key] = value
        return destination

    def load_system_config(self):
        """加载系统配置"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(base_dir, '../config/application.json')
        try:
            with open(config_file, 'r', encoding='utf-8') as file:
                self.default_config = json.load(file)
                logger.info(f"已加载系统配置文件: {os.path.normpath(config_file)}")
                logger.debug(f"系统配置项: \n{json.dumps(self.default_config, cls=JSONEncoder, indent=4)}")
                additional_config_name = self.get('Application', 'Profiles')
            if additional_config_name:
                additional_config_file = os.path.join(base_dir, f'../config/application-{additional_config_name}.json')
                if os.path.exists(additional_config_file):
                    with open(additional_config_file, 'r', encoding='utf-8') as additional_file:
                        self.additional_config = json.load(additional_file)
                        self.default_config = self._deep_merge(self.additional_config, self.default_config)
                    logger.info(f"已加载附加的配置文件: {os.path.normpath(additional_config_file)}")
                    logger.debug(f"附加配置项: \n{json.dumps(self.additional_config, cls=JSONEncoder, indent=4)}")
                    logger.debug(f"合并后的配置项: \n{json.dumps(self.default_config, cls=JSONEncoder, indent=4)}")
                else:
                    logger.warning(f"未找到附加的配置文件: {additional_config_file}")
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {config_file}")
        except json.JSONDecodeError:
            logger.error(f"配置文件解析错误: {config_file}")

    def get(self, *keys: str) -> str or None:
        """
        安全地从 JSON 数据中获取值。

        :param keys: 一系列按顺序访问的键
        :return: 获取到的值或默认值
        """
        try:
            value = self.default_config
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    raise KeyError()
            return value
        except (TypeError, KeyError):
            logger.error(f"[错误] 无法找到系统配置项: {keys}")
            return None


# 单例实例
config = Config()

if __name__ == '__main__':
    logger.info(config.get('Application', 'Profiles'))
