#!/usr/bin/env python
from SimPy.Lister import *
import heapq as hq
import types
import sys
import new
import random
import inspect

# $Revision: 1.1.1.31 $ $Date: 2008/03/03 13:52:23 $ kgm
"""SimulationStep 1.9.1 Supports stepping through SimPy simulation event-by-event.
Based on generators (Python 2.3 and later)

LICENSE:
Copyright (C) 2002,2005,2006,2007  Klaus G. Muller, Tony Vignaux
mailto: kgmuller@xs4all.nl and Tony.Vignaux@vuw.ac.nz

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
END OF LICENSE

**Change history:**

    Started out as SiPy 0.9
    
    5/9/2002: SiPy 0.9.1
    
        - Addition of '_cancel' method in class Process and supporting '_unpost' method in 
          class __Evlist.
        
        - Removal of redundant 'Action' method in class Process.
        
    12/9/2002:
    
        - Addition of resource class
        
        - Addition of "_request" and "_release" coroutine calls
        
    15/9/2002: moved into SimPy package
    
    16/9/2002:
        - Resource attributes fully implemented (resources can now have more
          than 1 shareable resource units)
        
    17/9/2002:
    
        - corrected removal from waitQ (Vignaux)
        
    17/9/2002:
    
        - added test for queue discipline in "test_demo()". Must be FIFO
        
    26/9/02: Version 0.2.0
    
        - cleaned up code; more consistent naming
        
        - prefixed all Simulation-private variable names with "_".
        
        - prefixed all class-private variable names with "__".
        
        - made normal exit quiet (but return message from scheduler()
        
    28/9/02:
    
        - included stopSimulation()
        
    15/10/02: Simulation version 0.3
    
        - Version printout now only if __TESTING
        
        - "_stop" initialized to True by module load, and set to False in 
      initialize()
        
        - Introduced 'simulate(until=0)' instead of 'scheduler(till=0)'. 
      Left 'scheduler()' in for backward compatibility, but marked
      as deprecated.
        
        - Added attribute "name" to class Process; default=="a_process"
        
        - Changed Resource constructor to 
      'def __init__(self,capacity=1,name="a_resource",unitName="units"'.
        
    13/11/02: Simulation version 0.6
    
        - Major changes to class Resource:
        
            - Added two queue types for resources, FIFO (default) and PriorityQ
            
            - Changed constructor to allow selection of queue type.
            
            - Introduced preemption of resources (to be used with PriorityQ
              queue type)
            
            - Changed constructor of class Resource to allow selection of preemption
            
            - Changes to class Process to support preemption of service
            
            - Cleaned up 'simulate' by replacing series of if-statements by dispatch table.

    19/11/02: Simulation version 0.6.1
        - Changed priority schemes so that higher values of Process 
          attribute "priority" represent higher priority.

    20/11/02: Simulation version 0.7
        - Major change of priority approach:

            - Priority set by "yield request,self,res,priority"

            - Priority of a Process instance associated with a specific 
              resource

    25/11/02: Simulation version 0.7.1

        - Code cleanup and optimization

        - Made process attributes remainService and preempted private 
         (_remainService and _preempted)

    11/12/2002: First process interrupt implementation

        - Addition of user methods 'interrupt' and 'resume'

        - Significant code cleanup to maintain process state

    20/12/2002: Changes to "interrupt"; addition of boolean methods to show
                     process states

    16/3/2003: Changed hold (allowing posting events past _endtime)
    
    18/3/2003: Changed _nextev to prevent _t going past _endtime

    23/3/2003: Introduced new interrupt construct; deleted 'resume' method
    
    25/3/2003: Expanded interrupt construct:
    
        - Made 'interrupt' a method  of Process

        - Added 'interruptCause' as an attribute of an interrupted process

        - Changed definition of 'active' to 
         'self._nextTime <> None and not self._inInterrupt'

        - Cleaned up test_interrupt function

    30/3/2003: Modification of 'simulate':

        - error message if 'initialize' not called (fatal)

        - error message if no process scheduled (warning)

        - Ensured that upon exit from 'simulate', now() == _endtime is 
          always valid

    2/04/2003:

        - Modification of 'simulate': leave _endtime alone (undid change
          of 30 Mar 03)

        - faster '_unpost'

    3/04/2003: Made 'priority' private ('_priority')

    4/04/2003: Catch activation of non-generator error

    5/04/2003: Added 'interruptReset()' function to Process.

    7/04/2003: Changed '_unpost' to ensure that process has
                   _nextTime == None (is passive) afterwards.

    8/04/2003: Changed _hold to allow for 'yield hold,self' 
                   (equiv to 'yield hold,self,0')

    10/04/2003: Changed 'cancel' syntax to 'Process().cancel(victim)'

    12/5/2003: Changed eventlist handling from dictionary to bisect
    
    9/6/2003: - Changed eventlist handling from pure dictionary to bisect-
                sorted "timestamps" list of keys, resulting in greatly 
                improved performance for models with large
                numbers of event notices with differing event times.
                =========================================================
                This great change was suggested by Prof. Simon Frost. 
                Thank you, Simon! This version 1.3 is dedicated to you!
                =========================================================
              - Added import of Lister which supports well-structured 
                printing of all attributes of Process and Resource instances.

    Oct 2003: Added monitored Resource instances (Monitors for activeQ and waitQ)

    13 Dec 2003: Merged in Monitor and Histogram

    27 Feb 2004: Repaired bug in activeQ monitor of class Resource. Now actMon
                 correctly records departures from activeQ.
                 
    19 May 2004: Added erroneously omitted Histogram class.

    5 Sep 2004: Added SimEvents synchronization constructs
    
    17 Sep 2004: Added waituntil synchronization construct
    
    01 Dec 2004: SimPy version 1.5
                 Changes in this module: Repaired SimEvents bug re proc.eventsFired
                 
    12 Jan 2005: SimPy version 1.5.1
                 Changes in this module: Monitor objects now have a default name
                                         'a_Monitor'
                                         
    29 Mar 2005: Start SimPy 1.6: compound "yield request" statements
    
    05 Jun 2005: Fixed bug in _request method -- waitMon did not work properly in
                 preemption case
                 
    09 Jun 2005: Added test in 'activate' to see whether 'initialize()' was called first.
    
    23 Aug 2005: - Added Tally data collection class
                 - Adjusted Resource to work with Tally
                 - Redid function allEventNotices() (returns prettyprinted string with event
                   times and names of process instances
                 - Added function allEventTimes (returns event times of all scheduled events)
                 
    16 Mar 2006: - Added Store and Level classes
                 - Added 'yield get' and 'yield put'
                 
    10 May 2006: - Repaired bug in Store._get method
                 - Repaired Level to allow initialBuffered have float value
                 - Added type test for Level get parameter 'nrToGet'
                 
    06 Jun 2006: - To improve pretty-printed output of 'Level' objects, changed attribute
                   _nrBuffered to nrBuffered (synonym for amount property)
                 - To improve pretty-printed output of 'Store' objects, added attribute
                   buffered (which refers to _theBuffer)
                   
    25 Aug 2006: - Start of version 1.8
                 - made 'version' public
                 - corrected condQ initialization bug
                 
    30 Sep 2006: - Introduced checks to ensure capacity of a Buffer > 0
                 - Removed from __future__ import (so Python 2.3 or later needed)
                
    15 Oct 2006: - Added code to register all Monitors and all Tallies in variables
                   'allMonitors' and 'allTallies'
                 - Added function 'startCollection' to activate Monitors and Tallies at a
                   specified time (e.g. after warmup period)
                 - Moved all test/demo programs to after 'if __name__=="__main__":'.
                
    17 Oct 2006: - Added compound 'put' and 'get' statements for Level and Store.
    
    18 Oct 2006: - Repaired bug: self.eventsFired now gets set after an event fires
                   in a compound yield get/put with a waitevent clause (reneging case).
                   
    21 Oct 2006: - Introduced Store 'yield get' with a filter function.
                
    22 Oct 2006: - Repaired bug in prettyprinting of Store objects (the buffer 
                   content==._theBuffer was not shown) by changing ._theBuffer 
                   to .theBuffer.
                
    04 Dec 2006: - Added printHistogram method to Tally and Monitor (generates
                   table-form histogram)
                    
    07 Dec 2006: - Changed the __str__ method of Histogram to print a table 
                   (like printHistogram).
    
    18 Dec 2006: - Added trace printing of Buffers' "unitName" for yield get and put.
    
    09 Jun 2007: - Cleaned out all uses of "object" to prevent name clash.
    
    18 Nov 2007: - Start of 1.9 development
                 - Added 'start' method (alternative to activate) to Process
                 
    22 Nov 2007: - Major change to event list handling to speed up larger models:
                    * Drop dictionary
                    * Replace bisect by heapq
                    * Mark cancelled event notices in unpost and skip them in
                      nextev (great idea of Tony Vignaux))
                      
    4 Dec 2007: - Added twVariance calculation for both Monitor and Tally (gav)
    
    5 Dec 2007: - Changed name back to timeVariance (gav)
    
    1 Mar 2008: - Start of 1.9.1 bugfix release
                - Delete circular reference in Process instances when event 
                  notice has been processed (caused much circular garbage)
                - Added capability for multiple preempts of a process
    
"""

__TESTING=False
version=__version__="1.9.1 $Revision: 1.1.1.31 $ $Date: 2008/03/03 13:52:23 $"
if __TESTING: 
    print "SimPy.SimulationStep %s" %__version__,
    if __debug__:
        print "__debug__ on"
    else:
        print

# yield keywords
hold=1
passivate=2
request=3
release=4
waitevent=5
queueevent=6
waituntil=7
get=8
put=9

_endtime=0
_t=0
_e=None
_stop=True
_step=False
_wustep=False #controls per event stepping for waituntil construct; not user API
try:
  True, False
except NameError:
  True, False = (1 == 1), (0 == 1)
condQ=[]
allMonitors=[]
allTallies=[]

def initialize():
    global _e,_t,_stop,condQ,allMonitors,allTallies
    _e=__Evlist()
    _t=0
    _stop=False
    condQ=[]
    allMonitors=[]
    allTallies=[]

def now():
    return _t

def stopSimulation():
    """Application function to stop simulation run"""
    global _stop
    _stop=True

