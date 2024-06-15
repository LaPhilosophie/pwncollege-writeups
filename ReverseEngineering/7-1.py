#!/usr/bin/env python3
from pwn import *
import struct

def reverse_mangle_input(buf):
    # 第1步：逆向交换操作，针对索引 4 和 22
    buf[4], buf[22] = buf[22], buf[4]

    # 第2步：逆向交换操作，针对索引 15 和 24
    buf[15], buf[24] = buf[24], buf[15]

    # 第3步：逆向反转操作
    for k in range(14):
        buf[k], buf[28 - k] = buf[28 - k], buf[k]

    # 第4步：逆向异或操作
    for j in range(29):
        if j % 5 == 0:
            buf[j] ^= 0xB4
        elif j % 5 == 1:
            buf[j] ^= 0xEC
        elif j % 5 == 2:
            buf[j] ^= 0x96
        elif j % 5 == 3:
            buf[j] ^= 0x33
        elif j % 5 == 4:
            buf[j] ^= 0x0A
    
    # 第5步：逆向反转操作
    for i in range(14):
        buf[i], buf[28 - i] = buf[28 - i], buf[i]
    
    return buf

def find_initial_input(expected_result):
    # 期望结果
    buf = bytearray(expected_result)
    
    # 反向操作得到初始输入
    original_buf = reverse_mangle_input(buf)

    return original_buf

def main():
    # 期望结果（输入结果）
    expected_result = bytearray([
        0x40, 0xF3, 0x82, 0xD6, 0x9B, 0x57, 0xE2, 0x98,
        0xDF, 0x6F, 0x5B, 0xF3, 0x9C, 0xD6, 0x7E, 0x68,
        0xFF, 0x94, 0xD0, 0x68, 0x52, 0xFD, 0x63, 0xC5,
        0x52, 0x4A, 0xE6, 0x9B, 0xC3, 0x00
    ])

    # 得到初始输入
    original_input = find_initial_input(expected_result)

    # 转换为字节串
    input_bytes = bytes(original_input)

    # 设置架构
    context.arch = 'amd64'
    # 创建一个进程对象 运行二进制文件
    p = process('/challenge/babyrev_level7.1')
    # 接收并丢弃一行输出
    p.recvline()
    # 发送数据
    p.send(input_bytes)
    # 打印输出
    print(p.readall())

if __name__ == "__main__":
    main()