#!/usr/bin/env python3

# Program is a list of operations.
# Op is a dict with the following possible fields:
# - 'type' -- the type of the Op. {OP_PUSH, OP_PLUS, OP_MINUS, ...} defined bellow
# - 'loc' -- location of the Op within a file. It's a tuple of 3 elements: `(file_path, row, col)`. `row` and `col` are 1-based indices.
# - 'value' - optional field. Exists only for OP_PUSH. Contains the value that needs to be pushed onto the stack.
# - 'jmp' -- optional field. Exists only for block Ops like `if`, `else`, `while`, etc. Contains an index of an Op within the Program that the execution has to jump to depending on the circumstantces. In case of `if` it's the place of else branch, in case of `else` it's the end of the construction, etc. The field is created during crossreference_blocks() step.

import os
import sys
import subprocess
import shlex
from os import path

debug=False

subscript_counter=0

def subscript(reset=False) -> int:
    global subscript_counter
    if reset:
        subscript_counter = 0
    result = subscript_counter
    subscript_counter += 1
    return result

OP_PUSH=subscript(True)
OP_PLUS=subscript()
OP_MINUS=subscript()
OP_MOD=subscript()
OP_EQ=subscript()
OP_GT=subscript()
OP_LT=subscript()
OP_GE=subscript()
OP_LE=subscript()
OP_NE=subscript()
OP_RSH=subscript()
OP_LSH=subscript()
OP_BOR=subscript()
OP_BAND=subscript()
OP_DUMP=subscript()
OP_IF=subscript()
OP_END=subscript()
OP_ELSE=subscript()
OP_DUPL=subscript()
OP_2DUPL=subscript()
OP_SWAP=subscript()
OP_DROP=subscript()
OP_OVER=subscript()
OP_WHILE=subscript()
OP_DO=subscript()
OP_MEM=subscript()
OP_LOAD=subscript()
OP_STORE=subscript()
OP_SYSCALL0=subscript()
OP_SYSCALL1=subscript()
OP_SYSCALL2=subscript()
OP_SYSCALL3=subscript()
OP_SYSCALL4=subscript()
OP_SYSCALL5=subscript()
OP_SYSCALL6=subscript()
COUNT_OPS=subscript()

MEM_CAPACITY = 640_000

