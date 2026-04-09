import niquests

from app import __version__

CLIENT_PARAMETERS = {
    "headers": {"User-Agent": f"ED-API/{__version__} (github.com/corenting/ED-API)"},
    "timeout": 3,
}


def get_niquests_session() -> niquests.Session:
    """Get an niquests session with proper configuration."""
    return niquests.Session(**CLIENT_PARAMETERS)


def get_async_niquests_session() -> niquests.AsyncSession:
    """Get an niquests async session with proper configuration."""
    return niquests.AsyncSession(**CLIENT_PARAMETERS)
