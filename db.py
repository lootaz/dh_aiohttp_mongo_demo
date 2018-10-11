import asyncio
import hashlib

import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

DSN = "mongodb://{username}:{password}@{host}:{port}"


async def init_mongo(app):
    conf = app['config']['mongo']
    client = AsyncIOMotorClient(DSN.format(host=conf['host'],
                                           port=conf['port'],
                                           username=conf['username'],
                                           password=conf['password']))
    db = client.dh
    app['db'] = db


async def close_mongo(app):
    app['db'].close()


def get_collection(collection_name):
    from settings import config

    conf = config['mongo']
    db_url = DSN.format(**conf)
    client = MongoClient(db_url)

    collection = client.dh[collection_name]
    return collection


def create_text_index():
    curs = get_collection('entity')
    curs.create_index([("text", pymongo.TEXT)])


def init_sample_data():
    curs = get_collection('user')

    user = {
        "username": "admin",
        "password": hashlib.sha256(b"nimda").hexdigest()
    }

    result = curs.update({"username": user.get('username')},
                         user, upsert=True)

    return result


if __name__ == '__main__':
    init_sample_data()
    create_text_index()
