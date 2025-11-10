class ParsingError(Exception):
    """Error parsing content"""

    pass


class ServiceLimitError(Exception):
    """Limit error or internal service error"""

    pass
