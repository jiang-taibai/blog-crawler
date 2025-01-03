import json
import os.path
import time
import uuid

from service.persistence.persistence import Persistence
from utils.data import resolve_data_path
from utils.utils import generate_random_string


class LocalPersistence(Persistence):
    """
    本地数据持久化服务
    """

    def __init__(self):
        super().__init__()
        work_dir = f'./local-persistence/{time.strftime("%Y%m%d%H%M%S")}-{generate_random_string()}'
        db_dir_path = resolve_data_path(f'{work_dir}')
        self.img_dir_path = resolve_data_path(f'{work_dir}/img')
        self.html_dir_path = resolve_data_path(f'{work_dir}/html')
        self.data_file_path = os.path.join(db_dir_path, f'db.json')
        with open(self.data_file_path, 'w', encoding='utf-8') as db_file:
            json.dump([], db_file)

    def save_article(self, title: str, cover: str, content: str, category: str, brief: str, urls: list):
        """
        保存文章到本地数据库
        """
        with open(self.data_file_path, 'r', encoding='utf-8') as db_file:
            try:
                data = json.load(db_file)
            except json.JSONDecodeError:
                data = []
            article_id = len(data) + 1
            article = {
                'id': article_id,
                'title': title,
                'cover': cover,
                'content': content,
                'category': category,
                'brief': brief,
                'urls': urls,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            data.append(article)
        with open(self.data_file_path, 'w', encoding='utf-8') as db_file:
            json.dump(data, db_file, ensure_ascii=False, indent=4)
        html_file_path = os.path.join(self.html_dir_path, f'{article_id}.html')
        with open(html_file_path, 'w', encoding='utf-8') as html_file:
            for url in urls:
                # 将图片链接的绝对地址替换为相对地址
                content = content.replace(url, os.path.relpath(url, os.path.dirname(html_file_path)))
            html_content = f'''<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="X-UA-Compatible" content="ie=edge">
                <title>{title}</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f4;
                    }}
                    header {{
                        background-color: #333;
                        color: white;
                        padding: 10px 0;
                        text-align: center;
                    }}
                    main {{
                        max-width: 900px;
                        margin: 20px auto;
                        padding: 20px;
                        background-color: white;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    }}
                    h1 {{
                        font-size: 2em;
                        margin-bottom: 20px;
                    }}
                    p {{
                        font-size: 1.2em;
                        color: #333;
                        line-height: 1.6;
                    }}
                    img {{
                        max-width: 100%;  /* 限制图片最大宽度为容器宽度 */
                        height: auto;     /* 保持图片的比例 */
                        display: block;   /* 使图片是块级元素，避免下面的文本环绕 */
                        margin: 0 auto;   /* 居中显示图片 */
                    }}
                </style>
            </head>
            <body>

                <header>
                    <h1>{title}</h1>
                </header>

                <main>
                    {content}
                </main>

            </body>
            </html>'''

            html_file.write(html_content)
        return {
            'code': 200,
            'message': '文章保存成功',
            'data': {'id': article_id, 'url': os.path.abspath(html_file_path)}
        }

    def upload_image(self, file: str or bytes) -> dict:
        """
        上传文件到数据库
        :param file: 文件路径或二进制内容
        :return: 上传结果，应当是 {code: int, message: str, data: {url: str}} 的形式
        """
        if isinstance(file, str) and os.path.exists(file):
            with open(file, 'rb') as f:
                content = f.read()
        elif isinstance(file, bytes):
            content = file
        else:
            return {'code': 500, 'message': '非法的文件', 'data': {}}

        file_id = uuid.uuid4()
        file_extension = os.path.splitext(file)[1] if isinstance(file, str) else '.png'
        file_name = f'{file_id}{file_extension}'
        file_path = os.path.join(self.img_dir_path, file_name)

        with open(file_path, 'wb') as img_file:
            img_file.write(content)

        return {
            'code': 200,
            'message': '文件上传成功',
            'data': {'url': os.path.abspath(file_path)}
        }
