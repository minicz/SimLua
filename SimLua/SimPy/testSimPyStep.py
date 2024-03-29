#!/usr/bin/env python
from SimPy.SimulationStep import *
from SimPy.MonitorTest import *
import unittest
from random import random
# $Revision: 1.1.1.16 $ $Date: 2008/03/03 13:56:00 $
"""testSimPyStep.py 
SimPy version 1.9.1 
Unit tests for SimulationStep.

**Change history:**
# 2002 11 15 Added tests for priority queues and preemption
# 2002 11 22 testing problem in accum
# 2003 03 30 added tests for SEP001v17 interrupts
# 2003 04 05 added test for interruptReset
# 2003 04 08 added tests for process state transitions
# 2003 04 10 changed to "self.cancel(victim)" syntax
# 2003 04 13 removed dummy init assertions
# 2004 02 28 added test for monitored queues (gav)
# 2004 05 03 corrected test for monitored queues (gav)
# 2004 05 15 first version of testSimPyStep; just
#            tests compatibility with Simulation.py
# 2004 09 17 added tests for waitevent, queueevent, waituntil (new in 1.5)
# 2005 05 19 added tests for compound yield statements (reneging)
# 2006 01 15 added tests for Store and Level and the get/put yield statements
# 2006 02 02 removed histogram plotting suite
# 2006 05 10 changed test testStatic for Level to test that float type 
             supported for initialBuffered
# 2006 05 16 added tests for Store and Level to test basic Producer/Consumer 
             principles
# 2006 10 16 added tests for compound get statement (Unmonitored Store/Level)
# 2006 10 17 added tests for compound put statement (Unmonitored Store/Level)
# 2007 01 08 added tests for monitoring of Store/Level with compound get/put
# 2007 01 08 added test for Store with filter function
# 2007 12 05 added tests for start method (Process)
# 2008 03 03 added test for nested preempts

#'$Revision: 1.1.1.16 $ $Date: 2008/03/03 13:56:00 $ kgm'

"""
__version__ = '1.9.1 $Revision: 1.1.1.16 $ $Date: 2008/03/03 13:56:00 $ '
print "testSimPyStep.py %s"%__version__

## -------------------------------------------------------------
##                    TEST SIMULATION
## -------------------------------------------------------------
class P(Process):
   """ P class for testing"""
   def __init__(self,name="",T = 0):
        Process.__init__(self)
        self.name=name
        self.T = T
        
   def execute(self):       
        yield hold,self,self.T

class PActions(Process):
   """ PActions class for testing"""
   def __init__(self,name="",T = 0):
        Process.__init__(self)
        self.name=name
        self.T = T
        
   def ACTIONS(self):       
        yield hold,self,self.T
        
class makeSimulationtestcase(unittest.TestCase):
   """ Tests of simulation
   """
   def testInit(self):
        """Test initialisation
        """
        initialize()
        simulate(until=10)
        assert(now()==0),"time not 0" 

   def testActivate(self):
        """Test activate()
        """
        P1 = P(name="P1",T=100.0)
        initialize()
        activate(P1,P1.execute(),0)
        simulate(until=5)
        assert(now()==5),"Simulate stopped at %s not %s"%(now(),5)
        
   def testStart(self):
       """Test start method
       """
       P1 = P(name="P1",T=100.0)
       initialize()
       P1.start(P1.execute(),0)
       simulate(until=5)
       assert(now()==5),"Simulate stopped at %s not %s"%(now(),5)

   def testStartActions(self):
      """Test start method with ACTIONS PEM
      """
      P1 = PActions(name="P1",T=100.0)
      initialize()
      P1.start()
      simulate(until=5)
      assert(now()==5),"Simulate stopped at %s not %s"%(now(),5)  

   def testYield(self):
        """Test yield hold and simulate(until)
        """
        P1 = P(name="P1",T=10)
        initialize()
        activate(P1,P1.execute(),0)
        simulate(until=5)
        assert(now()==5),"Simulate stopped at %s not %s"%(now(),5)
        ## should stop at 0 for next event is at 10s
        P2 = P(name="P2",T=10)
        initialize()
        activate(P2,P2.execute(),0)
        simulate(until=20)
        assert(now()==10),"P1 hold to %s not %s"%(now(),10)
        
       
def makeSSuite():
    suite = unittest.TestSuite()
    testInit = makeSimulationtestcase("testInit")
    testActivate = makeSimulationtestcase("testActivate")
    testStart=makeSimulationtestcase("testStart")
    testStartActions=makeSimulationtestcase("testStartActions")
    testYield = makeSimulationtestcase("testYield")
    ##testrequest3 = makeSimulationtestcase("testrequest3")
    ##testrequest4 = makeSimulationtestcase("testrequest4")
    suite.addTests([testInit,testActivate,testStart,testStartActions,testYield])
    return suite

## -------------------------------------------------------------
##                    TEST RESOURCES
## -------------------------------------------------------------

class Job(Process):
   """ Job class for testing"""
   def __init__(self,server=None,name=""):
        Process.__init__(self)
        self.name=name
        self.R=server
        
   def execute(self):       
        yield request,self,self.R


class makeResourcetestcase(unittest.TestCase):
   """ First simple tests of Resources
   """
   def testInit(self):
        """Test initialisation"""
        R = Resource()
        assert R.name == "a_resource", "Not null name"
        assert R.capacity == 1, "Not unit capacity"
        assert R.unitName =="units", "Not the correct unit name"
        R = Resource(name='',capacity=1)
        assert R.name == "", "Not null name"
        assert R.capacity == 1, "Not unit capacity"
        assert R.unitName =="units", "Not the correct unit name"
        R = Resource(capacity=3,name="3-version",unitName="blobs")
        assert R.name =="3-version" , "Wrong name, it is"+R.name
        assert R.capacity == 3, "Not capacity 3, it is "+`R.capacity`
        assert R.unitName =="blobs", "Not the correct unit name"
        ## next test 0 capacity is allowed
        R = Resource(capacity=0,name="0-version")
        assert R.capacity ==0, "Not capacity 0, it is "+`R.capacity`
       
   def testrequest(self):
        """Test request"""
        ## NB this next call should be changed to
        ## R = Resource() when Simulation is fixed
        R0 = Resource(name='',capacity=0)
        assert R0.name == "", "Not null name"
        assert R0.capacity == 0, "Not capacity 0, it is "+`R0.capacity`
        ## now test requesting: ------------------------------------
        initialize()
        R1 = Resource(capacity=0,name="3-version",unitName="blobs")
        J= Job(name="job",server=R1) 
        activate(J,J.execute(), at=0.0) # this requests a unit of R1
        ## when simulation starts
        simulate(until=10.0)
        assert R1.n == 0 , "Should be 0, it is "+str(R1.n)
        lenW = len(R1.waitQ)
        assert lenW==1,"Should be 1, it is "+str(lenW)
        assert len(R1.activeQ)==0,"len activeQ Should be 0, it is "+\
        str(len(R1.activeQ))

   def testrequest2(self):
        """Test request2 with capacity = 1"""
        ## now test requesting: ------------------------------------
        initialize()
        R2 = Resource(capacity=1,name="3-version",unitName="blobs")
        J2= Job(name="job",server=R2) 
        activate(J2,J2.execute(), at=0.0) # requests a unit of R2
        ## when simulation starts
        simulate(until = 10.0)
        assert R2.n == 0 , "Should be 0, it is "+str(R2.n)
        lenW = len(R2.waitQ)
        lenA = len(R2.activeQ)
        assert lenW==0,"lenW Should be 0, it is "+str(lenW)
        assert lenA==1,"lenA Should be 1, it is "+str(lenA)

   def testrequest3(self):
        """Test request3 with capacity = 1 several requests"""
        ## now test requesting: ------------------------------------
        initialize()
        R3 = Resource(capacity=1,name="3-version",unitName="blobs")
        J2= Job(name="job",server=R3) 
        J3= Job(name="job",server=R3)
        J4= Job(name="job",server=R3) 
        activate(J2,J2.execute(), at=0.0) # requests a unit of R3
        activate(J3,J3.execute(), at=0.0) # requests a unit of R3
        activate(J4,J4.execute(), at=0.0) # requests a unit of R3
        ## when simulation starts
        simulate(until = 10.0)
        assert R3.n == 0 , "Should be 0, it is "+str(R3.n)
        lenW = len(R3.waitQ)
        lenA = len(R3.activeQ)
        assert lenW==2,"lenW Should be 2, it is "+str(lenW)
        assert R3.waitQ==[J3,J4],"WaitQ wrong"+str(R3.waitQ)
        assert lenA==1,"lenA Should be 1, it is "+str(lenA)
        assert R3.activeQ==[J2],"activeQ wrong, it is "+str(R3.activeQ[0])

   def testrequest4(self):
        """Test request4 with capacity = 2 several requests"""
        ## now test requesting: ------------------------------------
        initialize()
        R3 = Resource(capacity=2,name="4-version",unitName="blobs")
        J2= Job(name="job",server=R3) 
        J3= Job(name="job",server=R3)
        J4= Job(name="job",server=R3) 
        activate(J2,J2.execute(), at=0.0) # requests a unit of R3
        activate(J3,J3.execute(), at=0.0) # requests a unit of R3
        activate(J4,J4.execute(), at=0.0) # requests a unit of R3
        ## when simulation starts
        simulate(until = 10.0)
        assert R3.n == 0 , "Should be 0, it is "+str(R3.n)
        lenW = len(R3.waitQ)
        lenA = len(R3.activeQ)
        assert lenW==1,"lenW Should be 1, it is "+str(lenW)
        assert R3.waitQ==[J4],"WaitQ wrong"+str(R3.waitQ)
        assert lenA==2,"lenA Should be 2, it is "+str(lenA)
        assert R3.activeQ==[J2,J3],"activeQ wrong, it is "+str(R3.activeQ[0])
        