def _startWUStepping():
    """Application function to start stepping through simulation for waituntil construct."""
    global _wustep
    _wustep=True

def _stopWUStepping():
    """Application function to stop stepping through simulation."""
    global _wustep
    _wustep=False
 
def startStepping():
    """Application function to start stepping through simulation."""
    global _step
    _step=True

def stopStepping():
    """Application function to stop stepping through simulation."""
    global _step
    _step=False
    
class Simerror(Exception):
    def __init__(self,value):
        self.value=value

    def __str__(self):
        return `self.value`
        
class FatalSimerror(Simerror):
    def __init__(self,value):
        Simerror.__init__(self,value)
        self.value=value
    
class Process(Lister):
    """Superclass of classes which may use generator functions"""
    def __init__(self,name="a_process"):
        #the reference to this Process instances single process (==generator)
        self._nextpoint=None
        self.name=name
        self._nextTime=None #next activation time
        self._remainService=0
        self._preempted=0
        self._priority={}
        self._getpriority={}
        self._putpriority={}
        self._terminated= False     
        self._inInterrupt= False
        self.eventsFired=[] #which events process waited/queued for occurred

    def active(self):
        return self._nextTime <> None and not self._inInterrupt 

    def passive(self):
        return self._nextTime is None and not self._terminated

    def terminated(self):
        return self._terminated

    def interrupted(self):
        return self._inInterrupt and not self._terminated

    def queuing(self,resource):
        return self in resource.waitQ
          
    def cancel(self,victim): 
        """Application function to cancel all event notices for this Process
        instance;(should be all event notices for the _generator_)."""
        _e._unpost(whom=victim)

    def start(self,pem=None,at="undefined",delay="undefined",prior=False):
        """Activates PEM of this Process.
        p.start(p.pemname([args])[,{at= t |delay=period}][,prior=False]) or
        p.start([p.ACTIONS()][,{at= t |delay=period}][,prior=False]) (ACTIONS
                parameter optional)
        """
        if pem is None:
            try:
                pem=self.ACTIONS()
            except AttributeError:
                raise FatalSimerror\
                       ("Fatal SimPy error: no generator function to activate")
        else:
            pass
        if _e is None:
            raise FatalSimerror\
              ("Fatal SimPy error: simulation is not initialized"\
                                 "(call initialize() first)")
        if not (type(pem) == types.GeneratorType):
            raise FatalSimerror("Fatal SimPy error: activating function which"+
                           " is not a generator (contains no 'yield')")
        if not self._terminated and not self._nextTime: 
            #store generator reference in object; needed for reactivation
            self._nextpoint=pem
            if at=="undefined":
                at=_t
            if delay=="undefined":
                zeit=max(_t,at)
            else:
                zeit=max(_t,_t+delay)
            _e._post(what=self,at=zeit,prior=prior)
            
    def _hold(self,a):
        if len(a[0]) == 3:
            delay=abs(a[0][2])
        else:
            delay=0
        who=a[1]
        self.interruptLeft=delay
        self._inInterrupt=False
        self.interruptCause=None
        _e._post(what=who,at=_t+delay)

    def _passivate(self,a):
        a[0][1]._nextTime=None

    def interrupt(self,victim):
        """Application function to interrupt active processes"""
        # can't interrupt terminated/passive/interrupted process
        if victim.active():
            victim.interruptCause=self  # self causes interrupt
            left=victim._nextTime-_t
            victim.interruptLeft=left   # time left in current 'hold'
            victim._inInterrupt=True
            reactivate(victim)
            return left
        else: #victim not active -- can't interrupt
            return None

    def interruptReset(self):
        """
        Application function for an interrupt victim to get out of
        'interrupted' state.
        """
        self._inInterrupt= False

    def acquired(self,res):
        """Multi-functional test for reneging for 'request' and 'get':
        (1)If res of type Resource:
            Tests whether resource res was acquired when proces reactivated.
            If yes, the parallel wakeup process is killed.
            If not, process is removed from res.waitQ (reneging).
        (2)If res of type Store:
            Tests whether item(s) gotten from Store res.
            If yes, the parallel wakeup process is killed.
            If no, process is removed from res.getQ
        (3)If res of type Level:
            Tests whether units gotten from Level res.
            If yes, the parallel wakeup process is killed.
            If no, process is removed from res.getQ.
        """
        if isinstance(res,Resource):
            test=self in res.activeQ
            if test:
                self.cancel(self._holder)
            else:
                res.waitQ.remove(self)
                if res.monitored:
                    res.waitMon.observe(len(res.waitQ),t=now())
            return test
        elif isinstance(res,Store):
            test=len(self.got)  
            if test:
                self.cancel(self._holder)
            else:
                res.getQ.remove(self)
                if res.monitored:
                    res.getQMon.observe(len(res.getQ),t=now())
            return test 
        elif isinstance(res,Level):
            test=not (self.got is None)
            if test:
                self.cancel(self._holder)
            else:
                res.getQ.remove(self)
                if res.monitored:
                    res.getQMon.observe(len(res.getQ),t=now())
            return test 

    def stored(self,buffer):
        """Test for reneging for 'yield put . . .' compound statement (Level and
        Store. Returns True if not reneged.
        If self not in buffer.putQ, kill wakeup process, else take self out of 
        buffer.putQ (reneged)"""
        test=self in buffer.putQ
        if test:    #reneged
            buffer.putQ.remove(self)
            if buffer.monitored:
                buffer.putQMon.observe(len(buffer.putQ),t=now())
        else:
            self.cancel(self._holder)
        return not test

def allEventNotices():
    """Returns string with eventlist as;
            t1: processname,processname2
            t2: processname4,processname5, . . .
            . . .  .
    """
    ret=""
    tempList=[]
    tempList[:]=_e.timestamps
    tempList.sort()
    # return only event notices which are not cancelled
    tempList=[[x[0],x[2].name] for x in tempList if not x[3]]
    tprev=-1
    for t in tempList:
        # if new time, new line
        if t[0]==tprev:
            # continue line
            ret+=",%s"%t[1]
        else:
            # new time
            if tprev==-1:
                ret="%s: %s"%(t[0],t[1])
            else:
                ret+="\n%s: %s"%(t[0],t[1])
            tprev=t[0]
    return ret+"\n"

def allEventTimes():
    """Returns list of all times for which events are scheduled.
    """
    r=[]
    r[:]=_e.timestamps
    r.sort()
    # return only event times of not cancelled event notices
    r1=[x[0] for x in r if not r[3]]
    tprev=-1
    ret=[]
    for t in r1:
        if t==tprev:
            #skip time, already in list
            pass
        else:
            ret.append(t)
            tprev=t
    return ret
        
class __Evlist(object):
    """Defines event list and operations on it"""
    def __init__(self):
        # always sorted list of events (sorted by time, priority)
        # make heapq
        self.timestamps = []
        self.sortpr=0

    def _post(self, what, at, prior=False):
        """Post an event notice for process what for time at"""
        # event notices are Process instances
        if at < _t:
            raise Simerror("Attempt to schedule event in the past")
        what._nextTime = at
        self.sortpr-=1
        if prior:
            # before all other event notices at this time
            # heappush with highest priority value so far (negative of 
            # monotonely decreasing number)
            # store event notice in process instance
            what._rec=[at,self.sortpr,what,False]
            # make event list refer to it
            hq.heappush(self.timestamps,what._rec)
        else:
            # heappush with lowest priority
            # store event notice in process instance
            what._rec=[at,-self.sortpr,what,False]
            # make event list refer to it
            hq.heappush(self.timestamps,what._rec)

    def _unpost(self, whom):
        """
        Mark event notice for whom as cancelled if whom is a suspended process
        """
        if whom._nextTime is not None:  # check if whom was actually active
            whom._rec[3]=True ## Mark as cancelled
            whom._nextTime=None  
            
    def _nextev(self):
        """Retrieve next event from event list"""
        global _t, _stop
        noActiveNotice=True
        ## Find next event notice which is not marked cancelled
        while noActiveNotice:
            if self.timestamps:
                 ## ignore priority value         
                (_tnotice, p,nextEvent,cancelled) = hq.heappop(self.timestamps)
                noActiveNotice=cancelled
            else:
                raise Simerror("No more events at time %s" % _t)
        nextEvent._rec=None
        _t=_tnotice
        if _t > _endtime:
            _t = _endtime
            _stop = True
            return (None,)
        try:
            resultTuple = nextEvent._nextpoint.next()
        except StopIteration:
            nextEvent._nextpoint = None
            nextEvent._terminated = True
            nextEvent._nextTime = None
            resultTuple = None
        return (resultTuple, nextEvent)

    def _isEmpty(self):
        return not self.timestamps

    def _allEventNotices(self):
        """Returns string with eventlist as
                t1: [procname,procname2]
                t2: [procname4,procname5, . . . ]
                . . .  .
        """
        ret=""
        for t in self.timestamps:
            ret+="%s:%s\n"%(t[1]._nextTime, t[1].name)
        return ret[:-1]

    def _allEventTimes(self):
        """Returns list of all times for which events are scheduled.
        """
        return self.timestamps

def activate(obj,process,at="undefined",delay="undefined",prior=False):
    """Application function to activate passive process."""
    if _e is None:
        raise FatalSimerror\
       ("Fatal error: simulation is not initialized (call initialize() first)")
    if not (type(process) == types.GeneratorType):
        raise FatalSimerror("Activating function which"+
                       " is not a generator (contains no 'yield')")
    if not obj._terminated and not obj._nextTime:
        #store generator reference in object; needed for reactivation
        obj._nextpoint=process
        if at=="undefined":
            at=_t
        if delay=="undefined":
            zeit=max(_t,at)
        else:
            zeit=max(_t,_t+delay)
        _e._post(obj,at=zeit,prior=prior)

def reactivate(obj,at="undefined",delay="undefined",prior=False):
    """Application function to reactivate a process which is active,
    suspended or passive."""
    # Object may be active, suspended or passive
    if not obj._terminated:
        a=Process("SimPysystem")
        a.cancel(obj)
        # object now passive
        if at=="undefined":
            at=_t
        if delay=="undefined":
            zeit=max(_t,at)
        else:
            zeit=max(_t,_t+delay)
        _e._post(obj,at=zeit,prior=prior)

