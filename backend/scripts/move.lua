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