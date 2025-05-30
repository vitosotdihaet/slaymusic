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