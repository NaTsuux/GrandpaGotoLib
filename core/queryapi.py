from abc import ABC, abstractmethod
import logging
from .config import Config
from .session import Session
from .querycontent import Query


class QueryApi(ABC):
    def __init__(self):
        self.debug_level = 1
        self.config = Config()
        self.session = Session()
        self._timer = None
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    def set_timer(self, timer=None):
        self._timer = timer

    @abstractmethod
    def do_lib_status_query(self):
        pass

    @abstractmethod
    def do_seat_status_query(self, lib_id: int):
        pass

    def do_keep_alive_query(self):
        return self.session.post(Query.do_keep_alive_query())
