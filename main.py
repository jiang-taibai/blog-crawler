from service.persistence.local_persistence import LocalPersistence
from service.persistence.oa_system_persistence import OASystemPersistence
from service.scheduler.url_base_csdn_scheduler import CSDNURLProducer, CSDNURLConsumer
from service.scheduler.url_base_scheduler import URLScheduler
from utils.logger import logger


def main():
    scheduler = URLScheduler()
    # 使用 OASystem 进行存储，适用 OASystem 内部人员
    # persistence = OASystemPersistence()
    # 使用本地存储服务进行测试，适用所有人
    persistence = LocalPersistence()
    producer = CSDNURLProducer(url_scheduler=scheduler)
    consumer = CSDNURLConsumer(url_scheduler=scheduler, persistence=persistence)
    scheduler.start()
    producer.start()
    consumer.start()

    scheduler.join()
    producer.join()
    consumer.join()

    logger.info('爬虫结束')


if __name__ == '__main__':
    main()
