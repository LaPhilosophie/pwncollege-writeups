from pwn import *

# 设置架构
context.arch = 'amd64'

# 创建一个进程对象并运行二进制文件
p = process('/challenge/run')

# 接收并丢弃一行输出
p.recvline()

shellcode = asm('''
    mov rax,[0x404000]
    mov rdi,[0x404000]
    mov rdi,0x1337
    add [0x404000],rdi
''')

# 发送汇编指令给进程
p.send(shellcode)

# 打印进程的输出
print(p.readallS())