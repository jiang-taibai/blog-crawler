import json
import os


def load_system_config():
    """加载系统配置"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(base_dir, '../config.json')
    with open(config_file, 'r', encoding='utf-8') as file:
        config = json.load(file)
    return config


def get_system_config(*keys: str) -> str:
    """
    安全地从 JSON 数据中获取值。

    :param keys: 一系列按顺序访问的键
    :return: 获取到的值或默认值
    """
    try:
        value = load_system_config()
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                raise KeyError()
        return value
    except (TypeError, KeyError):
        print(f"[错误] 无法找到系统配置项: {keys}")
        return ''
