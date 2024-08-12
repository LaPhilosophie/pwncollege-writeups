.intel_syntax noprefix
.globl _start

.section .data
    bind_address: .long 0x00000000          # 0.0.0.0 in hexadecimal (network byte order)
    bind_port: .word 0x5000                 # Port 80 in hexadecimal (network byte order)
    response_header: .asciz "HTTP/1.0 200 OK\r\n\r\n"
    not_found_header: .asciz "HTTP/1.0 404 Not Found\r\n\r\n"
    create_error_header: .asciz "HTTP/1.0 500 Internal Server Error\r\n\r\n"
    method_get: .asciz "GET "
    method_post: .asciz "POST "

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
    mov rsi, 128                           # backlog
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

    # Step 6: 创建子进程
    mov rax, 57                            # syscall number for fork (SYS_fork)
    syscall

    # 父进程
    cmp rax, 0
    jg parent_process

    # 子进程
    cmp rax, 0
    je child_process

parent_process:
    # 父进程关闭接受的套接字并继续监听
    mov rdi, r13                           # accepted socket file descriptor
    mov rax, 3                             # syscall number for close (SYS_close)
    syscall
    jmp .loop                              # 继续接受下一个请求

child_process:
    # 子进程关闭监听套接字
    mov rdi, r12                           # listening socket file descriptor
    mov rax, 3                             # syscall number for close (SYS_close)
    syscall

    # Step 7: 读取 HTTP 请求
    mov rdi, r13                           # accepted socket file descriptor
    lea rsi, [buffer]                      # buffer to read into
    mov rdx, 4096                          # maximum number of bytes to read
    mov rax, 0                             # syscall number for read (SYS_read)
    syscall
    test rax, rax
    js error_response                      # 读取错误时处理

    # Step 8: 检查请求类型（GET或POST）
    lea rdi, [buffer]                      # 回到请求开始
    lea rsi, [method_get]
    mov rcx, 4                             # "GET " 的长度
    repe cmpsb
    je handle_get                          # 如果匹配，处理GET请求

    lea rdi, [buffer]
    lea rsi, [method_post]
    mov rcx, 5                             # "POST " 的长度
    repe cmpsb
    je handle_post                         # 如果匹配，处理POST请求

    jmp error_response                     # 未知请求类型

handle_get:
    # 从请求中提取文件路径
    lea rdi, [buffer + 4]                  # 跳过 "GET "
    lea rsi, [file_path]                   # 目标文件路径缓冲区
    mov byte ptr [rsi], '/'                # 确保文件路径从根目录开始
    inc rsi                                # 跳过前面的斜杠
    mov rcx, 254                           # 最多读取 254 字节
extract_get_path:
    cmp byte ptr [rdi], ' '                # 检查空格字符
    je  open_get_file                      # 如果是空格，结束文件路径提取
    mov al, byte ptr [rdi]                 # 读取请求中的一个字符
    mov byte ptr [rsi], al                 # 将其写入文件路径缓冲区
    inc rdi
    inc rsi
    loop extract_get_path

open_get_file:
    mov byte ptr [rsi], 0                  # 在文件路径末尾添加 null 终止符

    # 打开文件并发送响应
    call open_and_send_file
    jmp close_connection

handle_post:
    # 从请求中提取文件路径
    lea rdi, [buffer + 5]                  # 跳过 "POST /"
    lea rsi, [file_path]
    mov byte ptr [rsi], '/'
    inc rsi
    mov rcx, 254
extract_post_path:
    cmp byte ptr [rdi], ' '
    je  open_post_file
    mov al, byte ptr [rdi]
    mov byte ptr [rsi], al
    inc rdi
    inc rsi
    loop extract_post_path

open_post_file:
    mov byte ptr [rsi], 0

    # 打开文件以写入数据
    lea rdi, [file_path]
    mov rsi, 65                           # O_WRONLY | O_CREAT 
    mov rdx, 0777                         # 权限 0777
    mov rax, 2                             # syscall number for open (SYS_open)
    syscall
    test rax, rax
    js error_response                      # 处理文件打开错误
    mov r15, rax                           # 保存文件描述符

    # 查找请求体数据并写入文件
    call find_and_write_body
    jmp close_connection

