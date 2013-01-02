#!/usr/bin/env lua

require "SimLua.Heap"
Heap = SimLua.Heap

print "Teste"
at = 1
t = 10

assert(at < t, "erro")
print "Fim"

h = Heap.new()
for i=1,3 do h:push(i, math.random()) end
while not h:isempty() do print(h:pop()) end