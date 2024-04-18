class ContentFetchingError(Exception):
    pass


class SystemNotFoundError(Exception):
    error_code = "System not found"

    def __init__(self, system_name: str) -> None:
        """Init the exception."""
        self.error_code = f"System {system_name} not found"


class CommodityNotFoundError(Exception):
    error_code = "Commodity not found"

    def __init__(self, commodity_name: str) -> None:
        """Init the exception."""
        self.error_code = f"Commodity {commodity_name} not found"


class OutfittingNotFoundError(Exception):
    error_code = "Outfitting not found"

    def __init__(self, outfitting: str) -> None:
        """Init the exception."""
        self.error_code = f"Outfitting {outfitting} not found"