open_and_send_file:
    # 尝试打开文件
    lea rdi, [file_path]
    mov rsi, 0                             # O_RDONLY
    mov rax, 2                             # syscall number for open (SYS_open)
    syscall
    test rax, rax
    js not_found                           # 如果文件打开失败，返回 404 响应

    mov r14, rax                           # 保存文件描述符

    # 读取文件内容
    mov rdi, r14                           # file descriptor
    lea rsi, [file_buffer]                 # buffer to read file into
    mov rdx, 4096                          # maximum number of bytes to read
    mov rax, 0                             # syscall number for read (SYS_read)
    syscall
    test rax, rax
    js error_response                      # 读取文件错误时处理

    mov r15, rax                           # 保存读取到的字节数

    # 关闭文件
    mov rdi, r14
    mov rax, 3                             # syscall number for close (SYS_close)
    syscall

    # 写入 HTTP 响应头
    mov rdi, r13                           # accepted socket file descriptor
    lea rsi, [response_header]             # pointer to response header
    mov rdx, 19                            # length of the response header
    mov rax, 1                             # syscall number for write (SYS_write)
    syscall

    # 写入文件内容
    mov rdi, r13                           # accepted socket file descriptor
    lea rsi, [file_buffer]                 # buffer with file content
    mov rdx, r15                           # length of the file content
    mov rax, 1                             # syscall number for write (SYS_write)
    syscall

    jmp close_connection                   # 跳到关闭连接部分

find_and_write_body:
    lea rdi, [buffer]                      # 回到请求开始
    xor rcx, rcx                           # 清空换行符计数器
    mov rbx, 8                             # 目标换行符数量
find_next_newline:
    mov al, byte ptr [rdi]                 # 读取当前字节
    cmp al, 10                             # 检查是否为 '\n' (ASCII 10)
    je count_newline
    inc rdi                                # 移动到下一个字节
    jmp find_next_newline

count_newline:
    inc rcx                                # 增加换行符计数
    inc rdi                                # 移动到下一个字节
    cmp rcx, rbx                           # 检查是否找到8个换行符
    jl find_next_newline                   # 如果少于8个，继续查找

    # 找到8个换行符后，rdi指向请求体数据开始处
    mov rsi, rdi                           # rsi 指向请求体数据开始处
    lea rdi, [write_buffer]                # 数据写入缓冲区
    mov rcx, 4096                          # 最大读取数据长度
    rep movsb                              # 复制数据到写入缓冲区
    sub rcx, 4096                          # 获取实际复制的字节数（4096 - 剩余的rcx）

    # 计算实际数据长度（直到第一个终止符\0）
    lea rsi, [write_buffer]
    mov rdi, rsi                           # 重新指向写入缓冲区的起点
    xor rcx, rcx                           # 清零计数器
count_data_length:
    cmp byte ptr [rdi], 0                  # 检查是否是终止符\0
    je write_to_file                       # 如果是，结束
    inc rdi                                # 移动到下一个字节
    inc rcx                                # 增加数据长度计数
    jmp count_data_length

write_to_file:
    # 写入文件
    mov rdi, r15                           # 文件描述符
    lea rsi, [write_buffer]                # 写入缓冲区
    mov rdx, rcx                           # 实际要写入的字节数
    mov rax, 1                             # syscall number for write (SYS_write)
    syscall
    test rax, rax                          # 检查写入是否成功
    js write_error                         # 如果失败，跳转到错误处理

    # 关闭文件
    mov rdi, r15
    mov rax, 3                             # syscall number for close (SYS_close)
    syscall
    test rax, rax                          # 检查关闭是否成功
    js write_error

    # 发送成功响应
    mov rdi, r13
    lea rsi, [response_header]
    mov rdx, 19
    mov rax, 1                             # syscall number for write (SYS_write)
    syscall
    test rax, rax                          # 检查写入是否成功
    js write_error

    jmp close_connection

write_error:
    # 发送500 Internal Server Error响应
    mov rdi, r13
    lea rsi, [create_error_header]
    mov rdx, 36
    mov rax, 1                             # syscall number for write (SYS_write)
    syscall
    jmp close_connection

not_found:
    # 写入 404 响应
    mov rdi, r13                           # accepted socket file descriptor
    lea rsi, [not_found_header]            # pointer to 404 response header
    mov rdx, 24                            # length of the 404 response header
    mov rax, 1                             # syscall number for write (SYS_write)
    syscall
    jmp close_connection

error_response:
    # 发送错误响应
    mov rdi, r13
    lea rsi, [create_error_header]
    mov rdx, 36
    mov rax, 1
    syscall
    jmp close_connection

close_connection:
    # 关闭接受的套接字
    mov rdi, r13
    mov rax, 3                             # syscall number for close (SYS_close)
    syscall

    # 子进程退出
    mov rdi, 0                             # Exit code 0
    mov rax, 60                            # syscall number for exit (SYS_exit)
    syscall
