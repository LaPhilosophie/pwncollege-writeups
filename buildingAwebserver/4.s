.intel_syntax noprefix
.globl _start

.section .data
    bind_address: .long 0x00000000        # 0.0.0.0 in hexadecimal (network byte order)
    bind_port: .word 0x5000               # Port 80 in hexadecimal (network byte order)

.section .bss

.section .text

_start:
    # Create socket
    mov rdi, 2              # AF_INET (IPv4)
    mov rsi, 1              # SOCK_STREAM (TCP)
    mov rdx, 0              # IPPROTO_IP (IP protocol)
    mov rax, 41             # syscall number for socket (SYS_socket)
    syscall

    # Save the socket file descriptor
    mov r12, rax

    # Prepare sockaddr_in structure
    sub rsp, 16
    mov rdi, rsp
    mov word ptr [rdi], 2                   # sa_family=AF_INET
    mov word ptr [rdi+2], 0x5000            # sin_port=htons(80)
    mov dword ptr [rdi+4], 0                # sin_addr=inet_addr("0.0.0.0")
    mov qword ptr [rdi+8], 0                # zero the rest of the structure

    # Bind socket
    # bind(sockfd, (struct sockaddr *)&addr, sizeof(addr))
    mov rdi, r12                           # socket file descriptor
    mov rsi, rsp                           # pointer to sockaddr_in
    mov rdx, 16                            # length of sockaddr_in
    mov rax, 49                            # syscall number for bind (SYS_bind)
    syscall

    # Listen on the socket
    mov rdi, r12                           # socket file descriptor
    mov rsi, 0                             # backlog
    mov rax, 50                            # syscall number for listen (SYS_listen)
    syscall

    # Clean up the stack
    add rsp, 16

    # Exit program
    mov rdi, 0                             # Exit code 0
    mov rax, 60                            # syscall number for exit (SYS_exit)
    syscall