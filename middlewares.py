import base64
import json

from aiohttp_session import AbstractStorage, Session
from cryptography import fernet
from cryptography.fernet import InvalidToken


class TokenStorage(AbstractStorage):
    def __init__(self, secret_key, *, header_name="AIOHTTP_TOKEN",
                 cookie_name="AIOHTTP_SESSION",
                 domain=None, max_age=None, path='/',
                 secure=None, httponly=True,
                 encoder=json.dumps, decoder=json.loads):
        super().__init__(cookie_name=cookie_name, domain=domain, max_age=max_age, path=path, secure=secure,
                         httponly=httponly, encoder=encoder, decoder=decoder)
        if isinstance(secret_key, str):
            pass
        elif isinstance(secret_key, (bytes, bytearray)):
            secret_key = base64.urlsafe_b64encode(secret_key)
        self._fernet = fernet.Fernet(secret_key)
        self._header_name = header_name

    def load_token(self, request):
        header = request.headers.get(self._header_name)
        return header

    def save_token(self, response, token_data):
        if not token_data:
            response.headers.pop(self._header_name, None)
        else:
            response.headers[self._header_name] = token_data

    async def load_session(self, request):
        token = self.load_token(request)
        if token is None:
            return Session(None, data=None, new=True, max_age=self.max_age)
        else:
            try:
                data = self._decoder(
                    self._fernet.decrypt(
                        token.encode('utf-8')).decode('utf-8'))
                return Session(None, data=data,
                               new=False, max_age=self.max_age)
            except InvalidToken:
                return Session(None, data=None, new=True, max_age=self.max_age)

    async def save_session(self, request, response, session):
        if session.empty:
            return self.save_token(response, '')

        token_data = self._encoder(
            self._get_session_data(session)
        ).encode('utf-8')
        self.save_token(
            response,
            self._fernet.encrypt(token_data).decode('utf-8')
        )
