from aiohttp_security import AbstractAuthorizationPolicy


class SimpleAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, app) -> None:
        self.app = app

    async def authorized_userid(self, identity):
        db = self.app['db']
        document = await db.user.find_one({"username": identity})
        if document:
            return identity

    async def permits(self, identity, permission, context=None):
        return True

