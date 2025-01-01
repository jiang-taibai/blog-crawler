from abc import ABC, abstractmethod


class Uploader(ABC):
    def __init__(self, upload_url: str):
        """初始化文件上传器，指定上传接口 URL"""
        self.upload_url = upload_url
        print(f"[Initialized Uploader] Upload URL: {self.upload_url}")

    @abstractmethod
    def upload(self, file):
        """抽象方法，上传文件或二进制内容"""
        pass
