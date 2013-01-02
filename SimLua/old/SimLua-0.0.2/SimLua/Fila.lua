-- Fila.lua
-- A simple priority queue implementation - partial ordenation

local assert, setmetatable = assert, setmetatable
local print = print

module(...)

local function push (h, k, v)
  assert(v ~= nil, "cannot push nil")
  h.heap[#h.heap + 1] = k
  h.nodes[k] = v
end

local function pop (h)
  local t = h.nodes
  local h = h.heap
  local s = #h
  assert(s > 0, "cannot pop from empty heap")
  if s == 1 then
    local e = h[1]
    local r = t[e]
    h[1] = nil
    t[1] = nil
    return e, r
  end
  for j=s-1, 1, -1 do
    if t[h[j]] < t[h[s]] then
      h[j], h[s] = h[s], h[j] 
    end
  end
  local e = h[s]
  local r = t[e]
  h[s] = nil
  t[e] = nil
  return e, r
end

local function isEmpty (h) return h.heap[1] == nil end

function create ()
  return setmetatable({heap = {}, nodes = {}},
      {__index = {push=push, pop=pop, isEmpty=isEmpty}})
end