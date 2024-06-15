#!/usr/bin/env python3
from pwn import *
import struct

def reverse_mangle_input(buf):
    # 第1步：逆向反转操作
    for i2 in range(18):
        buf[i2], buf[36 - i2] = buf[36 - i2], buf[i2]

    # 第2步：逆向交换操作，针对索引 5 和 28
    buf[5], buf[28] = buf[28], buf[5]

    # 第3步：逆向 XOR 操作
    for mm in range(37):
        if mm % 6 == 0:
            buf[mm] ^= 0x46
        elif mm % 6 == 1:
            buf[mm] ^= 0xAD
        elif mm % 6 == 2:
            buf[mm] ^= 0xDA
        elif mm % 6 == 3:
            buf[mm] ^= 0xFD
        elif mm % 6 == 4:
            buf[mm] ^= 0x2B
        elif mm % 6 == 5:
            buf[mm] ^= 0x3B

    # 第4步：逆向交换操作，针对索引 15 和 36
    buf[15], buf[36] = buf[36], buf[15]

    # 第5步：逆向交换操作，针对索引 6 和 10
    buf[6], buf[10] = buf[10], buf[6]

    # 第6步：逆向反转操作
    for j in range(18):
        buf[j], buf[36 - j] = buf[36 - j], buf[j]

    return buf


def find_initial_input(expected_result):
    # 期望结果
    buf = bytearray(expected_result)

    # 反向操作得到初始输入
    original_buf = reverse_mangle_input(buf)

    return original_buf


def main():
    # 期望结果
    expected_result = bytearray([
        0x3C, 0x43, 0x53, 0x8B, 0xAC, 0xD8, 0x32, 0x4F,
        0x59, 0x8F, 0xAB, 0xDD, 0x2B, 0x56, 0x40, 0x96,
        0xB1, 0xC7, 0x2C, 0x52, 0x43, 0x95, 0xB2, 0xCA,
        0x21, 0x5D, 0x4E, 0x99, 0xB9, 0xCE, 0x25, 0x5F,
        0x49, 0x9C, 0xBB, 0xCC, 0x27, 0x00
    ])

    # 得到初始输入
    original_input = find_initial_input(expected_result)

    # 转换为字节串
    input_bytes = bytes(original_input)

    # 设置架构
    context.arch = 'amd64'
    # 创建一个进程对象 运行二进制文件
    p = process('/challenge/babyrev_level8.0')
    # 接收并丢弃一行输出
    p.recvline()
    # 发送数据
    p.send(input_bytes)
    # 打印输出
    print(p.readallS())


if __name__ == "__main__":
    main()