def simulate_program(program):
    stack = []
    mem = bytearray(MEM_CAPACITY)
    ip = 0
    while ip < len(program):
        assert COUNT_OPS == 35, "Exhaustive handling of operations in simulation"
        op = program[ip]
        if op['type'] == OP_PUSH:
            stack.append(op['value'])
            ip += 1
        elif op['type'] == OP_PLUS:
            a = stack.pop()
            b = stack.pop()
            stack.append(a + b)
            ip += 1
        elif op['type'] == OP_MINUS:
            a = stack.pop()
            b = stack.pop()
            stack.append(b - a)
            ip += 1
        elif op['type'] == OP_MOD:
            a = stack.pop()
            b = stack.pop()
            stack.append(b % a)
            ip += 1
        elif op['type'] == OP_EQ:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(a == b))
            ip += 1
        elif op['type'] == OP_GT:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(a < b))
            ip += 1
        elif op['type'] == OP_LT:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(a > b))
            ip += 1
        elif op['type'] == OP_GE:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(b >= a))
            ip += 1
        elif op['type'] == OP_LE:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(b <= a))
            ip += 1
        elif op['type'] == OP_NE:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(b != a))
            ip += 1
        elif op['type'] == OP_RSH:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(b >> a))
            ip += 1
        elif op['type'] == OP_LSH:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(b << a))
            ip += 1
        elif op['type'] == OP_BOR:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(a | b))
            ip += 1
        elif op['type'] == OP_BAND:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(a & b))
            ip += 1
        elif op['type'] == OP_IF:
            a = stack.pop()
            if a == 0:
                assert 'jmp' in op, "'if' instruction does not have a reference to the end of its block. Please call crossreference_blocks() on the program before trying to simulate it"
                ip = op['jmp']
            else:
                ip += 1
        elif op['type'] == OP_ELSE:
            assert 'jmp' in op, "'else' instruction does not have a reference to the end of its block. Please call crossreference_blocks() on the program before trying to simulate it"
            ip = op['jmp']
        elif op['type'] == OP_END:
            assert 'jmp' in op, "'end' instruction does not have a reference to the next instruction to jump to. Please call crossreference_blocks() on the program before trying to simulate it"
            ip = op['jmp']
        elif op['type'] == OP_DUMP:
            a = stack.pop()
            print(a)
            ip += 1
        elif op['type'] == OP_DUPL:
            a = stack.pop()
            stack.append(a)
            stack.append(a)
            ip += 1
        elif op['type'] == OP_2DUPL:
            b = stack.pop()
            a = stack.pop()
            stack.append(a)
            stack.append(b)
            stack.append(a)
            stack.append(b)
            ip += 1
        elif op['type'] == OP_SWAP:
            a = stack.pop()
            b = stack.pop()
            stack.append(a)
            stack.append(b)
            ip += 1
        elif op['type'] == OP_DROP:
            stack.pop()
            ip += 1
        elif op['type'] == OP_OVER:
            a = stack.pop()
            b = stack.pop()
            stack.append(b)
            stack.append(a)
            stack.append(b)
            ip += 1
        elif op['type'] == OP_WHILE:
            ip += 1
        elif op['type'] == OP_DO:
            a = stack.pop()
            if a == 0:
                assert 'jmp' in op, "'end' instruction does not have a reference to the next instruction to jump to. Please call crossreference_blocks() on the program before trying to simulate it"
                ip = op['jmp']
            else:
                ip += 1
        elif op['type'] == OP_MEM:
            stack.append(0)
            ip += 1
        elif op['type'] == OP_LOAD:
            addr = stack.pop()
            byte = mem[addr]
            stack.append(byte)
            ip += 1
        elif op['type'] == OP_STORE:
            value = stack.pop()
            addr = stack.pop()
            mem[addr] = value & 0xFF
            ip += 1
        elif op['type'] == OP_SYSCALL0:
            syscall_number = stack.pop()
            if syscall_number == 39:
                stack.append(os.getpid())
            else:
                assert False, "unknown syscall number %d" % syscall_number
            ip += 1
        elif op['type'] == OP_SYSCALL1:
            assert False, "not implemented"
        elif op['type'] == OP_SYSCALL2:
            assert False, "not implemented"
        elif op['type'] == OP_SYSCALL3:
            syscall_number = stack.pop()
            arg1 = stack.pop()
            arg2 = stack.pop()
            arg3 = stack.pop()
            if syscall_number == 1:
                fd = arg1
                buf = arg2
                count = arg3
                s = mem[buf:buf+count].decode('utf-8')
                if fd == 1:
                    print(s, end='')
                elif fd == 2:
                    print(s, end='', file=sys.stderr)
                else:
                    assert False, "unknown file descriptor %d" % fd
                stack.append(count)
            else:
                assert False, "unknown syscall number %d" % syscall_number
            ip += 1
        elif op['type'] == OP_SYSCALL4:
            assert False, "not implemented"
        elif op['type'] == OP_SYSCALL5:
            assert False, "not implemented"
        elif op['type'] == OP_SYSCALL6:
            assert False, "not implemented"
        else:
            assert False, "unreachable"
    if debug:
        print("[INFO] Memory dump")
        print(mem[:20])

