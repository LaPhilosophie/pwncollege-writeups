.intel_syntax noprefix
.globl _start

.section .text

_start:
    # Create socket
    mov rdi, 2              # AF_INET (IPv4)
    mov rsi, 1              # SOCK_STREAM (TCP)
    mov rdx, 0              # IPPROTO_IP (IP protocol)
    mov rax, 41             # syscall number for socket (SYS_socket)
    syscall

    # Exit program
    mov rdi, 0              # Exit code 0
    mov rax, 60             # syscall number for exit (SYS_exit)
    syscall

