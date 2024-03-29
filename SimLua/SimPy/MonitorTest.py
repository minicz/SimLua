#!/usr/bin/env python
DEVELOPING = False
if DEVELOPING:
   from Simulation import *
else:
   from SimPy.Simulation import *
from random import *
# ------------------------------------------------------------
#from SimPy.SimPlot import SimPlot
import unittest
# $Revision: 1.1.1.23 $ $Date: 2008/03/03 13:56:37 $

"""MonitorTest.py
Testing Monitor, Tally. 
This may be included in SimPyTest eventually.

Change history:
2004 05 03 corrected test for Monitored queues (gav)
2005 09 06 added tests for Tally (kgm)
2007 12 04 adding twVariance for both Monitor and Tally (gav)
2007 12 05 changed name to timeVariance (gav)

"""
__version__="1.9.1 $Revision: 1.1.1.23 $ $Date: 2008/03/03 13:56:37 $"

## ------------------------------------------------------------
class Thing(Process):
   """ Thing process for testing Monitors in simulation"""
   def __init__(self,M=None,name="Thing"):
        Process.__init__(self)
        self.name=name
        self.y = 0.0
        self.M = M

   def execute(self):       
        DEBUG = 0
        self.y = 0.0
        if DEBUG: print self.name,now(),self.y
        self.M.observe(self.y)

        yield hold,self,10.0
        self.y = 10
        if DEBUG: print self.name,now(),self.y
        self.M.observe(self.y)

        yield hold,self,10.0
        self.y = 5
        if DEBUG: print self.name,now(),self.y
        self.M.observe(self.y)
       
## ------------------------------------------------------------

