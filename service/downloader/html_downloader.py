import hashlib
import os.path

import requests
import time

from fake_useragent import UserAgent
from requests.exceptions import RequestException

from utils.data import resolve_data_path
from utils.logger import logger


class HTMLDownloader:
    def __init__(self, retry_count: int = 3):
        """
        初始化 HTML 下载器
        :param retry_count: 下载失败时的重试次数
        """
        self.retry_count = retry_count
        self.ua = UserAgent()

    def get_requests_configs(self) -> dict:
        """
        获取请求配置，包括 headers 和 proxies 等
        :return: 配置字典
        """
        return {
            'headers': {
                'User-Agent': self.ua.random
            },
            # 禁用系统代理
            'proxies': {
                'http': None,
                'https': None
            },
            'timeout': 10,
        }

    def download(self, url: str) -> str or None:
        """
        下载网页内容
        :param url: 网页 URL
        :return: 网页内容，下载失败时返回 None
        """
        attempt = 0
        while attempt < self.retry_count:
            try:
                logger.info(f"第 {attempt + 1} 次尝试下载 {url}")
                response = requests.get(url, **self.get_requests_configs())
                if response.status_code == 200:
                    logger.info(f"下载 {url} 成功")
                    return response.text
                else:
                    logger.error(f"下载 {url} 时发生错误: HTTP {response.status_code}")
            except RequestException as e:
                logger.error(f"下载 {url} 时发生错误: {e}")
            attempt += 1
            time.sleep(1)  # 避免过于频繁的请求
        logger.error(f"{self.retry_count} 次重试后仍无法下载 {url}")
        return None


def main():
    downloader = HTMLDownloader()
    url = 'https://blog.csdn.net/qq_29997037/article/details/118562651'
    dir_path = resolve_data_path("./csdn-html/")
    md5_hash = hashlib.md5()
    md5_hash.update(url.encode('utf-8'))
    file_path = os.path.join(dir_path, f'csdn-{md5_hash.hexdigest()}.html')
    if not os.path.exists(file_path):
        content = downloader.download(url)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    logger.info(f"网页内容已保存到 {file_path}")


if __name__ == '__main__':
    main()
