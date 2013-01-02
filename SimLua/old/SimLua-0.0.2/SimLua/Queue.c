// Queue.c

#include <lua.h>
#include <lauxlib.h>
#include <lualib.h>

typedef struct stack {
    int head;
    int tail;
} queue;

static int Queue_push(lua_State *);
static int Queue_pop(lua_State *);
static int Queue_isEmpty(lua_State *);
static int Queue_new(lua_State *);
static void set_info(lua_State *);

static const luaL_reg Funcs[] = {
    { "push", q_push },
    { "pop", q_pop },
    { "isEmpty", q_isEmpty },
    { "new", q_new },
    { NULL, NULL }
};

int luaopen_Queue(lua_State *L) {
    luaL_register(L, "Queue", Funcs);
    set_info(L);
    return 1;
}

static void set_info(lua_State *L) {
    lua_pushliteral(L, "_COPYRIGHT");
    lua_pushliteral(L, "Copyright (C) 2008 Marcio F. Minicz");
    lua_settable(L, -3);
    lua_pushliteral(L, "_DESCRIPTION");
    lua_pushliteral(L, "Priority queue for threads");
    lua_settable(L, -3);
    lua_pushliteral(L, "_NAME");
    lua_pushliteral(L, "Queue");
    lua_settable(L, -3);
    lua_pushliteral(L, "_VERSION");
    lua_pushliteral(L, "0.1");
    lua_settable(L, -3);
}

static int Queue_push(lua_State *L) {
    //lua_State *t = lua_tothread(L, 1);
    //int p = lua_tonumber(L, 2);
    //printf("prioridade %i", p);
    int t = lua_isthread(L, 1);
    int p = lua_isnumber(L, 2);
    int v1 = lua_tonumber(L, 1);
    int v2 = lua_tonumber(L, 2);
    printf("%i %i %i %i", t, p, v1, v2);
    return 0;
}

static int Queue_pop(lua_State *L) {
    return 0;
}

static int Queue_isEmpty(lua_State *L) {
    return 0;
}

static int Queue_new(lua_State *L) {
    queue *q = (queue *) lua_newuserdata(L, sizeof(queue));
    q->head = 1;
    q->tail = 0;
    lua_pushvalue(L, LUA_ENVIRONINDEX);
    lua_setmetatable(L, -2);
    lua_newtable(L);
    lua_setfenv(L, -2);
    return 1;
}

//
// http://www.ime.usp.br/~yoshi//2006ii/mac122a/Slides/2006.11.07/lecture.pdf

// http://www.ime.usp.br/~pf/algoritmos/aulas/hpsrt.html
//
// void botom_up_heapsort (int n, int v[]) {
//    int m, p, f, max, t;
//    constroi_heap (n, v);
//    for (m = n; m > 1; m--) {
//       max = v[1];
//       p = 1, f = 2;
//       while (f <= m) {
//          if (f < m && v[f] < v[f+1]) ++f;
//          v[p] = v[f];
//          p = f, f = 2*p;
//       }
//       f = p;
//       if (f < m) {
//          t = v[m]; 
//          while (f > 1 && v[p=f/2] < t) { 
//             v[f] = v[p];
//             f = p;
//          }
//          v[f] = t;
//       }
//       v[m] = max;
//    }
// }
// void constroi_heap (int n, int v[]) {
//    int m, p, f, t;
//    for (m = 1; m < n; m++) {
//       f = m+1;
//       t = v[f];
//       while (f > 1 && v[p = f/2] < t) {
//          v[f] = v[p];
//          f = p;
//       }
//       v[f] = t;
//    }
// }
