.intel_syntax noprefix
.globl _start

.section .data
    bind_address: .long 0x00000000        # 0.0.0.0 in hexadecimal (network byte order)
    bind_port: .word 0x5000               # Port 80 in hexadecimal (network byte order)
    response: .asciz "HTTP/1.0 200 OK\r\n\r\n"

.section .bss
    .lcomm buffer, 4096                   # Buffer for reading requests

.section .text

_start:
    # Step 1: Create socket
    mov rdi, 2              # AF_INET (IPv4)
    mov rsi, 1              # SOCK_STREAM (TCP)
    mov rdx, 0              # IPPROTO_IP (IP protocol)
    mov rax, 41             # syscall number for socket (SYS_socket)
    syscall

    # Save the socket file descriptor
    mov r12, rax

    # Step 2: Prepare sockaddr_in structure
    sub rsp, 16
    mov rdi, rsp
    mov word ptr [rdi], 2                   # sa_family=AF_INET
    mov word ptr [rdi+2], 0x5000            # sin_port=htons(80)
    mov dword ptr [rdi+4], 0                # sin_addr=inet_addr("0.0.0.0")
    mov qword ptr [rdi+8], 0                # zero the rest of the structure

    # Step 3: Bind socket
    mov rdi, r12                           # socket file descriptor
    mov rsi, rsp                           # pointer to sockaddr_in
    mov rdx, 16                            # length of sockaddr_in
    mov rax, 49                            # syscall number for bind (SYS_bind)
    syscall

    # Step 4: Listen on the socket
    mov rdi, r12                           # socket file descriptor
    mov rsi, 0                             # backlog
    mov rax, 50                            # syscall number for listen (SYS_listen)
    syscall

    # Step 5: Accept a connection
    mov rdi, r12                           # socket file descriptor
    mov rsi, 0                             # NULL (pointer for sockaddr)
    mov rdx, 0                             # NULL (pointer for socklen_t)
    mov rax, 43                            # syscall number for accept (SYS_accept)
    syscall

    # Save the accepted socket file descriptor
    mov r13, rax

    # Step 6: Read the HTTP request
    mov rdi, r13                           # accepted socket file descriptor
    lea rsi, [buffer]                      # buffer to read into
    mov rdx, 4096                          # maximum number of bytes to read
    mov rax, 0                             # syscall number for read (SYS_read)
    syscall

    # Step 7: Write the HTTP response
    mov rdi, r13                           # accepted socket file descriptor
    mov rsi, offset response               # pointer to response
    mov rdx, 19                            # length of the response
    mov rax, 1                             # syscall number for write (SYS_write)
    syscall

    # Step 8: Close the accepted socket
    mov rdi, r13                           # accepted socket file descriptor
    mov rax, 3                             # syscall number for close (SYS_close)
    syscall

    # Clean up the stack
    add rsp, 16

    # Step 9: Exit the program
    mov rdi, 0                             # Exit code 0
    mov rax, 60                            # syscall number for exit (SYS_exit)
    syscall