from service.downloader.image_downloader import CSDNImageDownloader, ImageDownloader
from service.parser.parser import ContentParser
from bs4 import BeautifulSoup

from service.persistence.persistence import Persistence
from utils.logger import logger


class CSDNContentParser(ContentParser):
    def __init__(self,
                 uploader: Persistence,
                 image_downloader: ImageDownloader = CSDNImageDownloader()):
        """
        初始化 CSDN 内容解析器
        """
        self.uploader = uploader
        self.image_downloader = image_downloader
        super().__init__()

    def parse(self, content: str) -> dict:
        """
        解析 HTML，提取文章标题、封面、内容、简介和图片链接。
        统一使用 OA 系统的图片上传接口上传图片。
        :param content: HTML 内容
        :return: 解析结果
        """
        soup = BeautifulSoup(content, 'html.parser')

        # 1. 获取 id="content_views" 的内容
        content_views_element = soup.find(id='content_views')
        if not content_views_element:
            logger.error("在解析 HTML 时，未找到 id='content_views' 的文章内容元素")
            raise Exception("未找到文章内容")
        # 2. 获取标题
        title_element = soup.find(id='articleContentId')
        if not title_element:
            logger.error("在解析 HTML 时，未找到 id='articleContentId' 的文章标题元素")
            raise Exception("未找到文章标题")
        title = title_element.get_text()

        # 3. 获取文章前 100 个字符作为简介
        brief = content_views_element.get_text()[:100]

        # 4. 遍历所有 img 标签，转换 src 属性，返回图片链接列表
        image_urls = self.image_mirror_storage(content_views_element)

        # 5. 添加转载声明
        self.add_repost_notice(soup, content_views_element)

        # 6. 获取封面图片
        cover = self.get_cover(content_views_element)

        return dict(
            title=title,
            cover=cover,
            html=content_views_element.decode_contents(),  # 返回标签内部的 HTML 内容
            brief=brief,
            image_urls=image_urls
        )

    def image_mirror_storage(self, content_views_element: BeautifulSoup) -> list:
        """
        将文章图片镜像存储
        :param content_views_element: 文章内容元素
        :return: 转换后的图片链接列表
        """
        image_urls = []
        images = content_views_element.find_all('img')
        for img in images:
            original_src = img.get('src', '')
            if original_src:
                try:
                    img_data = self.image_downloader.download_image(original_src)
                    upload_response = self.uploader.upload(img_data)
                    if upload_response and upload_response.get('code') == 200:
                        new_src = upload_response.get('data').get('url')
                        img['src'] = new_src
                        logger.info(f"图片转换成功: {original_src} -> {new_src}")
                except Exception as e:
                    logger.error(f"图片镜像存储过程中下载/上传图片失败: {e}")
                image_urls.append(img['src'])
        return image_urls

    @staticmethod
    def add_repost_notice(soup: BeautifulSoup, content_views_element: BeautifulSoup) -> BeautifulSoup:
        """
        在 content_views 中添加转载声明，在文章中获取 URL 和 Creative Commons 信息。
        样例：
                <div class="slide-content-box">
                    <div class="article-copyright">
                        <div class="creativecommons">
                            本作品采用「署名 - 非商业性使用 - 禁止演绎 4.0 国际版」许可协议进行许可。
                        </div>
                        <div class="article-source-link">
                            本文链接：<a href="https://blog.csdn.net/qq_29997037/article/details/138949768" target="_blank">https://blog.csdn.net/qq_29997037/article/details/138949768</a>
                        </div>
                    </div>
                </div>
        :param soup: BeautifulSoup 对象
        :param content_views_element: 文章内容元素
        :return: 修改后的 soup 对象
        """
        article_copyright_element = soup.find(class_='article-copyright')
        if article_copyright_element:
            logger.warning("版权声明不存在，跳过添加")
            return soup

        # 获取文章链接
        article_link_tag = article_copyright_element.find('a', href=True)
        article_link = article_link_tag['href'] if article_link_tag else "#"

        # 获取 Creative Commons 信息
        creative_commons_tag = article_copyright_element.find(class_='creativecommons')
        creative_commons = creative_commons_tag.text.strip() if creative_commons_tag else "未提供许可信息"

        # 创建新的转载声明节点
        repost_notice_html = f'''
            <hr/>
            <p>本文转载自：<a href="{article_link}" target="_blank">{article_link}</a></p>
            <p>版权信息：{creative_commons}</p>
        '''

        repost_notice = BeautifulSoup(repost_notice_html, 'html.parser')
        content_views_element.append(repost_notice)
        logger.info("转载声明已添加到 content_views")
        return soup

    def get_cover(self, content_views_element: BeautifulSoup) -> str or None:
        """
        从文章内容中获取第一张图片作为封面图片
        :param content_views_element: 文章内容元素
        :return: 封面图片链接
        """
        cover = content_views_element.find('img')
        try:
            img_data = self.image_downloader.download_image(cover['src'])
            upload_response = self.uploader.upload(img_data)
            if upload_response and upload_response.get('code') == 200:
                cover_src = upload_response.get('data').get('url')
                return cover_src
        except Exception as e:
            logger.error(f"下载/上传封面图片失败: {e}")
            return None
        return None