class Histogram(list):
    """ A histogram gathering and sampling class"""

    def __init__(self,name = '',low=0.0,high=100.0,nbins=10):
        list.__init__(self)
        self.name  = name
        self.low   = float(low)
        self.high  = float(high)
        self.nbins = nbins
        self.binsize=(self.high-self.low)/nbins
        self._nrObs=0
        self._sum=0
        self[:] =[[low+(i-1)*self.binsize,0] for i in range(self.nbins+2)]
       
    def addIn(self,y):
        """ add a value into the correct bin"""
        self._nrObs+=1
        self._sum+=y
        b = int((y-self.low+self.binsize)/self.binsize)
        if b < 0: b = 0
        if b > self.nbins+1: b = self.nbins+1
        assert 0 <= b <=self.nbins+1,'Histogram.addIn: b out of range: %s'%b
        self[b][1]+=1
        
    def __str__(self):
        histo=self
        ylab="value"
        nrObs=self._nrObs
        width=len(str(nrObs))
        res=[]
        res.append("<Histogram %s:"%self.name)
        res.append("\nNumber of observations: %s"%nrObs)
        if nrObs:
            su=self._sum
            cum=histo[0][1]
            fmt="%s"
            line="\n%s <= %s < %s: %s (cum: %s/%s%s)"\
                 %(fmt,"%s",fmt,"%s","%s","%5.1f","%s")
            line1="\n%s%s < %s: %s (cum: %s/%s%s)"\
                 %("%s","%s",fmt,"%s","%s","%5.1f","%s")
            l1width=len(("%s <= "%fmt)%histo[1][0])
            res.append(line1\
                       %(" "*l1width,ylab,histo[1][0],str(histo[0][1]).rjust(width),\
                         str(cum).rjust(width),(float(cum)/nrObs)*100,"%")
                      )
            for i in range(1,len(histo)-1):
                cum+=histo[i][1]
                res.append(line\
                       %(histo[i][0],ylab,histo[i+1][0],str(histo[i][1]).rjust(width),\
                         str(cum).rjust(width),(float(cum)/nrObs)*100,"%")
                          )
            cum+=histo[-1][1]
            linen="\n%s <= %s %s : %s (cum: %s/%s%s)"\
                  %(fmt,"%s","%s","%s","%s","%5.1f","%s")
            lnwidth=len(("<%s"%fmt)%histo[1][0])
            res.append(linen\
                       %(histo[-1][0],ylab," "*lnwidth,str(histo[-1][1]).rjust(width),\
                       str(cum).rjust(width),(float(cum)/nrObs)*100,"%")
                       )
        res.append("\n>")
        return " ".join(res)

def startCollection(when=0.0,monitors=None,tallies=None):
    """Starts data collection of all designated Monitor and Tally objects 
    (default=all) at time 'when'.
    """
    class Starter(Process):
        def collect(self,monitors,tallies):
            for m in monitors:
                print m.name
                m.reset()
            for t in tallies:
                t.reset()
            yield hold,self
    if monitors is None:
        monitors=allMonitors
    if tallies is None:
        tallies=allTallies
    s=Starter()
    activate(s,s.collect(monitors=monitors,tallies=tallies),at=when)

class Monitor(list):
    """ Monitored variables

    A Class for monitored variables, that is, variables that allow one
    to gather simple statistics.  A Monitor is a subclass of list and
    list operations can be performed on it. An object is established
    using m= Monitor(name = '..'). It can be given a
    unique name for use in debugging and in tracing and ylab and tlab
    strings for labelling graphs.
    """
    def __init__(self,name='a_Monitor',ylab='y',tlab='t'):
        list.__init__(self)
        self.startTime = 0.0
        self.name = name
        self.ylab = ylab
        self.tlab = tlab
        allMonitors.append(self)
        
    def setHistogram(self,name = '',low=0.0,high=100.0,nbins=10):
        """Sets histogram parameters.
        Must be called before call to getHistogram"""
        if name=='':
            histname=self.name
        else:
            histname=name
        self.histo=Histogram(name=histname,low=low,high=high,nbins=nbins)

    def observe(self,y,t=None):
        """record y and t"""
        if t is  None: t = now()
        self.append([t,y])

    def tally(self,y):
        """ deprecated: tally for backward compatibility"""
        self.observe(y,0)
                   
    def accum(self,y,t=None):
        """ deprecated:  accum for backward compatibility"""
        self.observe(y,t)

    def reset(self,t=None):
        """reset the sums and counts for the monitored variable """
        self[:]=[]
        if t is None: t = now()
        self.startTime = t
        
    def tseries(self):
        """ the series of measured times"""
        return list(zip(*self)[0])

    def yseries(self):
        """ the series of measured values"""
        return list(zip(*self)[1])

    def count(self):
        """ deprecated: the number of observations made """
        return self.__len__()
        
    def total(self):
        """ the sum of the y"""
        if self.__len__()==0:  return 0
        else:
            sum = 0.0
            for i in range(self.__len__()):
                sum += self[i][1]
            return sum # replace by sum() later

    def mean(self):
        """ the simple average of the monitored variable"""
        try: return 1.0*self.total()/self.__len__()
        except:  print 'SimPy: No observations  for mean'

    def var(self):
        """ the sample variance of the monitored variable """
        n = len(self)
        tot = self.total()
        ssq=0.0
        ##yy = self.yseries()
        for i in range(self.__len__()):
            ssq += self[i][1]**2 # replace by sum() eventually
        try: return (ssq - float(tot*tot)/n)/n
        except: print 'SimPy: No observations for sample variance'
        
    def timeAverage(self,t=None):
        """ the time-weighted average of the monitored variable.

            If t is used it is assumed to be the current time,
            otherwise t =  now()
        """
        N = self.__len__()
        if N  == 0:
            print 'SimPy: No observations for timeAverage'
            return None

        if t is None: t = now()
        sum = 0.0
        tlast = self.startTime
        #print 'DEBUG: timave ',t,tlast
        ylast = 0.0
        for i in range(N):
            ti,yi = self[i]
            sum += ylast*(ti-tlast)
            tlast = ti
            ylast = yi
        sum += ylast*(t-tlast)
        T = t - self.startTime
        if T == 0:
             print 'SimPy: No elapsed time for timeAverage'
             return None
        #print 'DEBUG: timave ',sum,t,T
        return sum/float(T)

    def timeVariance(self,t=None):
        """ the time-weighted Variance of the monitored variable.

            If t is used it is assumed to be the current time,
            otherwise t =  now()
        """
        N = self.__len__()
        if N  == 0:
            print 'SimPy: No observations for timeVariance'
            return None
        if t is None: t = now()
        sm = 0.0
        ssq = 0.0
        tlast = self.startTime
        # print 'DEBUG: 1 twVar ',t,tlast
        ylast = 0.0
        for i in range(N):
            ti,yi = self[i]
            sm  += ylast*(ti-tlast)
            ssq += ylast*ylast*(ti-tlast)
            tlast = ti
            ylast = yi
        sm  += ylast*(t-tlast)
        ssq += ylast*ylast*(t-tlast)
        T = t - self.startTime
        if T == 0:
             print 'SimPy: No elapsed time for timeVariance'
             return None
        mn = sm/float(T)
        # print 'DEBUG: 2 twVar ',ssq,t,T
        return ssq/float(T) - mn*mn


    def histogram(self,low=0.0,high=100.0,nbins=10):
        """ A histogram of the monitored y data values.
        """
        h = Histogram(name=self.name,low=low,high=high,nbins=nbins)
        ys = self.yseries()
        for y in ys: h.addIn(y)
        return h
        
    def getHistogram(self):
        """Returns a histogram based on the parameters provided in
        preceding call to setHistogram.
        """
        ys = self.yseries()
        h=self.histo
        for y in ys: h.addIn(y)
        return h
    
    def printHistogram(self,fmt="%s"):
        """Returns formatted frequency distribution table string from Monitor.
        Precondition: setHistogram must have been called.
        fmt==format of bin range values
        """
        try:
            histo=self.getHistogram()
        except:
            raise FatalSimerror("histogramTable: call setHistogram first"\
                                " for Monitor %s"%self.name)            
        ylab=self.ylab
        nrObs=self.count()
        width=len(str(nrObs))
        res=[]
        res.append("\nHistogram for %s:"%histo.name)
        res.append("\nNumber of observations: %s"%nrObs)
        su=sum(self.yseries())
        cum=histo[0][1]
        line="\n%s <= %s < %s: %s (cum: %s/%s%s)"\
             %(fmt,"%s",fmt,"%s","%s","%5.1f","%s")
        line1="\n%s%s < %s: %s (cum: %s/%s%s)"\
             %("%s","%s",fmt,"%s","%s","%5.1f","%s")
        l1width=len(("%s <= "%fmt)%histo[1][0])
        res.append(line1\
                   %(" "*l1width,ylab,histo[1][0],str(histo[0][1]).rjust(width),\
                     str(cum).rjust(width),(float(cum)/nrObs)*100,"%")
                  )
        for i in range(1,len(histo)-1):
            cum+=histo[i][1]
            res.append(line\
                   %(histo[i][0],ylab,histo[i+1][0],str(histo[i][1]).rjust(width),\
                     str(cum).rjust(width),(float(cum)/nrObs)*100,"%")
                      )
        cum+=histo[-1][1]
        linen="\n%s <= %s %s : %s (cum: %s/%s%s)"\
              %(fmt,"%s","%s","%s","%s","%5.1f","%s")
        lnwidth=len(("<%s"%fmt)%histo[1][0])
        res.append(linen\
                   %(histo[-1][0],ylab," "*lnwidth,str(histo[-1][1]).rjust(width),\
                   str(cum).rjust(width),(float(cum)/nrObs)*100,"%")
                   )
        return " ".join(res)
        
