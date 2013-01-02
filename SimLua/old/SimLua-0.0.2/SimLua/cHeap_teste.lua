#!/usr/bin/env lua

print "Compilando..."
os.execute("gcc -fPIC -Wall -c cHeap.c")
os.execute("ld -shared cHeap.o -o cHeap.so")
print "----> Final de compilação"

local cHeap = require "cHeap"

cHeap.new()
cHeap.isEmpty()
cHeap.push()
cHeap.pop()

os.exit()

Queue.push(10,20)


queue = Queue

--print "Criando novo heap"
--q = queue.new()

print "Inserindo dados..."
q.push(1, 1)
q:push(2, 10)
q:push(3, 20)
q:push(4, 15)
q:push(5, 21)
q:push(6, 25)
q:push(7, 35)

print "--- Heap ---"
table.foreach(q.heap, print)
print "--- Node ---"
table.foreach(q.nodes, print)

print "Removendo dados..."
print(q:pop())
print(q:pop())
print(q:pop())
print(q:pop())
print(q:pop())
print(q:pop())
print(q:pop())

for m=1,100 do
    print("------------>", m)
    math.randomseed(os.time())
    print "Criando novo heap"
    h1 = Heap.create()
    print "Inserindo dados..."
    for i=1,1000000 do h1:push(i, math.random(50)) end
    print "Removendo dados..."
    _, f = h1:pop()
    while not h1:isEmpty() do
        _, g = h1:pop()
        assert(f <= g, "error!!!")
        f = g
    end
end