def compile_program(program, out_file_path):
    with open(out_file_path, "w") as out:
        out.write("BITS 64\n")
        out.write("segment .text\n")
        out.write("dump:\n")
        out.write("    mov     r9, -3689348814741910323\n")
        out.write("    sub     rsp, 40\n")
        out.write("    mov     BYTE [rsp+31], 10\n")
        out.write("    lea     rcx, [rsp+30]\n")
        out.write(".L2:\n")
        out.write("    mov     rax, rdi\n")
        out.write("    lea     r8, [rsp+32]\n")
        out.write("    mul     r9\n")
        out.write("    mov     rax, rdi\n")
        out.write("    sub     r8, rcx\n")
        out.write("    shr     rdx, 3\n")
        out.write("    lea     rsi, [rdx+rdx*4]\n")
        out.write("    add     rsi, rsi\n")
        out.write("    sub     rax, rsi\n")
        out.write("    add     eax, 48\n")
        out.write("    mov     BYTE [rcx], al\n")
        out.write("    mov     rax, rdi\n")
        out.write("    mov     rdi, rdx\n")
        out.write("    mov     rdx, rcx\n")
        out.write("    sub     rcx, 1\n")
        out.write("    cmp     rax, 9\n")
        out.write("    ja      .L2\n")
        out.write("    lea     rax, [rsp+32]\n")
        out.write("    mov     edi, 1\n")
        out.write("    sub     rdx, rax\n")
        out.write("    xor     eax, eax\n")
        out.write("    lea     rsi, [rsp+32+rdx]\n")
        out.write("    mov     rdx, r8\n")
        out.write("    mov     rax, 1\n")
        out.write("    syscall\n")
        out.write("    add     rsp, 40\n")
        out.write("    ret\n")
        out.write("global _start\n")
        out.write("_start:\n")
        for ip in range(len(program)):
            op = program[ip]
            assert COUNT_OPS == 35, "Exhaustive handling of operations in compilation!"
            out.write("addr_%d:\n" % ip)
            if op['type'] == OP_PUSH:
                out.write("    ;; -- push %d --\n" % op['value'])
                out.write("    mov rax, %d\n" % op['value'])
                out.write("    push rax\n")
            elif op['type'] == OP_PLUS:
                out.write("    ;; -- plus --\n")
                out.write("    pop rax\n")
                out.write("    pop rbx\n")
                out.write("    add rax, rbx\n")
                out.write("    push rax\n")
            elif op['type'] == OP_MINUS:
                out.write("    ;; -- minus --\n")
                out.write("    pop rax\n")
                out.write("    pop rbx\n")
                out.write("    sub rbx, rax\n")
                out.write("    push rbx\n")
            elif op['type'] == OP_DUMP:
                out.write("    ;; -- dump --\n")
                out.write("    pop rdi\n")
                out.write("    call dump\n")
            elif op['type'] == OP_EQ:
                out.write("    ;; -- equal --\n")
                out.write("    mov rcx, 0\n")
                out.write("    mov rdx, 1\n")
                out.write("    pop rax\n")
                out.write("    pop rbx\n")
                out.write("    cmp rax, rbx\n")
                out.write("    cmove rcx, rdx\n")
                out.write("    push rcx\n")
            elif op['type'] == OP_GT:
                out.write("    ;; -- gt --\n")
                out.write("    mov rcx, 0\n")
                out.write("    mov rdx, 1\n")
                out.write("    pop rbx\n")
                out.write("    pop rax\n")
                out.write("    cmp rax, rbx\n")
                out.write("    cmovg rcx, rdx\n")
                out.write("    push rcx\n")
            elif op['type'] == OP_LT:
                out.write("    ;; -- lt --\n")
                out.write("    mov rcx, 0\n")
                out.write("    mov rdx, 1\n")
                out.write("    pop rbx\n")
                out.write("    pop rax\n")
                out.write("    cmp rax, rbx\n")
                out.write("    cmovl rcx, rdx\n")
                out.write("    push rcx\n")
            elif op['type'] == OP_GE:
                out.write("    ;; -- gt --\n")
                out.write("    mov rcx, 0\n");
                out.write("    mov rdx, 1\n");
                out.write("    pop rbx\n");
                out.write("    pop rax\n");
                out.write("    cmp rax, rbx\n");
                out.write("    cmovge rcx, rdx\n");
                out.write("    push rcx\n")
            elif op['type'] == OP_LE:
                out.write("    ;; -- gt --\n")
                out.write("    mov rcx, 0\n");
                out.write("    mov rdx, 1\n");
                out.write("    pop rbx\n");
                out.write("    pop rax\n");
                out.write("    cmp rax, rbx\n");
                out.write("    cmovle rcx, rdx\n");
                out.write("    push rcx\n")
            elif op['type'] == OP_MOD:
                out.write("    ;; -- mod --\n")
                out.write("    xor rdx, rdx\n")
                out.write("    pop rbx\n")
                out.write("    pop rax\n")
                out.write("    div rbx\n")
                out.write("    push rdx\n")
            elif op['type'] == OP_NE:
                out.write("    ;; -- ne --\n")
                out.write("    mov rcx, 0\n")
                out.write("    mov rdx, 1\n")
                out.write("    pop rbx\n")
                out.write("    pop rax\n")
                out.write("    cmp rax, rbx\n")
                out.write("    cmovne rcx, rdx\n")
                out.write("    push rcx\n")
            elif op['type'] == OP_RSH:
                out.write("    ;; -- rsh --\n")
                out.write("    pop rcx\n")
                out.write("    pop rbx\n")
                out.write("    shr rbx, cl\n")
                out.write("    push rbx\n")
            elif op['type'] == OP_LSH:
                out.write("    ;; -- lsh --\n")
                out.write("    pop rcx\n")
                out.write("    pop rbx\n")
                out.write("    shl rbx, cl\n")
                out.write("    push rbx\n")
            elif op['type'] == OP_BOR:
                out.write("    ;; -- bor --\n")
                out.write("    pop rax\n")
                out.write("    pop rbx\n")
                out.write("    or rbx, rax\n")
                out.write("    push rbx\n")
            elif op['type'] == OP_BAND:
                out.write("    ;; -- band --\n")
                out.write("    pop rax\n")
                out.write("    pop rbx\n")
                out.write("    and rbx, rax\n")
                out.write("    push rbx\n")
            elif op['type'] == OP_IF:
                out.write("    ;; -- if --\n")
                out.write("    pop rax\n")
                out.write("    test rax, rax\n")
                assert 'jmp', "'if' instruction does not have a reference to the end of its block. Please call crossreference_blocks() on the program before trying to compile it"
                out.write("    jz addr_%d\n" % op['jmp'])
            elif op['type'] == OP_ELSE:
                out.write("    ;; -- else --\n")
                assert 'jmp' in op, "'else' instruction does not have a reference to the end of its block. Please call crossreference_blocks() on the program before trying to compile it"
                out.write("    jmp addr_%d\n\n" % op['jmp'])
            elif op['type'] == OP_END:
                assert 'jmp' in op, "'end' instruction does not have a reference to the next instruction to jump to. Please call crossreference_blocks() on the program before trying to compile it"
                out.write("    ;; -- end --\n")
                if ip + 1 != op['jmp']:
                    out.write("    jmp addr_%d\n" % op['jmp'])
            elif op['type'] == OP_DUPL:
                out.write("    ;; -- dupl --\n")
                out.write("    pop rax\n")
                out.write("    push rax\n")
                out.write("    push rax\n")
            elif op['type'] == OP_2DUPL:
                out.write("    ;; -- 2dupl -- \n")
                out.write("    pop rbx\n")
                out.write("    pop rax\n")
                out.write("    push rax\n")
                out.write("    push rbx\n")
                out.write("    push rax\n")
                out.write("    push rbx\n")
            elif op['type'] == OP_SWAP:
                out.write("    ;; -- swap --\n")
                out.write("    pop rax\n")
                out.write("    pop rbx\n")
                out.write("    push rax\n")
                out.write("    push rbx\n")
            elif op['type'] == OP_DROP:
                out.write("    ;; -- drop --\n")
                out.write("    pop rax\n")
            elif op['type'] == OP_OVER:
                out.write("    ;; -- over --\n")
                out.write("    pop rax\n")
                out.write("    pop rbx\n")
                out.write("    push rbx\n")
                out.write("    push rax\n")
                out.write("    push rbx\n")
            elif op['type'] == OP_WHILE:
                out.write("    ;; -- while --\n")
            elif op['type'] == OP_DO:
                out.write("    ;; -- do --\n")
                out.write("    pop rax\n")
                out.write("    test rax, rax\n")
                assert 'jmp' in op, "'do' instruction does not have a reference to the end of its block. Please call crossreference_blocks() on the program before trying to compile it"
                out.write("    jz addr_%d\n" % op['jmp'])
            elif op['type'] == OP_MEM:
                out.write("    ;; -- mem --\n")
                out.write("    push mem\n")
            elif op['type'] == OP_LOAD:
                out.write("    ;; -- load --\n")
                out.write("    pop rax\n")
                out.write("    xor rbx, rbx\n")
                out.write("    mov bl, [rax]\n")
                out.write("    push rbx\n")
            elif op['type'] == OP_STORE:
                out.write("    ;; -- store --\n")
                out.write("    pop rbx\n")
                out.write("    pop rax\n")
                out.write("    mov [rax], bl\n")
            elif op['type'] == OP_SYSCALL0:
                out.write("    ;; -- syscall0 --\n")
                out.write("    pop rax\n")
                out.write("    syscall\n")
                out.write("    push rax\n")
            elif op['type'] == OP_SYSCALL1:
                out.write("    ;; -- syscall1 --\n")
                out.write("    pop rax\n")
                out.write("    pop rdi\n")
                out.write("    syscall\n")
                out.write("    push rax\n")
            elif op['type'] == OP_SYSCALL2:
                out.write("    ;; -- syscall2 -- \n")
                out.write("    pop rax\n")
                out.write("    pop rdi\n")
                out.write("    pop rsi\n")
                out.write("    syscall\n")
                out.write("    push rax\n")
            elif op['type'] == OP_SYSCALL3:
                out.write("    ;; -- syscall3 --\n")
                out.write("    pop rax\n")
                out.write("    pop rdi\n")
                out.write("    pop rsi\n")
                out.write("    pop rdx\n")
                out.write("    syscall\n")
                out.write("    push rax\n")
            elif op['type'] == OP_SYSCALL4:
                out.write("    ;; -- syscall4 --\n")
                out.write("    pop rax\n")
                out.write("    pop rdi\n")
                out.write("    pop rsi\n")
                out.write("    pop rdx\n")
                out.write("    pop r10\n")
                out.write("    syscall\n")
                out.write("    push rax\n")
            elif op['type'] == OP_SYSCALL5:
                out.write("    ;; -- syscall5 --\n")
                out.write("    pop rax\n")
                out.write("    pop rdi\n")
                out.write("    pop rsi\n")
                out.write("    pop rdx\n")
                out.write("    pop r10\n")
                out.write("    pop r8\n")
                out.write("    syscall\n")
                out.write("    push rax\n")
            elif op['type'] == OP_SYSCALL6:
                out.write("    ;; -- syscall6 --\n")
                out.write("    pop rax\n")
                out.write("    pop rdi\n")
                out.write("    pop rsi\n")
                out.write("    pop rdx\n")
                out.write("    pop r10\n")
                out.write("    pop r8\n")
                out.write("    pop r9\n")
                out.write("    syscall\n")
                out.write("    push rax\n")
            else:
                assert False, "unreachable"

        out.write("addr_%d:\n" % len(program))
        out.write("    mov rax, 60\n")
        out.write("    mov rdi, 0\n")
        out.write("    syscall\n")
        out.write("segment .bss\n")
        out.write("mem: resb %d\n" % MEM_CAPACITY)

