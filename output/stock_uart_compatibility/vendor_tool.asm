; Executable pinned by vendor_tool_manifest.json; static evidence only.
; IAT 0x1401c7440: ICLM_Interface_RadarDevice_Serial_OpenByPortNum
; IAT 0x1401c7450: ICLM_Interface_RadarDevice_Protocol_SendCommand_NoCheckAck
; IAT 0x1401c7468: ICLM_Interface_RadarDevice_Serial_Close

140007c9e: mov dword ptr [rsp + 0x30], 0x96
140007ca6: mov dword ptr [rsp + 0x28], r14d
140007cab: mov dword ptr [rsp + 0x20], r14d
140007cb0: mov r9d, 2
140007cb6: mov r8d, esi
140007cb9: mov edx, eax
140007cbb: mov rcx, qword ptr [rdi + 0xa60]
140007cc2: call qword ptr [rip + 0x1bf778]
140007cc8: test eax, eax
140007cca: jne 0x140007cd6
140007ccc: mov edx, 0x28a4
140007cd1: jmp 0x140007d64
140007cd6: xor r9d, r9d
140007cd9: xor r8d, r8d
140007cdc: lea edx, [r9 + 0x66]
140007ce0: mov rcx, qword ptr [rdi + 0xa60]
140007ce7: call qword ptr [rip + 0x1bf763]
140007ced: mov rcx, qword ptr [rdi + 0xa60]
140007cf4: mov rax, qword ptr [rcx]
140007cf7: mov edx, 0x3e8
140007cfc: call qword ptr [rax + 0xd8]
140007d02: mov rcx, qword ptr [rdi + 0xa60]
140007d09: call qword ptr [rip + 0x1bf759]
140007d0f: mov dword ptr [rsp + 0x30], 0x96
140007d17: mov dword ptr [rsp + 0x28], r14d
140007d1c: mov dword ptr [rsp + 0x20], r14d
140007d21: mov r9d, 2
140007d27: mov r8d, 0x2580
140007d2d: mov edx, ebx
140007d2f: mov rcx, qword ptr [rdi + 0xa60]
140007d36: call qword ptr [rip + 0x1bf704]

140007d98: xorps xmm0, xmm0
140007d9b: movdqu xmmword ptr [rsp + 0x58], xmm0
140007da1: mov qword ptr [rsp + 0x68], r14
140007da6: lea r8, [rsp + 0x58]
140007dab: mov dl, 6
140007dad: lea rcx, [rbp + 0x40]
140007db1: call 0x140006650

140007f7d: mov dword ptr [rbp + 0x30], 0x2580
140007f84: lea rax, [rbp + 0x30]
140007f88: mov qword ptr [rsp + 0x70], rax
140007f8d: mov dword ptr [rsp + 0x78], 4
140007f95: xorps xmm0, xmm0

140007fc8: lea r8, [rsp + 0x40]
140007fcd: mov dl, 1
140007fcf: lea rcx, [rbp + 0x40]
140007fd3: call 0x140006650

140008495: movzx edi, byte ptr [rbx]
140008498: mov ecx, edi
14000849a: sub ecx, 2
14000849d: je 0x140008732
1400084a3: sub ecx, 1
1400084a6: je 0x1400086a1
1400084ac: sub ecx, 1
1400084af: je 0x1400085df
1400084b5: cmp ecx, 1
1400084b8: je 0x140008532

140008732: cmp eax, 9
140008735: jne 0x140008abb
14000873b: mov r14d, dword ptr [rbx + 1]
14000873f: mov ebx, dword ptr [rbx + 5]
140008742: mov dword ptr [rbp + 0x18], ebx
140008745: mov edx, dword ptr [rbp + 0x20]
140008748: cmp edx, r14d
14000874b: jae 0x140008878
