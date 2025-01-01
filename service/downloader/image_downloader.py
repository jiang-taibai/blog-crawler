from abc import ABC, abstractmethod
import requests
import os

from utils.data import resolve_data_path


class ImageDownloader(ABC):
    def __init__(self, save_dir: str):
        """初始化图片下载器，指定保存路径"""
        self.save_dir = resolve_data_path(save_dir)
        os.makedirs(self.save_dir, exist_ok=True)
        print(f"[Initialized] Save Directory: {self.save_dir}")

    @abstractmethod
    def download_image(self, url: str, filename: str):
        """抽象方法，下载图片并保存到指定路径"""
        pass


class CSDNImageDownloader(ImageDownloader):
    def __init__(self, save_dir: str = './csdn_images'):
        super().__init__(save_dir)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
        }
        self.proxies = {'http': None, 'https': None}

    def download_image(self, url: str, filename: str = None):
        """下载 CSDN 图片并保存到本地"""
        response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
        if response.status_code == 200:
            if filename:
                file_path = os.path.join(self.save_dir, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            return response.content
        else:
            raise Exception(f"Failed to download image, HTTP status code: {response.status_code}")


# 示例用法
if __name__ == '__main__':
    downloader = CSDNImageDownloader()
    image_url = 'https://i-blog.csdnimg.cn/blog_migrate/025552595da297ab543e3b3e463c73d8.png#pic_center'
    downloader.download_image(image_url, 'sample_image2.jpg')
