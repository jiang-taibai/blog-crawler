import os.path

import requests
import time
from requests.exceptions import RequestException

from utils.data import resolve_data_path
from utils.logger import logger


class HTMLDownloader:
    def __init__(self):
        self.session = requests.Session()
        self.retry_count = 3
        self.timeout = 5
        self.__initialized = True
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }
        self.proxies = {'http': None, 'https': None}  # 禁用系统代理

    def download(self, url):
        """下载网页内容，处理超时和重试逻辑"""
        attempt = 0
        while attempt < self.retry_count:
            try:
                logger.info(f"第 {attempt + 1} 次尝试下载 {url}")
                response = self.session.get(
                    url,
                    timeout=self.timeout,
                    headers=self.headers,
                    proxies=self.proxies
                )
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
    url = 'https://blog.csdn.net/qq_29997037/article/details/138949768'
    content = downloader.download(url)
    dir_path = resolve_data_path("./csdn-html/")
    with open(os.path.join(dir_path, 'csdn.html'), 'w', encoding='utf-8') as file:
        file.write(content)
    print("下载完成")


if __name__ == '__main__':
    main()
