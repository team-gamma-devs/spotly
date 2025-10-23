from typing import Optional, List

from app.infrastructure.database.repositories.filters_repository import (
    FiltersRepository,
)


class GetFilters:
    def __init__(self, filters_repo: Optional[FiltersRepository] = None):
        self.filters_repo = filters_repo or FiltersRepository()

    async def get_available_filters(self) -> List[str]:
        available_filters = await self.filters_repo.get_filters()
        return available_filters