#------- Test Priority Queues
        
   def testrequestPriority(self):
        """Test PriorityQ, with no preemption, 0 capacity"""
        class Job(Process):
           """ Job class for testing"""
           def __init__(self,server=None,name=""):
              Process.__init__(self)
              self.name=name
              self.R=server
        
           def execute(self,priority):
              yield request,self,self.R,priority
        
        initialize()
        Rp = Resource(capacity=0,qType=PriorityQ)
        J5 = Job(name="job 5",server=Rp)
        J6 = Job(name="job 6",server=Rp)
        J7 = Job(name="job 7",server=Rp)
        activate(J5,J5.execute(priority=3))
        activate(J6,J6.execute(priority=0))
        activate(J7,J7.execute(priority=1))
        simulate(until=100)
        assert Rp.waitQ == [J5,J7,J6],"WaitQ wrong"+str([(x.name,x.priority[Rp]) for x in Rp.waitQ])

        """Test PriorityQ mechanism"""

        def sorted(q):
           if not q or len(q) == 1:
              sortok=1
              return sortok
           sortok = q[0] >= q[1] and sorted(q[2:])
           return sortok

        initialize()
        Rp=Resource(capacity=0,qType=PriorityQ)
        for i in range(10):
           J=Job(name="job "+str(i),server=Rp) 
           activate(J,J.execute(priority=random()))
        simulate(until=1000)
        qp=[x._priority[Rp] for x in Rp.waitQ]
        assert sorted(qp),"waitQ not sorted by priority: "+str([(x.name,x._priority[Rp]) for x in Rp.waitQ])
      

   def testrequestPriority1(self):
        """Test PriorityQ, with no preemption, capacity == 1"""
        class Job(Process):
           """ Job class for testing"""
           def __init__(self,server=None,name=""):
              Process.__init__(self)
              self.name=name
              self.R=server
        
           def execute(self,priority):
              yield request,self,self.R,priority
              
        initialize()
        Rp = Resource(capacity=1,qType=PriorityQ)
        J5 = Job(name="job 5",server=Rp)
        J6 = Job(name="job 6",server=Rp)
        J7 = Job(name="job 7",server=Rp)
        activate(J5,J5.execute(priority=2))
        activate(J6,J6.execute(priority=4))
        activate(J7,J7.execute(priority=3))
        simulate(until=100)
        assert Rp.waitQ == [J6,J7],"WaitQ wrong "+str([(x.name,x._priority[Rp]) for x in Rp.waitQ])

   def testrequestPriority2(self):
       """Test PriorityQ, with preemption, capacity == 1"""
       class nuJob(Process):
          def __init__(self,name):
             Process.__init__(self,name)
             
          def execute(self,res,priority):
             self.preempt=len(res.activeQ) > 0 and priority > res.activeQ[-1]._priority[res]
             t=now()
             yield request,self,res,priority
             if self.preempt:
                assert len(res.waitQ) == 1, "No preemption "+"activeQ= "+str(res.activeQ[0].name)
             yield hold,self,30
             t1=now()
             if self.preempt:
                assert t+30 == t1,"Wrong completion time for preemptor "+self.name
             else:
                assert t+60 == t1, "Wrong completion time for preempted "+self.name+" "+str(now())
             yield release,self,res
             
       initialize()
       res=Resource(name="server",capacity=1,qType=PriorityQ,preemptable=1)
       n1=nuJob(name="nuJob 1")
       n2=nuJob(name="nuJob 2")
       activate(n1,n1.execute(res,priority=0))
       activate(n2,n2.execute(res,priority=1),at=15)
       simulate(until=100)

   def testrequestPriority3(self):
       """Test preemption of preemptor"""
       class nuJob(Process):
          seqOut=[]
          def __init__(self,name):
             Process.__init__(self,name)
             self.serviceTime=30
             
          def execute(self,res,priority):
             self.preempt=len(res.activeQ) > 0 and priority > res.activeQ[-1]._priority[res]
             nrwaiting=len(res.waitQ)
             yield request,self,res,priority
             if self.preempt:
                assert len(res.waitQ) == nrwaiting + 1, "No preemption "+"activeQ= "+str(res.activeQ[0].name)
             yield hold,self,self.serviceTime
             yield release,self,res
             nuJob.seqOut.append((self,now()))
             

            
       initialize()
       res=Resource(name="server",capacity=1,qType=PriorityQ,preemptable=1)
       n1=nuJob(name="nuJob 1")
       n2=nuJob(name="nuJob 2")
       n3=nuJob(name="nuJob 3")
       activate(n1,n1.execute(res,priority=-1))
       start2=10
       activate(n2,n2.execute(res,priority=0),at=start2)
       start3=20
       activate(n3,n3.execute(res,priority=1),at=start3)
       simulate(until=100)
       assert [x[1] for x in nuJob.seqOut] == [start3+n3.serviceTime,start2+2*n2.serviceTime,90],\
              "Wrong service sequence/times: "+str([x for x in nuJob.seqOut])
       
   def testrequestNestedPreempt(self):
      """Test that a process can preempt another process holding multiple resources
      """
      class Requestor(Process):
          def run(self,res1,res2,res3,priority=1):
              yield request,self,res1,priority
              yield request,self,res2,priority
              yield request,self,res3,priority
              record.observe(y=self.name)
              yield hold,self,100
              record.observe(y=self.name)
              yield release,self,res3
              yield release,self,res2
              yield release,self,res1
                
      initialize()
      outer=Resource(name="outer",qType=PriorityQ,preemptable=True)
      inner=Resource(name="inner",qType=PriorityQ,preemptable=True)
      innermost=Resource(name="innermost",qType=PriorityQ,preemptable=True)
      record=Monitor()
      r1=Requestor("r1") 
      activate(r1,r1.run(res1=outer,res2=inner,res3=innermost,priority=1))
      r2=Requestor("r2")
      activate(r2,r2.run(res1=outer,res2=inner,res3=innermost,priority=10),at=50)
      simulate(until=200)
      assert record==[[0,"r1"],[50,"r2"],[150,"r2"],[200,"r1"]],\
              "was %s; preempt did not work"%record


   def testmonitored(self):
      """ test monitoring of number in the two queues, waitQ and activeQ
      """
      class Job(Process):
          def __init__(self,name):
             Process.__init__(self,name)
             
          def execute(self,res):
             yield request,self,res
             yield hold,self,2
             yield release,self,res
             
      initialize()
      res=Resource(name="server",capacity=1,monitored=1)
      n1=Job(name="Job 1")
      n2=Job(name="Job 2")
      n3=Job(name="Job 3")
      activate(n1,n1.execute(res),at=2)
      activate(n2,n2.execute(res),at=2)
      activate(n3,n3.execute(res),at=2) # 3 arrive at 2
      simulate(until=100)
      assert res.waitMon == [[2, 1], [2, 2], [4, 1], [6, 0]],'Wrong waitMon:%s'%res.waitMon
      assert res.actMon == [[2, 1], [4, 0], [4, 1], [6, 0], [6, 1], [8, 0]],'Wrong actMon:%s'%res.actMon
      #print res.actMon
      assert res.waitMon.timeAverage() == (0*2+2*2+1*2)/8.0,'Wrong waitMon.timeAverage:%s'%res.waitMon.timeAverage()
      
               
def makeRSuite():
    suite = unittest.TestSuite()
    testInit = makeResourcetestcase("testInit")
    testrequest = makeResourcetestcase("testrequest")
    testrequest2 = makeResourcetestcase("testrequest2")
    testrequest3 = makeResourcetestcase("testrequest3")
    testrequest4 = makeResourcetestcase("testrequest4")
    testrequestPriority = makeResourcetestcase("testrequestPriority")
    testrequestPriority1 = makeResourcetestcase("testrequestPriority1")
    testrequestPriority2 = makeResourcetestcase("testrequestPriority2")
    testrequestPriority3 = makeResourcetestcase("testrequestPriority3")
    testrequestNestedPreempt = makeResourcetestcase("testrequestNestedPreempt")    
    testmonitored = makeResourcetestcase("testmonitored")
    suite.addTests([testInit,testrequest,testrequest2,testrequest3,testrequest4,testrequestPriority,
                    testrequestPriority1,testrequestPriority2,testrequestPriority3,
                    testrequestNestedPreempt,testmonitored]) 
    return suite
      

##=====================================================
##                   Test Interrupts
##=====================================================


class Interruptor(Process):
   def __init__(self):
      Process.__init__(self)

   def breakin(self,waitbefore,howoften=1):
      for i in range(howoften):
         yield hold,self,waitbefore
         self.interrupt(victim)

class Interrupted(Process):
   def __init__(self):
      Process.__init__(self)

   def myActivity(self,howlong,theEnd=200):
      global igothit
      igothit={}
      while now()<=theEnd:
         yield hold,self,howlong
         if self.interrupted():
            byWhom=self.interruptCause
            igothit[now()]=byWhom
         else:
            pass     
      
class makeInterrupttestcase(unittest.TestCase):
   """
   Tests interrupts as defined in SEP001v17
   """
   def testInterrupt1(self):
      """
      Test single interrupt during victim activity
      """
      global victim
      initialize()
      breaker=Interruptor()
      activate(breaker,breaker.breakin(10))
      victim=Interrupted()
      activate(victim,victim.myActivity(100))
      simulate(until=200)
      assert igothit[10] == breaker, "Not interrupted at 10 by breaker"
      assert len(igothit) == 1 , "Interrupted more than once"

   def testInterrupt2(self):
      """
      Test multiple interrupts during victim activity
      """
      global victim
      initialize()
      breaker=Interruptor()
      activate(breaker,breaker.breakin(10,howoften=3))
      victim=Interrupted()
      activate(victim,victim.myActivity(100))
      simulate(until=200)
      for i in (10,20,30):
         assert igothit[i] == breaker, "Not interrupted at %s by breaker" %i
      assert len(igothit) == 3 , "Interrupted wrong number of times"

   def testInterrupt3(self):
      """
      Test interrupts after victim activity
      """
      global victim
      initialize()
      breaker=Interruptor()
      activate(breaker,breaker.breakin(50,howoften=5))
      victim=Interrupted()
      activate(victim,victim.myActivity(10,theEnd=10))
      simulate(until=200)
      assert len(igothit) == 0 , "There has been an interrupt after victim lifetime"

   def testInterrupt4(self):
      """
      Test multiple interrupts by multiple processes during victim activity
      """
      global victim
      initialize()
      breaker1=Interruptor()
      activate(breaker1,breaker1.breakin(15,howoften=3))
      breaker2=Interruptor()
      activate(breaker2,breaker2.breakin(20,howoften=3))
      victim=Interrupted()
      activate(victim,victim.myActivity(100))
      simulate(until=200)
      for i in (15,30,45):
         assert igothit[i] == breaker1, "Not interrupted at %s by breaker1" %i
      for i in (20,40,60):
         assert igothit[i] == breaker2, "Not interrupted at %s by breaker2" %i
      assert len(igothit) == 6 , "Interrupted wrong number of times"

   def testInterrupt5(self):
      """
      Test reset of 'interrupted' state.
      """
      global victim
      initialize()
      breaker=Interruptor()
      victim=Interrupted()
      
      def newProcess(self):
         while True:
            assert not self.interrupted(),"Incorrectly interrupted"
            yield hold,self,100
            if self.interrupted():
               self.interruptReset()
               assert not self.interrupted(),"Incorrectly interrupted"
               
      victim.newProcess=newProcess
      activate(victim,newProcess(victim))
      activate(breaker,breaker.breakin(10,howoften=3))
      simulate(until=1000)   
         