class Tally:
    def __init__(self, name="a_Tally", ylab="y",tlab="t"):
        self.name = name
        self.ylab = ylab
        self.tlab = tlab
        self.reset()
        self.startTime = 0.0
        self.histo = None
        self.sum = 0.0
        self._sum_of_squares = 0
        self._integral = 0.0    # time-weighted sum
        self._integral2 = 0.0   # time-weighted sum of squares
        allTallies.append(self)
        
    def setHistogram(self,name = '',low=0.0,high=100.0,nbins=10):
        """Sets histogram parameters.
        Must be called to prior to observations initiate data collection 
        for histogram.
        """
        if name=='':
            hname=self.name
        else:
            hname=name
        self.histo=Histogram(name=hname,low=low,high=high,nbins=nbins)

    def observe(self, y, t=None):
        if t is None:
            t = now()
        self._integral += (t - self._last_timestamp) * self._last_observation
        yy =  self._last_observation* self._last_observation
        self._integral2 += (t - self._last_timestamp) * yy
        self._last_timestamp = t
        self._last_observation = y
        self._total += y
        self._count += 1
        self._sum += y
        self._sum_of_squares += y * y
        if self.histo:
            self.histo.addIn(y)
         
    def reset(self, t=None):
        if t is None:
            t = now()
        self.startTime = t
        self._last_timestamp = t
        self._last_observation = 0.0
        self._count = 0
        self._total = 0.0
        self._integral = 0.0
        self._integral2 = 0.0
        self._sum = 0.0
        self._sum_of_squares = 0.0
 
    def count(self):
        return self._count

    def total(self):
        return self._total

    def mean(self):
        return 1.0 * self._total / self._count

    def timeAverage(self,t=None):
        if t is None:
            t=now()
        integ=self._integral+(t - self._last_timestamp) * self._last_observation
        if (t > self.startTime):
            return 1.0 * integ/(t - self.startTime)
        else:
            print 'SimPy: No elapsed time for timeAverage'
            return None
 
    def var(self):
        return 1.0 * (self._sum_of_squares - (1.0 * (self._sum * self._sum)\
               / self._count)) / (self._count)

    def timeVariance(self,t=None):
        """ the time-weighted Variance of the Tallied variable.

            If t is used it is assumed to be the current time,
            otherwise t =  now()
        """
        if t is None:
            t=now()
        twAve = self.timeAverage(t)
        #print 'Tally timeVariance DEBUG: twave:', twAve
        last =  self._last_observation
        twinteg2=self._integral2+(t - self._last_timestamp) * last * last
        #print 'Tally timeVariance DEBUG:tinteg2:', twinteg2
        if (t > self.startTime):
            return 1.0 * twinteg2/(t - self.startTime) - twAve*twAve
        else:
            print 'SimPy: No elapsed time for timeVariance'
            return None


        
    def __len__(self):
        return self._count

    def __eq__(self, l):
        return len(l) == self._count
        
    def getHistogram(self):
        return self.histo
    
    def printHistogram(self,fmt="%s"):
        """Returns formatted frequency distribution table string from Tally.
        Precondition: setHistogram must have been called.
        fmt==format of bin range values
        """
        try:
            histo=self.getHistogram()
        except:
            raise FatalSimerror("histogramTable: call setHistogram first"\
                                " for Tally %s"%self.name)            
        ylab=self.ylab
        nrObs=self.count()
        width=len(str(nrObs))
        res=[]
        res.append("\nHistogram for %s:"%histo.name)
        res.append("\nNumber of observations: %s"%nrObs)
        su=self.total()
        cum=histo[0][1]
        line="\n%s <= %s < %s: %s (cum: %s/%s%s)"\
             %(fmt,"%s",fmt,"%s","%s","%5.1f","%s")
        line1="\n%s%s < %s: %s (cum: %s/%s%s)"\
             %("%s","%s",fmt,"%s","%s","%5.1f","%s")
        l1width=len(("%s <= "%fmt)%histo[1][0])
        res.append(line1\
                   %(" "*l1width,ylab,histo[1][0],str(histo[0][1]).rjust(width),\
                     str(cum).rjust(width),(float(cum)/nrObs)*100,"%")
                  )
        for i in range(1,len(histo)-1):
            cum+=histo[i][1]
            res.append(line\
                   %(histo[i][0],ylab,histo[i+1][0],str(histo[i][1]).rjust(width),\
                     str(cum).rjust(width),(float(cum)/nrObs)*100,"%")
                      )
        cum+=histo[-1][1]
        linen="\n%s <= %s %s : %s (cum: %s/%s%s)"\
              %(fmt,"%s","%s","%s","%s","%5.1f","%s")
        lnwidth=len(("<%s"%fmt)%histo[1][0])
        res.append(linen\
                   %(histo[-1][0],ylab," "*lnwidth,str(histo[-1][1]).rjust(width),\
                   str(cum).rjust(width),(float(cum)/nrObs)*100,"%")
                   )
        return " ".join(res)

class Queue(list):
    def __init__(self,res,moni):
        if not moni is None: #moni==[]:
            self.monit=True # True if a type of Monitor/Tally attached
        else:
            self.monit=False
        self.moni=moni # The Monitor/Tally
        self.resource=res # the resource/buffer this queue belongs to

    def enter(self,obj):
        pass

    def leave(self):
        pass
        
    def takeout(self,obj):
        self.remove(obj)
        if self.monit:
            self.moni.observe(len(self),t=now())
    
class FIFO(Queue):
    def __init__(self,res,moni):
        Queue.__init__(self,res,moni)

    def enter(self,obj):
        self.append(obj)
        if self.monit:
            self.moni.observe(len(self),t=now())
            
    def enterGet(self,obj):
        self.enter(obj)
        
    def enterPut(self,obj):
        self.enter(obj)

    def leave(self):
        a= self.pop(0)
        if self.monit:
            self.moni.observe(len(self),t=now())
        return a

class PriorityQ(FIFO):
    """Queue is always ordered according to priority.
    Higher value of priority attribute == higher priority.
    """
    def __init__(self,res,moni):
        FIFO.__init__(self,res,moni)

    def enter(self,obj):
        """Handles request queue for Resource"""
        if len(self):
            ix=self.resource
            if self[-1]._priority[ix] >= obj._priority[ix]:
                self.append(obj)
            else:
                z=0
                while self[z]._priority[ix] >= obj._priority[ix]:
                    z += 1
                self.insert(z,obj)
        else:
            self.append(obj)
        if self.monit:
            self.moni.observe(len(self),t=now())
            
    def enterGet(self,obj):
        """Handles getQ in Buffer"""
        if len(self):
            ix=self.resource
            #print "priority:",[x._priority[ix] for x in self]
            if self[-1]._getpriority[ix] >= obj._getpriority[ix]:
                self.append(obj)
            else:
                z=0
                while self[z]._getpriority[ix] >= obj._getpriority[ix]:
                    z += 1
                self.insert(z,obj)
        else:
            self.append(obj)
        if self.monit:
            self.moni.observe(len(self),t=now())
            
    def enterPut(self,obj):
        """Handles putQ in Buffer"""
        if len(self):
            ix=self.resource
            #print "priority:",[x._priority[ix] for x in self]
            if self[-1]._putpriority[ix] >= obj._putpriority[ix]:
                self.append(obj)
            else:
                z=0
                while self[z]._putpriority[ix] >= obj._putpriority[ix]:
                    z += 1
                self.insert(z,obj)
        else:
            self.append(obj)
        if self.monit:
            self.moni.observe(len(self),t=now())

class Resource(Lister):
    """Models shared, limited capacity resources with queuing;
    FIFO is default queuing discipline.
    """
    
    def __init__(self,capacity=1,name="a_resource",unitName="units",
                 qType=FIFO,preemptable=0,monitored=False,monitorType=Monitor): 
        """
        monitorType={Monitor(default)|Tally}
        """
        self.name=name          # resource name
        self.capacity=capacity  # resource units in this resource
        self.unitName=unitName  # type name of resource units
        self.n=capacity         # uncommitted resource units
        self.monitored=monitored

        if self.monitored:           # Monitor waitQ, activeQ
            self.actMon=monitorType(name="Active Queue Monitor %s"%self.name,
                                 ylab="nr in queue",tlab="time")
            monact=self.actMon
            self.waitMon=monitorType(name="Wait Queue Monitor %s"%self.name,
                                 ylab="nr in queue",tlab="time")
            monwait=self.waitMon
        else:
            monwait=None
            monact=None
        self.waitQ=qType(self,monwait)
        self.preemptable=preemptable
        self.activeQ=qType(self,monact)
        self.priority_default=0

    def _request(self,arg):
        """Process request event for this resource"""
        obj=arg[1]
        if len(arg[0]) == 4:        # yield request,self,resource,priority
            obj._priority[self]=arg[0][3]
        else:                       # yield request,self,resource
            obj._priority[self]=self.priority_default
        if self.preemptable and self.n == 0: # No free resource
            # test for preemption condition
            preempt=obj._priority[self] > self.activeQ[-1]._priority[self]
            # If yes:
            if preempt:
                z=self.activeQ[-1]
				# Keep track of preempt level
                z._preempted+=1
                # suspend lowest priority process being served
                # record remaining service time at first preempt only 
                if z._preempted==1:
                    z._remainService = z._nextTime - _t
                    # cancel only at first preempt
                    Process().cancel(z)
                # remove from activeQ
                self.activeQ.remove(z)
                # put into front of waitQ
                self.waitQ.insert(0,z)
                # if self is monitored, update waitQ monitor
                if self.monitored:
                    self.waitMon.observe(len(self.waitQ),now())
                # passivate re-queued process
                z._nextTime=None
                # assign resource unit to preemptor
                self.activeQ.enter(obj)
                # post event notice for preempting process
                _e._post(obj,at=_t,prior=1)
            else:
                self.waitQ.enter(obj)
                # passivate queuing process
                obj._nextTime=None
        else: # treat non-preemption case
            if self.n == 0:
                self.waitQ.enter(obj)
                # passivate queuing process
                obj._nextTime=None
            else:
                self.n -= 1
                self.activeQ.enter(obj)
                _e._post(obj,at=_t,prior=1)

    def _release(self,arg):
        """Process release request for this resource"""
        self.n += 1
        self.activeQ.remove(arg[1])
        if self.monitored:
            self.actMon.observe(len(self.activeQ),t=now())
        #reactivate first waiting requestor if any; assign Resource to it
        if self.waitQ:
            obj=self.waitQ.leave()
            self.n -= 1             #assign 1 resource unit to object
            self.activeQ.enter(obj)
            # if resource preemptable:
            if self.preemptable:
                # if object had been preempted:
                if obj._preempted:
                	# keep track of preempt level
                    obj._preempted-=1
                    # reactivate object delay= remaining service time
					# but only, if all other preempts are over
                    if obj._preempted==0:
                        reactivate(obj,delay=obj._remainService,prior=1)
                # else reactivate right away
                else:
                    reactivate(obj,delay=0,prior=1)
            # else:
            else:
                reactivate(obj,delay=0,prior=1)
        _e._post(arg[1],at=_t,prior=1)

