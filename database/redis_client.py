import redis.asyncio as redis

client = redis.Redis(host='localhost', port=12572, db=0)
