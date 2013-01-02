#!/usr/bin/env lua

require "SimLua.Heap"
Heap = SimLua.Heap

print "Teste"
at = 1
t = 10

assert(at < t, "erro")
print "Fim"

h = Heap.create()
for i=1,3 do h:push(i, math.random()) end
while not h:isEmpty() do print(h:pop()) end


Car = {name = "car"}
function Car:new(o)
    -- Process:new{name = name}
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    
    --io.write(string.format("Criado carro: %s\n", self.name))
    return o
end

function Car:go()
    print(self.name, "Starting")
end

local c1 = Car:new()
c1.name = "Car_01"
local c2 = Car:new()
c2.name = "Car_02"
Car.go(c1)
Car.go(c2)