def makeISuite():
   suite=unittest.TestSuite()
   testInterrupt1=makeInterrupttestcase("testInterrupt1")
   testInterrupt2=makeInterrupttestcase("testInterrupt2")
   testInterrupt3=makeInterrupttestcase("testInterrupt3")
   testInterrupt4=makeInterrupttestcase("testInterrupt4")
   testInterrupt5=makeInterrupttestcase("testInterrupt5")
   suite.addTests([testInterrupt1,testInterrupt2,testInterrupt3,testInterrupt4,testInterrupt5])
   return suite   

## -------------------------------------------------------------
##                    TEST PROCESS STATES
## -------------------------------------------------------------

class PS1(Process):
   def __init__(self):
      Process.__init__(self)
            
   def life1(self):
      yield hold,self,10

   def life2(self):
      yield hold,self,10
      yield passivate,self
      yield hold,self,10

class Observer1(Process):
   def __init__(self):
      Process.__init__(self)

   def look1(self,p):
      assert p.active(),"p not active"
      assert not p.passive(), "p passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"
      yield hold,self,11
      assert not p.active(),"p active"
      assert not p.passive(),"p passive"
      assert p.terminated(),"p not terminated"
      assert not p.interrupted(),"p interrupted"

   def look2(self,p):
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p not terminated"
      assert not p.interrupted(),"p interrupted"
      activate(p,p.life1())
      yield hold,self,11
      assert not p.active(),"p active"
      assert not p.passive(),"p not passive"
      assert p.terminated(),"p not terminated"
      assert not p.interrupted(),"p interrupted"

   def look3(self,p):
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p not terminated"
      assert not p.interrupted(),"p interrupted"
      activate(p,p.life2())
      yield hold,self,11
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"

   def look4(self,p):
      yield hold,self,5
      assert p.active(),"p not active"
      assert not p.passive(),"p passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"
      self.cancel(p)
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"
      reactivate(p)
      assert p.active(),"p not active"
      assert not p.passive(),"p passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"
      yield hold,self
      assert not p.active(),"p active"
      assert not p.passive(),"p passive"
      assert p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"

   def look5(self,p):
      yield hold,self,11
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"
      self.cancel(p)
      assert not p.active(),"p active"
      assert p.passive(),"p not passive"
      assert not p.terminated(),"p terminated"
      assert not p.interrupted(),"p interrupted"

class PS2(Process):
   def __init__(self):
      Process.__init__(self)

   def life1(self,res):
      yield hold,self,1
      yield request,self,res
      yield hold,self,5
      yield request,self,res

   def life2(self,res):
      yield request,self,res
      assert self.interrupted(),"p not interrupted"
      assert self.queuing(res)
      self.interruptReset()
      assert not self.interrupted(), "p interrupted"
      assert self.queuing(res)

class Observer2(Process):
   def __init__(self):
      Process.__init__(self)

   def look1(self,p1,p2,res):
      assert p1.active(), "p1 not active"
      assert not p1.queuing(res), "p1 queuing"
      assert p2.active(), "p2 noit active"
      assert not p2.queuing(res), "p2 queuing"
      yield hold,self,2
      assert p1.active(), "p1 not active"
      assert not p1.queuing(res), "p1 queuing"
      assert p2.passive(), "p2 active"
      assert p2.queuing(res), "p2 not queuing"

   def look2(self,p,res):
      yield request,self,res
      yield hold,self,5
      assert p.passive(),"p not passive"
      assert p.queuing(res),"p not queuing for resource"
      assert not p.interrupted(), "p interrupted"
      self.interrupt(p)
      yield hold,self

class makePStatetestcase(unittest.TestCase):
   """
   Tests states and state transitions as defined in SEP003
   """
   
   def testState1(self):
      """
      Tests state transitions by hold
      """
      ## active => hold => terminated
      initialize()
      p=PS1()
      activate(p,p.life1())
      ob=Observer1()
      activate(ob,ob.look1(p),prior=True)
      simulate(until=12)

   def testState2(self):
      """
      Tests state transitions by activate and passivate
      """
      ## passive => activate => hold => terminated
      initialize()
      p=PS1()
      ob1=Observer1()
      activate(ob1,ob1.look2(p))
      simulate(until=12)
      ## passive => activate => hold => active => passivate => passive
      initialize()
      p1=PS1()
      ob2=Observer1()
      activate(ob2,ob2.look3(p1),prior=True)
      simulate(until=12)

   def testState3(self):
      """
      Tests state transitions by cancel()
      """
      ## active => cancel => passive => reactivate => active => terminated
      initialize()
      p2=PS1()
      activate(p2,p2.life1())
      ob3=Observer1()
      activate(ob3,ob3.look4(p2))
      simulate(until=12)

      ## passive => cancel => passive 
      initialize()
      p3=PS1()
      activate(p3,p3.life2())
      ob4=Observer1()
      activate(ob4,ob4.look5(p3))
      simulate(until=12)

   def testState4(self):
      """
      Test request/release state transitions
      """
      ## not queuing,active => request => queuing,passive => release => not queuing,active
      initialize()
      res=Resource(capacity=1)
      pq1=PS2()
      activate(pq1,pq1.life1(res))
      pq2=PS2()
      activate(pq2,pq2.life1(res))
      obq1=Observer2()
      activate(obq1,obq1.look1(pq1,pq2,res))
      simulate(until=12)

      ## queuing,passive => interrupt =>  queuing, interrupted => interruptRest => queuing, not interrupted
      initialize()
      res=Resource(capacity=1)
      pq3=PS2()
      activate(pq3,pq3.life2(res))
      obq2=Observer2()
      activate(obq2,obq2.look2(pq3,res),prior=True)
      simulate(until=12)
      
      
      
def makePSuite():
   suite=unittest.TestSuite()
   testState1=makePStatetestcase("testState1")
   testState2=makePStatetestcase("testState2")
   testState3=makePStatetestcase("testState3")
   testState4=makePStatetestcase("testState4")
   suite.addTests([testState1,testState2,testState3,testState4])
   return suite

## -------------------------------------------------------------
##                    TEST Events/Signals
## -------------------------------------------------------------

class SignalProcess(Process):
   def makeSignal(self,ev1,ev2):
      yield hold,self,1
      ev1.signal("from SignalProcess")
      while ev2.queues:
         nq0=len(ev2.queues)
         ev2.signal("from SignalProcess")
         assert len(ev2.queues)==(nq0-1),"wrong number of processes dequeued"

class WaitProcess(Process):
   def waitForSig(self,ev1):
      yield waitevent,self,ev1
      assert ev1.waits==[],"not all processes waiting for event out of waiting list"
      assert ev1 in self.eventsFired,"did not record firing event"
      
class QueueProcess(Process):
   def queueForSig(self,ev2):
      yield queueevent,self,ev2
      assert ev2 in self.eventsFired,"did not record firing event"
      
class SignalProcessOR(Process):
   def makeSignal(self,ev1,ev2):
      yield hold,self,1
      ev1.signal("from SignalProcess")
      yield hold,self,3
      assert len(ev2.queues)==QueueProcessOR.nrProcesses,"wrong number of processes queuing for event ev2"
      while ev2.queues:
         nq0=len(ev2.queues)
         ev2.signal("from SignalProcess")
         assert len(ev2.queues)==(nq0-1),"wrong number of processes dequeued"
      assert not ev2.queues,"not all processes queuing for ev2 dequeued"

class WaitProcessOR(Process):
   def waitForSig(self,evset):
      yield waitevent,self,evset
      for e in evset:
         assert e.waits==[],"process not out of waiting list for all events in OR"
         
class WaitProcessOR1(Process):
    def signalandwait(self):
      e1=SimEvent()
      e1.signal()
      e2=SimEvent()
      e2.signal()
      yield waitevent,self,[e1,e2]
      assert self.eventsFired==[e1,e2],"eventsFired does not report all events"
        
      
class QueueProcessOR(Process):
    nrProcesses=0
    def __init__(self):
        Process.__init__(self)
        QueueProcessOR.nrProcesses+=1
    def queueForSig(self,evset):
      yield queueevent,self,evset
      occurred=False
      for e in evset:
          occurred=occurred or (e in self.eventsFired)
      assert occurred,"queuing process activated by wrong event(s)"
      
class QueueProcessOR1(Process):
    def signalandqueue(self):
        e1=SimEvent()
        e1.signal()
        e2=SimEvent()
        e2.signal()
        yield queueevent,self,[e1,e2]
        assert self.eventsFired==[e1,e2],\
                "(queueevent) eventsFired does not report all fired events"
        
