#!/usr/bin/env python3
from pwn import *
# 设置架构
context.arch='amd64'
# 创建一个进程对象 运行二进制文件
p=process('/challenge/babyrev_level6.0')
# 接收并丢弃一行输出
p.recvline()
# 发送数据
# 初始化 buf 数组
buf = bytearray([
    0x49, 0x4B, 0x4E, 0x4F, 0x55, 0x55, 0x59, 0x5D, 0x82, 0x86,
    0x88, 0x8B, 0x8D, 0x93, 0x93, 0x93, 0x96, 0x00
])

# swap buf[12] and buf[16]
buf[12], buf[16] = buf[16], buf[12]

# 对 buf 进行指定的 XOR 操作
for k in range(17):
    if k % 2 == 1:
        buf[k] ^= 0x3C
    else:
        buf[k] ^= 0xE0
# 输出 buf
for byte in buf:
    print(chr(byte), end='')

buf_string = ''.join(chr(byte) for byte in buf)
p.send(buf_string)
# 打印输出
print(p.readall())