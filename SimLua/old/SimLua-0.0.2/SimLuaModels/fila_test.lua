#!/usr/bin/env lua

require "SimLua.Fila"

Fila = SimLua.Fila

print "Criando novo heap"
f = Fila.create()

print "Inserindo dados..."
f:push(0.1, 1)
f:push(0.2, 10)
f:push(0.3, 20)
f:push(0.4, 15)
f:push(0.5, 21)
f:push(0.6, 25)
f:push(0.7, 35)

print "--- Heap ---"
table.foreach(f.heap, print)
print "--- Node ---"
table.foreach(f.nodes, print)

print "Removendo dados..."
print(f:pop())
print(f:pop())
print(f:pop())
print(f:pop())
print(f:pop())
print(f:pop())
print(f:pop())

--os.exit()


print "Criando novo heap"
f = nil
f = Fila.create()

print "Inserindo dados..."
f:push(1, 1)
f:push(2, 10)
f:push(3, 20)
f:push(4, 15)
f:push(5, 21)
f:push(6, 25)
f:push(7, 35)

print "--- Heap ---"
table.foreach(f.heap, print)
print "--- Node ---"
table.foreach(f.nodes, print)

print "Removendo dados..."
print(f:pop())
print(f:pop())
print(f:pop())
print(f:pop())
print(f:pop())
print(f:pop())
print(f:pop())

--os.exit()
for m=1,100 do
    print("------------>", m)
    math.randomseed(os.time())
    print "Criando novo heap"
    f1 = Fila.create()
    print "Inserindo dados..."
    for i=1,1000000 do f1:push(i, math.random(50)) end
    print "Removendo dados..."
    _, h = f1:pop()
    while not f1:isEmpty() do
        _, g = f1:pop()
        assert(h <= g, "error!!!")
        h = g
    end
end