def parse_token_as_op(token):
    (file_path, row, col, word) = token
    loc = (file_path, row + 1, col + 1)
    assert COUNT_OPS == 35, "Exhaustive op handling in parse_token_as_op"
    if word == '+':
        return {'type': OP_PLUS, 'loc': loc}
    elif word == '-':
        return {'type': OP_MINUS, 'loc': loc} 
    elif word == 'mod':
        return {'type': OP_MOD, 'loc': loc}
    elif word == '=>':
        return {'type': OP_DUMP, 'loc': loc}
    elif word == '=':
        return {'type': OP_EQ, 'loc': loc}
    elif word == '>':
        return {'type': OP_GT, 'loc': loc}
    elif word == '<':
        return {'type': OP_LT, 'loc': loc}
    elif word == '>=':
        return {'type': OP_GE, 'loc': loc}
    elif word == '<=':
        return {'type': OP_LE, 'loc': loc}
    elif word == '!=':
        return {'type': OP_NE, 'loc': loc}
    elif word == '>>':
        return {'type': OP_RSH, 'loc': loc}
    elif word == '<<':
        return {'type': OP_LSH, 'loc': loc}
    elif word == '|':
        return {'type': OP_BOR, 'loc': loc}
    elif word == '&':
        return {'type': OP_BAND, 'loc': loc}
    elif word == 'if':
        return {'type': OP_IF, 'loc': loc}
    elif word == 'end':
        return {'type': OP_END, 'loc': loc}
    elif word == 'else':
        return {'type': OP_ELSE, 'loc': loc}
    elif word == 'cp':
        return {'type': OP_DUPL, 'loc': loc}
    elif word == 'pcp':
        return {'type': OP_2DUPL, 'loc': loc}
    elif word == '~':
        return {'type': OP_SWAP, 'loc': loc}
    elif word == '#':
        return {'type': OP_DROP, 'loc': loc}
    elif word == 'over':
        return {'type': OP_OVER, 'loc': loc}
    elif word == 'while':
        return {'type': OP_WHILE, 'loc': loc}
    elif word == 'do':
        return {'type': OP_DO, 'loc': loc}
    elif word == 'mem':
        return {'type': OP_MEM, 'loc': loc}
    elif word == '&s':
        return {'type': OP_STORE, 'loc': loc}
    elif word == '&l':
        return {'type': OP_LOAD, 'loc': loc}
    elif word == 'syscall0':
        return {'type': OP_SYSCALL0, 'loc': loc}
    elif word == 'syscall1':
        return {'type': OP_SYSCALL1, 'loc': loc}
    elif word == 'syscall2':
        return {'type': OP_SYSCALL2, 'loc': loc}
    elif word == 'syscall3':
        return {'type': OP_SYSCALL3, 'loc': loc}
    elif word == 'syscall4':
        return {'type': OP_SYSCALL4, 'loc': loc}
    elif word == 'syscall5':
        return {'type': OP_SYSCALL5, 'loc': loc}
    elif word == 'syscall6':
        return {'type': OP_SYSCALL6, 'loc': loc}
    else:
        try:
            return {'type': OP_PUSH, 'value': int(word), 'loc': loc}
        except ValueError as err:
            print("%s:%d:%d: unknown word `%s`" % (loc + (word, )))
            exit(1)

