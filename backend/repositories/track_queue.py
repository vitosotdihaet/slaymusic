from typing import Callable
import redis.asyncio.client
from configs.database import ensure_scripts
from exceptions.track_queue import TrackQueueNotFoundException
from dto.track_queue import (
    InQueueID,
    QueueParameters,
    QueueSrcDestIDs,
    TrackInQueueIDs,
    TrackQueue,
)
from dto.music import TrackID
from repositories.interfaces import ITrackQueueRepository


scripts = {
    "insert": """
-- KEYS[1]: queue key
-- ARGV[1]: track ID
-- ARGV[2]: position (0-based)
-- ARGV[3]: TTL seconds

local key = KEYS[1]
local value = ARGV[1]
local pos = tonumber(ARGV[2]) + 1
local ttl = tonumber(ARGV[3])

local len = redis.call('LLEN', key)
if len == 0 then return redis.error_reply("e") end
if pos > len then pos = len + 1 end

local elements = redis.call('LRANGE', key, 0, -1)
table.insert(elements, pos, value)

redis.call('DEL', key)

if #elements > 0 then
    redis.call('RPUSH', key, unpack(elements))
end

redis.call('EXPIRE', key, ttl)
return 'OK'
""",
    "move": """
-- KEYS[1]: queue key
-- ARGV[1]: source position (0-based)
-- ARGV[2]: dest position (0-based)
-- ARGV[3]: TTL seconds

local key = KEYS[1]
local src = tonumber(ARGV[1]) + 1
local dest = tonumber(ARGV[2]) + 1
local ttl = tonumber(ARGV[3])

local len = redis.call('LLEN', key)
if len == 0 then return redis.error_reply("e") end
if src > len then src = len end
if dest >= len then dest = len + 1 end

local elements = redis.call('LRANGE', key, 0, -1)
local elem = table.remove(elements, src)  -- Remove from source

-- Adjust destination after removal
if dest > src then dest = dest - 1 end

table.insert(elements, dest, elem)  -- Insert at destination
redis.call('DEL', key)
if #elements > 0 then
    redis.call('RPUSH', key, unpack(elements))
end

redis.call('EXPIRE', key, ttl)
return 'OK'
""",
    "remove": """
-- KEYS[1]: queue key
-- ARGV[1]: position (0-based)
-- ARGV[2]: TTL seconds

local key = KEYS[1]
local pos = tonumber(ARGV[1]) + 1
local ttl = tonumber(ARGV[2])

local len = redis.call('LLEN', key)
if len == 0 then return redis.error_reply("e") end
if pos > len then pos = len end

local elements = redis.call('LRANGE', key, 0, -1)
table.remove(elements, pos)
redis.call('DEL', key)
if #elements > 0 then
    redis.call('RPUSH', key, unpack(elements))
end

redis.call('EXPIRE', key, ttl)
return 'OK'
""",
}


class RedisTrackQueueRepository(ITrackQueueRepository):
    def __init__(
        self,
        client_factory: Callable[[], redis.asyncio.client.Redis],
        ttl_sec: int,
        script_sha1s: dict[str, str],
    ) -> None:
        self.client_factory = client_factory
        self.ttl_sec = ttl_sec
        self.script_sha1s = script_sha1s

    @staticmethod
    async def create(
        client_factory: Callable[[], redis.asyncio.client.Redis], ttl_sec: int
    ) -> "RedisTrackQueueRepository":
        return RedisTrackQueueRepository(
            client_factory, ttl_sec, await ensure_scripts("track-queue", scripts)
        )

    @staticmethod
    def _queue_key(user_id: int) -> str:
        return f"queue:{user_id}"

    async def push_left(self, user_id: int, id: TrackID) -> None:
        async with self.client_factory() as client:
            queue_key = self._queue_key(user_id)
            await client.lpush(queue_key, id.id)
            await client.expire(queue_key, self.ttl_sec)

    async def push_right(self, user_id: int, id: TrackID) -> None:
        async with self.client_factory() as client:
            queue_key = self._queue_key(user_id)
            await client.rpush(queue_key, id.id)
            await client.expire(queue_key, self.ttl_sec)

    async def list(self, user_id: int, params: QueueParameters) -> TrackQueue:
        async with self.client_factory() as client:
            offset, limit = 0, -1
            offset = params.offset
            if params.limit > 0:
                limit = offset + params.limit - 1

            queue_key = self._queue_key(user_id)
            res = await client.lrange(queue_key, offset, limit)
            await client.expire(queue_key, self.ttl_sec)
            if len(res) == 0:
                raise TrackQueueNotFoundException
            return TrackQueue.model_validate({"track_ids": [int(r) for r in res]})

    async def delete(self, user_id: int) -> None:
        async with self.client_factory() as client:
            res = await client.delete(self._queue_key(user_id))
            if res == 0:
                raise TrackQueueNotFoundException

    async def insert(self, user_id: int, ids: TrackInQueueIDs) -> None:
        async with self.client_factory() as client:
            try:
                await client.evalsha(
                    self.script_sha1s["insert"],
                    1,
                    self._queue_key(user_id),
                    ids.track_id,
                    ids.queue_id,
                    self.ttl_sec,
                )
            except Exception as e:
                if str(e) == "e":
                    raise TrackQueueNotFoundException
                raise e

    async def move(self, user_id: int, ids: QueueSrcDestIDs) -> None:
        async with self.client_factory() as client:
            try:
                await client.evalsha(
                    self.script_sha1s["move"],
                    1,
                    self._queue_key(user_id),
                    ids.src_id,
                    ids.dest_id,
                    self.ttl_sec,
                )
            except Exception as e:
                if str(e) == "e":
                    raise TrackQueueNotFoundException
                raise e

    async def remove(self, user_id: int, id: InQueueID) -> None:
        async with self.client_factory() as client:
            try:
                await client.evalsha(
                    self.script_sha1s["remove"],
                    1,
                    self._queue_key(user_id),
                    id.id,
                    self.ttl_sec,
                )
            except Exception as e:
                if str(e) == "e":
                    raise TrackQueueNotFoundException
                raise e
