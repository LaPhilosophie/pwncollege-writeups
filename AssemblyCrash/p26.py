from pwn import *

# 设置架构
context.arch = 'amd64'
# 创建一个进程对象并运行二进制文件
p = process('/challenge/run')


# 接收并丢弃一行输出
p.recvline()

shellcode = asm('''
    cmp rdi, 4        
    jge default_case                               
    lea rax, [rsi + rdi*8] 
    jmp [rax]    
default_case:
    mov rax,rsi
    add rax,0x20
    jmp [rax]
''')

# 发送汇编指令给进程
p.send(shellcode)

# 打印进程的输出
print(p.readallS())
