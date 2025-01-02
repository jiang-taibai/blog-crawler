from service.downloader.html_downloader import HTMLDownloader
from service.downloader.image_downloader import CSDNImageDownloader
from service.parser.csdn_parser import CSDNContentParser
from service.persistence.persistence import OASystemPersistence
from service.scheduler.url_base_scheduler import URLScheduler, URLProducer, URLConsumer

from utils.logger import logger


class CSDNURLProducer(URLProducer):
    def __init__(self, url_scheduler: URLScheduler):
        super().__init__(scheduler=url_scheduler, task_type='CSDN-URL')
        self.urls = [
            'https://blog.csdn.net/qq_29997037/article/details/118562651',
        ]
        self.index = 0

    def _generate_url(self):
        url = self.urls[self.index]
        self.index += 1
        if self.index >= len(self.urls):
            self.stop()
        return url


class CSDNURLConsumer(URLConsumer):
    def __init__(self, url_scheduler: URLScheduler):
        super().__init__(scheduler=url_scheduler, task_type='CSDN-URL')
        self.persistence = OASystemPersistence()
        self.html_downloader = HTMLDownloader()
        self.image_downloader = CSDNImageDownloader()
        self.parser = CSDNContentParser(self.persistence, self.image_downloader)

    def _process_url(self, url):
        logger.info(f"开始处理CSDN博客: {url}")
        html_content = self.html_downloader.download(url)
        if html_content:
            result = self.parser.parse(html_content, url=url)
            self.persistence.save_article(
                title=result['title'],
                cover=result['cover'],
                content=result['html'],
                category='编程开发',
                brief=result['brief'],
                urls=result['image_urls']
            )
            logger.info(f"CSDN博客爬取成功: {url}")
        else:
            logger.error(f"CSDN博客爬取失败: {url}")
