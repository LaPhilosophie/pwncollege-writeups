#!/usr/bin/env python3
from pwn import *
# 设置架构
context.arch='amd64'
# 创建一个进程对象 运行二进制文件
p=process('/challenge/run')
# 接收并丢弃一行输出
p.recvline()


# 发送数据
p.send(asm('mov rdi,0x1337'))
# 打印输出
print(p.readall())