def crossreference_blocks(program):
    stack = []
    for ip in range(len(program)):
        op = program[ip]
        assert COUNT_OPS == 35, "Exhaustive handling of ops in crossreference_program. Keep in mind that not all of the ops need to be handled in here. Only those that form blocks."
        if op['type'] == OP_IF:
            stack.append(ip)
        elif op['type'] == OP_ELSE:
            if_ip = stack.pop()
            if program[if_ip]['type'] != OP_IF:
                print(f"{program[if_ip]['loc']}: [ERROR] 'else' can only be used in 'if'-blocks")
                exit(1)
            program[if_ip]['jmp'] = ip + 1
            stack.append(ip)
        elif op['type'] == OP_END:
            block_ip = stack.pop()
            if program[block_ip]['type'] == OP_IF or program[block_ip]['type'] == OP_ELSE:
                program[block_ip]['jmp'] = ip
                program[ip]['jmp'] = ip + 1
            elif program[block_ip]['type'] == OP_DO:
                assert len(program[block_ip]) >= 2
                program[ip]['jmp'] = program[block_ip]['jmp']
                program[block_ip]['jmp'] = ip + 1
            else:
                print(f"{program[block_ip]['loc']}: [ERROR] 'end' can only close 'if', 'else' or 'do' blocks for now")
                exit(1)
        elif op['type'] == OP_WHILE:
            stack.append(ip)
        elif op['type'] == OP_DO:
            while_ip = stack.pop()
            program[ip]['jmp'] = while_ip
            stack.append(ip)

    if len(stack) > 0:
        print(f"{program[stack.pop()]['loc']}: [ERROR] unclosed block")
        exit(1)

    return program

