-- Evlist.lua
-- List of Events

local assert, setmetatable = assert, setmetatable

module(...)

require "Heap"
local Heap = Heap

---->    """Defines event list and operations on it"""
---->    def __init__(self):
---->        # always sorted list of events (sorted by time, priority)
---->        # make heapq
---->        self.timestamps = []
---->        self.sortpr=0
function Evlist.create()
    self.timestamps = {}
    self.sortpr = 0
end

---->    def _post(self, what, at, prior=False):
---->        """Post an event notice for process what for time at"""
---->        # event notices are Process instances
---->        if at < _t:
---->            raise Simerror("Attempt to schedule event in the past")
---->        what._nextTime = at
---->        self.sortpr-=1
---->        if prior:
---->            # before all other event notices at this time
---->            # heappush with highest priority value so far (negative of 
---->            # monotonely decreasing number)
---->            # store event notice in process instance
---->            what._rec=[at,self.sortpr,what,False]
---->            # make event list refer to it
---->            hq.heappush(self.timestamps,what._rec)
---->        else:
---->            # heappush with lowest priority
---->            # store event notice in process instance
---->            what._rec=[at,-self.sortpr,what,False]
---->            # make event list refer to it
---->            hq.heappush(self.timestamps,what._rec)
local function post(ev, what, at, prior=false)
    assert(at < t, "Attempt to schedule event in the past")
end

---->    def _unpost(self, whom):
---->        """
---->        Mark event notice for whom as cancelled if whom is a suspended process
---->        """
---->        if whom._nextTime is not None:  # check if whom was actually active
---->            whom._rec[3]=True ## Mark as cancelled
---->            whom._nextTime=None
local function unpost(ev, whom)
end

---->    def _nextev(self):
---->        """Retrieve next event from event list"""
---->        global _t, _stop
---->        noActiveNotice=True
---->        ## Find next event notice which is not marked cancelled
---->        while noActiveNotice:
---->            if self.timestamps:
---->                 ## ignore priority value         
---->                (_tnotice, p,nextEvent,cancelled) = hq.heappop(self.timestamps)
---->                noActiveNotice=cancelled
---->            else:
---->                raise Simerror("No more events at time %s" % _t)
---->        nextEvent._rec=None
---->        _t=_tnotice
---->        if _t > _endtime:
---->            _t = _endtime
---->            _stop = True
---->            return (None,)
---->        try:
---->            resultTuple = nextEvent._nextpoint.next()
---->        except StopIteration:
---->            nextEvent._nextpoint = None
---->            nextEvent._terminated = True
---->            nextEvent._nextTime = None
---->            resultTuple = None
---->        return (resultTuple, nextEvent)
local function nextev(ev)
end

---->    def _isEmpty(self):
---->        return not self.timestamps
local function isEmpty(ev)
    return not timestamps
end

---->    def _allEventNotices(self):
---->        """Returns string with eventlist as
---->                t1: [procname,procname2]
---->                t2: [procname4,procname5, . . . ]
---->                . . .  .
---->        """
---->        ret=""
---->        for t in self.timestamps:
---->            ret+="%s:%s\n"%(t[1]._nextTime, t[1].name)
---->        return ret[:-1]
local function allEventNotices(ev)
end

---->    def _allEventTimes(self):
---->        return self.timestamps
local function allEventTimes(ev)
-- Returns list of all times for which events are scheduled
    return timestamps
end

function new()
    return setmetatable({timestamps = nil, sortpr = 0},
        {__index = {post = post,
                    unpost = unpost,
                    nextev = nextev,
                    isEmpty = isEmpty,
                    allEventNotices = allEventNotices,
                    allEventTimes = allEvenTimes}})
end