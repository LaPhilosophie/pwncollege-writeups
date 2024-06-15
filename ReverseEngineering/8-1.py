#!/usr/bin/env python3
from pwn import *
import struct

def reverse_operations(buf):

    # Steps 1 and 2 cancel each other out

    # Step 3 Reverse Swaps
    buf[6], buf[7] = buf[7], buf[6]
    buf[2], buf[30] = buf[30], buf[2]
    buf[0], buf[13] = buf[13], buf[0]

    # Step 4 Reverse XOR
    for j in range(38):
        if j % 6 == 0:
            buf[j] ^= 0x3E
        elif j % 6 == 1:
            buf[j] ^= 0xB2
        elif j % 6 == 2:
            buf[j] ^= 0x4C
        elif j % 6 == 3:
            buf[j] ^= 0xC5
        elif j % 6 == 4:
            buf[j] ^= 0xAC
        elif j % 6 == 5:
            buf[j] ^= 0x02

    # Step 5 Reverse (Same as Step 1)
    for i in range(19):
        buf[i], buf[37 - i] = buf[37 - i], buf[i]

    return buf

def main():
    # Initialize buffer with the provided data values
    buf = bytearray([
        0xC7, 0xDC, 0x5D, 0xAE, 0xD4, 0x71, 0xC3, 0x44,
        0x2A, 0xB6, 0xDE, 0x61, 0x44, 0x4F, 0x2E, 0xB3,
        0xCA, 0x71, 0x59, 0xC2, 0x2D, 0xB6, 0xDE, 0x77,
        0x54, 0xDD, 0x25, 0xB1, 0xCA, 0x6B, 0x3A, 0xC4,
        0x2F, 0xB7, 0xC0, 0x6E, 0x52, 0xDA, 0x00
    ])

    # Reverse the operations
    original_buf = reverse_operations(buf)

    # 转换为字节串
    #input_bytes = bytes(original_input)

    # 设置架构
    context.arch = 'amd64'
    # 创建一个进程对象 运行二进制文件
    p = process('/challenge/babyrev_level8.1')
    # 接收并丢弃一行输出
    p.recvline()
    # 发送数据
    p.send(original_buf)
    # 打印输出
    print(p.readallS())

if __name__ == "__main__":
    main()