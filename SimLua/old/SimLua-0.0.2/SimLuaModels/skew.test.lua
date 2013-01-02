#!/usr/bin/env lua

insert = require "skew".insert

for m=1,10000 do
    print("------------>", m)
    math.randomseed(os.time())
    print "Inserindo dados..."
    for i= 1, 10000 do h = insert(h, math.random(), i) end
    print "Removendo dados..."
    while h~= nil do h, p, v = h:retrieve() end
end