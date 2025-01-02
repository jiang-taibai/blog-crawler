import os
from abc import ABC, abstractmethod
import requests
from fake_useragent import UserAgent

from utils.config import get_system_config
from utils.logger import logger


class Persistence(ABC):
    """
    数据库持久化抽象类
    """

    def __init__(self):
        pass

    @abstractmethod
    def save_article(self, title: str, cover: str, content: str, category: str, brief: str, urls: list):
        """保存文章到数据库"""
        pass

    @abstractmethod
    def upload_image(self, file):
        """上传文件到数据库"""
        pass


class OASystemPersistence(Persistence):
    """
    使用 OA 系统的 HTTP 接口进行数据库持久化
    """

    def __init__(self):
        super().__init__()
        self.base_url = get_system_config('OASystem', 'BaseURL')
        self.upload_api_path = get_system_config('OASystem', 'UploadApiPath')
        self.add_article_api_path = get_system_config('OASystem', 'AddArticleApiPath')
        self.ua = UserAgent()

    def get_requests_configs(self) -> dict:
        """
        获取请求配置，包括 headers 和 proxies 等
        :return: 配置字典
        """
        return {
            'headers': {
                'Content-Type': 'application/json',
                'User-Agent': self.ua.random,
                'Authorization': get_system_config('OASystem', 'Authorization')
            },
            # 禁用系统代理
            'proxies': {
                'http': None,
                'https': None
            },
            'timeout': 10,
        }

    def get_file_requests_configs(self) -> dict:
        """
        获取请求配置，包括 headers 和 proxies 等
        :return: 配置字典
        """
        return {
            'headers': {
                'User-Agent': self.ua.random,
                'Authorization': get_system_config('OASystem', 'Authorization')
            },
            # 禁用系统代理
            'proxies': {
                'http': None,
                'https': None
            },
            'timeout': 10,
        }

    def save_article(self, title: str, cover: str, content: str, category: str, brief: str, urls: list):
        """保存文章到远程 HTTP 数据库接口"""
        payload = {
            'title': title,
            'cover': cover,
            'content': content,
            'category': category,
            'brief': brief,
            'urls': urls
        }
        response = requests.post(self.base_url + self.add_article_api_path, json=payload, **self.get_requests_configs())
        if response.status_code == 200 and response.json()['code'] == 200:
            logger.info(f"成功保存文章: {title}")
            return response.json()
        else:
            raise Exception(f"保存文章【{title}】失败 {response.status_code}: {response.text}")

    def upload_image(self, file):
        """上传文件到 HTTP 接口，支持文件路径或二进制内容"""
        if isinstance(file, str):
            if not os.path.isfile(file):
                logger.error(f"文件未找到: {file}")
                raise FileNotFoundError(f"文件未找到: {file}")
            with open(file, 'rb') as f:
                files = {'file': (os.path.basename(file), f)}
                response = requests.post(self.base_url + self.upload_api_path, files=files, **self.get_file_requests_configs())
        elif isinstance(file, bytes):
            files = {'file': (f'image.jpg', file)}
            response = requests.post(self.base_url + self.upload_api_path, files=files, **self.get_file_requests_configs())
        else:
            logger.error("不支持的文件类型。预期为文件路径 (str) 或二进制内容 (bytes)。")
            raise TypeError("不支持的文件类型。预期为文件路径 (str) 或二进制内容 (bytes)。")

        if response.status_code == 200:
            logger.info(f"文件上传成功")
            return response.json()
        else:
            logger.error(f"上传失败: {response.status_code}: {response.text}")
            raise Exception(f"[Failed] Upload failed with status code {response.status_code}: {response.text}")


def main():
    db_persistence = OASystemPersistence()
    try:
        response = db_persistence.save_article(
            title='My First Article',
            cover='https://example.com/cover.jpg',
            content='This is the content of the article.',
            category='Tech',
            brief='This is a brief introduction to the article.',
            urls=['https://example.com/file1.jpg', 'https://example.com/file2.jpg']
        )
        print(response)
    except Exception as e:
        print(f"[Error] {e}")


# 示例用法
if __name__ == '__main__':
    main()
