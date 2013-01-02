require "SimLua.Simulation"

Car = Process:create{}
function Car.create(name, cc)
    Process:create{name = name}
    self.cc = cc
end

function Car.go()
    print(now(), self.name, "Starting")
    coroutine.yield(hold, 100.0)
    print(now(), self.name, "Arrived")
end

initialize()
c1  = Car{"Car1", 2000}       -- a new car
activate{c1, c1.go(), at=6.0}  -- activate at time 6.0
c2  = Car{"Car2", 1600}
activate{c2, c2.go()}         -- activate at time 0
simulate(until = 200)
print("Current time is ",now()) -- will print 106.0

---->from SimPy.Simulation import *
---->
---->class Car(Process):
---->  def __init__(self,name,cc):
---->     Process.__init__(self,name=name)
---->     self.cc = cc
---->
---->  def go(self):
---->     print now( ), self.name, "Starting"
---->     yield hold,self,100.0
---->     print now( ), self.name, "Arrived"
---->
---->initialize( )
---->c1  = Car("Car1",2000)       # a new car
---->activate(c1,c1.go( ),at=6.0) # activate at time 6.0
---->c2  = Car("Car2",1600)
---->activate(c2,c2.go( ))        # activate at time 0
---->simulate(until=200)
---->print 'Current time is ',now( ) # will print 106.0
---->
---->
---->
---->
----># Saida:
---->
---->#0 Car2 Starting
---->#6.0 Car1 Starting
---->#100.0 Car2 Arrived
---->#106.0 Car1 Arrived
---->#Current time is  106.0
---->