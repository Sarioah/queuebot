import json
import os
import secrets
import time
import webbrowser
from contextlib import suppress
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import parse_qs, urlencode
from wsgiref.simple_server import make_server

import requests
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("TWITCH_API_ID")
CLIENT_SECRET = os.getenv("TWITCH_API_SECRET")
AUTH_URL = "https://id.twitch.tv/oauth2/authorize"
TOKEN_URL = "https://id.twitch.tv/oauth2/token"
REDIRECT_HOST = "localhost"
REDIRECT_PORT = 3000
REDIRECT_URI = f"http://{REDIRECT_HOST}:{REDIRECT_PORT}/callback"
SCOPES = [
    "chat:read",
    "chat:edit",
    "user:read:chat",
]


class AuthorisedContext:
    def __init__(self, channel_name, /, *, scopes: list[str] = [i for i in SCOPES]):
        self.channel_name = channel_name
        self._token = self._load_token()
        self.channel_id = self.token.get("channel_id")
        self.scopes = scopes
        try:
            print("Logging in")
            self.refresh_token()
            if self.token_expired() or self.token_invalid():
                raise Exception("Token is not usable")
        except Exception:
            print("Please authenticate with browser")
            self.authenticate()
        self._populate_channel_id()

    @property
    def token(self):
        if not self._token:
            self._token = self._load_token()
        return self._token

    @token.setter
    def token(self, token):
        self._token = self._enrich_token(token, self.channel_id)
        print(f"new token set to {self._token}")
        self._save_token()

    @staticmethod
    def _enrich_token(token, channel_id):
        new_token = token.copy()
        new_token["expires_at"] = time.time() + new_token["expires_in"]
        new_token["channel_id"] = channel_id
        return new_token

    def _populate_channel_id(self):
        if c_id := self.token.get("channel_id"):
            self.channel_id = c_id
            return
        print("need to grab ID")
        channel_info = requests.get(
            f"https://api.twitch.tv/helix/users?login={self.channel_name}",
            headers={
                "Client-Id": CLIENT_ID,
                "Authorization": f"Bearer {self.token.get('access_token')}",
            },
        ).json()
        self.channel_id = channel_info["data"][0]["id"]
        self.token = self.token

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def _load_token(self) -> Mapping[str, Any] | dict:
        Path("data").mkdir(exist_ok=True)
        with suppress(Exception):
            return json.loads(
                Path(f"data/{self.channel_name} auth.json").read_text(encoding="utf-8")
            )
        return {}

    def _save_token(self):
        Path("data").mkdir(exist_ok=True)
        Path(f"data/{self.channel_name} auth.json").write_text(
            json.dumps(self.token, indent=4, sort_keys=True)
        )

    def refresh_token(self):
        print("refreshing token")
        new_token = _refresh_token(self.token)
        self.token = new_token

    def token_expired(self) -> bool:
        return self.token.get("expires_at", 0) - time.time() <= 3600

    def token_invalid(self) -> bool:
        res = requests.get(
            "https://id.twitch.tv/oauth2/validate",
            headers={
                "Client-Id": CLIENT_ID,
                "Authorization": f"Bearer {self.token.get('access_token')}",
            },
        )
        data = res.json()
        return not (
            res.ok
            and data["client_id"] == CLIENT_ID
            and data["user_id"] == self.channel_id
            and set(data["scopes"]) == set(self.scopes)
        )

    def authenticate(self):
        print("requesting new token")
        state = secrets.token_urlsafe(16)
        params = {
            "client_id": CLIENT_ID,
            "force_verify": "true",
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": " ".join(SCOPES),
            "state": state,
        }
        webbrowser.open(f"{AUTH_URL}?{urlencode(params)}")
        code = _wait_for_response(state)
        token = _exchange_code_for_token(code)
        token["expires_at"] = time.time() + token["expires_in"]
        self.token = token


def _wait_for_response(expected_state: str):
    result = {}

    def application(environment: Mapping[str, str], status_cb: Callable) -> Iterable[bytes]:
        if environment["PATH_INFO"] != "/callback":
            status_cb("404 NOT FOUND", [])
            return ["Not found".encode("utf-8")]
        params = parse_qs(environment.get("QUERY_STRING", ""))
        code = params.get("code", [None])[0]
        returned_state = params.get("state", [None])[0]
        error = params.get("error", [None])[0]

        if error:
            status_cb("400 Bad Request", [("Content-Type", "text/plain")])
            return [f"OAuth error: {error}".encode("utf-8")]

        if returned_state != expected_state:
            status_cb("400 Bad Request", [("ContentType", "text/plain")])
            return ["State mismatch".encode("utf-8")]

        result["code"] = code

        status_cb("200 OK", [("ContentType", "text/plain")])
        return [f"Auth complete with code '{code}'".encode("utf-8")]

    with make_server(REDIRECT_HOST, REDIRECT_PORT, application) as server:
        server.handle_request()

    return result.get("code")


def _exchange_code_for_token(code):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "code": code,
        "grant_type": "authorization_code",
    }
    res = requests.post(TOKEN_URL, data=urlencode(data).encode("utf-8")).json()
    return res


def _refresh_token(token):
    res = requests.post(
        "https://id.twitch.tv/oauth2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        params={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": token.get("refresh_token"),
        },
    )
    if res.ok:
        return res.json()
    return {}


if __name__ == "__main__":
    auth = AuthorisedContext("sarioah", scopes=SCOPES)
    token = auth.token
    print(f"{token = }")
    exit(0)
    channel_info = requests.get(
        "https://api.twitch.tv/helix/users?login=sarioah",
        headers={"Client-Id": CLIENT_ID, "Authorization": f"Bearer {token['access_token']}"},
    ).json()

    target_id = requests.get(
        "https://api.twitch.tv/helix/users?login=shayehayes",
        headers={"Client-Id": CLIENT_ID, "Authorization": f"Bearer {token['access_token']}"},
    ).json()["data"][0]["id"]
    channel_id = channel_info["data"][0]["id"]
    print(f"channel_id: {json.dumps(channel_id, indent=4)}")

    params = {"broadcaster_id": target_id, "moderator_id": channel_id}
    response = requests.get(
        f"https://api.twitch.tv/helix/guest_star/session?{urlencode(params)}",
        headers={"Client-Id": CLIENT_ID, "Authorization": f"Bearer {token['access_token']}"},
    ).json()
    print(f"response: {json.dumps(response, indent=4)}")

    params = {"broadcaster_id": channel_id, "first": 10}
    response = requests.get(
        f"https://api.twitch.tv/helix/users/blocks?{urlencode(params)}",
        headers={"Client-Id": CLIENT_ID, "Authorization": f"Bearer {token['access_token']}"},
    ).json()
    print(f"response: {json.dumps(response, indent=4)}")

    params = {"client_id": CLIENT_ID, "token": token["access_token"]}

    # TODO: this needs proper auth handling / splitting into a module + API interface object