class makeEtestcase(unittest.TestCase):
   """
   Test SimEvent/signal as introduced with SimPy 1.5
   """
   
   def testSimEvents1(self):
      """
      Tests basic signal semantics
      """
      e=SimEvent()
      e.signal("param")
      assert e.occurred,"signal does not set 'occurred' to True"
      assert e.signalparam=="param","signal parameter wrong"
      e.signal()
      assert e.signalparam is None,"signal with no parameter did not overwrite signalparam"
      e.signal()
      assert e.occurred,"multiple calls to signal do not set 'occurred'"
      
   def testSimEvents2(self):
      """
      Tests basic waiting and queuing semantics
      """
      initialize()
      ev1=SimEvent("ev1")
      ev2=SimEvent("ev2")
      w1=WaitProcess()
      activate(w1,w1.waitForSig(ev1))
      w2=WaitProcess()
      activate(w2,w2.waitForSig(ev1))
      for i in range(3):
         q=QueueProcess()
         activate(q,q.queueForSig(ev2))  
      simulate(until=2)      
      
   def testSimEvents3(self):
      """
      Tests waiting, queuing for at least one event out of a list/tuple.
      """
      initialize()
      e1=SimEvent("e1")
      e2=SimEvent("e2")
      e3=SimEvent("e3")
      s=SignalProcessOR()
      activate(s,s.makeSignal(e1,e3))
      w=WaitProcessOR()
      activate(w,w.waitForSig([e1,e2]))
      for i in range(5):
         q=QueueProcessOR()
         activate(q,q.queueForSig([e2,e3]))
      simulate(until=10) 

   def testSimEvents4(self):
      """Tests that eventsFired reports all events which fired
      """
      initialize()
      w=WaitProcessOR1()
      activate(w,w.signalandwait())
      simulate(until=5)
      
   def testSimEvents5(self):
      """Tests that eventsFired reports all events which fired
      """
      initialize()
      w=QueueProcessOR1()
      activate(w,w.signalandqueue())
      simulate(until=5)

def makeESuite():
   suite=unittest.TestSuite()
   testSimEvents1=makeEtestcase("testSimEvents1")
   testSimEvents2=makeEtestcase("testSimEvents2")
   testSimEvents3=makeEtestcase("testSimEvents3")
   testSimEvents4=makeEtestcase("testSimEvents4")
   testSimEvents5=makeEtestcase("testSimEvents5")
   suite.addTests([testSimEvents1,testSimEvents2,testSimEvents3,testSimEvents4,testSimEvents5])
   return suite
   
## -------------------------------------------------------------
##                    TEST waituntil
## -------------------------------------------------------------

class Signaller(Process):
    def makeconditions(self,waiter):
        global a,b,c
        a=True
        yield hold,self,1
        b=True
        yield hold,self,1
        c=True
        yield hold,self,1
        assert waiter.terminated(),"waituntil did not fire"
        
class Waiter(Process):
    def waitforit(self):
        def waitcond():
            return a and b and c
        yield waituntil,self,waitcond

class makeWtestcase(unittest.TestCase):
   """
   Test waituntil as introduced with SimPy 1.5
   """
   
   def testwaituntil1(self):
       global a,b,c
       a=b=c=False
       initialize()
       w=Waiter()
       activate(w,w.waitforit())
       s=Signaller()
       activate(s,s.makeconditions(w))
       simulate(until=5)
 
def makeWSuite():
   suite=unittest.TestSuite()
   testwaituntil1=makeWtestcase("testwaituntil1")
   suite.addTests([testwaituntil1])
   return suite
   
## -------------------------------------------------------------
##                    TEST COMPOUND "YIELD REQUEST" COMMANDS
## -------------------------------------------------------------

## -------------------------------------------------------------
##             TEST "yield (request,self,res),(hold,self,delay)"
##                   == timeout renege
##             for both unmonitored and monitored resources
## -------------------------------------------------------------

class JobTO(Process):
   """ Job class for testing timeout reneging
   """
   def __init__(self,server=None,name=""):
        Process.__init__(self,name)
        self.res=server
        self.gotResource=None
        
   def execute(self,timeout,usetime):       
        yield (request,self,self.res),(hold,self,timeout)
        if self.acquired(self.res):
            self.gotResource=True
            yield hold,self,usetime
            yield release,self,self.res
        else:
            self.gotResource=False
            
class JobTO_P(Process):
   """ Job class for testing timeout reneging with priorities
   """
   def __init__(self,server=None,name=""):
        Process.__init__(self,name)
        self.res=server
        self.gotResource=None
        
   def execute(self,timeout,usetime,priority):       
        yield (request,self,self.res,priority),(hold,self,timeout)
        if self.acquired(self.res):
            self.gotResource=True
            yield hold,self,usetime
            yield release,self,self.res
        else:
            self.gotResource=False
            
class makeTimeoutTestcase(unittest.TestCase):
    """ Tests of "yield (request,self,res),(hold,self,delay)"
        timeout reneging command
    """
    def testNoTimeout(self):
        """Test that resource gets acquired without timeout
        """
        res=Resource(name="Server",capacity=1)
        initialize()
        usetime=5
        timeout=1000000
        j1=JobTO(server=res,name="Job_1")
        activate(j1,j1.execute(timeout=timeout,usetime=usetime))
        j2=JobTO(server=res,name="Job_2")
        activate(j2,j2.execute(timeout=timeout,usetime=usetime))      
        simulate(until=2*usetime)
        assert now()==2*usetime,"time not ==2*usetime" 
        assert j1.gotResource and j2.gotResource,\
            "at least one job failed to get resource"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"
            
    def testNoTimeoutM(self):
        """Test that resource gets acquired without timeout.
           Resource monitored.
        """
        res=Resource(name="Server",capacity=1,monitored=True)
        initialize()
        usetime=5
        timeout=1000000
        j1=JobTO(server=res,name="Job_1")
        activate(j1,j1.execute(timeout=timeout,usetime=usetime))
        j2=JobTO(server=res,name="Job_2")
        activate(j2,j2.execute(timeout=timeout,usetime=usetime))      
        simulate(until=2*usetime)
        assert now()==2*usetime,"time not ==2*usetime" 
        assert j1.gotResource and j2.gotResource,\
            "at least one job failed to get resource"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"
        assert res.waitMon==[[0,1],[usetime,0]],"res.waitMon wrong: %s"%res.waitMon
            
    def testTimeout1(self):
        """Test that timeout occurs when resource busy
        """
        res=Resource(name="Server",capacity=1)
        initialize()
        usetime=5
        timeout=3
        j1=JobTO(server=res,name="Job_1")
        activate(j1,j1.execute(timeout=timeout,usetime=usetime))
        j2=JobTO(server=res,name="Job_2")
        activate(j2,j2.execute(timeout=timeout,usetime=usetime))      
        simulate(until=2*usetime)
        assert(now()==usetime),"time not ==usetime"
        assert(j1.gotResource),"Job_1 did not get resource"
        assert(not j2.gotResource),"Job_2 did not renege"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"
            
    def testTimeout1M(self):
        """Test that timeout occurs when resource busy.
           Resource monitored.
        """
        res=Resource(name="Server",capacity=1,monitored=True)
        initialize()
        usetime=5
        timeout=3
        j1=JobTO(server=res,name="Job_1")
        activate(j1,j1.execute(timeout=timeout,usetime=usetime))
        j2=JobTO(server=res,name="Job_2")
        activate(j2,j2.execute(timeout=timeout,usetime=usetime))      
        simulate(until=2*usetime)
        assert(now()==usetime),"time not == usetime"
        assert(j1.gotResource),"Job_1 did not get resource"
        assert(not j2.gotResource),"Job_2 did not renege"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"
        assert res.waitMon==[[0,1],[timeout,0]],"res.waitMon wrong: %s"%res.waitMon
        
    def testTimeout_MP(self):
        """Test that timeout occurs when resource busy.
           Resource monitored. Requests with priority and preemption.
        """
        res=Resource(name="Server",capacity=1,monitored=True,qType=PriorityQ,preemptable=True)
        initialize()
        usetime=5
        timeout=3
        j1=JobTO_P(server=res,name="Job_1")
        activate(j1,j1.execute(timeout=timeout,usetime=usetime,priority=1))
        j2=JobTO_P(server=res,name="Job_2")
        j2_arrival=1
        activate(j2,j2.execute(timeout=timeout,usetime=usetime,priority=5),at=j2_arrival)
        j3=JobTO_P(server=res,name="Job_2")
        j3_arrival=2
        activate(j3,j3.execute(timeout=timeout,usetime=usetime,priority=10),at=j3_arrival)           
        simulate(until=3*usetime)
        assert(now()== 3*usetime),"time not == 2* usetime, but %s"%now()
        assert(j1.gotResource),"Job_1 did not get resource"
        assert(j2.gotResource),"Job_2 did renege"
        assert(j2.gotResource),"Job_3 did renege"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"
        assert res.waitMon==[[j2_arrival,1],[j3_arrival,2],[usetime+j3_arrival,1],[usetime+j2_arrival+usetime,0]],\
             "res.waitMon wrong: %s"%res.waitMon

    def testTimeout2(self):
        """Test that timeout occurs when resource has no capacity free
        """
        res=Resource(name="Server",capacity=0)
        initialize()
        usetime=5
        timeout=3
        j1=JobTO(server=res,name="Job_1")
        activate(j1,j1.execute(timeout=timeout,usetime=usetime))
        j2=JobTO(server=res,name="Job_2")
        activate(j2,j2.execute(timeout=timeout,usetime=usetime))      
        simulate(until=2*usetime)
        assert now()==timeout,"time %s not == timeout"%now()
        assert not j1.gotResource,"Job_1 got resource"
        assert not j2.gotResource,"Job_2 got resource"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"  
            
    def testTimeout2M(self):
        """Test that timeout occurs when resource has no capacity free.
           Resource monitored.
        """
        res=Resource(name="Server",capacity=0,monitored=True)
        initialize()
        usetime=5
        timeout=3
        j1=JobTO(server=res,name="Job_1")
        activate(j1,j1.execute(timeout=timeout,usetime=usetime))
        j2=JobTO(server=res,name="Job_2")
        activate(j2,j2.execute(timeout=timeout,usetime=usetime))      
        simulate(until=2*usetime)
        assert now()==timeout,"time %s not == timeout"%now()
        assert not j1.gotResource,"Job_1 got resource"
        assert not j2.gotResource,"Job_2 got resource"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"  
        assert res.waitMon==[[0,1],[0,2],[timeout,1],[timeout,0]],\
            "res.waitMon is wrong: %s"%res.waitMon
            
