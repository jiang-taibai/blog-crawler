from service.scheduler.url_base_csdn_scheduler import CSDNURLProducer, CSDNURLConsumer
from service.scheduler.url_base_scheduler import URLScheduler
from utils.logger import logger


def main():
    scheduler = URLScheduler()
    producer = CSDNURLProducer(scheduler)
    consumer = CSDNURLConsumer(scheduler)
    scheduler.start()
    producer.start()
    consumer.start()

    scheduler.join()
    producer.join()
    consumer.join()

    logger.info('爬虫结束')


if __name__ == '__main__':
    main()
