import logging

from app.domain.models.cvinfo import CVInfo

logger = logging.getLogger(__name__)


class CVProcessor:
    def __init__(self, ia_service=None):
        self.ia_service = ia_service


    def process_cv(self, )