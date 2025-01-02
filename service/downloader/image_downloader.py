from abc import ABC, abstractmethod
import requests
import os

from fake_useragent import UserAgent

from utils.data import resolve_data_path


class ImageDownloader(ABC):
    def __init__(self, save_dir: str):
        """
        初始化图片下载器，指定保存路径
        注意，save_dir 为相对数据目录的路径，如 './example'，会自动转换为 $PROJECT_ROOT/data/example
        """
        self.save_dir = resolve_data_path(save_dir)
        os.makedirs(self.save_dir, exist_ok=True)

    @abstractmethod
    def download_image(self, url: str, filename: str = None) -> bytes:
        """
        下载图片并保存到本地，返回图片的二进制内容，下载失败时抛出异常
        :param url: 图片 URL
        :param filename: 保存的文件名，如不提供则不保存
        """
        pass


class CSDNImageDownloader(ImageDownloader):
    def __init__(self):
        super().__init__(save_dir='./csdn_images')
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

    def download_image(self, url: str, filename: str = None) -> bytes:
        """
        下载 CSDN 图片并保存到本地，返回图片的二进制内容，下载失败时抛出异常
        :param url: 图片 URL
        :param filename: 保存的文件名，如不提供则不保存
        """
        response = requests.get(url, **self.get_requests_configs())
        if response.status_code == 200:
            if filename:
                file_path = os.path.join(self.save_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            return response.content
        else:
            raise Exception(f"图片下载失败, HTTP 状态码: {response.status_code}")


def main():
    downloader = CSDNImageDownloader()
    image_url = 'https://i-blog.csdnimg.cn/blog_migrate/025552595da297ab543e3b3e463c73d8.png#pic_center'
    image_bytes = downloader.download_image(image_url, 'sample_image2.jpg')


# 示例用法
if __name__ == '__main__':
    main()
