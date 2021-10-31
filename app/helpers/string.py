def string_to_int(string: str) -> int:
    """Convert a string to an integer and removes non-numeric characters."""
    return int("".join(filter(str.isdigit, string)))