def makeTOSuite():
    suite = unittest.TestSuite()
    testNoTimeout = makeTimeoutTestcase("testNoTimeout")
    testNoTimeoutM = makeTimeoutTestcase("testNoTimeoutM")
    testTimeout1=makeTimeoutTestcase("testTimeout1")
    testTimeout1M=makeTimeoutTestcase("testTimeout1M")
    testTimeout_MP=makeTimeoutTestcase("testTimeout_MP")       
    testTimeout2=makeTimeoutTestcase("testTimeout2")
    testTimeout2M=makeTimeoutTestcase("testTimeout2M")
    suite.addTests([testNoTimeout,testNoTimeoutM,
                    testTimeout1,testTimeout1M,testTimeout_MP,
                   testTimeout2,testTimeout2M]) 
    return suite

## ------------------------------------------------------------------
##             TEST "yield (request,self,res),(waitevent,self,event)"
##                   == event renege
##             for both unmonitored and monitored resources
## ------------------------------------------------------------------


class JobEvt(Process):
   """ Job class for testing event reneging
   """
   def __init__(self,server=None,name=""):
        Process.__init__(self,name)
        self.res=server
        self.gotResource=None
        
   def execute(self,event,usetime):       
        yield (request,self,self.res),(waitevent,self,event)
        if self.acquired(self.res):
            self.gotResource=True
            yield hold,self,usetime
            yield release,self,self.res
        else:
            self.gotResource=False
            
class JobEvtMulti(Process):
   """ Job class for testing event reneging with multi-event lists
   """
   def __init__(self,server=None,name=""):
        Process.__init__(self,name)
        self.res=server
        self.gotResource=None
        
   def execute(self,eventlist,usetime):       
        yield (request,self,self.res),(waitevent,self,eventlist)
        if self.acquired(self.res):
            self.gotResource=True
            yield hold,self,usetime
            yield release,self,self.res
        else:
            self.gotResource=False
            
class FireEvent(Process):
    """Fires reneging event
    """
    def fire(self,fireDelay,event):
        yield hold,self,fireDelay
        event.signal()
            
class makeEventRenegeTestcase(unittest.TestCase):
    """Tests of "yield (request,self,res),(waiteevent,self,event)" 
       event reneging command 
    """
    def testNoEvent(self):
        """Test that processes acquire resource normally if no event fires
        """
        res=Resource(name="Server",capacity=1)
        event=SimEvent("Renege_trigger") #never gets fired
        initialize()
        usetime=5
        j1=JobEvt(server=res,name="Job_1")
        activate(j1,j1.execute(event=event,usetime=usetime))
        j2=JobEvt(server=res,name="Job_2")
        activate(j2,j2.execute(event=event,usetime=usetime))      
        simulate(until=2*usetime)
        # Both jobs should get server (in sequence)
        assert now()==2*usetime,"time not ==2*usetime" 
        assert j1.gotResource and j2.gotResource,\
            "at least one job failed to get resource"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"
 
    def testNoEventM(self):
        """Test that processes acquire resource normally if no event fires.
           Resource monitored.
        """
        res=Resource(name="Server",capacity=1,monitored=True)
        event=SimEvent("Renege_trigger") #never gets fired
        initialize()
        usetime=5
        j1=JobEvt(server=res,name="Job_1")
        activate(j1,j1.execute(event=event,usetime=usetime))
        j2=JobEvt(server=res,name="Job_2")
        activate(j2,j2.execute(event=event,usetime=usetime))      
        simulate(until=2*usetime)
        # Both jobs should get server (in sequence)
        assert now()==2*usetime,"time not ==2*usetime" 
        assert j1.gotResource and j2.gotResource,\
            "at least one job failed to get resource"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource" 
        assert res.waitMon==[[0,1],[usetime,0]],"res.waitMoni is wrong: %s"%res.waitMon
            
    def testWaitEvent1(self):
        """Test that signalled event leads to renege when resource busy
        """
        res=Resource(name="Server",capacity=1)
        initialize()
        event=SimEvent("Renege_trigger")
        usetime=5
        eventtime=1
        j1=JobEvt(server=res,name="Job_1")
        activate(j1,j1.execute(event=event,usetime=usetime))
        j2=JobEvt(server=res,name="Job_2")
        activate(j2,j2.execute(event=event,usetime=usetime))
        f=FireEvent(name="FireEvent")
        activate(f,f.fire(fireDelay=eventtime,event=event))           
        simulate(until=2*usetime)
        # Job_1 should get server, Job_2 renege
        assert(now()==usetime),"time not ==usetime"
        assert(j1.gotResource),"Job_1 did not get resource"
        assert(not j2.gotResource),"Job_2 did not renege"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"
            
    def testWaitEvent1M(self):
        """Test that signalled event leads to renege when resource busy.
           Resource monitored.
        """
        res=Resource(name="Server",capacity=1,monitored=True)
        initialize()
        event=SimEvent("Renege_trigger")
        usetime=5
        eventtime=1
        j1=JobEvt(server=res,name="Job_1")
        activate(j1,j1.execute(event=event,usetime=usetime))
        j2=JobEvt(server=res,name="Job_2")
        activate(j2,j2.execute(event=event,usetime=usetime))
        f=FireEvent(name="FireEvent")
        activate(f,f.fire(fireDelay=eventtime,event=event))           
        simulate(until=2*usetime)
        # Job_1 should get server, Job_2 renege
        assert(now()==usetime),"time not ==usetime"
        assert(j1.gotResource),"Job_1 did not get resource"
        assert(not j2.gotResource),"Job_2 did not renege"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"
        assert res.waitMon==[[0,1],[eventtime,0]],"res.waitMon is wrong: %s"%res.waitMon
            
    def testWaitEvent2(self):
        """Test that renege-triggering event can be one of an event list
        """
        res=Resource(name="Server",capacity=1)
        initialize()
        event1=SimEvent("Renege_trigger_1")
        event2=SimEvent("Renege_trigger_2")
        usetime=5
        eventtime=1 #for both events
        j1=JobEvtMulti(server=res,name="Job_1")
        activate(j1,j1.execute(eventlist=[event1,event2],usetime=usetime))
        j2=JobEvtMulti(server=res,name="Job_2")
        activate(j2,j2.execute(eventlist=[event1,event2],usetime=usetime))
        f1=FireEvent(name="FireEvent_1")
        activate(f1,f1.fire(fireDelay=eventtime,event=event1))
        f2=FireEvent(name="FireEvent_2")
        activate(f2,f2.fire(fireDelay=eventtime,event=event2))             
        simulate(until=2*usetime)
        # Job_1 should get server, Job_2 should renege
        assert(now()==usetime),"time not ==usetime"
        assert(j1.gotResource),"Job_1 did not get resource"
        assert(not j2.gotResource),"Job_2 did not renege"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"
            
    def testWaitEvent2M(self):
        """Test that renege-triggering event can be one of an event list.
           Resource monitored.
        """
        res=Resource(name="Server",capacity=1,monitored=True)
        initialize()
        event1=SimEvent("Renege_trigger_1")
        event2=SimEvent("Renege_trigger_2")
        usetime=5
        eventtime=1 #for both events
        j1=JobEvtMulti(server=res,name="Job_1")
        activate(j1,j1.execute(eventlist=[event1,event2],usetime=usetime))
        j2=JobEvtMulti(server=res,name="Job_2")
        activate(j2,j2.execute(eventlist=[event1,event2],usetime=usetime))
        f1=FireEvent(name="FireEvent_1")
        activate(f1,f1.fire(fireDelay=eventtime,event=event1))
        f2=FireEvent(name="FireEvent_2")
        activate(f2,f2.fire(fireDelay=eventtime,event=event2))             
        simulate(until=2*usetime)
        # Job_1 should get server, Job_2 should renege
        assert(now()==usetime),"time not ==usetime"
        assert(j1.gotResource),"Job_1 did not get resource"
        assert(not j2.gotResource),"Job_2 did not renege"
        assert not (res.waitQ or res.activeQ),\
            "job waiting or using resource"
        assert res.waitMon==[[0,1],[eventtime,0]],"res.waitMon is wrong: %s"%res.waitMon
    
def makeEvtRenegeSuite():
    suite = unittest.TestSuite()
    testNoEvent = makeEventRenegeTestcase("testNoEvent")
    testNoEventM = makeEventRenegeTestcase("testNoEventM")
    testWaitEvent1=makeEventRenegeTestcase("testWaitEvent1")
    testWaitEvent1M=makeEventRenegeTestcase("testWaitEvent1M")    
    testWaitEvent2=makeEventRenegeTestcase("testWaitEvent2")
    testWaitEvent2M=makeEventRenegeTestcase("testWaitEvent2M")
    
    suite.addTests([testNoEvent,testNoEventM,testWaitEvent1,testWaitEvent1M,
                    testWaitEvent2,testWaitEvent2M]) 
    return suite
    
#---Buffer tests (post 1.6.1)-------------------------------------
## ------------------------------------------------------------------
##             TEST "yield get,self,level,whatToGet" and 
##                  "yield put,self,level,whatToPut,priority"
##             for Level instances
## ------------------------------------------------------------------
class Producer(Process):
    produced=0
    def produce(self,buffer):
        for i in range(4):
            Producer.produced+=1
            yield put,self,buffer
            yield hold,self,1
    def producePriority(self,buffer,priority):
        """PriorityQ for Producers"""
        Producer.produced+=4
        yield put,self,buffer,4,priority
        yield hold,self,1
        self.done=now()
        doneList.append(self.name)
    def produce1(self,buffer):
        for i in range(4):
            yield put,self,buffer,4
            yield hold,self,1
class Consumer(Process):
    consumed=0
    def consume(self,buffer):
        """FIFO"""
        yield get,self,buffer
        Consumer.consumed+=1
        assert self.got==1,"wrong self.got: %s"%self.got 
        yield get,self,buffer,3
        Consumer.consumed+=3
        assert self.got==3,"wrong self.got: %s"%self.got
        
    def consume1(self,buffer):
        """producer PriorityQ, consumer FIFO"""
        while True:
            yield get,self,buffer,2
            yield hold,self,1
    def consumePriority(self,buffer,priority):
        """PriorityQ for Consumers"""
        yield get,self,buffer,4,priority
        doneList.append(self.name)
        
### Begin classes for testConPrinciple (Level) ###
class  ProducerPrincL(Process):
    def produce(self,buffer,productionTime):     
        while True:
            assert not(buffer.amount>0 and len(buffer.getQ)>0),\
                "Consumer(s) waiting while buffer not empty"
            yield hold,self,productionTime
            yield put,self,buffer,1

