from pwn import *

# 设置架构
context.arch = 'amd64'

# 创建一个进程对象并运行二进制文件
p = process('/challenge/run')

# 接收并丢弃一行输出
p.recvline()

shellcode = asm('''
    mov eax,[rdi]
    cmp eax, 0x7f454c46
    je elf_format       
    cmp eax, 0x00005A4D
    je dos_format       
    jmp other_format    
elf_format:
    mov eax, [rdi + 4]  
    add eax, [rdi + 8]  
    add eax, [rdi + 12] 
    jmp end             

dos_format:
    mov eax, [rdi + 4]  
    sub eax, [rdi + 8]  
    sub eax, [rdi + 12] 
    jmp end             

other_format:
    mov eax, [rdi + 4]  
    imul eax, [rdi + 8] 
    imul eax, [rdi + 12]
end:
    nop
''')

    


# 发送汇编指令给进程
p.send(shellcode)

# 打印进程的输出
print(p.readallS())