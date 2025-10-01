from abc import ABC
from datetime import datetime, timezone
from uuid import uuid4


class DBModel(ABC):
    def __init__(self):
        self.__id = str(uuid4())
        self.__created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    @property
    def id(self):
        return self.__id

    @property
    def created_at(self):
        return self.__created_at
