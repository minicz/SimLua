from SimPy.Simulation import *
from random import *


class Car(Process):
  def __init__(self,name,cc):
    Process.__init__(self,name=name)
    self.cc = cc

  def go(self):
    #print now( ), self.name, "Starting"
    yield hold,self, uniform(50,200)
    #print now( ), self.name, "Arrived"

initialize( )
c = []
for i in range(100000):
  c.append(Car("Car"+str(i),200))
  activate(c[i],c[i].go( ),at=uniform(5,100)) # activate at time 6.0

simulate(until=2000000)
print 'Current time is ',now( ) # will print 106.0
