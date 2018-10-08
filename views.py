import hashlib
import pymongo

from aiohttp import web
from aiohttp_security import remember
from bson import ObjectId

from utils import auth_required, JSONEncoder

routes = web.RouteTableDef()


@routes.post('/api/auth')
async def auth(request):
    data = await request.json()

    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        raise web.HTTPBadRequest(text="Username or Password not found")

    db = request.app['db']
    user = await db.user.find_one({"username": username})
    if not user or user.get('password') != hashlib.sha256(bytearray(password, 'utf-8')).hexdigest():
        raise web.HTTPBadRequest(text="Username or Password incorrect")

    await remember(request, web.Response, username)
    return web.json_response()



@routes.post('/api/entity/insert')
@auth_required
async def insert(request):
    entity = await request.json()

    db = request.app['db']
    result = await db.entity.replace_one(
        {"name": entity.get("name")},
        entity,
        upsert=True
    )

    return web.json_response()



@routes.post('/api/entity/find')
@auth_required
async def find(request):
    data = await request.json()
    db = request.app['db']
    await db.entity.create_index([("text", pymongo.TEXT)])

    entities = db.entity.find({
        "$text": {
            "$search": data.get('search_request')
        }
    })

    result = []
    async for entity in entities:
        pipeline = [
            {
                "$graphLookup": {
                    "from": "entity",
                    "startWith": "$name",
                    "connectFromField": "parent_name",
                    "connectToField": "name",
                    "as": "parents"
                }
            },
            {
                "$match": {
                    "name": entity.get('name')
                }
            }
        ]
        async for doc in db.entity.aggregate(pipeline):
            result.append(doc)

    return web.json_response(text=JSONEncoder().encode(result))



@routes.get('/api/entity/{id}/subtree')
@auth_required
async def subtree(request):
    id = request.match_info.get('id')
    db = request.app['db']

    entity = await db.entity.find_one({"_id": ObjectId(id)})
    pipeline = [
        {
            "$graphLookup": {
                "from": "entity",
                "startWith": "$name",
                "connectFromField": "parent_name",
                "connectToField": "name",
                "as": "parents"
            }
        },
        {
            "$match": {
                "name": entity.get('name')
            }
        }
    ]
    result = []
    async for doc in db.entity.aggregate(pipeline):
        result.append(doc)
    return web.json_response(text=JSONEncoder().encode(result))
