import hashlib
import pymongo

from aiohttp import web
from aiohttp_security import remember
from bson import ObjectId

from utils import auth_required, JSONEncoder

routes = web.RouteTableDef()


def get_entity_parent_pipeline(entity_id: ObjectId):
    return [
        {
            "$graphLookup": {
                "from": "entity",
                "startWith": "$_id",
                "connectFromField": "parent_id",
                "connectToField": "_id",
                "as": "parents"
            }
        },
        {
            "$match": {
                "_id": entity_id
            }
        }
    ]


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
    parent_id = entity.get('parent_id')
    if parent_id:
        parent_id = ObjectId(parent_id)
        entity['parent_id'] = parent_id

    db = request.app['db']
    await db.entity.insert_one(entity)

    return web.json_response(text=JSONEncoder().encode(entity))


@routes.post('/api/entity/find')
@auth_required
async def find(request):
    data = await request.json()
    db = request.app['db']

    entities = db.entity.find({
        "$text": {
            "$search": data.get('search_request')
        }
    })

    result = []
    async for entity in entities:
        result = []
        async for doc in db.entity.aggregate(get_entity_parent_pipeline(entity.get('_id'))):
            parents = doc.get('parents')
            for parent in parents:
                result.append(parent.get('_id'))

    return web.json_response(text=JSONEncoder().encode(result))


@routes.get('/api/entity/{id}/subtree')
@auth_required
async def subtree(request):
    id = request.match_info.get('id')
    db = request.app['db']

    result = []
    async for doc in db.entity.aggregate(get_entity_parent_pipeline(ObjectId(id))):
        parents = doc.get('parents')
        for parent in parents:
            result.append(parent.get('_id'))

    return web.json_response(text=JSONEncoder().encode(result))
