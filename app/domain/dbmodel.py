from abc import ABC, abstractmethod
from datetime import datetime, timezone
from uuid import uuid4


class DBModel(ABC):
    def __init__(
        self, id: str = None, created_at: datetime = None, updated_at: datetime = None
    ):
        self.__id = id or str(uuid4())
        self.__created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    @property
    def id(self):
        return self.__id

    @property
    def created_at(self):
        return self.__created_at

    @abstractmethod
    def to_dict(self):
        pass
