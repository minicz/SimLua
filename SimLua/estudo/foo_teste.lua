for n,v in pairs(Foo) do print(n,v) end

local a = Foo.new()
local b = Foo.new(99,100)

MyFunction = Foo.yourCfunction

print(a, MyFunction(a))
print(b, MyFunction(b))

function Foo:show(msg)
  print(msg, self, self:yourCfunction())
  return self
end

function Foo:point(t)
  assert(type(t) == 'table')
  self:setx(t.x or t[1]):sety(t.y or t[2])
  return self
end

setmetatable(Foo, { __call = function(self, x, y)
                               local bar = self.new(x,y)
                               print('created', bar)
                               return bar
                             end } )

local p = Foo(1,2)
p:show('p is')
p:setx(3):show'p is':sety(4):show'p is'
p:point{33,44}:show'p is'
p = nil

collectgarbage()

a:point{x=500, y=1000}
a:show'a is'

r = Foo.add(a,b)
r:show'r is'

a:show'a is'
b:show'b is'
s = a + b
s:show's is'

--debug.debug()

