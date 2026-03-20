"""Re-export the external pyteslaconnectpk library for internal use.

All API communication is handled by the ``pyteslaconnectpk`` package
published on PyPI, as required by Home Assistant's guidelines that
external device/service communication must be wrapped in an external
Python library.
"""

from pyteslaconnectpk import (  # noqa: F401
    TeslaConnectApi,
    TeslaConnectApiError,
    TeslaConnectAuthError,
    TOKEN_MAX_AGE,
)
from pyteslaconnectpk.auth import Auth  # noqa: F401