class ConsumerPrincL(Process):
    def consume(self,buffer,consumptionTime):
        while True:
            assert not(buffer.amount==0 and len(buffer.putQ)>0),\
                "Producer(s) waiting while buffer empty"
            yield get,self,buffer,1
            yield hold,self,consumptionTime        
                
### End classes for testConPrinciple (Level) ###

class makeLevelTestcase(unittest.TestCase):
    def testStatic(self):
        """Tests initialization of Level instances
        """
        a=Level()
        assert a.capacity==sys.maxint,"wrong capacity:%s"%a
        assert a.amount==0,"wrong buffer content: %s"%a
        assert a.name=="a_level","wrong name: %s"%a
        assert not a.monitored,"should not be monitored: %s"%a
        assert a.putQMon is None,"should not have putQMon: %s"%a
        assert a.getQMon is None,"should not have getQMon: %s"%a
        assert a.bufferMon is None,"should not have bufferMon: %s"%a
        assert a.putQType.__name__=="FIFO" and a.getQType.__name__=="FIFO",\
               "putQType and getQType should be FIFO: %s"%a
        
        b=Level(name="b",initialBuffered=10.0,monitored=True,capacity=12,
                    putQType=PriorityQ)
        a=Level()
        assert b.capacity==12,"wrong capacity:%s"%b
        assert b.amount==10,"wrong buffer content: %s"%b
        assert b.name=="b","wrong name: %s"%b
        assert b.monitored,"should be monitored: %s"%b
        assert not (b.putQMon is None),"should have putQMon: %s"%b
        assert not (b.getQMon is None),"should have getQMon: %s"%b
        assert not (b.bufferMon is None),"should have bufferMon: %s"%b
        assert b.putQType.__name__=="PriorityQ",\
               "putQType should be PriorityQ: %s"%b
        assert b.getQType.__name__=="FIFO",\
                "getQType should be PriorityQ: %s"%b
                
    def testConProdPrinciple(self):
        """Level: tests basic Producer/Consumer principles:
        -   Consumers must not be waiting while Level buffer value > 0,
        -   Producers must not be waiting while Level buffer value == 0
        """
        bufferSize=1
        productionTime=1
        consumptionTime=5
        endtime=50
    
        initialize()
        buffer=Level(capacity=bufferSize)
        consumer=ConsumerPrincL()
        activate(consumer,consumer.consume(buffer,consumptionTime))
        producer=ProducerPrincL()
        activate(producer,producer.produce(buffer,productionTime))
        simulate(until=endtime)

    def testConProd1(self):
        """Level: tests put/get in 1 Producer/ 1 Consumer scenario"""
        initialize()
        buffer=Level(initialBuffered=0)
        p=Producer()
        activate(p,p.produce(buffer))
        c=Consumer()
        activate(c,c.consume(buffer))
        simulate(until=100)
        assert Producer.produced-Consumer.consumed==buffer.amount,\
            "items produced/consumed/buffered do not tally: %s %s %s"\
                %(Producer.produced,Consumer.consumed,buffer.amount)
        
    def testConProdM(self):
        """Level: tests put/get in multiple Producer/Consumer scenario"""
        initialize()
        buffer=Level(initialBuffered=0)
        Producer.produced=0
        Consumer.consumed=0
        for i in range(2):
            c=Consumer()
            activate(c,c.consume(buffer))
        for i in range(3):
            p=Producer()
            activate(p,p.produce(buffer))
        simulate(until=10)
        assert Producer.produced-Consumer.consumed==buffer.amount,\
            "items produced/consumed/buffered do not tally: %s %s %s"\
                %(Producer.produced,Consumer.consumed,buffer.amount)

    def testConProdPriorM(self):
        """Level: tests put/get in multiple Producer/Consumer scenario, 
        with Producers having different priorities.
        How: Producers forced to queue; all after first should be done in
        priority order
        """
        global doneList
        doneList=[]
        initialize()
        buffer=Level(capacity=7,putQType=PriorityQ,monitored=True)
        for i in range(4):
            p=Producer(i)
            pPriority=i
            activate(p,p.producePriority(buffer=buffer,priority=pPriority))
        c=Consumer()
        activate(c,c.consume1(buffer=buffer))
        simulate(until=100)
        assert doneList==[0,3,2,1],"puts were not done in priority order: %s"\
                                    %doneList
                                    
    def testConPriorProdM(self):
        """Level: tests put/get in multiple Producer/Consumer scenario, with
        Consumers having different priorities.
        How: Consumers forced to queue; all after first should be done in
        priority order
        """
        global doneList
        doneList=[]
        initialize()
        buffer=Level(capacity=7,getQType=PriorityQ,monitored=True)
        for i in range(4):
            c=Consumer(i)
            cPriority=i
            activate(c,c.consumePriority(buffer=buffer,priority=cPriority))
        p=Producer()
        activate(p,p.produce1(buffer=buffer))
        simulate(until=100)
        assert doneList==[3,2,1,0],"gets were not done in priority order: %s"\
                                    %doneList

def makeLevelSuite():
    suite = unittest.TestSuite()
    testStatic = makeLevelTestcase("testStatic")
    testConProdPrinciple=makeLevelTestcase("testConProdPrinciple")
    testConProd1=makeLevelTestcase("testConProd1")
    testConProdM=makeLevelTestcase("testConProdM")
    testConProdPriorM=makeLevelTestcase("testConProdPriorM")
    testConPriorProdM=makeLevelTestcase("testConPriorProdM")
    suite.addTests([testStatic,testConProdPrinciple,testConProd1,
                    testConProdM,testConProdPriorM,
                    testConPriorProdM]) 
    return suite

## ------------------------------------------------------------------
##             TEST "yield get,self,store,whatToGet" and 
##                  "yield put,self,store,whatToPut"
##             for Store instances
## ------------------------------------------------------------------

class ProducerWidget(Process):
    produced=0
    def produce(self,buffer):
        for i in range(4):
            ProducerWidget.produced+=1
            yield put,self,buffer,[Widget(weight=5)]
            yield hold,self,1
    def producePriority(self,buffer,priority):
        """PriorityQ for Producers"""
        ProducerWidget.produced+=4
        toStore=[Widget(weight=5)]*4
        yield put,self,buffer,toStore,priority
        yield hold,self,1
        self.done=now()
        doneList.append(self.name)
    def produce1(self,buffer):
        for i in range(4):
            yield put,self,buffer,[Widget(weight=5)]*4
            yield hold,self,1
    def produceUnordered(self,buffer):
        produced=[Widget(weight=i) for i in [9,1,8,2,7,3,6,4,5]]
        yield put,self,buffer,produced

class ConsumerWidget(Process):
    consumed=0
    def consume(self,buffer):
        """FIFO"""
        yield get,self,buffer
        ConsumerWidget.consumed+=1
        assert len(self.got)==1,"wrong self.got: %s"%self.got 
        yield get,self,buffer,3
        ConsumerWidget.consumed+=3
        assert len(self.got)==3,"wrong self.got: %s"%self.got
        
    def consume1(self,buffer):
        """producer PriorityQ, consumer FIFO"""
        while True:
            yield get,self,buffer,2
            yield hold,self,1
        
    def consumePriority(self,buffer,priority):
        """PriorityQ for Consumers"""
        yield get,self,buffer,4,priority
        doneList.append(self.name)
        
    def consumeSorted(self,buffer,gotten):
        yield get,self,buffer
        gotten.append(self.got[0].weight)

class Widget:
    def __init__(self,weight):
        self.weight=weight
        
def mySortFunc(self,par):
    """Sorts Widget instances by weight attribute."""
    tmplist=[(x.weight,x) for x in par]
    tmplist.sort()
    return [x for (key,x) in tmplist]
    
### Begin classes for testConPrinciple (Store) ###
class  ProducerPrincS(Process):
    def produce(self,buffer,productionTime):     
        while True:
            assert not(buffer.nrBuffered>0 and len(buffer.getQ)>0),\
                "Consumer(s) waiting while buffer not empty"
            yield hold,self,productionTime
            product=WidgetPrinc()
            yield put,self,buffer,[product]

class ConsumerPrincS(Process):
    def consume(self,buffer,consumptionTime):
        while True:
            assert not(buffer.nrBuffered==0 and buffer.putQ),\
                "Producer(s) waiting while buffer empty"
            yield get,self,buffer,1
            yield hold,self,consumptionTime        
                
class WidgetPrinc:
    pass
    
class FilterConsumer(Process):
    """Used in testBufferFilter"""
    class Widget:
        def __init__(self,weighs):
            self.weight=weighs
            
    def getItems(self,store,a,b):
        """get all items with weight between a and b"""
        def between_a_and_b(buf):
            res=[]
            for item in buf:
                if a<item.weight<b:
                    res.append(item)
                    
        all=store.buffered
        yield get,self,store,between_a_and_b
        "All retrieved items weight in range?"
        for it in self.got:
            assert a<it.weight<b,"weight %s not in range %s..%s"\
                                 %(it.weight,a,b)
        "Any item fitting filter pred left in buffer?"
        for it in store.buffer:
            assert not (a<it.weight<b),\
                "item left in buffer which fits filter (%s<%s<%s)"\
                %(a,it.weight,b)
        "All items either in store.buffer of self.got?"
        for it in all:
            assert (it in self.buffer) or (it in self.got),\
                   "item w. weight %s neither in store nor in got"%it.weight 

### End classes for testConPrinciple (Store) ###

