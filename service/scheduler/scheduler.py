import queue
import threading
import time
from abc import ABC, abstractmethod
from typing import Dict, Set, List

from utils.logger import logger


class BaseScheduler(threading.Thread, ABC):
    """基础调度器，负责管理队列、生产者、消费者和自监听停止条件"""

    def __init__(self):
        super().__init__()
        self.task_queues: Dict[str, queue.Queue] = {}
        self.visited_tasks: Set[str] = set()
        self.producers: List[threading.Thread] = []
        self.consumers: List[threading.Thread] = []
        self.lock = threading.Lock()
        self.running = True
        self.daemon = True

    def register_task_type(self, task_type: str):
        with self.lock:
            if task_type not in self.task_queues:
                self.task_queues[task_type] = queue.Queue()

    def register_producer(self, producer: threading.Thread):
        with self.lock:
            self.producers.append(producer)

    def register_consumer(self, consumer: threading.Thread):
        with self.lock:
            self.consumers.append(consumer)

    def stop(self):
        logger.info("BaseScheduler 已停止")
        self.running = False

    def run(self):
        while self.running:
            time.sleep(1)
            with self.lock:
                if not any(p.is_alive() for p in self.producers) and all(q.empty() for q in self.task_queues.values()):
                    self.stop()


class BaseProducer(threading.Thread, ABC):
    """基础生产者，负责注册到调度器"""

    def __init__(self, scheduler: BaseScheduler, task_type='DEFAULT'):
        super().__init__()
        self.scheduler = scheduler
        self.task_type = task_type
        self.scheduler.register_task_type(self.task_type)
        self.scheduler.register_producer(self)
        self.running = True

    def stop(self):
        if self.running:
            logger.info(f"Producer {self.task_type} 已停止")
            self.running = False

    @abstractmethod
    def run(self):
        while self.running and self.scheduler.running:
            logger.info(f"生成 {self.task_type} 的任务")
            time.sleep(1)


class BaseConsumer(threading.Thread, ABC):
    """基础消费者，负责注册到调度器"""

    def __init__(self, scheduler: BaseScheduler, task_type='DEFAULT'):
        super().__init__()
        self.scheduler = scheduler
        self.task_type = task_type
        self.scheduler.register_task_type(self.task_type)
        self.scheduler.register_consumer(self)
        self.running = True

    def stop(self):
        if self.running:
            logger.info(f"Consumer {self.task_type} 已停止")
            self.running = False

    @abstractmethod
    def run(self):
        while self.running and self.scheduler.running:
            try:
                task = self.scheduler.task_queues[self.task_type].get(timeout=1)
                logger.info(f"获取到 {self.task_type} 的任务")
            except queue.Empty:
                pass
