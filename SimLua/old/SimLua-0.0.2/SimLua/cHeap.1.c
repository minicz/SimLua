// cHeap.c
//
// Prove 4 funcoes basicas:
//   new     - para criar um novo heap
//   push    - para incluir um dado no heap
//   pop     - para retirar o menor valor do heap
//   isEmpty - diz se o heap esta vazio ou nao
//
// O heap armazenara dois valores: o thread e um numero sequencial
//

#include <lua.h>
#include <lauxlib.h>
#include <lualib.h>
#include <stdio.h>

typedef struct heap {
    int size;
    int value[1];
} heap;

typedef struct node {
    int size;
    int value[1];
} node;

static int cHeap_push(lua_State *);
static int cHeap_pop(lua_State *);
static int cHeap_isEmpty(lua_State *);
static int cHeap_new(lua_State *);
static void set_info(lua_State *);

static const luaL_reg Funcs[] = {
    { "push", cHeap_push },
    { "pop", cHeap_pop },
    { "isEmpty", cHeap_isEmpty },
    { "new", cHeap_new },
    { NULL, NULL }
};

int luaopen_cHeap(lua_State *L) {
    luaL_register(L, "cHeap", Funcs);
    set_info(L);
    return 1;
}

static void set_info(lua_State *L) {
    lua_pushliteral(L, "_COPYRIGHT");
    lua_pushliteral(L, "Copyright (C) 2008 Marcio F. Minicz");
    lua_settable(L, -3);
    lua_pushliteral(L, "_DESCRIPTION");
    lua_pushliteral(L, "Heap Priority queue for threads");
    lua_settable(L, -3);
    lua_pushliteral(L, "_NAME");
    lua_pushliteral(L, "cHeap");
    lua_settable(L, -3);
    lua_pushliteral(L, "_VERSION");
    lua_pushliteral(L, "0.1");
    lua_settable(L, -3);
}

static int cHeap_push(lua_State *L) {
    //lua_State *t = lua_tothread(L, 1);
    //int p = lua_tonumber(L, 2);
    //printf("prioridade %i", p);
    puts("cHeap_push\n");
    return 0;
    //int t = lua_isthread(L, 1);
    //int p = lua_isnumber(L, 2);
    //int v1 = lua_tonumber(L, 1);
    //int v2 = lua_tonumber(L, 2);
    //printf("%i %i %i %i", t, p, v1, v2);
    //return 0;
}

static int cHeap_pop(lua_State *L) {
    puts("cHeap_pop\n");
    return 0;
}

static int cHeap_isEmpty(lua_State *L) {
    puts("cHeap_isEmpty\n");
    return 0;
}

static int cHeap_new(lua_State *L) {
    puts("cHeap_new\n");
    lua_newtable(L);
    lua_newtable(L);
    return 2;
    //queue *q = (queue *) lua_newuserdata(L, sizeof(queue));
    //q->head = 1;
    //q->tail = 0;
    //lua_pushvalue(L, LUA_ENVIRONINDEX);
    //lua_setmetatable(L, -2);
    //lua_newtable(L);
    //lua_setfenv(L, -2);
    //return 1;
}

