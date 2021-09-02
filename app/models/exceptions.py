class ContentFetchingException(Exception):
    pass


class SystemNotFoundException(Exception):
    error_code = "System not found"

    def __init__(self, system_name: str) -> None:
        """Init the exception."""
        self.error_code = f"System {system_name} not found"
