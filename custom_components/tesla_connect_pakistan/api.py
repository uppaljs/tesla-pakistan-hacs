"""API client for the Tesla Connect Pakistan integration."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import requests

from .const import API_AUTH_KEY, BASE_URL, OKHTTP_UA

_LOGGER = logging.getLogger(__name__)

# Seconds before a cached token is considered stale and a re-login is forced.
# The app does not expose an explicit TTL; 55 minutes stays safely below any
# server-side session window.
TOKEN_MAX_AGE = 55 * 60


class TeslaConnectAuthError(Exception):
    """Raised when authentication against the Tesla Connect API fails."""


class TeslaConnectApiError(Exception):
    """Raised when a non-authentication API call returns an error."""


class TeslaConnectApi:
    """Synchronous wrapper around the Tesla Connect REST API.

    All network I/O uses :mod:`requests` and is intended to be dispatched
    from Home Assistant via ``hass.async_add_executor_job``.
    """

    def __init__(self, phone: str, password: str) -> None:
        """Initialise the API client with user credentials.

        Args:
            phone: The account phone number used to authenticate.
            password: The account password used to authenticate.
        """
        self._phone = phone
        self._password = password
        self._token_ts: float = 0.0
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Accept-Encoding": "gzip",
                "Connection": "keep-alive",
                "User-Agent": OKHTTP_UA,
            }
        )
        self.devices: list[dict[str, Any]] = []
        self.phone: str | None = None
        self.token: str | None = None
        self.user_name: str | None = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _post(self, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a JSON POST request and return the parsed response body.

        Args:
            path: API endpoint path relative to :data:`.BASE_URL`.
            payload: Optional request body that will be JSON-serialised.

        Returns:
            Parsed JSON response as a dictionary.

        Raises:
            TeslaConnectApiError: On connection failure, timeout, or HTTP error.
        """
        url = f"{BASE_URL}{path}"
        ts = str(int(time.time()))
        body = json.dumps(payload or {}, separators=(",", ":"))
        try:
            resp = self._session.post(
                url,
                data=body,
                headers={
                    "Content-Length": str(len(body.encode())),
                    "Content-Type": "application/json; charset=utf-8",
                    "key": ts + API_AUTH_KEY,
                },
                timeout=30,
            )
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as exc:
            raise TeslaConnectApiError(f"Connection error: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            raise TeslaConnectApiError(f"Request timed out: {exc}") from exc
        except requests.exceptions.HTTPError as exc:
            raise TeslaConnectApiError(f"HTTP {resp.status_code}") from exc

        data: dict[str, Any] = resp.json()
        _LOGGER.debug("POST %s status=%s", path, data.get("status", "?"))
        return data

    @property
    def token_expired(self) -> bool:
        """Return True when the cached token is absent or older than TOKEN_MAX_AGE."""
        if not self.token:
            return True
        return (time.time() - self._token_ts) > TOKEN_MAX_AGE

    def ensure_token(self) -> None:
        """Re-authenticate if the cached token is missing or stale."""
        if self.token_expired:
            self.sign_in()

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def sign_in(self) -> dict[str, Any]:
        """Authenticate with the API and cache the returned token.

        Returns:
            The raw API response dictionary on success.

        Raises:
            TeslaConnectAuthError: When the API returns a non-success status.
        """
        data = self._post(
            "sign-in",
            {
                "firebase_token": "",
                "password": self._password,
                "phone": self._phone,
            },
        )
        if data.get("status") != "Success":
            raise TeslaConnectAuthError(data.get("message", "Login failed"))
        self.token = data["token"]
        self._token_ts = time.time()
        self.devices = data.get("devices", [])
        self.phone = data.get("phone")
        self.user_name = data.get("name")
        _LOGGER.info(
            "Signed in as %s with %d device(s)", self.user_name, len(self.devices)
        )
        return data

    def change_password(self, new_password: str) -> dict[str, Any]:
        """Change the account password.

        Args:
            new_password: The replacement password to set on the account.

        Returns:
            The raw API response dictionary.
        """
        self.ensure_token()
        return self._post(
            "change-password",
            {"password": new_password, "token": self.token},
        )

    # ------------------------------------------------------------------
    # Device management
    # ------------------------------------------------------------------

    def refresh_devices(self) -> list[dict[str, Any]]:
        """Re-authenticate to obtain a fresh device list from the API.

        The login response is the only reliable source of device data.

        Returns:
            Updated list of device dictionaries.
        """
        self.sign_in()
        return self.devices

    def add_device(self, device_id: str, name: str) -> dict[str, Any]:
        """Register a new device on the account.

        Args:
            device_id: Unique identifier of the device to add.
            name: Human-readable label for the device.

        Returns:
            The raw API response dictionary.
        """
        self.ensure_token()
        return self._post(
            "device-add",
            {"device_id": device_id, "name": name, "token": self.token},
        )

    def delete_device(self, device_id: str, name: str) -> dict[str, Any]:
        """Remove a device from the account.

        Args:
            device_id: Unique identifier of the device to remove.
            name: Human-readable label for the device.

        Returns:
            The raw API response dictionary.
        """
        self.ensure_token()
        return self._post(
            "device-delete",
            {"device_id": device_id, "name": name, "token": self.token},
        )

    # ------------------------------------------------------------------
    # Geyser reads
    # ------------------------------------------------------------------

    def get_geyser_details(self, device_id: str, name: str = "") -> dict[str, Any]:
        """Fetch the current state of a geyser device.

        Args:
            device_id: Unique identifier of the geyser.
            name: Optional human-readable label sent alongside the request.

        Returns:
            The raw API response dictionary containing geyser state.
        """
        self.ensure_token()
        return self._post(
            "geyser-details",
            {"device_id": device_id, "name": name, "token": self.token},
        )

    # ------------------------------------------------------------------
    # Geyser controls
    # ------------------------------------------------------------------

    def set_geyser_boost(self, device_id: str, enabled: bool) -> dict[str, Any]:
        """Enable or disable boost mode on a geyser.

        Args:
            device_id: Unique identifier of the geyser.
            enabled: True to enable boost, False to disable.

        Returns:
            The raw API response dictionary.
        """
        self.ensure_token()
        return self._post(
            "geyser-boost",
            {"boost": 1 if enabled else 0, "device_id": device_id, "token": self.token},
        )

    def set_geyser_mode(
        self, device_id: str, curr_mode: int, user_mode: int
    ) -> dict[str, Any]:
        """Set the operating mode on a geyser.

        Args:
            device_id: Unique identifier of the geyser.
            curr_mode: The current mode integer reported by the device.
            user_mode: The desired mode integer to apply.

        Returns:
            The raw API response dictionary.
        """
        self.ensure_token()
        return self._post(
            "geyser-mode",
            {
                "curr_mode": curr_mode,
                "device_id": device_id,
                "token": self.token,
                "user_mode": user_mode,
            },
        )

    def set_geyser_temp_limit(self, device_id: str, temp_limit: int) -> dict[str, Any]:
        """Set the upper temperature limit on a geyser.

        Args:
            device_id: Unique identifier of the geyser.
            temp_limit: Target maximum temperature in degrees Celsius.

        Returns:
            The raw API response dictionary.
        """
        self.ensure_token()
        return self._post(
            "geyser-temp-limit",
            {"device_id": device_id, "temp_limit": temp_limit, "token": self.token},
        )

    def set_geyser_timer(
        self, device_id: str, times: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Configure scheduled timer slots on a geyser.

        Args:
            device_id: Unique identifier of the geyser.
            times: List of timer slot dictionaries as expected by the API.

        Returns:
            The raw API response dictionary.
        """
        self.ensure_token()
        return self._post(
            "geyser-time",
            {"device_id": device_id, "times": times, "token": self.token},
        )

    def set_geyser_two_hour_mode(
        self, device_id: str, enabled: bool
    ) -> dict[str, Any]:
        """Enable or disable two-hour heating mode on a geyser.

        Args:
            device_id: Unique identifier of the geyser.
            enabled: True to enable two-hour mode, False to disable.

        Returns:
            The raw API response dictionary.
        """
        self.ensure_token()
        return self._post(
            "geyser-two-hour-mode",
            {
                "device_id": device_id,
                "token": self.token,
                "two_hour_mode": 1 if enabled else 0,
            },
        )

    def set_geyser_vacation_mode(
        self, device_id: str, enabled: bool
    ) -> dict[str, Any]:
        """Enable or disable vacation mode on a geyser.

        Args:
            device_id: Unique identifier of the geyser.
            enabled: True to enable vacation mode, False to disable.

        Returns:
            The raw API response dictionary.
        """
        self.ensure_token()
        return self._post(
            "geyser-vacation-mode",
            {"device_id": device_id, "token": self.token, "vacation": 1 if enabled else 0},
        )

    # ------------------------------------------------------------------
    # Inverter reads
    # ------------------------------------------------------------------

    def get_inverter_details(self, device_id: str, name: str = "") -> dict[str, Any]:
        """Fetch the current state of an inverter device.

        Args:
            device_id: Unique identifier of the inverter.
            name: Optional human-readable label sent alongside the request.

        Returns:
            The raw API response dictionary containing inverter state.
        """
        self.ensure_token()
        return self._post(
            "inverter-details",
            {"device_id": device_id, "name": name, "token": self.token},
        )

    # ------------------------------------------------------------------
    # Miscellaneous
    # ------------------------------------------------------------------

    def get_strings(self) -> dict[str, Any]:
        """Fetch the localisation strings bundle from the API.

        Returns:
            The raw API response dictionary containing string resources.
        """
        return self._post("strings.json")