class Buffer(Lister):
    """Abstract class for buffers
    Blocks a process when a put would cause buffer overflow or a get would cause
    buffer underflow.
    Default queuing discipline for blocked processes is FIFO."""

    priorityDefault=0
    def __init__(self,name=None,capacity="unbounded",unitName="units",
                putQType=FIFO,getQType=FIFO,
                monitored=False,monitorType=Monitor,initialBuffered=None):
        if capacity=="unbounded": capacity=sys.maxint
        self.capacity=capacity
        self.name=name
        self.putQType=putQType
        self.getQType=getQType
        self.monitored=monitored
        self.initialBuffered=initialBuffered
        self.unitName=unitName
        if self.monitored:
            ## monitor for Producer processes' queue
            self.putQMon=monitorType(name="Producer Queue Monitor %s"%self.name,
                                    ylab="nr in queue",tlab="time")
            ## monitor for Consumer processes' queue
            self.getQMon=monitorType(name="Consumer Queue Monitor %s"%self.name,
                                    ylab="nr in queue",tlab="time")
            ## monitor for nr items in buffer
            self.bufferMon=monitorType(name="Buffer Monitor %s"%self.name,
                                    ylab="nr in buffer",tlab="time")
        else:
            self.putQMon=None
            self.getQMon=None
            self.bufferMon=None
        self.putQ=self.putQType(res=self,moni=self.putQMon)
        self.getQ=self.getQType(res=self,moni=self.getQMon)
        if self.monitored:
            self.putQMon.observe(y=len(self.putQ),t=now())
            self.getQMon.observe(y=len(self.getQ),t=now())
        self._putpriority={}
        self._getpriority={}

        def _put(self):
            pass
        def _get(self):
            pass

class Level(Buffer):
    """Models buffers for processes putting/getting un-distinguishable items.
    """
    def getamount(self):
        return self.nrBuffered

    def gettheBuffer(self):
        return self.nrBuffered

    theBuffer=property(gettheBuffer)

    def __init__(self,**pars):
        Buffer.__init__(self,**pars)
        if self.name is None:
            self.name="a_level"   ## default name

        if (type(self.capacity)!=type(1.0) and\
                type(self.capacity)!=type(1)) or\
                self.capacity<0:
                raise FatalSimerror\
                    ("Level: capacity parameter not a positive number: %s"\
                    %self.initialBuffered)

        if type(self.initialBuffered)==type(1.0) or\
                type(self.initialBuffered)==type(1):
            if self.initialBuffered>self.capacity:
                raise FatalSimerror("initialBuffered exceeds capacity")
            if self.initialBuffered>=0:
                self.nrBuffered=self.initialBuffered ## nr items initially in buffer
                                        ## buffer is just a counter (int type)
            else:
                raise FatalSimerror\
                ("initialBuffered param of Level negative: %s"\
                %self.initialBuffered)
        elif self.initialBuffered is None:
            self.initialBuffered=0
            self.nrBuffered=0
        else:
            raise FatalSimerror\
                ("Level: wrong type of initialBuffered (parameter=%s)"\
                %self.initialBuffered)
        if self.monitored:
            self.bufferMon.observe(y=self.amount,t=now())
    amount=property(getamount)

    def _put(self,arg):
        """Handles put requests for Level instances"""
        obj=arg[1]
        if len(arg[0]) == 5:        # yield put,self,buff,whattoput,priority
            obj._putpriority[self]=arg[0][4]
            whatToPut=arg[0][3]
        elif len(arg[0]) == 4:      # yield get,self,buff,whattoput
            obj._putpriority[self]=Buffer.priorityDefault #default
            whatToPut=arg[0][3]
        else:                       # yield get,self,buff
            obj._putpriority[self]=Buffer.priorityDefault #default
            whatToPut=1
        if type(whatToPut)!=type(1) and type(whatToPut)!=type(1.0):
            raise FatalSimerror("Level: put parameter not a number")
        if not whatToPut>=0.0:
            raise FatalSimerror("Level: put parameter not positive number")
        whatToPutNr=whatToPut
        if whatToPutNr+self.amount>self.capacity:
            obj._nextTime=None      #passivate put requestor
            obj._whatToPut=whatToPutNr
            self.putQ.enterPut(obj)    #and queue, with size of put
        else:
            self.nrBuffered+=whatToPutNr
            if self.monitored:
                self.bufferMon.observe(y=self.amount,t=now())
            # service any getters waiting
            # service in queue-order; do not serve second in queue before first
            # has been served
            while len(self.getQ) and self.amount>0:
                proc=self.getQ[0]
                if proc._nrToGet<=self.amount:
                    proc.got=proc._nrToGet
                    self.nrBuffered-=proc.got
                    if self.monitored:
                        self.bufferMon.observe(y=self.amount,t=now())
                    self.getQ.takeout(proc) # get requestor's record out of queue
                    _e._post(proc,at=_t) # continue a blocked get requestor
                else:
                    break
            _e._post(obj,at=_t,prior=1) # continue the put requestor

    def _get(self,arg):
        """Handles get requests for Level instances"""
        obj=arg[1]
        obj.got=None
        if len(arg[0]) == 5:        # yield get,self,buff,whattoget,priority
            obj._getpriority[self]=arg[0][4]
            nrToGet=arg[0][3]
        elif len(arg[0]) == 4:      # yield get,self,buff,whattoget
            obj._getpriority[self]=Buffer.priorityDefault #default
            nrToGet=arg[0][3]
        else:                       # yield get,self,buff
            obj._getpriority[self]=Buffer.priorityDefault
            nrToGet=1
        if type(nrToGet)!=type(1.0) and type(nrToGet)!=type(1):
            raise FatalSimerror\
                ("Level: get parameter not a number: %s"%nrToGet)
        if nrToGet<0:
            raise FatalSimerror\
                ("Level: get parameter not positive number: %s"%nrToGet)
        if self.amount < nrToGet:
            obj._nrToGet=nrToGet
            self.getQ.enterGet(obj)
            # passivate queuing process
            obj._nextTime=None
        else:
            obj.got=nrToGet
            self.nrBuffered-=nrToGet
            if self.monitored:
                self.bufferMon.observe(y=self.amount,t=now())
            _e._post(obj,at=_t,prior=1)
            # reactivate any put requestors for which space is now available
            # service in queue-order; do not serve second in queue before first
            # has been served
            while len(self.putQ): #test for queued producers
                proc=self.putQ[0]
                if proc._whatToPut+self.amount<=self.capacity:
                    self.nrBuffered+=proc._whatToPut
                    if self.monitored:
                        self.bufferMon.observe(y=self.amount,t=now())
                    self.putQ.takeout(proc)#requestor's record out of queue
                    _e._post(proc,at=_t) # continue a blocked put requestor
                else:
                    break

