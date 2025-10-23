from typing import Optional, Any

from app.infrastructure.database.repositories.user_repository import UserRepository


class GraduatesFilter:
    def __init__(self, user_repo: Optional[UserRepository] = None):
        self.user_repo = user_repo or UserRepository()

    def process_filters(self, filters: dict[str, Any]) -> dict[str, Any]:
        pass
