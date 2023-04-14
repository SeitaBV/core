"""authoristaion."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
import socket
from typing import Any, cast

from aiohttp.client import ClientError, ClientSession
import async_timeout
from yarl import URL


@dataclass
class FlexMeasures:
    """Main class for handling data fetching from EnergyZero."""

    incl_btw: str = "true"
    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = "POST",
        path: str = "/v3/",
        params: dict[str, Any] | None = None,
        json: dict | None = None,
    ) -> Any:
        """Handle a request to the API of EnergyZero.

        Args:
            uri: Request URI, without '/', for example, 'status'
            *: anything
            method: HTTP method to use, for example, 'GET'
            path: The version of the api currently
            params: Extra options to improve or limit the response.
            json: json for post requests

        Returns:
        -------
            A Python dictionary (json) with the response from EnergyZero.

        Raises:
        ------
            EnergyZeroConnectionError: An error occurred while
                communicating with the API.
            EnergyZeroError: Received an unexpected response from
                the API.
        """
        # version = metadata.version(__package__)
        url = URL.build(scheme="http", host="localhost:5000", path=path).join(
            URL(uri),
        )

        headers: dict = {}

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    json=json,
                    ssl=False,
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to the API."
            raise ConnectionError(
                msg,
            ) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with the API."
            raise ConnectionError(
                msg,
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected content type response from the EnergyZero API"
            raise TypeError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return cast(dict[str, Any], await response.json())

    async def get_access_token(self, password, email):
        """lalalal.Missing argument descriptions in the docstring: `json`, `method`, `params`, `path`, `uri`."""
        response = await self._request(
            uri="requestAuthToken",
            path="/api/",
            json={
                "email": email,
                "password": password,
            },
        )
        return response["auth_token"]
