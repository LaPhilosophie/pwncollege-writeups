.intel_syntax noprefix
.globl _start

.section .bss

.section .text

_start:
    # Create socket
    #  sockfd = socket(AF_INET, SOCK_STREAM, 0);
    mov rdi, 2              # AF_INET (IPv4)
    mov rsi, 1              # SOCK_STREAM (TCP)
    mov rdx, 0              # IPPROTO_IP (IP protocol)
    mov rax, 41             # syscall number for socket (SYS_socket)
    syscall

    # Save the socket file descriptor
    # sockfd
    mov r12, rax

    # Prepare sockaddr_in structure
    # addr.sin_family = AF_INET;
    # addr.sin_port = htons(80); // Port 80
    # addr.sin_addr.s_addr = INADDR_ANY; // IP address "0.0.0.0"
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

    # Clean up the stack
    add rsp, 16

    # Exit program
    mov rdi, 0                             # Exit code 0
    mov rax, 60                            # syscall number for exit (SYS_exit)
    syscall