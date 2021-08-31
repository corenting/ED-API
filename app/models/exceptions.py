class ContentFetchingException(Exception):
    pass


class SystemNotFoundException:
    def __init__(self, system_name: str) -> None:
        """Init the exception."""
        self.error_code = f"System {system_name} not found"
