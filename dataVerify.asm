section .data
    file_checksum db 0x00 
    expected_checksum db 0x12 

section .text
    global _start

_start:

    cmp byte [file_checksum], byte [expected_checksum]
    jne file_corrupt ; Jump to file_corrupt label if the checksums don't match
    mov eax, 1
    xor ebx, ebx
    int 0x80

file_corrupt:

    mov eax, 1
    mov ebx, 1 ;
    int 0x80