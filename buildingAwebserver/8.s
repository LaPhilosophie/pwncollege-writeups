.intel_syntax noprefix
.globl _start

.section .data
    bind_address: .long 0x00000000          # 0.0.0.0 in hexadecimal (network byte order)
    bind_port: .word 0x5000                 # Port 80 in hexadecimal (network byte order)
    response_header: .asciz "HTTP/1.0 200 OK\r\n\r\n"
    not_found_header: .asciz "HTTP/1.0 404 Not Found\r\n\r\n"

.section .bss
    .lcomm buffer, 4096                     # Buffer for reading requests
    .lcomm file_buffer, 4096                # Buffer for reading file contents
    .lcomm file_path, 256                   # Buffer for storing file path

.section .text

_start:
    # Step 1: 创建套接字
    mov rdi, 2              # AF_INET (IPv4)
    mov rsi, 1              # SOCK_STREAM (TCP)
    mov rdx, 0              # IPPROTO_IP (IP protocol)
    mov rax, 41             # syscall number for socket (SYS_socket)
    syscall

    # 保存套接字文件描述符
    mov r12, rax

    # Step 2: 准备 sockaddr_in 结构体
    sub rsp, 16
    mov rdi, rsp
    mov word ptr [rdi], 2                   # sa_family=AF_INET
    mov word ptr [rdi+2], 0x5000            # sin_port=htons(80)
    mov dword ptr [rdi+4], 0                # sin_addr=inet_addr("0.0.0.0")
    mov qword ptr [rdi+8], 0                # zero the rest of the structure

    # Step 3: 绑定套接字
    mov rdi, r12                           # socket file descriptor
    mov rsi, rsp                           # pointer to sockaddr_in
    mov rdx, 16                            # length of sockaddr_in
    mov rax, 49                            # syscall number for bind (SYS_bind)
    syscall

    # Step 4: 监听套接字
    mov rdi, r12                           # socket file descriptor
    mov rsi, 0                             # backlog
    mov rax, 50                            # syscall number for listen (SYS_listen)
    syscall

.loop:
    # Step 5: 接受连接
    mov rdi, r12                           # socket file descriptor
    mov rsi, 0                             # NULL (pointer for sockaddr)
    mov rdx, 0                             # NULL (pointer for socklen_t)
    mov rax, 43                            # syscall number for accept (SYS_accept)
    syscall

    # 保存接受的套接字文件描述符
    mov r13, rax

    # Step 6: 读取 HTTP 请求
    mov rdi, r13                           # accepted socket file descriptor
    lea rsi, [buffer]                      # buffer to read into
    mov rdx, 4096                          # maximum number of bytes to read
    mov rax, 0                             # syscall number for read (SYS_read)
    syscall

    # Step 7: 从请求中提取文件路径
    lea rdi, [buffer + 5]                  # 跳过 "GET /"
    lea rsi, [file_path]                   # 目标文件路径缓冲区
    mov byte ptr [rsi], '/'                # 确保文件路径从根目录开始
    inc rsi                                # 跳过前面的斜杠
    mov rcx, 254                           # 最多读取 254 字节
extract_path:
    cmp byte ptr [rdi], ' '                # 检查空格字符
    je  open_file                          # 如果是空格，结束文件路径提取
    mov al, byte ptr [rdi]                 # 读取请求中的一个字符
    mov byte ptr [rsi], al                 # 将其写入文件路径缓冲区
    inc rdi
    inc rsi
    loop extract_path

open_file:
    mov byte ptr [rsi], 0                  # 在文件路径末尾添加 null 终止符

    # Step 8: 尝试打开文件
    lea rdi, [file_path]                   # 文件路径
    mov rsi, 0                             # O_RDONLY
    mov rax, 2                             # syscall number for open (SYS_open)
    syscall

    # 检查文件是否成功打开
    cmp rax, 0
    js  not_found                          # 如果文件打开失败，返回 404 响应

    # 保存文件描述符
    mov r14, rax

    # Step 9: 读取文件内容
    mov rdi, r14                           # file descriptor
    lea rsi, [file_buffer]                 # buffer to read file into
    mov rdx, 4096                          # maximum number of bytes to read
    mov rax, 0                             # syscall number for read (SYS_read)
    syscall

    # 保存读取到的字节数
    mov r15, rax

    # Step 10: 关闭文件
    mov rdi, r14                           # file descriptor
    mov rax, 3                             # syscall number for close (SYS_close)
    syscall

    # Step 11: 写入 HTTP 响应头
    mov rdi, r13                           # accepted socket file descriptor
    lea rsi, [response_header]             # pointer to response header
    mov rdx, 19                            # length of the response header
    mov rax, 1                             # syscall number for write (SYS_write)
    syscall

    # Step 12: 写入文件内容
    mov rdi, r13                           # accepted socket file descriptor
    lea rsi, [file_buffer]                 # buffer with file content
    mov rdx, r15                           # length of the file content
    mov rax, 1                             # syscall number for write (SYS_write)
    syscall

    jmp close_connection                   # 跳到关闭连接部分

not_found:
    # 写入 404 响应
    mov rdi, r13                           # accepted socket file descriptor
    lea rsi, [not_found_header]            # pointer to 404 response header
    mov rdx, 24                            # length of the 404 response header
    mov rax, 1                             # syscall number for write (SYS_write)
    syscall

close_connection:
    # Step 13: 关闭接受的套接字
    mov rdi, r13                           # accepted socket file descriptor
    mov rax, 3                             # syscall number for close (SYS_close)
    syscall

    jmp .loop                              # 继续接受下一个请求

    # 清理栈
    add rsp, 16

    # Step 14: 退出程序
    mov rdi, 0                             # Exit code 0
    mov rax, 60                            # syscall number for exit (SYS_exit)
    syscall