class makeStoreTestcase(unittest.TestCase):
    def testStatic(self):
        """Store: tests initialization of Store instances
        """
        a=Store()
        assert a.capacity==sys.maxint,"wrong capacity:%s"%a
        assert a.nrBuffered==0,"wrong buffer content: %s"%a
        assert a.name=="a_store","wrong name: %s"%a
        assert not a.monitored,"should not be monitored: %s"%a
        assert a.putQMon is None,"should not have putQMon: %s"%a
        assert a.getQMon is None,"should not have getQMon: %s"%a
        assert a.bufferMon is None,"should not have bufferMon: %s"%a
        assert a.putQType.__name__=="FIFO" and a.getQType.__name__=="FIFO",\
               "putQType and getQType should be FIFO: %s"%a
            
        stored=[Widget(weight=5)]*10       
        b=Store(name="b",initialBuffered=stored,monitored=True,capacity=12,
                    putQType=PriorityQ)
        assert b.capacity==12,"wrong capacity:%s"%b
        assert b.nrBuffered==10,"wrong buffer content: %s"%b
        assert b.name=="b","wrong name: %s"%b
        assert b.monitored,"should be monitored: %s"%b
        assert not (b.putQMon is None),"should have putQMon: %s"%b
        assert not (b.getQMon is None),"should have getQMon: %s"%b
        assert not (b.bufferMon is None),"should have bufferMon: %s"%b
        assert b.putQType.__name__=="PriorityQ",\
               "putQType should be PriorityQ: %s"%b
        assert b.getQType.__name__=="FIFO",\
                "getQType should be PriorityQ: %s"%b

    def testConProdPrinciple(self):
        """Store: tests basic Producer/Consumer principles:
        -   Consumers must not be waiting while items in Store buffer,
        -   Producers must not be waiting while space available in Store buffer
        """
        bufferSize=1
        productionTime=1
        consumptionTime=5
        endtime=50

        initialize()
        buffer=Store(capacity=bufferSize)
        consumer=ConsumerPrincS()
        activate(consumer,consumer.consume(buffer,consumptionTime))
        producer=ProducerPrincS()
        activate(producer,producer.produce(buffer,productionTime))
        simulate(until=endtime)

    def testConProd1(self):
        """Store: tests put/get in 1 Producer/ 1 Consumer scenario"""
        initialize()
        buffer=Store(initialBuffered=[])
        p=ProducerWidget()
        activate(p,p.produce(buffer))
        c=ConsumerWidget()
        activate(c,c.consume(buffer))
        simulate(until=100)
        assert \
           ProducerWidget.produced-ConsumerWidget.consumed==buffer.nrBuffered,\
           "items produced/consumed/buffered do not tally: %s %s %s"\
           %(ProducerWidget.produced,ConsumerWidget.consumed,buffer.nrBuffered)
        
    def testConProdM(self):
        """Store: tests put/get in multiple Producer/Consumer scenario"""
        initialize()
        buffer=Store(initialBuffered=[])
        ProducerWidget.produced=0
        ConsumerWidget.consumed=0
        for i in range(2):
            c=ConsumerWidget()
            activate(c,c.consume(buffer))
        for i in range(3):
            p=ProducerWidget()
            activate(p,p.produce(buffer))
        simulate(until=10)
        assert ProducerWidget.produced-ConsumerWidget.consumed==buffer.nrBuffered,\
            "items produced/consumed/buffered do not tally: %s %s %s"\
            %(ProducerWidget.produced,ConsumerWidget.consumed,buffer.nrBuffered)

    def testConProdPriorM(self):
        """Store: Tests put/get in multiple Producer/Consumer scenario, 
        with Producers having different priorities.
        How; Producers forced to queue; all after first should be done in
        priority order
        """
        global doneList
        doneList=[]
        initialize()
        buffer=Store(capacity=7,putQType=PriorityQ,monitored=True)
        for i in range(4):
            p=ProducerWidget(i)
            pPriority=i
            activate(p,p.producePriority(buffer=buffer,priority=pPriority))
        c=ConsumerWidget()
        activate(c,c.consume1(buffer=buffer))
        simulate(until=100)
        assert doneList==[0,3,2,1],"puts were not done in priority order: %s"\
                                    %doneList
                                    
    def testConPriorProdM(self):
        """Tests put/get in multiple Producer/Consumer scenario, with
        Consumers having different priorities.
        How; Consumers forced to queue; all after first should be done in
        priority order
        """
        global doneList
        doneList=[]
        initialize()
        buffer=Store(capacity=7,getQType=PriorityQ,monitored=True)
        for i in range(4):
            c=ConsumerWidget(str(i))
            cPriority=i
            activate(c,c.consumePriority(buffer=buffer,priority=cPriority))
        p=ProducerWidget()
        activate(p,p.produce1(buffer=buffer))
        simulate(until=100)
        assert doneList==["3","2","1","0"],\
              "gets were not done in priority order: %s"%doneList
                                    
    def testBufferSort(self):
        """Tests the optional sorting of theBuffer by applying a user-defined
        sort function."""
        initialize()
        gotten=[]
        sortedStore=Store()
        sortedStore.addSort(mySortFunc)
        p=ProducerWidget()
        activate(p,p.produceUnordered(sortedStore))
        for i in range(9):
            c=ConsumerWidget()
            activate(c,c.consumeSorted(buffer=sortedStore,gotten=gotten),at=1)
        simulate(until=10)
        assert gotten==[1,2,3,4,5,6,7,8,9],"sort wrong: %s"%gotten
        
    def testBufferFilter(self):
        """Tests get from a Store with a filter function
        """
        initialize()
        ItClass=FilterConsumer.Widget
        all=[ItClass(1),ItClass(4),ItClass(6),ItClass(12)]
        st=Store(initialBuffered=all)
        fc=FilterConsumer()
        minw=2;maxw=10
        activate(fc,fc.getItems(store=st,a=minw,b=maxw))
        simulate(until=1)
        
def makeStoreSuite():
    suite = unittest.TestSuite()
    testStatic = makeStoreTestcase("testStatic")
    testConProdPrinciple=makeStoreTestcase("testConProdPrinciple")
    testConProd1=makeStoreTestcase("testConProd1")
    testConProdM=makeStoreTestcase("testConProdM")
    testConProdPriorM=makeStoreTestcase("testConProdPriorM")
    testConPriorProdM=makeStoreTestcase("testConPriorProdM")
    testBufferSort=makeStoreTestcase("testBufferSort")
    testBufferFilter=makeStoreTestcase("testBufferFilter")
    suite.addTests([testStatic,testConProdPrinciple,testConProd1,
                    testConProdM,testConProdPriorM,
                    testConPriorProdM,testBufferSort,
                    testBufferFilter]) 
    return suite

## ------------------------------------------------------------------
##             
##  Store: Tests for compound get/put                
##             
## ------------------------------------------------------------------
class TBT(Process):
    """Store: For testBasicTime"""
    def tbt(self,store):
        yield get,self,store,1
        assert self.got,"Did not get Item"
        yield (get,self,store,1),(hold,self,5)
        if self.acquired(store):
            assert len(self.got)==1,"did not get 1 Item"
        else:
            assert not self.got and now()==5 and not store.getQ,\
                   "time renege not working"
        
class TBE(Process):
    """Store: For testBasicEvent"""
    def tbe(self,store,trigger):
        yield get,self,store,1
        assert self.got,"Did not get Item"
        yield (get,self,store,1),(waitevent,self,trigger)
        if self.acquired(store):
            assert False, "should have reneged"
        else:
            assert self.eventsFired[0]==trigger and now()==5 \
                and not store.getQ,"event renege not working"
        
class TBEtrigger(Process):
    """Store: For testBasicEvent"""
    def fire(self,trigger):
        yield hold,self,5
        trigger.signal()
    
class makeStoreCompTestcase(unittest.TestCase):
    """Store: Testcase for compound get statements"""
    
class TBTput(Process):
    """Store: for testBasicTimePut"""
    def tbt(self,store):
        class Item:pass
        yield (put,self,store,[Item()]),(hold,self,4)
        if self.stored(store):
            assert store.nrBuffered==1 and not store.putQ,\
                   "put did not execute"
        else:
            assert False,"should not have reneged"
        yield (put,self,store,[Item()]),(hold,self,5)
        if self.stored(store):
            assert False,"should have reneged"
        else:
            assert store.nrBuffered==1 and not store.putQ,\
                   "renege not working correctly"   

class TBEput(Process):
    """Store: for testBasicEventPut"""
    def tbe(self,store,trigger):
        class Item:pass
        yield (put,self,store,[Item()]),(waitevent,self,trigger)
        if self.stored(store):
            assert store.nrBuffered==1 and not store.putQ,\
                   "put did not execute"
        else:
            assert False,"should have not have reneged"
        yield (put,self,store,[Item()]),(waitevent,self,trigger)
        if self.stored(store):
            assert False,"should have reneged"
        else:
            assert now()==5 and self.eventsFired[0]==trigger\
                   and not store.putQ,"renege not working correctly"   

class TBEtriggerPut(Process):
    """Store: For testBasicEventPut"""
    def fire(self,trigger):
        yield hold,self,5
        trigger.signal()            
    
