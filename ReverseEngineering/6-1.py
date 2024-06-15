#!/usr/bin/env python3
from pwn import *
# 设置架构
context.arch='amd64'
# 创建一个进程对象 运行二进制文件
p=process('/challenge/babyrev_level6.1')
# 接收并丢弃一行输出
p.recvline()


# 初始化 buf 数组
buf = bytearray([
    0x81, 0x89, 0x91, 0x93, 0x94, 0x95, 0x9A, 0x9F,
    0xE5, 0xED, 0xEE, 0xF2, 0xF6, 0xF8, 0xFC, 0xFE,
    0xFF, 0x00
])

# 第一步：交换前 8 个元素和后 8 个元素
for i in range(8):
    v4 = buf[i]
    buf[i] = buf[16 - i]
    buf[16 - i] = v4

print("After swapping:", [hex(x) for x in buf])

# 第二步：对每个元素进行 XOR 操作
for j in range(17):
    if j % 2 == 1:
        buf[j] ^= 0xF8
    else:
        buf[j] ^= 0x9D

buf_string = ''.join(chr(byte) for byte in buf)
p.send(buf_string)
# 打印输出
print(p.readall())