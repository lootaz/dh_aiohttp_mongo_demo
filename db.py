import asyncio
import hashlib

from motor.motor_asyncio import AsyncIOMotorClient

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


def init_sample_data():
    from settings import config

    conf = config['mongo']
    # client = AsyncIOMotorClient(conf['host'], conf['port'])

    from pymongo import MongoClient
    db_url = DSN.format(**conf)
    client = MongoClient(db_url)

    db = client.dh

    user = {
        "username": "admin",
        "password": hashlib.sha256(b"nimda").hexdigest()
    }

    result = db.user.update({"username": user.get('username')},
                            user, upsert=True)

    return result


if __name__ == '__main__':
    print(init_sample_data())
