class ContentFetchingException(Exception):
    pass


class ContentNotFound(Exception):
    def __init__(self, message: str):
        """Initialize exception with message."""
        self.message = message


class ShipModelNotFound(ContentNotFound):
    error_code = "Ship model not found"

    def __init__(self) -> None:
        """Init the exception."""
        super().__init__(self.error_code)