class Store(Buffer):
    """Models buffers for processes coupled by putting/getting distinguishable
    items.
    Blocks a process when a put would cause buffer overflow or a get would cause
    buffer underflow.
    Default queuing discipline for blocked processes is priority FIFO.
    """
    def getnrBuffered(self):
        return len(self.theBuffer)
    nrBuffered=property(getnrBuffered)
    
    def getbuffered(self):
        return self.theBuffer
    buffered=property(getbuffered)
        
    def __init__(self,**pars):
        Buffer.__init__(self,**pars)
        self.theBuffer=[]
        if self.name is None:
            self.name="a_store" ## default name
        if type(self.capacity)!=type(1) or self.capacity<=0:
            raise FatalSimerror\
                ("Store: capacity parameter not a positive integer > 0: %s"\
                    %self.initialBuffered)
        if type(self.initialBuffered)==type([]):
            if len(self.initialBuffered)>self.capacity:
                raise FatalSimerror("initialBuffered exceeds capacity")
            else:
                self.theBuffer[:]=self.initialBuffered##buffer==list of objects
        elif self.initialBuffered is None: 
            self.theBuffer=[]
        else:
            raise FatalSimerror\
                ("Store: initialBuffered not a list")
        if self.monitored:
            self.bufferMon.observe(y=self.nrBuffered,t=now())
        self._sort=None
            

    
    def addSort(self,sortFunc):
        """Adds buffer sorting to this instance of Store. It maintains
        theBuffer sorted by the sortAttr attribute of the objects in the
        buffer.
        The user-provided 'sortFunc' must look like this:
        
        def mySort(self,par):
            tmplist=[(x.sortAttr,x) for x in par]
            tmplist.sort()
            return [x for (key,x) in tmplist]
        
        """

        self._sort=new.instancemethod(sortFunc,self,self.__class__)
        self.theBuffer=self._sort(self.theBuffer)
        
    def _put(self,arg):
        """Handles put requests for Store instances"""
        obj=arg[1]
        if len(arg[0]) == 5:        # yield put,self,buff,whattoput,priority
            obj._putpriority[self]=arg[0][4]
            whatToPut=arg[0][3]
        elif len(arg[0]) == 4:      # yield put,self,buff,whattoput
            obj._putpriority[self]=Buffer.priorityDefault #default
            whatToPut=arg[0][3]
        else:                       # error, whattoput missing
            raise FatalSimerror("Item to put missing in yield put stmt")
        if type(whatToPut)!=type([]):
            raise FatalSimerror("put parameter is not a list")
        whatToPutNr=len(whatToPut)
        if whatToPutNr+self.nrBuffered>self.capacity:
            obj._nextTime=None      #passivate put requestor
            obj._whatToPut=whatToPut
            self.putQ.enterPut(obj) #and queue, with items to put
        else:
            self.theBuffer.extend(whatToPut)
            if not(self._sort is None):
                self.theBuffer=self._sort(self.theBuffer)
            if self.monitored:
                self.bufferMon.observe(y=self.nrBuffered,t=now())

            # service any waiting getters
            # service in queue order: do not serve second in queue before first
            # has been served
            while self.nrBuffered>0 and len(self.getQ):
                proc=self.getQ[0]
                if inspect.isfunction(proc._nrToGet):
                    movCand=proc._nrToGet(self.theBuffer) #predicate parameter
                    if movCand:
                        proc.got=movCand[:]
                        for i in movCand:
                            self.theBuffer.remove(i)
                        self.getQ.takeout(proc)
                        if self.monitored:
                            self.bufferMon.observe(y=self.nrBuffered,t=now()) 
                        _e._post(what=proc,at=_t) # continue a blocked get requestor
                    else:
                        break
                else: #numerical parameter
                    if proc._nrToGet<=self.nrBuffered:
                        nrToGet=proc._nrToGet
                        proc.got=[]
                        proc.got[:]=self.theBuffer[0:nrToGet]
                        self.theBuffer[:]=self.theBuffer[nrToGet:]
                        if self.monitored:
                            self.bufferMon.observe(y=self.nrBuffered,t=now())           
                        # take this get requestor's record out of queue:
                        self.getQ.takeout(proc) 
                        _e._post(what=proc,at=_t) # continue a blocked get requestor
                    else:
                        break
                    
            _e._post(what=obj,at=_t,prior=1) # continue the put requestor

    def _get(self,arg):
        """Handles get requests"""
        filtfunc=None
        obj=arg[1]
        obj.got=[]                  # the list of items retrieved by 'get'
        if len(arg[0]) == 5:        # yield get,self,buff,whattoget,priority
            obj._getpriority[self]=arg[0][4]
            if inspect.isfunction(arg[0][3]):
                filtfunc=arg[0][3]
            else:
                nrToGet=arg[0][3]
        elif len(arg[0]) == 4:      # yield get,self,buff,whattoget
            obj._getpriority[self]=Buffer.priorityDefault #default
            if inspect.isfunction(arg[0][3]):
                filtfunc=arg[0][3]
            else:
                nrToGet=arg[0][3]
        else:                       # yield get,self,buff 
            obj._getpriority[self]=Buffer.priorityDefault
            nrToGet=1
        if not filtfunc: #number specifies nr items to get
            if nrToGet<0:
                raise FatalSimerror\
                    ("Store: get parameter not positive number: %s"%nrToGet)            
            if self.nrBuffered < nrToGet:
                obj._nrToGet=nrToGet
                self.getQ.enterGet(obj)
                # passivate/block queuing 'get' process
                obj._nextTime=None          
            else:
                for i in range(nrToGet):
                    obj.got.append(self.theBuffer.pop(0)) # move items from 
                                                # buffer to requesting process
                if self.monitored:
                    self.bufferMon.observe(y=self.nrBuffered,t=now())
                _e._post(obj,at=_t,prior=1)
                # reactivate any put requestors for which space is now available
                # serve in queue order: do not serve second in queue before first
                # has been served
                while len(self.putQ): 
                    proc=self.putQ[0]
                    if len(proc._whatToPut)+self.nrBuffered<=self.capacity:
                        for i in proc._whatToPut:
                            self.theBuffer.append(i) #move items to buffer
                        if not(self._sort is None):
                            self.theBuffer=self._sort(self.theBuffer)
                        if self.monitored:
                            self.bufferMon.observe(y=self.nrBuffered,t=now())           
                        self.putQ.takeout(proc) # dequeue requestor's record 
                        _e._post(proc,at=_t) # continue a blocked put requestor
                    else:
                        break
        else: # items to get determined by filtfunc
            movCand=filtfunc(self.theBuffer)
            if movCand: # get succeded
                _e._post(obj,at=_t,prior=1)
                obj.got=movCand[:]
                for item in movCand:
                    self.theBuffer.remove(item)
                if self.monitored:
                    self.bufferMon.observe(y=self.nrBuffered,t=now())
                # reactivate any put requestors for which space is now available
                # serve in queue order: do not serve second in queue before first
                # has been served
                while len(self.putQ): 
                    proc=self.putQ[0]
                    if len(proc._whatToPut)+self.nrBuffered<=self.capacity:
                        for i in proc._whatToPut:
                            self.theBuffer.append(i) #move items to buffer
                        if not(self._sort is None):
                            self.theBuffer=self._sort(self.theBuffer)
                        if self.monitored:
                            self.bufferMon.observe(y=self.nrBuffered,t=now())           
                        self.putQ.takeout(proc) # dequeue requestor's record 
                        _e._post(proc,at=_t) # continue a blocked put requestor 
                    else:
                        break
            else: # get did not succeed, block
                obj._nrToGet=filtfunc
                self.getQ.enterGet(obj)
                # passivate/block queuing 'get' process
                obj._nextTime=None   
            
class SimEvent(Lister):
    """Supports one-shot signalling between processes. All processes waiting for an event to occur
    get activated when its occurrence is signalled. From the processes queuing for an event, only
    the first gets activated.
    """
    def __init__(self,name="a_SimEvent"):
        self.name=name
        self.waits=[]
        self.queues=[]
        self.occurred=False
        self.signalparam=None
        
    def signal(self,param=None):
        """Produces a signal to self;
        Fires this event (makes it occur).
        Reactivates ALL processes waiting for this event. (Cleanup waits lists
        of other events if wait was for an event-group (OR).)
        Reactivates the first process for which event(s) it is queuing for
        have fired. (Cleanup queues of other events if wait was for an event-group (OR).)
        """
        self.signalparam=param
        if not self.waits and not self.queues:
            self.occurred=True
        else:
            #reactivate all waiting processes
            for p in self.waits:
                p[0].eventsFired.append(self)
                reactivate(p[0],prior=True)
                #delete waits entries for this process in other events
                for ev in p[1]:
                    if ev!=self:
                        if ev.occurred:
                            p[0].eventsFired.append(ev)
                        for iev in ev.waits:
                            if iev[0]==p[0]:
                                ev.waits.remove(iev)
                                break
            self.waits=[]
            if self.queues:
                proc=self.queues.pop(0)[0]
                proc.eventsFired.append(self)
                reactivate(proc)

    def _wait(self,par):
        """Consumes a signal if it has occurred, otherwise process 'proc'
        waits for this event.
        """
        proc=par[0][1] #the process issuing the yield waitevent command
        proc.eventsFired=[]
        if not self.occurred:
            self.waits.append([proc,[self]])
            proc._nextTime=None #passivate calling process
        else:
            proc.eventsFired.append(self)
            self.occurred=False
            _e._post(proc,at=_t,prior=1)

    def _waitOR(self,par):
        """Handles waiting for an OR of events in a tuple/list.
        """
        proc=par[0][1]
        evlist=par[0][2]
        proc.eventsFired=[]
        anyoccur=False
        for ev in evlist:
            if ev.occurred:
                anyoccur=True
                proc.eventsFired.append(ev)
                ev.occurred=False
        if anyoccur: #at least one event has fired; continue process
            _e._post(proc,at=_t,prior=1)

        else: #no event in list has fired, enter process in all 'waits' lists
            proc.eventsFired=[]
            proc._nextTime=None #passivate calling process
            for ev in evlist:
                ev.waits.append([proc,evlist])

    def _queue(self,par):
        """Consumes a signal if it has occurred, otherwise process 'proc'
        queues for this event.
        """
        proc=par[0][1] #the process issuing the yield queueevent command
        proc.eventsFired=[]
        if not self.occurred:
            self.queues.append([proc,[self]])
            proc._nextTime=None #passivate calling process
        else:
            proc.eventsFired.append(self)
            self.occurred=False
            _e._post(proc,at=_t,prior=1)

    def _queueOR(self,par):
        """Handles queueing for an OR of events in a tuple/list.
        """
        proc=par[0][1]
        evlist=par[0][2]
        proc.eventsFired=[]
        anyoccur=False
        for ev in evlist:
            if ev.occurred:
                anyoccur=True
                proc.eventsFired.append(ev)
                ev.occurred=False
        if anyoccur: #at least one event has fired; continue process
            _e._post(proc,at=_t,prior=1)

        else: #no event in list has fired, enter process in all 'waits' lists
            proc.eventsFired=[]
            proc._nextTime=None #passivate calling process
            for ev in evlist:
                ev.queues.append([proc,evlist])

## begin waituntil functionality
def _test():
    """
    Gets called by simulate after every event, as long as there are processes
    waiting in condQ for a condition to be satisfied.
    Tests the conditions for all waiting processes. Where condition satisfied,
    reactivates that process immediately and removes it from queue.
    """
    global condQ
    rList=[]
    for el in condQ:
        if el.cond():
            rList.append(el)
            reactivate(el)
    for i in rList:
        condQ.remove(i)

    if not condQ:
        _stopWUStepping()

def _waitUntilFunc(proc,cond):
    global condQ
    """
    Puts a process 'proc' waiting for a condition into a waiting queue.
    'cond' is a predicate function which returns True if the condition is
    satisfied.
    """    
    if not cond():
        condQ.append(proc)
        proc.cond=cond
        _startWUStepping()         #signal 'simulate' that a process is waiting
        # passivate calling process
        proc._nextTime=None
    else:
        #schedule continuation of calling process
        _e._post(proc,at=_t,prior=1)


##end waituntil functionality

def scheduler(till=0):
    """Schedules Processes/semi-coroutines until time 'till'.
    Deprecated since version 0.5.
    """
    simulate(until=till)

def holdfunc(a):
    a[0][1]._hold(a)

def requestfunc(a):
    """Handles 'yield request,self,res' and 'yield (request,self,res),(<code>,self,par)'.
    <code> can be 'hold' or 'waitevent'.
    """
    if type(a[0][0])==tuple:
        ## Compound yield request statement
        ## first tuple in ((request,self,res),(xx,self,yy))
        b=a[0][0]
        ## b[2]==res (the resource requested)
        ##process the first part of the compound yield statement
        ##a[1] is the Process instance
        b[2]._request(arg=(b,a[1]))
        ##deal with add-on condition to command
        ##Trigger processes for reneging
        class _Holder(Process):
            """Provides timeout process"""
            def trigger(self,delay):
                yield hold,self,delay
                if not proc in b[2].activeQ:
                    reactivate(proc)

        class _EventWait(Process):
            """Provides event waiting process"""
            def trigger(self,event):
                yield waitevent,self,event
                if not proc in b[2].activeQ:
                    a[1].eventsFired=self.eventsFired
                    reactivate(proc)
               
        #activate it
        proc=a[0][0][1] # the process to be woken up
        actCode=a[0][1][0]
        if actCode==hold:
            proc._holder=_Holder(name="RENEGE-hold for %s"%proc.name)
            ##                                          the timeout delay
            activate(proc._holder,proc._holder.trigger(a[0][1][2]))
        elif actCode==waituntil:
            raise FatalSimerror("Illegal code for reneging: waituntil")
        elif actCode==waitevent:
            proc._holder=_EventWait(name="RENEGE-waitevent for %s"%proc.name)
            ##                                          the event
            activate(proc._holder,proc._holder.trigger(a[0][1][2]))
        elif actCode==queueevent:
            raise FatalSimerror("Illegal code for reneging: queueevent")
        else:
            raise FatalSimerror("Illegal code for reneging %s"%actCode)
    else:
        ## Simple yield request command
        a[0][2]._request(a)

