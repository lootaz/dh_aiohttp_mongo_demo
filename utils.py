import json
from aiohttp import web
from aiohttp_security import authorized_userid
from bson import ObjectId


def auth_required(func):
    async def wrap(request, *args, **kwargs):
        userid = await authorized_userid(request)
        if not userid:
            raise web.HTTPForbidden()
        return await func(request, *args, **kwargs)

    return wrap


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return super().default(o)
