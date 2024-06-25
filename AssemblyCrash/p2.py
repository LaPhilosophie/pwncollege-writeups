#!/usr/bin/env python3
from pwn import *

# 设置架构
context.arch = 'amd64'

# 创建一个进程对象并运行二进制文件
p = process('/challenge/run')

# 接收并丢弃一行输出
p.recvline()

# 设置寄存器的值
shellcode = asm('mov rax, 0x1337')
shellcode += asm('mov r12, 0xCAFED00D1337BEEF')
shellcode += asm('mov rsp, 0x31337')

print(shellcode)

pause()

# 发送汇编指令给进程
p.send(shellcode)

# 打印进程的输出
print(p.readall())