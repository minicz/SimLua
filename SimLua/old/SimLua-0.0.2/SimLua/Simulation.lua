#!/usr/bin/env lua

local Heap = require "SimLua.Heap"
local create = coroutine.create
local resume = coroutine.resume


--require "Process"

-- Simulation 0.0.1 Implements SimLua Processes, Resources, Buffers, and the backbone
-- simulation scheduling by coroutine calls. Provides data collection through classes 
-- Monitor and Tally.
--
-- Based on SimPy 1.9.1
--
-- LICENSE:
-- Copyright (C) 2008  Marcio F. Minicz
-- mailto: TODO
--
--     This library is free software; you can redistribute it and/or
--     modify it under the terms of the GNU Lesser General Public
--     License as published by the Free Software Foundation; either
--     version 2.1 of the License, or (at your option) any later version.
--
--     This library is distributed in the hope that it will be useful,
--     but WITHOUT ANY WARRANTY; without even the implied warranty of
--     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
--     Lesser General Public License for more details.
--
--     You should have received a copy of the GNU Lesser General Public
--     License along with this library; if not, write to the Free Software
--     Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
-- END OF LICENSE
--
-- **Change history:**
--
--     20 Jul 2008: Version 0.0.2
--         - function activate(), allEventTimes(), simulate()
--
--     06 Jul 2008: Version 0.0.1
--         - yield values and global variables defined
--         - functions: initialize(), now(), stopSimulation()
--
--     01 Mar 2008:
--         - Start of 1.9.1 bugfix release
--
-- ** Next Versions**
--
-- Basic statisctics
-- Lua Lanes to multithreading?!?
--        http://kotisivu.dnainternet.net/askok/bin/lanes/index.html
--


-- yield keywords
local hold = "hold"
local passivate = "passivate"
local request = "request"
local release = "release"
local waitevent = "waitevent"
local queueevent = "queueevent"
local waituntil = "waituntil"
local get = "get"
local put = "put"

local endtime = 0       -- when simulation will finish
local t = 0             -- current simulation time
local e = nil
local stop = True

function initialize()
    e = Heap.create()
    t = 0
    stop = false
end

function now()
    -- what simulation time is now?
    return t
end

function stopSimulation()
    -- stop simulation run
    stop = true
end

function simulate(etime)
    -- Schedules Processes/semi-coroutines until time 'etime'

    stop = false
    assert(e, "Fatal Error: Simulation not initializes")
    assert(not e:isEmpty(), "SimLua: No activities scheduled")
    assert(type(etime)=="number", "Function simulate need a number parameter.")
    endtime = etime

    while not stop and t <= endtime do
        a, t = e:pop()
        ok, command, delta = resume(a)
        if command == "hold" then e:push(a, t+delta) end

        if e:isEmpty() then break end
    end
    e = nil
end

function activate(proc, at)
    -- Application function to activate passive process.
    assert(e, "Fatal error: simulation is not initializes (call initialize() first)")
    if at == nil  then at = t end
    assert(type(at)=="number", "Error: activate function (at is not a number)")
    
    --table.foreach(proc, print)
    --print("at", at)
    
    --if not obj.terminated and not obj.nextTime then
        --store generator reference in object; needed for reactivation
      --  obj.nextpoint=process
        local co = create(function () proc:go() end)
        e:push(co, at)
    --end
    --table.foreach(e.nodes, print)
    --table.foreach(e.heap,print)
end


function allEventTimes()
    -- Returns list of all times for which events are scheduled.
    print "--- Heap ---"
    table.foreach(e.heap, print)
    print "--- Node ---"
    table.foreach(e.nodes, print)
    --local h = Heap.create()
    --table.foreach(e.nodes, 
    --print("e", e, "h", h)
    --print(h:pop())
end