def find_col(line, start, predicate) -> int:
    while start < len(line) and not predicate(line[start]):
        start += 1
    return start

def lex_line(line):
    col = find_col(line, 0, lambda k: not k.isspace())
    while col < len(line):
        col_end = find_col(line, col, lambda k: k.isspace())
        yield (col, line[col:col_end])
        col = find_col(line, col_end, lambda k: not k.isspace())

def lex_file(file_path):
    with open(file_path, "r") as f:
        return [(file_path, row, col, token)
                for (row, line) in enumerate(f.readlines())
                for (col, token) in lex_line(line.split("--")[0])]

def load_program_from_file(file_path):
    return crossreference_blocks([parse_token_as_op(token) for token in lex_file(file_path)])

def cmd_call_echoed(cmd):
    print("[CMD] %s" % " ".join(map(shlex.quote, cmd)))
    return subprocess.call(cmd)

def usage(compiler_name):
    print(f"Usage: {compiler_name} [OPTIONS] <SUBCOMMAND> [ARGS]\n")
    print("OPTIONS")
    print("     -dbg                     Enable debug mode\n")
    print("SUBCOMMANDS")
    print("     -s           <file>      Simulate the program")
    print("     -c [OPTIONS] <file>      Compile the program")
    print("     -h                       Print help to STDOUT and exit 0\n")
    print("OPTIONS")
    print("     -r                       Run the program after successful compilation")
    print("     -o         <file|dir>    Customize the output path")
    
