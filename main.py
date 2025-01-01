from service.scheduler.csdn_scheduler import CSDNURLProducer, CSDNURLConsumer


def main():
    url_producer = CSDNURLProducer()
    url_consumer = CSDNURLConsumer()
    url_producer.start()
    url_consumer.start()

    url_producer.join()
    url_consumer.join()

    print('爬虫结束')


if __name__ == '__main__':
    main()
