
--
-- class Process
--
local assert, setmetatable = assert, setmetatable

module(...)

require "Heap"

local function Process.Create(p, name)
    -- the reference to this Process instances single process (==generator)

    if name then self.name = name end
    self.remainService = 0
    self.preempted = 0
    self.priority = {}
    self.getpriority = {}
    self.putpriority = {}
    self.terminated = false
    self.inInterrupt = false
    self.eventsFired = {}
end

local function Process.active(p)
    -- Retorna true se tiver aguardando algum evento agendado
    return self.nextTime and not self.inInterrupt
end

local function Process.passive(p)
    -- Retorna true se não estiver ativo ou se terminou. Pode ser (re)-ativado
    -- por outros processos
    return nextTime and not terminated
end

local function Process.terminated()
    -- Retorna true se o processo executou todas as ações
    return self.terminated
end

local function Process.interrupted()
    -- Retorna true se o processo foi interrompido por algum outro processo
    return self.inInterrupt and not self.terminated
end

local function Process.cancel(victim)
    -- Application function to cancel all event notices for this Process
    -- instance.
    e.unpost(victim)
end

function new ()
  return setmetatable(
    {nextpoint = nil,
    name = nil,
    nextTime = nil,         -- next activation time
    remainService = nil,
    preempted = nil,
    priority = nil,
    getpriority = nil,
    putpriority = nil,
    terminated = nil,
    inInterrupt = nil,
    eventsFired = nil},       -- which events process waited/queued for occurred 
    {__index = {push=push,
                pop=pop,
                isempty=isempty}})
end