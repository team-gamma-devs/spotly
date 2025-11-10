from typing import Optional, List
from app.infrastructure.database.repositories.filters_repository import (
    FiltersRepository,
)


class GetFilters:
    """
    Use case class to retrieve available filters from the FiltersRepository.

    Provides an abstraction layer between the repository and higher-level application logic.
    """

    def __init__(self, filters_repo: Optional[FiltersRepository] = None):
        """
        Initialize the GetFilters use case.

        Args:
            filters_repo (Optional[FiltersRepository]):
                An instance of FiltersRepository. If not provided, a default instance is created.
        """
        self.filters_repo = filters_repo or FiltersRepository()

    async def get_available_filters(self) -> List[str]:
        """
        Retrieve the list of currently available filters from the repository.

        Returns:
            List[str]: A list of filter names (as strings) currently stored in the system.
        """
        available_filters = await self.filters_repo.get_filters()
        return available_filters
