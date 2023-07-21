import redis.asyncio as redis


class RedisClient:
    def __init__(self) -> None:
        self._host = "redis"
        self._port = 6379
        self._db = 0
    
    async def get_connection(self):
        try:
            r = redis.from_url(
                url=f"redis://{self._host}:{self._port}",
                db=self._db,
                decode_responses=True
            )
            yield r
        finally:
            await r.close()