if __name__ == "__main__" and "__file__" in globals():
    argv = sys.argv
    assert len(argv) >= 1
    compiler_name, *argv = argv

    while len(argv) > 0:
        if argv[0] == '-dbg':
            debug = True
            argv = argv[1:]
        else:
            break

    if debug:
        print("[INFO] Debug mode is enabled")

    if len(argv) < 1:
        usage(compiler_name)
        print("[ERROR] No subcommand is provided")
        exit(1)
    subcommand, *argv = argv

    if subcommand in ["simulate","-s"]:
        if len(argv) < 1:
            usage(compiler_name)
            print("[ERROR] No input file is provided")
            exit(1)
        program_path, *argv = argv
        program = load_program_from_file(program_path)
        simulate_program(program)
    elif subcommand in ["compile","-c"]:
        run = False
        program_path = None
        output_path = None
        while len(argv) > 0:
            arg, *argv = argv
            if arg == "-r":
                run = True
            elif arg == "-o":
                if len(argv) == 0:
                    usage(compiler_name)
                    print("[ERROR] No argument is provided for parameter -o")
                    exit(1)
                output_path, *argv = argv
            else:
                program_path = arg
                break
        if program_path is None:
            usage(compiler_name)
            print("[ERROR] No input file is provided")
            exit(1)
            
        basename = None
        basedir = None
        if output_path is not None:
            if path.isdir(output_path):
                basename = path.basename(program_path)
                musc_ext = '.musc'
                if basename.endswith(musc_ext):
                    basename = basename[:-len(musc_ext)]
                basedir = path.dirname(output_path)
            else:
                basename = path.basename(output_path)
                basedir = path.dirname(output_path)
        else:
            basename = path.basename(program_path)
            musc_ext = '.musc'
            if basename.endswith(musc_ext):
                basename = basename[:-len(musc_ext)]
            basedir = path.dirname(program_path)
        basepath = path.join(basedir, basename)

        print(f"[INFO] Generating {basename}.asm")
        program = load_program_from_file(program_path)
        compile_program(program, basepath + ".asm")
        cmd_call_echoed(["nasm", "-felf64", basepath + ".asm"])
        cmd_call_echoed(["ld", "-o", basepath, basepath + ".o"])
        if run:
            exit(cmd_call_echoed([basepath] + argv))
    elif subcommand in ["help","-h"]:
        usage(compiler_name)
        exit(0)
    else:
        usage(compiler_name)
        print(f"[ERROR] Unkown subcommand '{subcommand}'")
        exit(1)