def releasefunc(a):
    a[0][2]._release(a)

def passivatefunc(a):
    a[0][1]._passivate(a)

def waitevfunc(a):
    #if waiting for one event only (not a tuple or list)
    evtpar=a[0][2]
    if isinstance(evtpar,SimEvent):
        a[0][2]._wait(a)
    # else, if waiting for an OR of events (list/tuple):
    else: #it should be a list/tuple of events
        # call _waitOR for first event
        evtpar[0]._waitOR(a)
            
def queueevfunc(a):
    #if queueing for one event only (not a tuple or list)
    evtpar=a[0][2]
    if isinstance(evtpar,SimEvent):
        a[0][2]._queue(a)
    #else, if queueing for an OR of events (list/tuple):
    else: #it should be a list/tuple of events
        # call _queueOR for first event
        evtpar[0]._queueOR(a)
    
def waituntilfunc(par):
    _waitUntilFunc(par[0][1],par[0][2])
    
def getfunc(a):
    """Handles 'yield get,self,buffer,what,priority' and 
    'yield (get,self,buffer,what,priority),(<code>,self,par)'.
    <code> can be 'hold' or 'waitevent'.
    """
    if type(a[0][0])==tuple:
        ## Compound yield request statement
        ## first tuple in ((request,self,res),(xx,self,yy))
        b=a[0][0]
        ## b[2]==res (the resource requested)
        ##process the first part of the compound yield statement
        ##a[1] is the Process instance 
        b[2]._get(arg=(b,a[1]))
        ##deal with add-on condition to command
        ##Trigger processes for reneging
        class _Holder(Process):
            """Provides timeout process"""
            def trigger(self,delay):
                yield hold,self,delay
                #if not proc in b[2].activeQ:
                if proc in b[2].getQ:
                    reactivate(proc)

        class _EventWait(Process):
            """Provides event waiting process"""
            def trigger(self,event):
                yield waitevent,self,event
                if proc in b[2].getQ:
                    a[1].eventsFired=self.eventsFired
                    reactivate(proc)
               
        #activate it
        proc=a[0][0][1] # the process to be woken up
        actCode=a[0][1][0]
        if actCode==hold:
            proc._holder=_Holder("RENEGE-hold for %s"%proc.name)
            ##                                          the timeout delay
            activate(proc._holder,proc._holder.trigger(a[0][1][2]))
        elif actCode==waituntil:
            raise FatalSimerror("Illegal code for reneging: waituntil")
        elif actCode==waitevent:
            proc._holder=_EventWait(proc.name)
            ##                                          the event
            activate(proc._holder,proc._holder.trigger(a[0][1][2]))
        elif actCode==queueevent:
            raise FatalSimerror("Illegal code for reneging: queueevent")
        else:
            raise FatalSimerror("Illegal code for reneging %s"%actCode)
    else:
        ## Simple yield request command
        a[0][2]._get(a)


def putfunc(a):
    """Handles 'yield put' (simple and compound hold/waitevent)
    """
    if type(a[0][0])==tuple:
        ## Compound yield request statement
        ## first tuple in ((request,self,res),(xx,self,yy))
        b=a[0][0]
        ## b[2]==res (the resource requested)
        ##process the first part of the compound yield statement
        ##a[1] is the Process instance 
        b[2]._put(arg=(b,a[1]))
        ##deal with add-on condition to command
        ##Trigger processes for reneging
        class _Holder(Process):
            """Provides timeout process"""
            def trigger(self,delay):
                yield hold,self,delay
                #if not proc in b[2].activeQ:
                if proc in b[2].putQ:
                    reactivate(proc)

        class _EventWait(Process):
            """Provides event waiting process"""
            def trigger(self,event):
                yield waitevent,self,event
                if proc in b[2].putQ:
                    a[1].eventsFired=self.eventsFired
                    reactivate(proc)
               
        #activate it
        proc=a[0][0][1] # the process to be woken up
        actCode=a[0][1][0]
        if actCode==hold:
            proc._holder=_Holder("RENEGE-hold for %s"%proc.name)
            ##                                          the timeout delay
            activate(proc._holder,proc._holder.trigger(a[0][1][2]))
        elif actCode==waituntil:
            raise FatalSimerror("Illegal code for reneging: waituntil")
        elif actCode==waitevent:
            proc._holder=_EventWait("RENEGE-waitevent for %s"%proc.name)
            ##                                          the event
            activate(proc._holder,proc._holder.trigger(a[0][1][2]))
        elif actCode==queueevent:
            raise FatalSimerror("Illegal code for reneging: queueevent")
        else:
            raise FatalSimerror("Illegal code for reneging %s"%actCode)
    else:
        ## Simple yield request command
        a[0][2]._put(a)

def simulate(callback=lambda :None,until=0):
    """Schedules Processes/semi-coroutines until time 'until'"""
    
    """Gets called once. Afterwards, co-routines (generators) return by 
    'yield' with a cargo:
    yield hold, self, <delay>: schedules the "self" process for activation 
                               after <delay> time units.If <,delay> missing,
                               same as "yield hold,self,0"
                               
    yield passivate,self    :  makes the "self" process wait to be re-activated

    yield request,self,<Resource>[,<priority>]: request 1 unit from <Resource>
        with <priority> pos integer (default=0)

    yield release,self,<Resource> : release 1 unit to <Resource>

    yield waitevent,self,<SimEvent>|[<Evt1>,<Evt2>,<Evt3), . . . ]:
        wait for one or more of several events
        

    yield queueevent,self,<SimEvent>|[<Evt1>,<Evt2>,<Evt3), . . . ]:
        queue for one or more of several events

    yield waituntil,self,cond : wait for arbitrary condition

    yield get,self,<buffer>[,<WhatToGet>[,<priority>]]
        get <WhatToGet> items from buffer (default=1); 
        <WhatToGet> can be a pos integer or a filter function
        (Store only)
        
    yield put,self,<buffer>[,<WhatToPut>[,priority]]
        put <WhatToPut> items into buffer (default=1);
        <WhatToPut> can be a pos integer (Level) or a list of objects
        (Store)

    EXTENSIONS:
    Request with timeout reneging:
    yield (request,self,<Resource>),(hold,self,<patience>) :
        requests 1 unit from <Resource>. If unit not acquired in time period
        <patience>, self leaves waitQ (reneges).

    Request with event-based reneging:
    yield (request,self,<Resource>),(waitevent,self,<eventlist>):
        requests 1 unit from <Resource>. If one of the events in <eventlist> occurs before unit
        acquired, self leaves waitQ (reneges).
        
    Get with timeout reneging (for Store and Level):
    yield (get,self,<buffer>,nrToGet etc.),(hold,self,<patience>)
        requests <nrToGet> items/units from <buffer>. If not acquired <nrToGet> in time period
        <patience>, self leaves <buffer>.getQ (reneges).
        
    Get with event-based reneging (for Store and Level):
    yield (get,self,<buffer>,nrToGet etc.),(waitevent,self,<eventlist>)
        requests <nrToGet> items/units from <buffer>. If not acquired <nrToGet> before one of
        the events in <eventlist> occurs, self leaves <buffer>.getQ (reneges).

        

    Event notices get posted in event-list by scheduler after "yield" or by 
    "activate"/"reactivate" functions.

    Nov 9, 2003: Added capability to step through simulation event by event if
                 step==True. 'callback' gets called after every event. It can
                 cancel stepping or end run. API and semantics backwards
                 compatible with previous versions of simulate().
    
    """
    global _endtime,_e,_stop,_t,_step,_wustep
    paused=False
    _stop=False

    if _e is None:
        raise FatalSimerror("Simulation not initialized")
    if _e._isEmpty():
        message="SimPy: No activities scheduled"
        return message
        
    _endtime=until
    message="SimPy: Normal exit"
    dispatch={hold:holdfunc,request:requestfunc,release:releasefunc,
              passivate:passivatefunc,waitevent:waitevfunc,queueevent:queueevfunc,
              waituntil:waituntilfunc,get:getfunc,put:putfunc}
    commandcodes=dispatch.keys()
    commandwords={hold:"hold",request:"request",release:"release",passivate:"passivate",
        waitevent:"waitevent",queueevent:"queueevent",waituntil:"waituntil",
        get:"get",put:"put"}
    nextev=_e._nextev ## just a timesaver
    while not _stop and _t<=_endtime:
        try:
            a=nextev()
            if not a[0] is None:
                ## 'a' is tuple "(<yield command>, <action>)"  
                if type(a[0][0])==tuple:
                    ##allowing for yield (request,self,res),(waituntil,self,cond)
                    command=a[0][0][0]
                else: 
                    command = a[0][0]
                if __debug__:
                    if not command in commandcodes:
                        raise FatalSimerror("Illegal command: yield %s"%command)
                dispatch[command](a)     
        except FatalSimerror,error:
            print "SimPy: "+error.value
            sys.exit(1)
        except Simerror,error:
            message="SimPy: "+error.value
            _stop = True
        if _step:
            callback()
        if _wustep:
            _test()
    _stopWUStepping()            
    stopStepping()
    _e=None
    return message

