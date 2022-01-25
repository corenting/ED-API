class ContentFetchingException(Exception):
    pass


class SystemNotFoundException(Exception):
    error_code = "System not found"

    def __init__(self, system_name: str) -> None:
        """Init the exception."""
        self.error_code = f"System {system_name} not found"


class CommodityNotFoundException(Exception):
    error_code = "Commodity not found"

    def __init__(self, commodity_name: str) -> None:
        """Init the exception."""
        self.error_code = f"Commodity {commodity_name} not found"
