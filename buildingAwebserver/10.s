.intel_syntax noprefix
.globl _start

.section .data
    bind_address: .long 0x00000000          # 0.0.0.0 in hexadecimal (network byte order)
    bind_port: .word 0x5000                 # Port 80 in hexadecimal (network byte order)
    response_header: .asciz "HTTP/1.0 200 OK\r\n\r\n"
    not_found_header: .asciz "HTTP/1.0 404 Not Found\r\n\r\n"
    create_error_header: .asciz "HTTP/1.0 500 Internal Server Error\r\n\r\n"

.section .bss
    .lcomm buffer, 4096                     # Buffer for reading requests
    .lcomm file_buffer, 4096                # Buffer for reading file contents
    .lcomm file_path, 256                   # Buffer for storing file path
    .lcomm content_length_buffer, 16        # Buffer for Content-Length value
    .lcomm write_buffer, 4096               # Buffer for writing data to file

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
    mov rdi, r12
    mov rsi, 0
    mov rdx, 0
    mov rax, 43
    syscall
    
    mov r13, rax

    # Step 6: 创建子进程
    mov rax, 57
    syscall

    # 父进程
    cmp rax, 0
    jg parent_process

    # 子进程
    cmp rax, 0
    je child_process

parent_process:
    mov rdi, r13
    mov rax, 3
    syscall
    jmp .loop

child_process:
    mov rdi, r12
    mov rax, 3
    syscall

    # Step 7: 读取 HTTP 请求
    mov rdi, r13
    lea rsi, [buffer]
    mov rdx, 4096
    mov rax, 0
    syscall

    # Step 8: 从请求中提取文件路径
    lea rdi, [buffer + 6]                  # 跳过 "POST /"
    lea rsi, [file_path]
    mov byte ptr [rsi], '/'
    inc rsi
    mov rcx, 254
extract_path:
    cmp byte ptr [rdi], ' '
    je  open_file
    mov al, byte ptr [rdi]
    mov byte ptr [rsi], al
    inc rdi
    inc rsi
    loop extract_path
    
open_file:

    mov byte ptr [rsi], 0

    # Step 9: 尝试打开文件
    lea rdi, [file_path]
    mov rsi, 65                           # O_WRONLY | O_CREAT 
    mov rdx, 0777                           # 权限 0777
    mov rax, 2                             # syscall number for open (SYS_open)
    syscall

    # 保存文件描述符
    mov r15, rax

    jmp find_body

find_body:
    lea rdi, [buffer]                    # 回到请求开始
    xor rcx, rcx                         # 清空换行符计数器
    mov rbx, 8                           # 目标换行符数量
find_next_newline:
    mov al, byte ptr [rdi]               # 读取当前字节
    cmp al, 10                           # 检查是否为 '\n' (ASCII 10)
    je count_newline
    inc rdi                              # 移动到下一个字节
    jmp find_next_newline

count_newline:
    inc rcx                              # 增加换行符计数
    inc rdi                              # 移动到下一个字节
    cmp rcx, rbx                         # 检查是否找到8个换行符
    jl find_next_newline                 # 如果少于8个，继续查找

    # 找到8个换行符后，rdi指向请求体数据开始处
    mov rsi, rdi                         # rsi 指向请求体数据开始处
    lea rdi, [write_buffer]              # 数据写入缓冲区
    mov rcx, 4096                        # 最大读取数据长度
    rep movsb                            # 复制数据到写入缓冲区
    sub rcx, 4096                        # 获取实际复制的字节数（4096 - 剩余的rcx）

    # 计算实际数据长度（直到第一个终止符\0）
    lea rsi, [write_buffer]
    mov rdi, rsi                         # 重新指向写入缓冲区的起点
    xor rcx, rcx                         # 清零计数器
count_data_length:
    cmp byte ptr [rdi], 0                # 检查是否是终止符\0
    je write_to_file                     # 如果是，结束
    inc rdi                              # 移动到下一个字节
    inc rcx                              # 增加数据长度计数
    jmp count_data_length

write_to_file:
    # 写入文件
    mov rdi, r15                         # 文件描述符
    lea rsi, [write_buffer]              # 写入缓冲区
    mov rdx, rcx                         # 实际要写入的字节数
    mov rax, 1                           # syscall number for write (SYS_write)
    syscall
    test rax, rax                        # 检查写入是否成功
    js write_error                       # 如果失败，跳转到错误处理

    # 关闭文件
    mov rdi, r15
    mov rax, 3                           # syscall number for close (SYS_close)
    syscall
    test rax, rax                        # 检查关闭是否成功
    js write_error

    # 发送成功响应
    mov rdi, r13
    lea rsi, [response_header]
    mov rdx, 19
    mov rax, 1                           # syscall number for write (SYS_write)
    syscall
    test rax, rax                        # 检查写入是否成功
    js write_error

    jmp close_connection

write_error:
    # 发送500 Internal Server Error响应
    mov rdi, r13
    lea rsi, [create_error_header]
    mov rdx, 36
    mov rax, 1
    syscall
    jmp close_connection

close_connection:
    mov rdi, r13
    mov rax, 3                           # syscall number for close (SYS_close)
    syscall

    mov rdi, 0                           # Exit code 0
    mov rax, 60                          # syscall number for exit (SYS_exit)
    syscall
