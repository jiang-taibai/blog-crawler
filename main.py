from service.scheduler.url_csdn_scheduler import CSDNURLProducer, CSDNURLConsumer
from service.scheduler.url_base_scheduler import URLScheduler


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

    print('爬虫结束')


if __name__ == '__main__':
    main()
