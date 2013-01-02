#!/usr/bin/env lua

require "SimLua.Simulation"

-- Car = Process:new{}
Car = {name = "car"}
function Car:new(o)
    -- Process:new{name = name}
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    -- io.write(string.format("Criado carro: %s\n", self.name))
    return o
end

function Car:go()
    --print(now(), self.name, "Starting")
    coroutine.yield(hold, math.random(50,200))
    --print(now(), self.name, "Arrived")
end

math.randomseed(os.time())

initialize()
c = {}

for i=1,100000 do
    --print("Carro: "..i)
    c[i] = Car:new(); c[i].name = "Car"..i
    activate(c[i], math.random(5,100))
end

-- start simulation
simulate(1000000)
print("Current time is ",now()) -- will print 106.0
