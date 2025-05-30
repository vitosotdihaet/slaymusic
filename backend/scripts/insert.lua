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