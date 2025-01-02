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

    def parse(self, content: str, **kwargs) -> dict:
        """
        解析 HTML，提取文章标题、封面、内容、简介和图片链接。
        统一使用 OA 系统的图片上传接口上传图片。
        :param content: HTML 内容
        :return: 解析结果
        """
        # 1. 初始化
        soup, content_views_element = self.init(content, **kwargs)

        # 2. 获取标题
        title = self.get_title(soup)

        # 3. 获取文章前 100 个字符作为简介
        brief = content_views_element.get_text()[:100]

        # 4. 遍历所有 img 标签，转换 src 属性，返回图片链接列表
        image_urls = self.image_mirror_storage(content_views_element)

        # 5. 添加转载声明
        blog_url = kwargs['url'] if 'url' in kwargs else None
        self.add_repost_notice(soup, content_views_element, blog_url)

        # 6. 获取封面图片
        cover = self.get_cover(content_views_element)

        # 7. 代码块优化
        self.parse_code(content_views_element)

        return dict(
            title=title,
            cover=cover,
            html=content_views_element.decode_contents(),  # 返回标签内部的 HTML 内容
            brief=brief,
            image_urls=image_urls
        )

    @staticmethod
    def init(content: str, **kwargs):
        soup = BeautifulSoup(content, 'html.parser')

        # 1. 获取 id="content_views" 的内容
        content_views_element = soup.find(id='content_views')
        if not content_views_element:
            logger.error("在解析 HTML 时，未找到 id='content_views' 的文章内容元素")
            raise Exception("未找到文章内容")
        return soup, content_views_element

    def image_mirror_storage(self, content_views_element: BeautifulSoup) -> list:
        """
        将文章图片镜像存储
        :param content_views_element: 文章内容元素
        :return: 转换后的图片链接列表
        """
        image_urls = []
        images = content_views_element.find_all('img')
        for img in images:
            original_src = img.get('src', None)
            if original_src:
                try:
                    img_data = self.image_downloader.download_image(original_src)
                    upload_response = self.uploader.upload_image(img_data)
                    if upload_response and upload_response.get('code') == 200:
                        new_src = upload_response.get('data').get('url')
                        img['src'] = new_src
                        logger.info(f"图片转换成功: {original_src} -> {new_src}")
                except Exception as e:
                    logger.error(f"图片镜像存储过程中下载/上传图片失败: {e}")
                image_urls.append(img['src'])
        return image_urls

    @staticmethod
    def add_repost_notice(soup: BeautifulSoup, content_views_element: BeautifulSoup, url: str) -> BeautifulSoup:
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
        :param url:  文章链接
        :return: 修改后的 soup 对象
        """
        article_copyright_element = soup.find(class_='article-copyright')
        article_link = url
        if article_copyright_element:
            # 获取 Creative Commons 信息
            creative_commons_tag = article_copyright_element.find(class_='creativecommons')
            creative_commons = creative_commons_tag.text.strip() if creative_commons_tag else "暂未提供许可信息"
            logger.info("获取版权声明成功")
        elif url:
            logger.info("版权声明不存在，使用文章链接作为转载声明")
            creative_commons = "暂未提供许可信息"
        else:
            logger.warning("版权声明不存在，且文章链接未提供，无法生成转载声明")
            return soup

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
        covers = content_views_element.find_all('img')
        for cover in covers:
            if not cover or not cover.get('src'):
                continue
            try:
                img_data = self.image_downloader.download_image(cover.get('src'))
                upload_response = self.uploader.upload_image(img_data)
                if upload_response and upload_response.get('code') == 200:
                    cover_src = upload_response.get('data').get('url')
                    return cover_src
            except Exception as e:
                logger.info(f"下载/上传封面图片失败: {e}")
        logger.info("文章中未出现图片，不使用封面")
        return None

    @staticmethod
    def parse_code(content_views_element: BeautifulSoup) -> BeautifulSoup:
        """
        解析代码块，提取纯文本代码，保留代码格式
        例如将以下爬取的代码块：

        <pre><code class="prism language-java"><span class="token keyword">public</span> <span class="token keyword">class</span> <span class="token class-name">HelloWorld</span> <span class="token punctuation">{<!-- --></span>
            <span class="token keyword">public</span> <span class="token keyword">static</span> <span class="token keyword">void</span> <span class="token function">main</span><span class="token punctuation">(</span><span class="token class-name">String</span><span class="token punctuation">[</span><span class="token punctuation">]</span> args<span class="token punctuation">)</span> <span class="token punctuation">{<!-- --></span>
                <span class="token class-name">System</span><span class="token punctuation">.</span>out<span class="token punctuation">.</span><span class="token function">println</span><span class="token punctuation">(</span><span class="token string">&#34;Hello, World!&#34;</span><span class="token punctuation">)</span><span class="token punctuation">;</span>
            <span class="token punctuation">}</span>
        <span class="token punctuation">}</span>
        </code></pre>

        转换成：

        <pre><code class="language-java">public class HelloWorld {
            public static void main(String[] args) {
                System.out.println("Hello, World!");
            }
        }</code></pre>

        :param content_views_element: 文章内容元素
        :return: 转换后的 soup 对象
        """
        code_elements = content_views_element.findAll('code')
        for code_element in code_elements:
            # 1. 提取纯文本内容，去除标签
            clean_code = code_element.get_text('', strip=False)
            clean_code = '\r\n'.join(line for line in clean_code.splitlines())
            code_element.string = clean_code
            # 2. 清除 code 标签多余的类名，只保留 language-xxx
            if 'class' not in code_element.attrs:
                continue
            for class_name in code_element['class']:
                if 'language-' not in class_name:
                    code_element['class'].remove(class_name)
        return content_views_element

    @staticmethod
    def get_title(soup: BeautifulSoup) -> str:
        """
        获取文章标题
        :param soup: BeautifulSoup 对象
        :return: 文章标题
        """
        title_wrapper_element = soup.find(id='articleContentId')
        if not title_wrapper_element:
            logger.info("在解析 HTML 时，未找到 id='articleContentId' 的文章标题元素，使用默认标题")
            return "暂无标题"
        tit_element = title_wrapper_element.find(class_='tit')
        if not tit_element:
            logger.info("在解析 HTML 时，未找到 class='tit' 的文章标题元素，也许是转载文章，尝试获取转载文章标题")
            title = title_wrapper_element.get_text().strip()
            if not title:
                logger.info("在解析 HTML 时，未找到 class='tit' 的文章标题元素，使用默认标题")
                return "暂无标题"
            return title
        return tit_element.get_text()
