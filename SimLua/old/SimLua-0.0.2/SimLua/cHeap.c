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

#define QUEUE "queue"

typedef struct queue {
    int node;
    int heap;
} queue;

// funcoes internas
static queue *checkQueue(lua_State *, int index);

// funcoes externas
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

static queue *checkQueue(lua_State *L, int index){
    puts("checkQueue");
    queue* q;
    luaL_checktype(L, index, LUA_TUSERDATA);
    q = (queue *) luaL_checkudata(L, index, QUEUE);
    if(q == NULL) luaL_typerror(L, index, QUEUE);
    return q;
}

static int cHeap_push(lua_State *L) {
    puts("cHeap_push");

    queue* q = checkQueue(L, 1);
    q->heap = luaL_checkint(L, 2);
    q->node = luaL_checkint(L, 3);
    lua_settop(L, 1);
    return 1;
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
    puts("cHeap_new");

    queue* q = (queue *) lua_newuserdata(L, sizeof(queue));
    luaL_getmetatable(L, QUEUE);
    lua_setmetatable(L, -2);

    //lua_newtable(L);
    q->heap = (int *)lua_newtable(L);
    q->node = (int *)lua_newtable(L);

    return 1;
}

