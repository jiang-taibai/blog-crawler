from service.downloader.html_downloader import HTMLDownloader
from service.downloader.image_downloader import CSDNImageDownloader
from service.parser.csdn_parser import CSDNContentParser
from service.persistence.persistence import OASystemPersistence
from service.scheduler.scheduler import URLProducer, URLConsumer
from utils.logger import logger


class CSDNURLProducer(URLProducer):
    def __init__(self):
        super().__init__(task_type='CSDN')
        self.urls = [
            "https://blog.csdn.net/southink/article/details/136050254",
            "https://blog.csdn.net/xqdd/article/details/144666427",
            "https://blog.csdn.net/yelangkingwuzuhu/article/details/144494609",
            "https://blog.csdn.net/nemoiu/article/details/143792588",
            "https://blog.csdn.net/qq_28419035/article/details/141822578",
            "https://blog.csdn.net/qq_34272964/article/details/144067757",
            "https://blog.csdn.net/littlefun591/article/details/144204091",
            "https://blog.csdn.net/yx13186308025/article/details/135518317",
            "https://blog.csdn.net/cuclife/article/details/144090100",

            "https://blog.csdn.net/zhengzhaoyang122/article/details/144477149",
            "https://blog.csdn.net/senllang/article/details/144131024",
            "https://blog.csdn.net/yelangkingwuzuhu/article/details/144201649",
            "https://blog.csdn.net/2202_76097976/article/details/144144722",
            "https://blog.csdn.net/qq_32682301/article/details/144022495",
            "https://blog.csdn.net/2301_80374809/article/details/143109589",
            "https://blog.csdn.net/mss359681091/article/details/144471082",
            "https://blog.csdn.net/2301_81253185/article/details/144653478",
            "https://blog.csdn.net/penggerhe/article/details/135367769",
            "https://blog.csdn.net/2301_76161469/article/details/143241972",
            "https://blog.csdn.net/weixin_51360584/article/details/128098109",

        ]
        self.index = 0

    def _generate_url(self):
        url = self.urls[self.index]
        self.index += 1
        if self.index >= len(self.urls):
            self.stop()
        return url


class CSDNURLConsumer(URLConsumer):
    def __init__(self):
        super().__init__(task_type='CSDN')
        self.persistence = OASystemPersistence()
        self.html_downloader = HTMLDownloader()
        self.image_downloader = CSDNImageDownloader()
        self.parser = CSDNContentParser(self.persistence, self.image_downloader)

    def _process_url(self, url):
        logger.info(f"开始处理CSDN博客: {url}")
        html_content = self.html_downloader.download(url)
        if html_content:
            result = self.parser.parse(html_content)
            self.persistence.save_article(
                title=result['title'],
                cover=result['cover'],
                content=result['html'],
                category='编程开发',
                brief=result['brief'],
                urls=result['image_urls']
            )
            logger.info(f"下载成功: {url}")
        else:
            logger.error(f"下载失败: {url}")
