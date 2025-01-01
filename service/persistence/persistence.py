from abc import ABC, abstractmethod
import requests

from utils.config import get_system_config
from utils.logger import logger


class DatabasePersistence(ABC):
    """
    数据库持久化抽象类
    """

    def __init__(self):
        pass

    @abstractmethod
    def save_article(self, title: str, cover: str, content: str, category: str, brief: str, urls: list):
        """抽象方法，保存文章到数据库"""
        pass


class OADatabasePersistence(DatabasePersistence):
    """
    使用 OA 系统的 HTTP 接口进行数据库持久化
    """

    def __init__(self):
        super().__init__()
        self.add_article_url = get_system_config('OASystem', 'AddArticleURL')
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'Authorization': get_system_config('OASystem', 'Authorization')
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
        response = requests.post(self.add_article_url, json=payload, headers=self.headers)
        if response.status_code == 200 and response.json()['code'] == 200:
            logger.info(f"成功保存文章: {title}")
            return response.json()
        else:
            raise Exception(f"保存文章【{title}】失败 {response.status_code}: {response.text}")


def main():
    db_persistence = OADatabasePersistence()
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
