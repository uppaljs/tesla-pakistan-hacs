"""Tests for the Tesla Connect Pakistan API client."""

from __future__ import annotations

import json
import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from custom_components.tesla_connect_pakistan.api import (
    TOKEN_MAX_AGE,
    TeslaConnectApi,
    TeslaConnectApiError,
    TeslaConnectAuthError,
)
from custom_components.tesla_connect_pakistan.const import API_AUTH_KEY, OKHTTP_UA

from .conftest import MOCK_PASSWORD, MOCK_PHONE, MOCK_SIGN_IN_RESPONSE


class TestApiClient:
    """Tests for TeslaConnectApi."""

    def test_init_sets_okhttp_user_agent(self) -> None:
        """User-Agent header should mimic OkHttp."""
        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        assert api._session.headers["User-Agent"] == OKHTTP_UA

    def test_init_token_is_none(self) -> None:
        """A fresh client should have no token."""
        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        assert api.token is None
        assert api.token_expired is True

    def test_token_expired_when_stale(self) -> None:
        """Token should be considered expired after TOKEN_MAX_AGE seconds."""
        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        api.token = "some_token"
        api._token_ts = time.time() - TOKEN_MAX_AGE - 1
        assert api.token_expired is True

    def test_token_valid_when_fresh(self) -> None:
        """Token should be valid when recently acquired."""
        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        api.token = "some_token"
        api._token_ts = time.time()
        assert api.token_expired is False

    @patch("custom_components.tesla_connect_pakistan.api.requests.Session")
    def test_sign_in_success(self, mock_session_cls: MagicMock) -> None:
        """Successful sign-in should set token and devices."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_SIGN_IN_RESPONSE
        mock_resp.raise_for_status.return_value = None

        session = mock_session_cls.return_value
        session.post.return_value = mock_resp
        session.headers = {}

        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        api._session = session
        result = api.sign_in()

        assert result["status"] == "Success"
        assert api.token == MOCK_SIGN_IN_RESPONSE["token"]
        assert api.user_name == MOCK_SIGN_IN_RESPONSE["name"]
        assert len(api.devices) == 2

    @patch("custom_components.tesla_connect_pakistan.api.requests.Session")
    def test_sign_in_failure_raises(self, mock_session_cls: MagicMock) -> None:
        """Failed sign-in should raise TeslaConnectAuthError."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {
            "message": "Invalid credentials",
            "status": "Failure",
        }
        mock_resp.raise_for_status.return_value = None

        session = mock_session_cls.return_value
        session.post.return_value = mock_resp
        session.headers = {}

        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        api._session = session

        with pytest.raises(TeslaConnectAuthError, match="Invalid credentials"):
            api.sign_in()

    @patch("custom_components.tesla_connect_pakistan.api.requests.Session")
    def test_post_connection_error(self, mock_session_cls: MagicMock) -> None:
        """Connection errors should raise TeslaConnectApiError."""
        session = mock_session_cls.return_value
        session.post.side_effect = requests.exceptions.ConnectionError("refused")
        session.headers = {}

        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        api._session = session

        with pytest.raises(TeslaConnectApiError, match="Connection error"):
            api._post("test-endpoint")

    @patch("custom_components.tesla_connect_pakistan.api.requests.Session")
    def test_post_timeout(self, mock_session_cls: MagicMock) -> None:
        """Timeouts should raise TeslaConnectApiError."""
        session = mock_session_cls.return_value
        session.post.side_effect = requests.exceptions.Timeout("timed out")
        session.headers = {}

        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        api._session = session

        with pytest.raises(TeslaConnectApiError, match="timed out"):
            api._post("test-endpoint")

    @patch("custom_components.tesla_connect_pakistan.api.requests.Session")
    def test_key_header_format(self, mock_session_cls: MagicMock) -> None:
        """The key header should be timestamp + API_AUTH_KEY."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "Success"}
        mock_resp.raise_for_status.return_value = None

        session = mock_session_cls.return_value
        session.post.return_value = mock_resp
        session.headers = {}

        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        api._session = session
        api._post("test")

        call_kwargs = session.post.call_args
        key_header = call_kwargs.kwargs["headers"]["key"]
        assert key_header.endswith(API_AUTH_KEY)
        # The prefix should be a valid unix timestamp.
        ts_part = key_header[: -len(API_AUTH_KEY)]
        assert ts_part.isdigit()

    @patch("custom_components.tesla_connect_pakistan.api.requests.Session")
    def test_post_sends_compact_json(self, mock_session_cls: MagicMock) -> None:
        """Request body should use compact JSON (no spaces)."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "Success"}
        mock_resp.raise_for_status.return_value = None

        session = mock_session_cls.return_value
        session.post.return_value = mock_resp
        session.headers = {}

        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        api._session = session
        api._post("test", {"alpha": "one", "beta": 2})

        call_kwargs = session.post.call_args
        body = call_kwargs.kwargs["data"]
        parsed = json.loads(body)
        assert parsed == {"alpha": "one", "beta": 2}
        # No spaces in the compact encoding.
        assert " " not in body

    def test_ensure_token_calls_sign_in_when_expired(self) -> None:
        """ensure_token should re-authenticate when token is stale."""
        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        api.sign_in = MagicMock()  # type: ignore[method-assign]
        api.ensure_token()
        api.sign_in.assert_called_once()

    def test_ensure_token_skips_when_valid(self) -> None:
        """ensure_token should not re-authenticate when token is fresh."""
        api = TeslaConnectApi(MOCK_PHONE, MOCK_PASSWORD)
        api.token = "valid"
        api._token_ts = time.time()
        api.sign_in = MagicMock()  # type: ignore[method-assign]
        api.ensure_token()
        api.sign_in.assert_not_called()
