/*
 * skew.c
 * Bottom-up skew heaps, adapted from
 * Sleator, D. D., and Tarjan, R. E. (1986), "Self-adjusting heaps",
 * SIAM J. COMPUT., 15 (1)
 * http://www.cs.cmu.edu/~sleator/papers/Adjusting-Heaps.htm
 *
 * Check bottom of this file for license
*/

#include <lua.h>
#include <lauxlib.h>

typedef struct heapstc *heapptr;
typedef struct heapstc {
  lua_Number value;
  heapptr up;
  heapptr down;
} heap;


static heap *checkheap (lua_State *L, int pos) {
  heap *h = NULL;
  if (lua_isnoneornil(L, pos) || !lua_getmetatable(L, pos)) return NULL;
  if (lua_rawequal(L, -1, LUA_ENVIRONINDEX))
    h = (heap *) lua_touserdata(L, pos);
  lua_pop(L, 1); /* MT */
  return h;
}

/* assumes key is at top of stack */
static heap *newheap (lua_State *L, lua_Number v) {
  heap *h = lua_newuserdata(L, sizeof(heap));
  h->value = v;
  lua_pushvalue(L, LUA_ENVIRONINDEX);
  lua_pushvalue(L, -2); /* h */
  lua_pushvalue(L, -4); /* stack top: key */
  lua_rawset(L, -3); /* env[h] = key */
  lua_pushlightuserdata(L, (void *) h);
  lua_pushvalue(L, -3); /* h */
  lua_rawset(L, -3); /* env[light(h)] = h */
  lua_setmetatable(L, -2);
  return h;
}

static void pushheap (lua_State *L, heap *h) {
  if (h == NULL) lua_pushnil(L);
  else {
    lua_pushvalue(L, LUA_ENVIRONINDEX);
    lua_pushlightuserdata(L, (void *) h);
    lua_rawget(L, -2);
    lua_replace(L, -2);
  }
}

static void delheap (lua_State *L, heap *h) {
  if (h == NULL) return;
  lua_pushvalue(L, LUA_ENVIRONINDEX);
  lua_pushlightuserdata(L, (void *) h);
  lua_pushvalue(L, -1);
  lua_rawget(L, -3);
  lua_pushnil(L);
  lua_rawset(L, -4); /* env[h] = nil */
  lua_pushnil(L);
  lua_rawset(L, -3); /* env[light(h)] = nil */
  lua_pop(L, 1); /* env */
}

static void pushvaluekey (lua_State *L, heap *h) {
  if (h == NULL) {
    lua_pushnil(L); lua_pushnil(L); return;
  }
  lua_pushnumber(L, h->value);
  lua_pushvalue(L, LUA_ENVIRONINDEX);
  lua_pushlightuserdata(L, (void *) h);
  lua_rawget(L, -2); /* heap */
  lua_rawget(L, -2); /* key */
  lua_replace(L, -2);
}

static heap *meld (heap *h1, heap *h2) {
  heap *h3, *x;
  if (h1 == NULL) return h2;
  if (h2 == NULL) return h1;
  if (h1->up->value < h2->up->value) {
    x = h1; h1 = h2; h2 = x; /* h1 <-> h2 */
  }
  /* initialize h3 to hold the bottom right node of h1 */
  h3 = h1->up; h1->up = h3->up; h3->up = h3;
  while (h1 != h3) {
    if (h1->up->value < h2->up->value) {
      x = h1; h1 = h2; h2 = x; /* h1 <-> h2 */
    }
    /* remove from h1 its bottom right node, x */
    x = h1->up; h1->up = x->up;
    /* add x to the top of h3 and swap its children */
    x->up = x->down; x->down = h3->up; h3->up = x; h3 = h3->up;
  }
  /* attach h3 to the bottom right of h2 */
  h2->up = h3->up;
  return h2;
}


static int skew_merge (lua_State *L) {
  heap *h1 = checkheap(L, 1);
  heap *h2 = checkheap(L, 2);
  lua_settop(L, 2);
  if (h2 == NULL) { lua_pop(L, 1); return 1; } /* h1 */
  meld(h1, h2);
  return 1; /* h2 */
}

static int skew_insert (lua_State *L) {
  heap *h = checkheap(L, 1);
  lua_Number v = luaL_checknumber(L, 2);
  heap *x, *y, *z;
  lua_settop(L, 3); /* heap, value [, key] */
  /* insertion */
  x = newheap(L, v);
  if (h == NULL) { /* empty heap? */
    x->down = x; x->up = x->down;
    return 1; /* x */
  }
  if (x->value < h->value) { /* x becomes root */
    x->down = h->up; h->up = x; x->up = h->up;
    return 1; /* x */
  }
  lua_settop(L, 1); /* h is the root */
  if (x->value > h->up->value) { /* x becomes new lowest node in major path */
    x->up = h->up; h->up = x; x->down = h->up;
    return 1; /* h */
  }
  z = h->up; y = z;
  while (x->value < y->up->value) {
    heap *s;
    y = y->up;
    s = z; z = y->down; y->down = s; /* z <-> y->down */
  }
  x->up = y->up; x->down = z;
  h->up = x; y->up = h->up;
  return 1; /* h */
}

static int skew_min (lua_State *L) {
  pushvaluekey(L, checkheap(L, 1));
  return 2;
}

static int skew_retrieve (lua_State *L) { /* delete */
  heap *h = checkheap(L, 1);
  heap *h3; /* output heap */
  heap *y1, *y2; /* current nodes on the major and minor paths */
  heap *x; /* next node to be added to the output heap */
  lua_settop(L, 1);
  if (h == NULL) {
    lua_pushnil(L); lua_pushnil(L);
    return 3;
  }
  y1 = h->up; y2 = h->down;
  if (y1->value < y2->value) {
    x = y1; y1 = y2; y2 = x; /* y1 <-> y2 */
  }
  if (y1 == h) {
    pushheap(L, NULL); /* h = NULL */
    pushvaluekey(L, y1);
    delheap(L, h);
    return 3;
  }
  /* initialize h3 to hold y1 */
  h3 = y1; y1 = y1->up; h3->up = h3;
  while (1) {
    if (y1->value < y2->value) {
      x = y1; y1 = y2; y2 = x; /* y1 <-> y2 */
    }
    if (y1 == h) {
      pushheap(L, h3); /* h = h3 */
      pushvaluekey(L, y1);
      delheap(L, h);
      return 3;
    }
    /* remove x == y1 from its path */
    x = y1; y1 = y1->up;
    /* add x to the top of h3 and swap its children */
    x->up = x->down; x->down = h3->up; h3->up = x; h3 = h3->up;
  }
}


/* __tostring */
static int tostring (lua_State *L) {
  lua_pushfstring(L, "heap: %p", lua_touserdata(L, 1));
  return 1;
}

static const luaL_reg skew_func[] = {
  {"insert", skew_insert},
  {"min", skew_min},
  {"retrieve", skew_retrieve},
  {"merge", skew_merge},
  {NULL, NULL}
};

int luaopen_skew (lua_State *L) {
  lua_newtable(L); /* class */
  lua_newtable(L); /* new environment */
  lua_pushvalue(L, -1);
  lua_replace(L, LUA_ENVIRONINDEX);
  lua_pushcfunction(L, tostring);
  lua_setfield(L, -2, "__tostring");
  lua_pushvalue(L, -2);
  lua_setfield(L, -2, "__index");
  lua_pop(L, 1); /* env/metatable */
  luaL_register(L, NULL, skew_func);
  return 1; /* class */
}


/*
Copyright (c) 2008 Luis Carvalho

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation files
(the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/
