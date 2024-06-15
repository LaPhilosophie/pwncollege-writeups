#!/usr/bin/env python3
from pwn import *
def reverse_mangle_input(buf):
    # 第1步：逆向交换操作，针对索引 3 和 20
    buf[3], buf[20] = buf[20], buf[3]

    # 第2步：逆向 XOR 操作 (0xDE, 0xA6)
    for jj in range(29):
        if jj % 2:
            buf[jj] ^= 0xA6
        else:
            buf[jj] ^= 0xDE

    # 第3步：逆向交换操作，针对索引 4 和 6
    buf[4], buf[6] = buf[6], buf[4]

    # 第4步：逆向 XOR 操作 (0x1C, 0x58, 0xC7)
    for m in range(29):
        if m % 3 == 2:
            buf[m] ^= 0xC7
        elif m % 3 == 1:
            buf[m] ^= 0x58
        else:
            buf[m] ^= 0x1C

    # 第5步：逆向 XOR 操作 (0x78, 0xD0)
    for j in range(29):
        if j % 2:
            buf[j] ^= 0xD0
        else:
            buf[j] ^= 0x78

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
        0xCD, 0x4F, 0x05, 0x0E, 0xDD, 0xDA, 0x98, 0x56,
        0x18, 0x0B, 0x97, 0xD9, 0xD0, 0x56, 0x03, 0x0E,
        0x92, 0xD6, 0xCF, 0x5E, 0x0E, 0x00, 0x9B, 0xDB,
        0xD9, 0x48, 0x05, 0x1B, 0x9C, 0x00
    ])

    # 得到初始输入
    initial_input = find_initial_input(expected_result)


    # 设置架构
    context.arch='amd64'
    # 创建一个进程对象 运行二进制文件
    p=process('/challenge/babyrev_level7.0')
    # 接收并丢弃一行输出
    p.recvline()


    p.send(initial_input)
    # 打印输出
    print(p.readallS())

if __name__ == "__main__":
    main()



