import json
import secrets
import webbrowser
from contextlib import suppress
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import parse_qs, urlencode
from wsgiref.simple_server import make_server

import requests
from readchar import readchar

CLIENT_ID = "girpl6ubjgsd8p8ooui2dkhhfatfh5"
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
    def __init__(self, /, *, scopes: list[str] = [i for i in SCOPES]):
        self._token = self._load_token()
        self.channel_id = self.token.get("channel_id")
        self.channel_name = self.token.get("channel_name")
        self.scopes = scopes
        try:
            print("\033[30;1mLogging in...\033[0m")
            if self.validate_token():
                raise Exception("Token is not usable")
        except Exception:
            print(
                "\033[34;1mPlease log into your bot account\n"
                "press any key to open a login window...\033[0m"
            )
            readchar()
            self.authenticate()
            self.validate_token()

    @property
    def token(self):
        if not self._token:
            self._token = self._load_token()
        return self._token

    @token.setter
    def token(self, token):
        self._token = self._enrich_token(token, self.channel_id, self.channel_name)
        self._save_token()

    @staticmethod
    def _enrich_token(token, channel_id, channel_name):
        new_token = token.copy()
        new_token["channel_id"] = channel_id
        new_token["channel_name"] = channel_name
        return new_token

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        pass

    def _load_token(self) -> Mapping[str, Any] | dict:
        Path("data").mkdir(exist_ok=True)
        with suppress(Exception):
            return json.loads(Path("data/login auth.json").read_text(encoding="utf-8"))
        return {}

    def _save_token(self):
        Path("data").mkdir(exist_ok=True)
        Path("data/login auth.json").write_text(json.dumps(self.token, indent=4, sort_keys=True))

    def validate_token(self) -> bool:
        res = requests.get(
            "https://id.twitch.tv/oauth2/validate",
            headers={
                "Client-Id": CLIENT_ID,
                "Authorization": f"Bearer {self.token.get('access_token')}",
            },
        )
        data = res.json()
        self.channel_name = data.get("login")
        self.channel_id = data.get("user_id")
        self.token = self.token
        return not (
            res.ok
            and data["client_id"] == CLIENT_ID
            and data["user_id"] == self.channel_id
            and set(data["scopes"]) == set(self.scopes)
        )

    def authenticate(self):
        state = secrets.token_urlsafe(16)
        params = {
            "client_id": CLIENT_ID,
            "force_verify": "true",
            "redirect_uri": REDIRECT_URI,
            "response_type": "token",
            "scope": " ".join(SCOPES),
            "state": state,
        }
        webbrowser.open(f"{AUTH_URL}?{urlencode(params)}")
        token = _receive_auth_response(state)
        self.token = token


def _receive_auth_response(expected_state: str):
    logging_in = True
    result = {}

    def application(environment: Mapping[str, str], status_cb: Callable) -> Iterable[bytes]:
        nonlocal logging_in, result
        if environment["PATH_INFO"] not in ["/callback", "/token"]:
            status_cb("404 NOT FOUND", [])
            return ["Not found".encode("utf-8")]
        path = environment["PATH_INFO"]
        result = parse_qs(environment.get("QUERY_STRING", ""))
        returned_state = result.get("state", [None])[0]
        error = result.get("error", [None])[0]

        if error:
            logging_in = False
            status_cb("400 Bad Request", [("Content-Type", "text/plain")])
            return [
                f"OAuth error: {error}, please close this tab and restart the bot".encode("utf-8")
            ]

        if path == "/callback":
            status_cb("200 OK", [("ContentType", "text/html")])
            return [
                b"""<script>
                const fragment = window.location.hash.slice(1);
                if (fragment) {
                window.location.replace("/token?" + fragment);
                } else {
                document.body.innerText = "Missing token.";
                }
                </script>"""
            ]
        elif path == "/token":
            logging_in = False
            if returned_state != expected_state:
                status_cb("400 Bad Request", [("ContentType", "text/plain")])
                return ["State mismatch".encode("utf-8")]

        status_cb("200 OK", [("ContentType", "text/plain")])
        return [b"Login complete! You may now close this tab"]

    with make_server(REDIRECT_HOST, REDIRECT_PORT, application) as server:
        while logging_in:
            server.handle_request()
    if "error" in result:
        raise Exception(result["error_description"])
    token = {
        "access_token": result["access_token"][0],
        "scope": result["scope"][0].split(" "),
        "token_type": result["token_type"][0],
    }
    return token
