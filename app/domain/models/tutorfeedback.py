from typing import Optional, Literal
from datetime import datetime
import uuid

from app.domain.models.bmodel import BModel


class TutorFeedback:
    options = ["poor", "average", "very good", "excellent"]

    def __init__(
        self,
        tutor_id: str,
        tutor_name: str,
        id: Optional[str] = None,
        professional_score: Optional[str] = None,
        technical_score: Optional[str] = None,
        annotation: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ):
        self.__id = id or uuid.uuid4()
        self.__tutor_id = BModel.validate_id(tutor_id, "tutor_id")
        self.__tutor_name = BModel.validate_string(tutor_name, "tutor_name")
        self.professional_score = professional_score
        self.technical_score = technical_score
        self.annotation = annotation
        self.created_at = created_at

    @property
    def id(self):
        return self.__id

    @property
    def tutor_id(self):
        return self.__tutor_id

    @property
    def tutor_name(self):
        return self.__tutor_name

    @property
    def professional_score(self):
        return self.__professional_score

    @property
    def technical_score(self):
        return self.__technical_score

    @property
    def annotation(self):
        return self.__annotation

    @property
    def created_at(self):
        return self.__created_at

    @professional_score.setter
    def professional_score(self, value: Optional[str]):
        if not value:
            self.__professional_score = None

        if isinstance(value, str):
            value = value.lower().strip()

        if value not in self.options:
            raise ValueError(
                f"Invalid professional score: {value}. Allowed: {self.options}"
            )

        self.__professional_score = value.capitalize()

    @technical_score.setter
    def technical_score(self, value: Optional[str]):
        if not value:
            self.__technical_score = None

        if isinstance(value, str):
            value = value.lower().strip()

        if value not in self.options:
            raise ValueError(
                f"Invalid technical score: {value}. Allowed: {self.options}"
            )

        self.__technical_score = value.capitalize()

    @annotation.setter
    def annotation(self, value: Optional[str]):
        if not value:
            self.__annotation = None

        self.__annotation = BModel.validate_string(value, "annotation")

    @created_at.setter
    def created_at(self, value: Optional[datetime]):
        if not value:
            self.__created_at = datetime.now()

        self.__created_at = BModel.validate_datetime(value, "created_at")

    def to_dict(self):
        data = {
            "id": self.id,
            "tutor_id": self.tutor_id,
            "tutor_name": self.tutor_name,
            "created_at": self.created_at,
        }

        if self.technical_score:
            data["technical_score"] = self.technical_score

        if self.professional_score:
            data["professional_score"] = self.professional_score

        if self.annotation:
            data["annotation"] = self.annotation

        return data
