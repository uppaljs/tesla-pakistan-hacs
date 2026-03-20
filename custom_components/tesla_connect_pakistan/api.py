"""Tesla Connect API client — mimics the Android app's OkHttp fingerprint."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import requests

from .const import API_AUTH_KEY, BASE_URL, OKHTTP_UA

_LOGGER = logging.getLogger(__name__)

# Token lifetime before we force a re-login (seconds).
# The app doesn't expose an explicit TTL, so we re-auth every 55 minutes
# to stay safely below any server-side session window.
TOKEN_MAX_AGE = 55 * 60


class TeslaConnectAuthError(Exception):
    """Raised on authentication failure."""


class TeslaConnectApiError(Exception):
    """Raised on non-auth API errors."""


class TeslaConnectApi:
    """Async-safe wrapper around the Tesla Connect REST API.

    All network I/O uses ``requests`` (sync) and is expected to be called
    from Home Assistant via ``hass.async_add_executor_job``.
    """

    def __init__(self, phone: str, password: str) -> None:
        self._phone = phone
        self._password = password
        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": OKHTTP_UA,
                "Accept-Encoding": "gzip",
                "Connection": "keep-alive",
            }
        )
        self.token: str | None = None
        self.user_name: str | None = None
        self.phone: str | None = None
        self.devices: list[dict[str, Any]] = []
        self._token_ts: float = 0.0

    # ── helpers ──────────────────────────────────────────────────────

    def _post(self, path: str, payload: dict | None = None) -> dict[str, Any]:
        url = f"{BASE_URL}{path}"
        ts = str(int(time.time()))
        body = json.dumps(payload or {}, separators=(",", ":"))
        try:
            resp = self._session.post(
                url,
                data=body,
                headers={
                    "key": ts + API_AUTH_KEY,
                    "Content-Type": "application/json; charset=utf-8",
                    "Content-Length": str(len(body.encode())),
                },
                timeout=30,
            )
            resp.raise_for_status()
        except requests.exceptions.ConnectionError as exc:
            raise TeslaConnectApiError(f"Connection error: {exc}") from exc
        except requests.exceptions.Timeout as exc:
            raise TeslaConnectApiError(f"Timeout: {exc}") from exc
        except requests.exceptions.HTTPError as exc:
            raise TeslaConnectApiError(f"HTTP {resp.status_code}") from exc

        data: dict[str, Any] = resp.json()
        _LOGGER.debug("POST %s → %s", path, data.get("status", "?"))
        return data

    @property
    def token_expired(self) -> bool:
        if not self.token:
            return True
        return (time.time() - self._token_ts) > TOKEN_MAX_AGE

    def ensure_token(self) -> None:
        """Re-authenticate if the token is missing or stale."""
        if self.token_expired:
            self.sign_in()

    # ── auth ─────────────────────────────────────────────────────────

    def sign_in(self) -> dict[str, Any]:
        data = self._post(
            "sign-in",
            {
                "phone": self._phone,
                "password": self._password,
                "firebase_token": "",
            },
        )
        if data.get("status") != "Success":
            raise TeslaConnectAuthError(
                data.get("message", "Login failed")
            )
        self.token = data["token"]
        self._token_ts = time.time()
        self.user_name = data.get("name")
        self.phone = data.get("phone")
        self.devices = data.get("devices", [])
        _LOGGER.info(
            "Signed in as %s — %d device(s)", self.user_name, len(self.devices)
        )
        return data

    def change_password(self, new_password: str) -> dict[str, Any]:
        self.ensure_token()
        return self._post("change-password", {"token": self.token, "password": new_password})

    # ── devices ──────────────────────────────────────────────────────

    def refresh_devices(self) -> list[dict[str, Any]]:
        """Re-login to refresh the device list (login is the only reliable source)."""
        self.sign_in()
        return self.devices

    def add_device(self, device_id: str, name: str) -> dict[str, Any]:
        self.ensure_token()
        return self._post("device-add", {"token": self.token, "device_id": device_id, "name": name})

    def delete_device(self, device_id: str, name: str) -> dict[str, Any]:
        self.ensure_token()
        return self._post("device-delete", {"token": self.token, "device_id": device_id, "name": name})

    # ── geyser read ──────────────────────────────────────────────────

    def get_geyser_details(self, device_id: str, name: str = "") -> dict[str, Any]:
        self.ensure_token()
        return self._post("geyser-details", {"token": self.token, "device_id": device_id, "name": name})

    # ── geyser control ───────────────────────────────────────────────

    def set_geyser_boost(self, device_id: str, enabled: bool) -> dict[str, Any]:
        self.ensure_token()
        return self._post("geyser-boost", {"token": self.token, "device_id": device_id, "boost": 1 if enabled else 0})

    def set_geyser_mode(self, device_id: str, curr_mode: int, user_mode: int) -> dict[str, Any]:
        self.ensure_token()
        return self._post("geyser-mode", {"token": self.token, "device_id": device_id, "curr_mode": curr_mode, "user_mode": user_mode})

    def set_geyser_temp_limit(self, device_id: str, temp_limit: int) -> dict[str, Any]:
        self.ensure_token()
        return self._post("geyser-temp-limit", {"token": self.token, "device_id": device_id, "temp_limit": temp_limit})

    def set_geyser_timer(self, device_id: str, times: list[dict]) -> dict[str, Any]:
        self.ensure_token()
        return self._post("geyser-time", {"token": self.token, "device_id": device_id, "times": times})

    def set_geyser_two_hour_mode(self, device_id: str, enabled: bool) -> dict[str, Any]:
        self.ensure_token()
        return self._post("geyser-two-hour-mode", {"token": self.token, "device_id": device_id, "two_hour_mode": 1 if enabled else 0})

    def set_geyser_vacation_mode(self, device_id: str, enabled: bool) -> dict[str, Any]:
        self.ensure_token()
        return self._post("geyser-vacation-mode", {"token": self.token, "device_id": device_id, "vacation": 1 if enabled else 0})

    # ── inverter read ────────────────────────────────────────────────

    def get_inverter_details(self, device_id: str, name: str = "") -> dict[str, Any]:
        self.ensure_token()
        return self._post("inverter-details", {"token": self.token, "device_id": device_id, "name": name})

    # ── misc ─────────────────────────────────────────────────────────

    def get_strings(self) -> dict[str, Any]:
        return self._post("strings.json")
