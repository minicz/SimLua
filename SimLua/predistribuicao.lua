#!/usr/bin/env lua

function uso()
    -- analisa para saber se algum parametro foi passado
    -- se não, é informado a forma de uso
    io.write(string.format("Uso: lua %s [opção] [nome_arq]\n", arg[0]))
    io.write(string.format("\tOpções:\n"))
    io.write(string.format("\t-p\tComenta código em Python\n"))
    io.write(string.format("\t-l\tRemove linha comentadas por -p\n"))
    io.write(string.format("\t-a\tArquiva a versão atual --> nil|M|m\n"))
    os.exit(1)   -- sai indicando erro 1
end

function arq()
    -- Testa se arg[2] é uma string
    if not(type(arg[2]) == "string") then uso() end
end

function comenta()
    arq()
    io.write("Comentando arquivo...")

    assert(io.input(arg[2], "r"))
    f2 = string.gsub(arg[2], ".py", ".lua")
    assert(io.output(f2, "w"))

    while true do
        local line = io.read()
        if line == nil then break end
        io.write("---->", line, "\n")
    end

    print("ok")
    os.exit(0)
end

function limpa()
    arq()
    io.write("Limpando arquivo...")
    assert(io.input(arg[2], "r"))
    assert(io.output("dist/" ..arg[2], "w"))

    while true do
        local line = io.read()
        if line == nil then break end
        if not(string.sub(line, 1, 5) == "---->") then
            io.write(line, "\n")
        end
    end

    print("ok")
    os.exit(0)
end

function arquiva(r)
    local f = assert(io.open("./old/version", "r"))
    local v = f:read("*all")
    f:close()
    _, _, v_M, v_m, v_s = string.find(v, "(%d+)%.(%d+)%.(%d+)")
    if r == nil then v_s = v_s + 1
    elseif r == "M" then v_M = v_M + 1
    elseif r == "m" then v_m = v_m + 1
    else uso() end
    v = string.format("%d.%d.%d", v_M, v_m, v_s)
    io.write(string.format("Arquivando versão %s...\n", v))
    os.execute(string.format("mkdir old/SimLua-%s", v))
    io.write(string.format("SimLua...\n"))
    os.execute(string.format("cp -p -r SimLua old/SimLua-%s/SimLua", v))
    io.write(string.format("SimLuaDoc...\n"))
    os.execute(string.format("cp -p -r SimLuaDoc old/SimLua-%s/SimLuaDoc", v))
    io.write(string.format("SimLuaModels...\n"))
    os.execute(string.format("cp -p -r SimLuaModels old/SimLua-%s/SimLuaModels", v))
    local f = assert(io.open("./old/version", "w+"))
    f:write(v)
    f:close()
    io.write("Arquivado.")
end


if arg[1] == "-p" then comenta()
elseif arg[1] == "-l" then limpa()
elseif arg[1] == "-a" then arquiva(arg[2])
else uso() end
