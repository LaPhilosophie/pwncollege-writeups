#!/usr/bin/env python3
from pwn import *

# 设置二进制文件路径
context.binary = '/challenge/babyrev_level13.0'  # 替换为你的二进制文件路径
context.arch = 'amd64'

# 创建一个进程运行二进制文件
p = process('/challenge/babyrev_level13.0')

# 构造正确输入
correct_input = bytes([0x9D, 0x56, 0x6D, 0xAD, 0x44, 0x4D, 0x73, 0x04])

# 交互并发送输入
#p.recvuntil("Ready to receive your license key!\n")
p.recvline()
# 发送正确的输入
p.send(correct_input)

# 打印输出，应该包含 flag
print(p.readall().decode())

# 关闭进程
p.close()