class makeStoreCompTestcase(unittest.TestCase):
    """Store: Testcase for compound get statements"""
    ## ------------------------------------------------------------------
    ##             TEST "yield (get,self,store),(hold,self,time)"
    ##                   == timeout renege
    ##             for both unmonitored and monitored Stores
    ## ------------------------------------------------------------------

    def testBasicTime(self):
        """Store (unmonitored): 
        test 'yield (get,self,store),(hold,self,timeout)"""
        class Item:pass
        initialize()
        st=Store(initialBuffered=[Item()])
        t=TBT()
        activate(t,t.tbt(store=st))
        simulate(until=10)
        

    ## ------------------------------------------------------------------
    ##             TEST "yield (put,self,store),(hold,self,time)"
    ##                   == timeout renege
    ##             for both unmonitored and monitored Stores
    ## ------------------------------------------------------------------
    def testBasicTimePut(self):
        """Store (unmonitored): 
        test 'yield (put,self,store),(hold,self,time)"""
        initialize()
        st=Store(capacity=1)
        t=TBTput()
        activate(t,t.tbt(store=st))
        simulate(until=10)
        
    def testBasicTimePutM(self):
        """Store (monitored): 
        test monitors with 'yield (put,self,store),(hold,self,time)"""
        initialize()
        st=Store(capacity=1,monitored=True)
        t=TBTput()
        activate(t,t.tbt(store=st))
        simulate(until=10)
        #First put succeeds, second attempt reneges at t=5?
        assert st.putQMon==[[0,0],[0,1],[5,0]],"putQMon wrong: %s"\
                                               %st.putQMon
        #First Item goes into buffer at t=0, second not (renege)?
        assert st.bufferMon==[[0,0],[0,1]],"bufferMon wrong: %s"%st.bufferMon
                                            
        
    ## ------------------------------------------------------------------
    ##             TEST "yield (get,self,store),(waitevent,self,event)"
    ##                   == event renege
    ##             for both unmonitored and monitored Stores
    ## ------------------------------------------------------------------ 
    def testBasicEvent(self):
        """Store (unmonitored): 
        test 'yield (get,self,store),(waitevent,self,event)"""
        class Item:pass
        initialize()
        st=Store(initialBuffered=[Item()])
        trig=SimEvent()
        t=TBE()
        activate(t,t.tbe(store=st,trigger=trig))
        tr=TBEtrigger()
        activate(tr,tr.fire(trigger=trig))
        simulate(until=10) 
        

    ## ------------------------------------------------------------------
    ##             TEST "yield (put,self,store),(waitevent,self,event)"
    ##                   == event renege
    ##             for both unmonitored and monitored Stores
    ## ------------------------------------------------------------------ 
    def testBasicEventPut(self):
        """Store (unmonitored): 
        test 'yield (put,self,store),(waitevent,self,event)"""
        initialize()
        s=SimEvent()
        store=Store(capacity=1)
        t=TBEtriggerPut()
        activate(t,t.fire(trigger=s))
        tb=TBEput()
        activate(tb,tb.tbe(store=store,trigger=s))
        simulate(until=10)

    def testBasicEventPutM(self):
        """Store (monitored): 
        test monitors with 'yield (put,self,store),(waitevent,self,event)""" 
        initialize()
        s=SimEvent()
        st=Store(capacity=1,monitored=True)
        t=TBEtriggerPut()
        activate(t,t.fire(trigger=s))
        tb=TBEput()
        activate(tb,tb.tbe(store=st,trigger=s))
        simulate(until=10)
        #First put succeeds, second attempt reneges at t=5?
        assert st.putQMon==[[0,0],[0,1],[5,0]],"putQMon wrong: %s"\
                                               %st.putQMon
        #First Item goes into buffer at t=0, second not (renege)?
        assert st.bufferMon==[[0,0],[0,1]],"bufferMon wrong: %s"%st.bufferMon        
       
def makeStoreCompSuite():
    suite = unittest.TestSuite()
    ## Unmonitored Stores
    testBasicTime  = makeStoreCompTestcase("testBasicTime")
    testBasicEvent = makeStoreCompTestcase("testBasicEvent")
    testBasicTimePut  = makeStoreCompTestcase("testBasicTimePut")
    testBasicEventPut = makeStoreCompTestcase("testBasicEventPut")
    ## Monitored Stores
    testBasicTimePutM = makeStoreCompTestcase("testBasicTimePutM")
    testBasicEventPutM = makeStoreCompTestcase("testBasicEventPutM")
    
    suite.addTests([testBasicTime,
                    testBasicEvent,
                    testBasicTimePut,
                    testBasicEventPut,
                    testBasicTimePutM,
                    testBasicEventPutM]) 
    return suite

## ------------------------------------------------------------------
##             
##  Level: Tests for compound get               
##             
## ------------------------------------------------------------------
class TBTLev(Process):
    """Level: For testBasicTime"""
    def tbt(self,level):
        yield get,self,level,1
        assert self.got,"did not get 1 unit"
        yield (get,self,level,1),(hold,self,5)
        if self.acquired(level):
            assert self.got==1,"did not get 1 unit"
        else:
            assert not self.got and now()==5,"time renege not working"
        
class TBELev(Process):
    """Level: For testBasicEvent"""
    def tbe(self,level,trigger):
        yield get,self,level,1
        assert self.got,"did not get 1 unit"
        yield (get,self,level,1),(waitevent,self,trigger)
        if self.acquired(level):
            assert self.got==1,"did not get 1 Item"
        else:
            assert now()==5.5 and self.eventsFired[0]==trigger,\
                   "event renege not working"
        
class TBEtriggerLev(Process):
    """Level: For testBasicEvent"""
    def fire(self,trigger):
        yield hold,self,5.5
        trigger.signal()
        
class TBTLevPut(Process):
    """Level: For testBasicTimePut"""
    def tbt(self,level):
        yield put,self,level,1
        assert level.amount,"did not put 1 unit"
        yield (put,self,level,1),(hold,self,5)
        if self.stored(level):
            assert False,"should have reneged"
        else:
            assert level.amount==1 and now()==5,"time renege not working" 

class TBELevPut(Process):
    """Level: For testBasicEventPut and testBasicEventPutM"""
    def tbe(self,level,trigger):
        yield (put,self,level,1),(waitevent,self,trigger)
        if self.stored(level):
            assert level.amount==1,"did not put 1 unit"
        else:
            assert False,"should not have reneged"
        yield (put,self,level,1),(waitevent,self,trigger) 
        if self.stored(level):
            assert False, "should have reneged"
        else:
            assert now()==5.5 and self.eventsFired[0]==trigger ,\
                   "renege not working"

class TBEtriggerLevPut(Process):
    """Level: For testBasicEventPut"""
    def fire(self,trigger):
        yield hold,self,5.5
        trigger.signal()
        
class makeLevelCompTestcase(unittest.TestCase):
    """Level: Testcase for compound get and put statements"""
    ## ------------------------------------------------------------------
    ##             TEST "yield (get,self,level),(hold,self,time)"
    ##                   == timeout renege
    ##             for both unmonitored and monitored Levels
    ## ------------------------------------------------------------------

    def testBasicTime(self):
        """Level (unmonitored): test 'yield (get,self,level),(hold,self,timeout)"""
        initialize()
        l=Level(initialBuffered=1)
        t=TBTLev()
        activate(t,t.tbt(level=l))
        simulate(until=10)
        
    ## ------------------------------------------------------------------
    ##             TEST "yield (put,self,store),(hold,self,time)"
    ##                   == timeout renege
    ##             for both unmonitored and monitored Stores
    ## ------------------------------------------------------------------
    def testBasicTimePut(self):
        """Level (unmonitored): 
        test 'yield (put,self,level),(hold,self,timeout)"""
        initialize()
        l=Level(capacity=1)
        t=TBTLevPut()
        activate(t,t.tbt(level=l))
        simulate(until=10)
        
           
    ## ------------------------------------------------------------------
    ##             TEST "yield (get,self,store),(waitevent,self,event)"
    ##                   == event renege
    ##             for both unmonitored and monitored Levels
    ## ------------------------------------------------------------------
    def testBasicEvent(self):
        """Level (unmonitored): 
        test 'yield (get,self,level),(waitevent,self,event)"""
        initialize()
        l=Level(initialBuffered=1)
        trig=SimEvent()
        t=TBELev()
        activate(t,t.tbe(level=l,trigger=trig))
        tr=TBEtriggerLev()
        activate(tr,tr.fire(trigger=trig))
        simulate(until=10)
        
    def testBasicEventM(self):
        """Level (monitored): 
        test monitors with 'yield (get,self,level),(waitevent,self,event)"""
        initialize()
        l=Level(initialBuffered=1,monitored=True)
        trig=SimEvent()
        t=TBELev()
        activate(t,t.tbe(level=l,trigger=trig))
        tr=TBEtriggerLev()
        activate(tr,tr.fire(trigger=trig))
        simulate(until=10)
        #First get (t=0) succeeded and second timed out at t=5.5?
        assert l.getQMon==[[0,0],[0,1],[5.5,0]],"getQMon not working: %s"\
                                               %l.getQMon
        #Level amount incr. then decr. by 1 (t=0), 2nd get reneged at t=5.5?
        assert l.bufferMon==[[0,1],[0,0]],\
               "bufferMon not working: %s"%l.bufferMon
                                            
    ## ------------------------------------------------------------------
    ##             TEST "yield (put,self,store),(waitevent,self,event)"
    ##                   == event renege
    ##             for both unmonitored and monitored Levels
    ## ------------------------------------------------------------------
    def testBasicEventPut(self):
        """Level (unmonitored): 
        test 'yield (put,self,level),(waitevent,self,event)"""
        initialize()
        l=Level(capacity=1)
        trig=SimEvent()
        t=TBELevPut()
        activate(t,t.tbe(level=l,trigger=trig))
        tr=TBEtriggerLevPut()
        activate(tr,tr.fire(trigger=trig))
        simulate(until=10)
        
    def testBasicEventPutM(self):
        """Level (monitored): 
        test monitors with 'yield (put,self,level),(waitevent,self,event)"""
        initialize()
        l=Level(capacity=1,monitored=True)
        trig=SimEvent()
        t=TBELevPut()
        activate(t,t.tbe(level=l,trigger=trig))
        tr=TBEtriggerLevPut()
        activate(tr,tr.fire(trigger=trig))
        simulate(until=10)
        "First put succeeds, second reneges at t=5.5?"
        assert l.putQMon==[[0,0],[0,1],[5.5,0]],"putQMon wrong: %s"\
                                                %l.putQMon
        "1 unit added at t=0, renege at t=5 before 2nd unit added?"
        assert l.bufferMon==[[0,0],[0,1]],"bufferMon wrong: %s"%l.bufferMon

def makeLevelCompSuite():
    suite = unittest.TestSuite()
    ## Unmonitored Levels
    testBasicTime  = makeLevelCompTestcase("testBasicTime")
    testBasicEvent = makeLevelCompTestcase("testBasicEvent")
    testBasicTimePut = makeLevelCompTestcase("testBasicTimePut")
    testBasicEventPut = makeLevelCompTestcase("testBasicEventPut")
    ## Monitored Levels
    testBasicEventM = makeLevelCompTestcase("testBasicEventM")
    testBasicEventPutM = makeLevelCompTestcase("testBasicEventPutM")
    
    suite.addTests([testBasicTime,
                    testBasicEvent,
                    testBasicTimePut,
                    testBasicEventPut,
                    testBasicEventM,
                    testBasicEventPutM]) 
    return suite

if __name__ == '__main__':
    alltests = unittest.TestSuite((makeSSuite(),makeRSuite(),
                                   makeMSuite(),#makeHSuite(),
                                   makeISuite(),makePSuite(),
                                   makeESuite(),makeWSuite(),
                                   makeTOSuite(),makeEvtRenegeSuite(),
                                   makeLevelSuite(),
                                   makeStoreSuite(),
                                   makeStoreCompSuite(),
                                   makeLevelCompSuite()
                                ))
    runner = unittest.TextTestRunner()
    runner.run(alltests)


