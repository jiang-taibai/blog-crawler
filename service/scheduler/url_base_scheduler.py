import queue
import time
from abc import abstractmethod, ABC

from service.scheduler.scheduler import BaseScheduler, BaseProducer, BaseConsumer
from utils.logger import logger


class Task:
    def __init__(self, url, task_type):
        self.url = url
        self.task_type = task_type


class URLScheduler(BaseScheduler):
    """具体URL调度器逻辑，由子类扩展"""
    pass


class URLProducer(BaseProducer):
    def __init__(self, scheduler: BaseScheduler, task_type='DEFAULT_URL'):
        super().__init__(scheduler=scheduler, task_type=task_type)

    def _generate_url(self):
        return f"https://example.com/{time.time()}"

    def run(self):
        while self.running and self.scheduler.running:
            url = self._generate_url()
            self.scheduler.task_queues[self.task_type].put(Task(url, self.task_type))
            logger.info(f"生成 URL: {url}")
            time.sleep(1)
        self.stop()


class URLConsumer(BaseConsumer):
    def __init__(self, scheduler: BaseScheduler, task_type='DEFAULT_URL'):
        super().__init__(scheduler=scheduler, task_type=task_type)

    def _process_url(self, url):
        logger.info(f"处理 URL: {url}")

    def run(self):
        while self.running and self.scheduler.running:
            try:
                task = self.scheduler.task_queues[self.task_type].get(timeout=1)
                self._process_url(task.url)
            except queue.Empty:
                pass
        self.stop()


"""
2025-01-02 14:11:11,461 - INFO - 生成 URL: https://example.com/1735798271.4619803
2025-01-02 14:11:11,461 - INFO - 获取到 URL: https://example.com/1735798271.4619803
...................................................................................
2025-01-02 14:11:20,517 - INFO - 生成 URL: https://example.com/1735798280.5171666
2025-01-02 14:11:20,517 - INFO - 获取到 URL: https://example.com/1735798280.5171666
2025-01-02 14:11:21,475 - INFO - Producer example 已停止
2025-01-02 14:11:22,525 - INFO - BaseScheduler 已停止
2025-01-02 14:11:23,532 - INFO - Consumer example 已停止
2025-01-02 14:11:23,532 - INFO - 主函数执行完毕
"""


def main():
    scheduler = URLScheduler()
    producer = URLProducer(scheduler, task_type='example')
    consumer = URLConsumer(scheduler, task_type='example')

    scheduler.start()
    producer.start()
    consumer.start()

    time.sleep(10)
    producer.stop()

    scheduler.join()
    producer.join()
    consumer.join()

    logger.info("主函数执行完毕")


if __name__ == '__main__':
    main()