class makeMtestCase(unittest.TestCase):
    """ Test Monitor
    """
        
    def setUp(self):
        self.M = Monitor(name='First')
        for i in range(10):
            self.M.observe(2*i,i)
        self.T = Tally(name='tallier')
        self.M2 = Monitor(name="second")
        T = [0,1,4,5]
        Y = [1,2,1,0]
        for t,y in zip(T,Y):
           self.M2.observe(y,t)
        assert self.M2.tseries() == T, 'wrong M2'
        assert self.M2.yseries() == Y, 'wrong M2'


    def testObserve(self):
        """Test Monitor - observe"""
        m = self.M
        #for i in m.series():
        #   print i
        assert m == [[i, 2*i] for i in range(10)],'series wrong'
        assert m.name == 'First','name wrong'
        assert m.tseries() == list(range(10)),'tseries wrong:%s'%(m.tseries(),)
        assert m.yseries() == [2*i for i in range(10)],'yseries wrong:%s'%(m.yseries(),)
        assert m.total() == 90, 'total wrong:%s'%m.total()
        assert m.mean() == 9.0,'mean wrong:%s'%m.mean()
        assert m.var() == (4*285.-(90*90/10.0))/10.0,'sample var wrong: %s'%(m.var(),)

    def testObserveNoTime(self):
        """Test Monitor - observe with time being picked up from now()"""
        m = Monitor(name='No time')
        initialize()
        t = Thing(m)
        activate(t,t.execute(),0.0)
        simulate(until=20.0)
        assert m.yseries() == [0,10,5],'yseries wrong:%s'%(m.yseries(),)
        assert m.tseries() == [0,10,20],'tseries wrong:%s'%(m.tseries(),)
        assert m.total() == 15, 'total wrong:%s'%m.total()
        assert m.timeAverage(10.0) == 5.0 ,'time average is wrong: %s'%m.timeAverage(10.0)
 
    def testObserveTally(self):
        """Test Monitor - observe without time values"""
        m = self.T
        for i in range(10):
           m.observe(2*i)
        assert m == [[0, 2*i] for i in range(10)],'series wrong'
        assert m.total() == 90, 'total wrong:%s'%m.total()
        assert m.mean() == 9.0,'mean wrong:%s'%m.mean()
        assert m.var() == (4*285.-(90*90/10.0))/10.0,'sample var wrong: %s'%(m.var(),)

    def testtimeAverage(self):
       """ test time averages """
       # old version
       m = self.M
       assert m == [[i,2*i] for i in range(10)],'series wrong'
       assert m.timeAverage(10.0) == 9.0 ,'time average is wrong: %s'%m.timeAverage(10)
       m2 = self.M2
       assert m2.timeAverage(5.0) == 8.0/5,'m2 time average is wrong: %s'%m2.timeAverage(5)
       # now the new recursive version
       #m = self.M
       #assert m.newtimeAverage(10.0) == 9.0 ,'m1: new time average wrong: %s'%m.newtimeAverage(10)
       #m2 = self.M2
       #assert m2.newtimeAverage(5.0) == 8.0/5,'m2: new time average wrong: %s'%m2.newtimeAverage(5.0)
       

    def testtimeVariance(self):
       """ test time-weighted variance """
       m = self.M
       assert m == [[i,2*i] for i in range(10)],'series wrong'
       assert abs(m.timeVariance(10.0) - 33)<0.0001 ,'time-weighted variance is wrong: %s'%m.timeVariance(10.0)
       m2 = self.M2
       assert abs(m2.timeVariance(5) - 6.0/25)<0.0001,'time-weighted variance is wrong: %s'%m2.timeVariance(5)

    def testreset(self):
       """ test time averages """
       m=self.M
       m.reset(t = 10.0)
       assert m.startTime == 10.0,'reset time  wrong'
       assert m == [],'reset series wrong: %s'%(m,)


    def testTally(self):
        """Test Monitor - tally"""
        m = Monitor(name='First')
        S = []
        for i in range(10):
            m.tally(i)
            S.append([0,i])
        assert m == S,'Stored series is wrong: %s'%(m,)
        assert m.name == 'First','Tally name wrong'
        assert m.total() == 45,'Tally total wrong'
        assert m.mean() == 4.5,'Tally mean wrong'
        assert m.var()  == (285-(45*45/10.0))/10.0,'Tally sample var wrong %s'%(m.var(),)       


    def testAccumulate(self):
        """Test Monitor - accumulate"""
        #print 'Monitor version '+__version__
        m2 = Monitor(name='Second')
        assert m2.startTime == 0,'accum startTime wrong'
        for i in range(5):
            m2.accum(10,i)  # this is (y,t)
        # print 'debug', m2.data
        assert m2.total() == 50,'accum total wrong:%s'%(m2.total(),)
        assert m2.startTime == 0,'accum startTime wrong'
        assert m2.timeAverage(5.0) == 10.0,'accum timeAverage wrong:%s'%(m2.timeAverage(10.0),)
        ## test reset
        m2.reset(10)
        assert m2 == [],'accum reset list wrong:%s'%(m2,)
        assert m2.total() == 0.0,'accum reset total wrong'
        assert m2.startTime == 10,'accum startTime wrong'

    def testAccumulateInTime(self):
        """Test Monitor - accumulate over simulation time"""
        #print 'Monitor version '+__version__
        initialize()
        m3 = Monitor(name='third')
        T3 = Thing(name="Job",M=m3)
        assert m3.startTime == 0,'Accumulate startTime wrong'
        activate(T3,T3.execute(),0.0)
        simulate(until=30.0)
        assert m3.startTime == 0,'Accumulate startTime wrong'

    def testListStuff(self):
       """Test some Monitor list operations"""
       shouldBe=[[i,2*i] for i in range(10)]
       assert shouldBe == self.M, 'M list is wrong'
       assert [2,4] == self.M[2], 'indexing wrong:%s'%(self.M[2],)
       self.M[0] = [10,10]
       assert [10,10] == self.M[0], 'item replacement wrong:%s'%(self.M[0],)
       self.M.reverse()
       assert [10,10] == self.M[-1], 'list reverse wrong:%s'%(self.M[-1],)
       self.M.sort()
       assert [1,2] == self.M[0], 'list sort wrong:%s'%(self.M[0],)
       assert 10 == len(self.M), 'list length wrong'
       assert [2,4] in self.M, 'item in list wrong'
       
       
    def testhistogram(self):
       """Test Monitor histogram"""
       m = Monitor(name='First')      
       for y in [-5, 0, 5, 15,99,105,120]:m.observe(y)
       h = m.histogram(low=0.0,high=100.0,nbins=10)
       shouldBe = list(zip(*h)[1])
       assert shouldBe == [1,2,1,0,0,0,0,0,0,0,1,2], 'm histogram is wrong: %s'%(shouldBe,)

def makeMSuite():
    suite = unittest.TestSuite()
    testObserve = makeMtestCase("testObserve")
    testObserveNoTime = makeMtestCase("testObserveNoTime")
    testObserveTally = makeMtestCase("testObserveTally")
    testtimeAverage = makeMtestCase("testtimeAverage")
    testtimeVariance = makeMtestCase("testtimeVariance")
    testreset = makeMtestCase("testreset")
    testTally = makeMtestCase("testTally")
    testAccumulate = makeMtestCase("testAccumulate")
    testAccumulateInTime = makeMtestCase("testAccumulateInTime")
    testListStuff = makeMtestCase("testListStuff")
    testhistogram = makeMtestCase("testhistogram")
    suite.addTests([testObserve,testObserveNoTime,
                    testObserveTally,
                    testtimeAverage,
                    testtimeVariance,
                    testreset,
                    testTally,testAccumulate,
                    testAccumulateInTime,
                    testListStuff,
                    testhistogram,
                    ]) 
    return suite
   
