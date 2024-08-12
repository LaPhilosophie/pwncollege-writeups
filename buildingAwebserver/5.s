.intel_syntax noprefix
.globl _start

.section .bss

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

    # Step 6: Exit the program
    mov rdi, 0                             # Exit code 0
    mov rax, 60                            # syscall number for exit (SYS_exit)
    syscall