import os

import requests

from service.downloader.image_downloader import CSDNImageDownloader
from service.uploader.uploader import Uploader
from utils.config import get_system_config


class OASystemUploader(Uploader):
    def __init__(self):
        upload_url = get_system_config('OASystem', 'UploadURL')
        super().__init__(upload_url)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'Authorization': get_system_config('OASystem', 'Authorization')
        }

    def upload(self, file):
        """上传文件到 HTTP 接口，支持文件路径或二进制内容"""
        if isinstance(file, str):
            if not os.path.isfile(file):
                raise FileNotFoundError(f"File not found: {file}")
            with open(file, 'rb') as f:
                files = {'file': (os.path.basename(file), f)}
                response = requests.post(self.upload_url, headers=self.headers, files=files)
        elif isinstance(file, bytes):
            files = {'file': ('uploaded_image.jpg', file)}
            response = requests.post(self.upload_url, headers=self.headers, files=files)
        else:
            raise TypeError("Unsupported file type. Expected file path (str) or binary content (bytes).")

        if response.status_code == 200:
            print(f"[Success] File uploaded successfully")
            return response.json()
        else:
            raise Exception(f"[Failed] Upload failed with status code {response.status_code}: {response.text}")


def main():
    downloader = CSDNImageDownloader()
    uploader = OASystemUploader()
    image_url = 'https://i-blog.csdnimg.cn/blog_migrate/025552595da297ab543e3b3e463c73d8.png#pic_center'
    file = downloader.download_image(image_url)
    try:
        response = uploader.upload(file)
        print(response)
    except Exception as e:
        print(f"[Error] {e}")


# 示例用法
if __name__ == '__main__':
    main()