## -----------------------------------------------------------------------
## Tally test cases
## -----------------------------------------------------------------------
class makeTtestCase(unittest.TestCase):
    """ Test Tally
    """
        
    def setUp(self):
        self.T = Tally(name='First')
        for i in range(10):
            self.T.observe(2*i,i)
        self.TT = Tally(name='tallier')
        self.T2 = Tally(name="tally2")
        T = [0,1,4,5]
        Y = [1,2,1,0]
        for t,y in zip(T,Y):
           self.T2.observe(y,t)
        

    def testObserve(self):
        """Test Tally - observe"""
        t = self.T
        #for i in m.series():
        #   print i
        assert t.name == 'First','name wrong'
        assert t.total() == 90, 'total wrong:%s'%m.total()
        assert t.mean() == 9.0,'mean wrong:%s'%m.mean()
        assert t.var() == (4*285.-(90*90/10.0))/10.0,'sample var wrong: %s'%(t.var(),)

    def testObserveNoTime(self):
        """Test Tally - observe with time being picked up from now()"""
        ta= Tally(name='No time')
        initialize()
        t = Thing(ta)
        activate(t,t.execute(),0.0)
        simulate(until=20.0)
        assert ta.total() == 15, 'total wrong:%s'%ta.total()
        assert ta.timeAverage(10.0) == 5.0 ,'time average is wrong: %s'%ta.timeAverage(10.0)

    def testtimeAverage(self):
       """ test time averages """
       ta= self.T
       assert ta.timeAverage(10.0) == 9.0 ,'time average is wrong: %s'%ta.timeAverage(10.0)
    
    def testtimeVariance(self):
       """ test time-weighted Variance for Tally """
       ta= self.T
       assert abs(ta.timeVariance(10.0) - 33) < 0.00001 ,'time-weighted variance is wrong: %s'%ta.timeVariance(10.0)
       t2 = self.T2
       assert abs(t2.timeVariance(5) - 6.0/25)<0.0001,'time-weighted variance is wrong: %s'%t2.timeVariance(5)

       
    def testreset(self):
       """ test time averages """
       ta=self.T
       ta.reset(t = 10.0)
       assert ta.startTime == 10.0,'reset time  wrong'
       
    def testhistogram(self):
       """Test some Monitor list operations"""
       ta = Monitor(name='First')      
       for y in [-5, 0, 5, 15,99,105,120]:ta.observe(y)
       ta.setHistogram(low=0.0,high=100.0,nbins=10)
       h = ta.histogram()
       shouldBe = list(zip(*h)[1])
       assert shouldBe == [1,2,1,0,0,0,0,0,0,0,1,2], 'm histogram is wrong: %s'%(shouldBe,)

def makeTSuite():
    suite = unittest.TestSuite()
    testObserve = makeTtestCase("testObserve")
    testObserveNoTime = makeTtestCase("testObserveNoTime")
    testtimeAverage = makeTtestCase("testtimeAverage")
    testtimeVariance = makeTtestCase("testtimeVariance")
    testreset = makeTtestCase("testreset")
    testhistogram = makeTtestCase("testhistogram")
    suite.addTests([testObserve,testObserveNoTime,
                    testtimeAverage,
                    testtimeVariance,
                    testreset,
                    testhistogram,
                    ]) 
    return suite
    
## -----------------------------------------------------------------------
## Test cases to test equivalence of Monitor and Tally
## for monitored Resource instances
## -----------------------------------------------------------------------

class Actor(Process):
    """Process used in MakeEquivTestCase"""
    def act(self,res):
        while True:
            yield request,self,res
            yield hold,self,1
            yield release,self,res
            
class makeEquivTestCase(unittest.TestCase):
    """To test that the histograms produced in monitoring
    a Resource instance's queues are equivalent
    """
    def testResHistogram(self):
        initialize()
        r=Resource(monitored=True,monitorType=Monitor,name="TheResource/Monitor")
        r.waitMon.setHistogram(high=3,nbins=3)
        r.actMon.setHistogram(high=3,nbins=3)

        for i in range (5):
          a=Actor()
          activate(a,a.act(r))
        simulate(until=20)
        mHistoAct= r.actMon.getHistogram()
        mHistoWait=r.waitMon.getHistogram()

        initialize()
        r=Resource(monitored=True,monitorType=Tally,name="TheResource/Tally")
        r.waitMon.setHistogram(high=3,nbins=3)
        r.actMon.setHistogram(high=3,nbins=3)
        for i in range (5):
          a=Actor()
          activate(a,a.act(r))
        simulate(until=20)
        tHistoAct= r.actMon.getHistogram()
        tHistoWait=r.waitMon.getHistogram()

        assert mHistoAct==tHistoAct,"actMon histograms are different"
        assert mHistoWait==tHistoWait,"waitMon histograms are different"

def makeEquivSuite():
    suite = unittest.TestSuite()
    testResHistogram = makeEquivTestCase("testResHistogram")
    suite.addTests([testResHistogram
                    ]) 
    return suite

## -----------------------------------------------------------------------

if __name__ == '__main__':
    print "MonitorTest.py %s"%__version__
    alltests = unittest.TestSuite((makeMSuite(),
##                                   makeHSuite(),
                                   makeTSuite(),
                                   makeEquivSuite()
                                   ))
    runner = unittest.TextTestRunner()
    runner.run(alltests)
