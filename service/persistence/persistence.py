from abc import ABC, abstractmethod


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
    def upload_image(self, file: str or bytes) -> dict:
        """
        上传文件到数据库
        :param file: 文件路径或二进制内容
        :return:    上传结果，应当是 {code: int, message: str, data: {url: str}} 的形式
        """
        pass
