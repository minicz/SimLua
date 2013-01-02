#!/usr/bin/env lua

local setmetatable = metatable
local print = print
local activate, simulate = activate, simulate

require "SimLua.Simulation"

-- Car = Process:new{}
local Car = {name = "car"}
function Car:new(o)
    -- Process:new{name = name}
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    -- io.write(string.format("Criado carro: %s\n", self.name))
    return o
end

function Car:go()
    print(now(), self.name, "Starting")
    coroutine.yield(hold, 100)
    print(now(), self.name, "Arrived")
end

--math.randomseed(os.time())

initialize()
-- a new car
c1 = Car:new(); c1.name = "Car_01"
-- activate at time 6.0
activate(c1, 6.0)

-- a new car
c2 = Car:new(); c2.name = "Car_02"
-- activate at time 0.0
activate(c2)

-- start simulation
simulate(200)
print("Current time is ",now()) -- will print 106.0

-- Saida:
--
-- 0        Car_02  Starting
-- 6        Car_01  Starting
-- 100      Car_02  Arrived
-- 106      Car_01  Arrived
-- Current time is          106.0