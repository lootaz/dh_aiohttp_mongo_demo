import base64

from aiohttp import web
from aiohttp_session import session_middleware, setup
from aiohttp_swagger import setup_swagger
from cryptography import fernet
from aiohttp_security import setup as setup_security, SessionIdentityPolicy

from db import init_mongo, close_mongo
from middlewares import TokenStorage
from policy import SimpleAuthorizationPolicy
from settings import config
from views import routes

fernet_key = fernet.Fernet.generate_key()
secret_key = base64.urlsafe_b64decode(fernet_key)
middleware = session_middleware(TokenStorage(secret_key))
app = web.Application(middlewares=[middleware])

app.router.add_routes(routes)
setup_swagger(app, swagger_from_file="docs/swagger.yaml")

app['config'] = config

app.on_startup.append(init_mongo)
app.on_cleanup.append(close_mongo)

setup_security(app, SessionIdentityPolicy(), SimpleAuthorizationPolicy(app))


web.run_app(app)