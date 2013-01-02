#include "lua.h"
#include "lauxlib.h"
#include <stdio.h>

#define FOO "Foo"

typedef struct Foo {
  int x;
  int y;
} Foo;

static Foo *toFoo (lua_State *L, int index)
{
  puts("Foo: toFoo");
  Foo *bar = (Foo *)lua_touserdata(L, index);
  if (bar == NULL) luaL_typerror(L, index, FOO);
  return bar;
}

static Foo *checkFoo (lua_State *L, int index)
{
  puts("Foo: checkFoo");
  Foo *bar;
  luaL_checktype(L, index, LUA_TUSERDATA);
  bar = (Foo *)luaL_checkudata(L, index, FOO);
  if (bar == NULL) luaL_typerror(L, index, FOO);
  return bar;
}

static Foo *pushFoo (lua_State *L)
{
  puts("Foo: pushFoo");
  Foo *bar = (Foo *)lua_newuserdata(L, sizeof(Foo));
  luaL_getmetatable(L, FOO);
  lua_setmetatable(L, -2);
  return bar;
}

static int Foo_new (lua_State *L)
{
  puts("Foo: Foo_new");
  int x = luaL_optint(L, 1, 0);
  int y = luaL_optint(L, 2, 0);
  Foo *bar = pushFoo(L);
  bar->x = x;
  bar->y = y;
  return 1;
}

static int Foo_yourCfunction (lua_State *L)
{
  puts("Foo: Foo_yourCfunction");
  Foo *bar = checkFoo(L, 1);
  printf("this is yourCfunction\t");
  lua_pushnumber(L, bar->x);
  lua_pushnumber(L, bar->y);
  return 2;
}

static int Foo_setx (lua_State *L)
{
  puts("Foo: Foo_setx");
  Foo *bar = checkFoo(L, 1);
  bar->x = luaL_checkint(L, 2);
  lua_settop(L, 1);
  return 1;
}

static int Foo_sety (lua_State *L)
{
  puts("Foo: Foo_sety");
  Foo *bar = checkFoo(L, 1);
  bar->y = luaL_checkint(L, 2);
  lua_settop(L, 1);
  return 1;
}

static int Foo_add (lua_State *L)
{
  puts("Foo: Foo_add");
  Foo *bar1 = checkFoo(L, 1);
  Foo *bar2 = checkFoo(L, 2);
  Foo *sum  = pushFoo(L);
  sum->x = bar1->x + bar2->x;
  sum->y = bar1->y + bar2->y;
  return 1;
}

static int Foo_dot (lua_State *L)
{
  puts("Foo: Foo_dot");
  Foo *bar1 = checkFoo(L, 1);
  Foo *bar2 = checkFoo(L, 2);
  lua_pushnumber(L, bar1->x * bar2->x + bar1->y * bar2->y);
  return 1;
}

static const luaL_reg Foo_methods[] = {
  {"new",           Foo_new},
  {"yourCfunction", Foo_yourCfunction},
  {"setx",          Foo_setx},
  {"sety",          Foo_sety},
  {"add",           Foo_add},
  {"dot",           Foo_dot},
  {0, 0}
};

static int Foo_gc (lua_State *L)
{
  puts("Foo: Foo_gc");
  printf("bye, bye, bar = %p\n", toFoo(L, 1));
  return 0;
}

static int Foo_tostring (lua_State *L)
{
  puts("Foo: Foo_tostring");
  char buff[32];
  sprintf(buff, "%p", toFoo(L, 1));
  lua_pushfstring(L, "Foo (%s)", buff);
  return 1;
}

static const luaL_reg Foo_meta[] = {
  {"__gc",       Foo_gc},
  {"__tostring", Foo_tostring},
  {"__add",      Foo_add},
  {0, 0}
};

int Foo_register (lua_State *L)
{
  puts("Foo: Foo_register");
  luaL_openlib(L, FOO, Foo_methods, 0);  /* create methods table,
                                            add it to the globals */
  luaL_newmetatable(L, FOO);          /* create metatable for Foo,
                                         and add it to the Lua registry */
  luaL_openlib(L, 0, Foo_meta, 0);    /* fill metatable */
  lua_pushliteral(L, "__index");
  lua_pushvalue(L, -3);               /* dup methods table*/
  lua_rawset(L, -3);                  /* metatable.__index = methods */
  lua_pushliteral(L, "__metatable");
  lua_pushvalue(L, -3);               /* dup methods table*/
  lua_rawset(L, -3);                  /* hide metatable:
                                         metatable.__metatable = methods */
  lua_pop(L, 1);                      /* drop metatable */
  return 1;                           /* return methods on the stack */
}

int luaopen_foo2 (lua_State *L) {
  luaL_register(L, "Foo", Foo_methods);
  return 1;
}
