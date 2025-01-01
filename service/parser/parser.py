from abc import ABC, abstractmethod


class ContentParser(ABC):
    def __init__(self):
        """初始化解析器"""
        pass

    @abstractmethod
    def parse(self, content: str):
        """
        应该返回一个解析后的 HTML，和一个图片 URL 列表，要求图片已经被下载并上传到 MinIO 中，其他内容不做要求
        """
        pass
