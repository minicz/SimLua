#!/usr/bin/env lua

require "SimLua.Heap"

Heap = SimLua.Heap

print "Criando novo heap"
h = Heap.new()

print "Inserindo dados..."
h:push(1, 1)
h:push(2, 10)
h:push(3, 20)
h:push(4, 15)
h:push(5, 21)
h:push(6, 25)
h:push(7, 35)

print "--- Heap ---"
table.foreach(h.heap, print)
print "--- Node ---"
table.foreach(h.nodes, print)

print "Removendo dados..."
print(h:pop())
print(h:pop())
print(h:pop())
print(h:pop())
print(h:pop())
print(h:pop())
print(h:pop())

for m=1,100 do
    print("------------>", m)
    math.randomseed(os.time())
    print "Criando novo heap"
    h1 = Heap.new()
    print "Inserindo dados..."
    for i=1,1000000 do h1:push(i, math.random(50)) end
    print "Removendo dados..."
    _, f = h1:pop()
    while not h1:isempty() do
        _, g = h1:pop()
        assert(f <= g, "error!!!")
        f = g
    end
end