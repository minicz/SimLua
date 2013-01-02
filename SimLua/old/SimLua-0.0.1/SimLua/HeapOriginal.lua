-- Heap.lua
-- A simple priority queue implementation
local assert, setmetatable = assert, setmetatable

module(...)

local function push (h, k, v)
  assert(v ~= nil, "cannot push nil")
  local t = h.nodes
  local h = h.heap
  local n = #h + 1 -- node position in heap array (leaf)
  local p = (n - n % 2) / 2 -- parent position in heap array
  h[n] = k -- insert at a leaf
  t[k] = v
  while n > 1 and t[h[p]] < v do -- climb heap?
    h[p], h[n] = h[n], h[p]
    n = p
    p = (n - n % 2) / 2
  end
end

local function pop (h)
  local t = h.nodes
  local h = h.heap
  local s = #h
  assert(s > 0, "cannot pop from empty heap")
  local e = h[1] -- min (heap root)
  local r = t[e]
  local v = t[h[s]]
  h[1] = h[s] -- move leaf to root
  h[s] = nil -- remove leaf
  t[e] = nil
  s = s - 1
  local n = 1 -- node position in heap array
  local p = 2 * n -- left sibling position
  if s > p and t[h[p]] < t[h[p + 1]] then
    p = 2 * n + 1 -- right sibling position
  end
  while s >= p and t[h[p]] > v do -- descend heap?
    h[p], h[n] = h[n], h[p]
    n = p
    p = 2 * n
    if s > p and t[h[p]] < t[h[p + 1]] then
      p = 2 * n + 1
    end
  end
  return e, r
end

local function isempty (h) return h.heap[1] == nil end

function new ()
  return setmetatable({heap = {}, nodes = {}},
      {__index = {push=push, pop=pop, isempty=isempty}})
end

-- http://lua-users.org/lists/lua-l/2007-07/msg00482.html

-- h = Heap.new()
-- for i=1,10 do h:push(i, math.random()) end
-- while not h:isempty() do print(h:pop()) end
--3       0.83096534611237
--7       0.67114938407724
--6       0.52970019333516
--2       0.51941637206795
--1       0.38350207748986
--9       0.38341565075489
--10      0.066842237518561
--5       0.053461635044525
--4       0.034572110527461
--8       0.0076981862111474

---Note that keys can be arbitrary:

-- for i=1,10 do h:push(math.random()>0.5 and newproxy() or {}, math.random()) end
--> while not h:isempty() do print(h:pop()) end
--table: 0x30b130 0.98255028621412
--table: 0x30b4c0 0.89765628655332
--userdata: 0x30b264      0.8847071285754
--userdata: 0x30b044      0.75335583498392
--userdata: 0x30b474      0.47773176500468
--table: 0x30b270 0.43641140565109
--table: 0x30b480 0.2749068403034
--table: 0x30b4a0 0.16650720041548
--userdata: 0x30b064      0.072685882948658
--userdata: 0x30b4f4      0.060564327547589