def simulateStep(callback=lambda :None,until=0):
    """Schedules Processes/semi-coroutines until next event"""
    
    """Can be called repeatedly.
    Behaves like "simulate", but does execute only one event per call.
                               

    
    """
    global _endtime,_e,_stop,_t,_step

    status="resumable"

    if _e == None:
        raise Simerror("Fatal SimPy error: Simulation not initialized")
    if _e._isEmpty():
        message="SimPy: No activities scheduled"
        status="notResumable"
        return message,status
        
    _endtime=until
    message="SimPy: Normal exit" 
    dispatch={hold:holdfunc,request:requestfunc,release:releasefunc,
              passivate:passivatefunc,waitevent:waitevfunc,queueevent:queueevfunc,
              waituntil:waituntilfunc,get:getfunc,put:putfunc}
    commandcodes=dispatch.keys()
    commandwords={hold:"hold",request:"request",release:"release",passivate:"passivate",
        waitevent:"waitevent",queueevent:"queueevent",waituntil:"waituntil",
        get:"get",put:"put"}
    if not _stop and _t<=_endtime:
        try:
            a=_e._nextev()        
            if not a[0]==None:
                ## 'a' is tuple "(<yield command>, <action>)"  
                if type(a[0][0])==tuple:
                    ##allowing for yield (request,self,res),(waituntil,self,cond)
                    command=a[0][0][0]
                else: 
                    command = a[0][0]
                if __debug__:
                    if not command in commandcodes:
                        raise FatalSimerror("Fatal error: illegal command: yield %s"%command)
                dispatch[command](a)         
        except FatalSimerror,error:
            print "SimPy: "+error.value
            sys.exit(1)
        except Simerror, error:
            message="SimPy: "+ error.value
            _stop = True
            status="notResumable"
        if _step:
            callback()
    return message,status
    

################### end of Simulation module
    
if __name__ == "__main__":
    print "SimPy.SimulationStep %s" %__version__
    ################### start of test/demo programs
    
    def askCancel():
        a=raw_input("[Time=%s] End run (e), Continue stepping (s), Run to end (r)"%now())
        if a=="e":
            stopSimulation()
        elif a=="s":
            return
        else:
            stopStepping()
    
    def test_demo():
        class Aa(Process):
            sequIn=[]
            sequOut=[]
            def __init__(self,holdtime,name):
                Process.__init__(self,name)
                self.holdtime=holdtime
    
            def life(self,priority):
                for i in range(1):
                    Aa.sequIn.append(self.name)
                    print now(),rrr.name,"waitQ:",len(rrr.waitQ),"activeQ:",\
                          len(rrr.activeQ)
                    print "waitQ: ",[(k.name,k._priority[rrr]) for k in rrr.waitQ]
                    print "activeQ: ",[(k.name,k._priority[rrr]) \
                               for k in rrr.activeQ]
                    assert rrr.n+len(rrr.activeQ)==rrr.capacity, \
                           "Inconsistent resource unit numbers"
                    print now(),self.name,"requests 1 ", rrr.unitName
                    yield request,self,rrr,priority
                    print now(),self.name,"has 1 ",rrr.unitName
                    print now(),rrr.name,"waitQ:",len(rrr.waitQ),"activeQ:",\
                          len(rrr.activeQ)
                    print now(),rrr.name,"waitQ:",len(rrr.waitQ),"activeQ:",\
                          len(rrr.activeQ)
                    assert rrr.n+len(rrr.activeQ)==rrr.capacity, \
                           "Inconsistent resource unit numbers"
                    yield hold,self,self.holdtime
                    print now(),self.name,"gives up 1",rrr.unitName
                    yield release,self,rrr
                    Aa.sequOut.append(self.name)
                    print now(),self.name,"has released 1 ",rrr.unitName
                    print "waitQ: ",[(k.name,k._priority[rrr]) for k in rrr.waitQ]
                    print now(),rrr.name,"waitQ:",len(rrr.waitQ),"activeQ:",\
                          len(rrr.activeQ)
                    assert rrr.n+len(rrr.activeQ)==rrr.capacity, \
                           "Inconsistent resource unit numbers"
    
        class Destroyer(Process):
            def __init__(self):
                Process.__init__(self)
    
            def destroy(self,whichProcesses):
                for i in whichProcesses:
                    Process().cancel(i)
                yield hold,self,0
    
        class Observer(Process):
            def __init__(self):
                Process.__init__(self)
    
            def observe(self,step,processes,res):
                while now()<11:
                    for i in processes:
                        print " %s %s: act:%s, pass:%s, term: %s,interr:%s, qu:%s"\
                              %(now(),i.name,i.active(),i.passive(),i.terminated()\
                            ,i.interrupted(),i.queuing(res))
                    print
                    yield hold,self,step
    
        class UserControl(Process):
            def letUserInteract(self,when):
                yield hold,self,when
                startStepping()
                        
        print "****First case == priority queue, resource service not preemptable"
        initialize()
        rrr=Resource(5,name="Parking",unitName="space(s)", qType=PriorityQ,
                     preemptable=0)
        procs=[]
        for i in range(10):
            z=Aa(holdtime=i,name="Car "+str(i))
            procs.append(z)
            activate(z,z.life(priority=i))
        o=Observer()
        activate(o,o.observe(1,procs,rrr))
        startStepping()
        a=simulate(until=10000,callback=askCancel)
        print "Input sequence: ",Aa.sequIn
        print "Output sequence: ",Aa.sequOut
    
        print "\n****Second case == priority queue, resource service preemptable"
        initialize()
        rrr=Resource(5,name="Parking",unitName="space(s)", qType=PriorityQ,
                     preemptable=1)
        procs=[]
        for i in range(10):
            z=Aa(holdtime=i,name="Car "+str(i))
            procs.append(z)
            activate(z,z.life(priority=i))
        o=Observer()
        activate(o,o.observe(1,procs,rrr))
        u=UserControl()
        activate(u,u.letUserInteract(4))
        Aa.sequIn=[]
        Aa.sequOut=[]
        a=simulate(askCancel,until=10000)
        print a
        print "Input sequence: ",Aa.sequIn
        print "Output sequence: ",Aa.sequOut   
    
    def test_interrupt():
        class Bus(Process):
            def __init__(self,name):
                Process.__init__(self,name)
    
            def operate(self,repairduration=0):
                print now(),">> %s starts" %(self.name)
                tripleft = 1000
                while tripleft > 0:
                    yield hold,self,tripleft
                    if self.interrupted():
                        print "interrupted by %s" %self.interruptCause.name
                        print "%s: %s breaks down " %(now(),self.name)
                        tripleft=self.interruptLeft
                        self.interruptReset()
                        print "tripleft ",tripleft
                        reactivate(br,delay=repairduration) # breakdowns only during operation
                        yield hold,self,repairduration
                        print now()," repaired"
                    else:
                        break # no breakdown, ergo bus arrived
                print now(),"<< %s done" %(self.name)
    
        class Breakdown(Process):
            def __init__(self,myBus):
                Process.__init__(self,name="Breakdown "+myBus.name)
                self.bus=myBus
    
            def breakBus(self,interval):
    
                while True:
                    yield hold,self,interval
                    if self.bus.terminated(): break
                    self.interrupt(self.bus)
                    
        print"\n\n+++test_interrupt"
        initialize()
        b=Bus("Bus 1")
        activate(b,b.operate(repairduration=20))
        br=Breakdown(b)
        activate(br,br.breakBus(200))
        startStepping()
        simulate(until=4000)
    
        
    def testSimEvents():
        class Waiter(Process):
            def waiting(self,theSignal):
                while True:
                    yield waitevent,self,theSignal
                    print "%s: process '%s' continued after waiting for %s"%(now(),self.name,theSignal.name)
                    yield queueevent,self,theSignal
                    print "%s: process '%s' continued after queueing for %s"%(now(),self.name,theSignal.name)
                    
        class ORWaiter(Process):
            def waiting(self,signals):
                while True:
                    yield waitevent,self,signals
                    print now(),"one of %s signals occurred"%[x.name for x in signals]
                    print "\t%s (fired/param)"%[(x.name,x.signalparam) for x in self.eventsFired]
                    yield hold,self,1
                    
        class Caller(Process):
            def calling(self):
                while True:
                    signal1.signal("wake up!")
                    print "%s: signal 1 has occurred"%now()
                    yield hold,self,10
                    signal2.signal("and again")
                    signal2.signal("sig 2 again")
                    print "%s: signal1, signal2 have occurred"%now()
                    yield hold,self,10
        print"\n+++testSimEvents output"
        initialize()
        signal1=SimEvent("signal 1")
        signal2=SimEvent("signal 2")
        signal1.signal("startup1")
        signal2.signal("startup2")
        w1=Waiter("waiting for signal 1")
        activate(w1,w1.waiting(signal1))
        w2=Waiter("waiting for signal 2")
        activate(w2,w2.waiting(signal2))
        w3=Waiter("also waiting for signal 2")
        activate(w3,w3.waiting(signal2))
        w4=ORWaiter("waiting for either signal 1 or signal 2")
        activate(w4,w4.waiting([signal1,signal2]),prior=True)
        c=Caller("Caller")
        activate(c,c.calling())
        print simulate(until=100)
        
    def testwaituntil():
        """
        Demo of waitUntil capability.
    
        Scenario:
        Three workers require sets of tools to do their jobs. Tools are shared, scarce
        resources for which they compete.
        """
    
    
        class Worker(Process):
            def __init__(self,name,heNeeds=[]):
                Process.__init__(self,name)
                self.heNeeds=heNeeds
            def work(self):
            
                def workerNeeds():
                    for item in self.heNeeds:
                        if item.n==0:
                            return False
                    return True
                         
                while now()<8*60:
                    yield waituntil,self,workerNeeds
                    for item in self.heNeeds:
                        yield request,self,item
                    print "%s %s has %s and starts job" %(now(),self.name,
                        [x.name for x in self.heNeeds])
                    yield hold,self,random.uniform(10,30)
                    for item in self.heNeeds:
                        yield release,self,item
                    yield hold,self,2 #rest
      
        print "\n+++ nwaituntil demo output"
        initialize()
        brush=Resource(capacity=1,name="brush")
        ladder=Resource(capacity=2,name="ladder")
        hammer=Resource(capacity=1,name="hammer")
        saw=Resource(capacity=1,name="saw")
        painter=Worker("painter",[brush,ladder])
        activate(painter,painter.work())
        roofer=Worker("roofer",[hammer,ladder,ladder])
        activate(roofer,roofer.work())
        treeguy=Worker("treeguy",[saw,ladder])
        activate(treeguy,treeguy.work())
        for who in (painter,roofer,treeguy):
            print "%s needs %s for his job" %(who.name,[x.name for x in who.heNeeds])
        print
        print simulate(until=9*60)    
        
        
        
        
    test_demo()
    test_interrupt()
    testSimEvents()
    testwaituntil()
    





































































    
