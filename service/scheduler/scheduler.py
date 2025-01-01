import queue
import threading
import time
import random
from abc import ABC, abstractmethod
from typing import final


class URLTask:
    def __init__(self, url, task_type):
        self.url = url
        self.task_type = task_type


class URLScheduler:
    """
    URL调度器，用于管理URL队列和已访问URL集合，单例模式，使用 URLScheduler() 获取实例
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(URLScheduler, cls).__new__(cls)
                cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.url_queue = queue.Queue()  # 阻塞队列
        self.visited_urls = set()  # 已访问URL集合
        self.lock = threading.Lock()
        self.running = True
        self.__initialized = True

    def add_url(self, url, task_type):
        """添加新的URL到队列中"""
        with self.lock:
            if url not in self.visited_urls:
                self.url_queue.put(URLTask(url, task_type))

    def get_url(self, task_type):
        """从队列中获取URL"""
        try:
            url_task = self.url_queue.get(block=True, timeout=5)  # 阻塞获取URL
            if task_type and url_task.task_type != task_type:
                self.url_queue.put(url_task)
                return None
            with self.lock:
                self.visited_urls.add(url_task.url)
            return url_task
        except queue.Empty:
            return None

    def stop(self):
        """停止调度器"""
        self.running = False


class URLProducer(threading.Thread, ABC):
    def __init__(self, task_type='DEFAULT'):
        super().__init__()
        self.scheduler = URLScheduler()
        self.task_type = task_type
        self.running = True

    @final
    def _add_url(self, url):
        self.scheduler.add_url(url, self.task_type)

    @abstractmethod
    def _generate_url(self):
        raise NotImplementedError('请在子类中实现该方法')

    def stop(self):
        self.running = False

    @final
    def run(self):
        while self.running and self.scheduler.running:
            url = self._generate_url()
            if url:
                self._add_url(url)
                time.sleep(random.randint(1, 3))


class URLConsumer(threading.Thread, ABC):
    def __init__(self, task_type='DEFAULT'):
        super().__init__()
        self.scheduler = URLScheduler()
        self.task_type = task_type
        self.running = True

    @final
    def _get_url(self):
        return self.scheduler.get_url(self.task_type)

    @abstractmethod
    def _process_url(self, url):
        raise NotImplementedError('请在子类中实现该方法')

    def stop(self):
        self.running = False

    @final
    def run(self):
        while self.running and self.scheduler.running or not self.scheduler.url_queue.empty():
            url = self._get_url()
            if url:
                self._process_url(url.url)


def main():
    producer = URLProducer()
    consumer = URLConsumer()

    producer.start()
    consumer.start()

    producer.join()
    consumer.join()

    print("[Scheduler Stopped]")


if __name__ == '__main__':
    main()
