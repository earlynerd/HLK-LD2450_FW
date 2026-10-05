; Static PI32v2 decoding; offsets refer to extracted app.bin.
; This is disassembly evidence, not validated firmware emulation.

; copy_initial_data_to_ram
000062  01e00182  c4ff00000000      mov r4, #0x0
000068  01e00188  c1ffd075e201      mov r1, #0x1e275d0
00006e  01e0018e  c2ffac430000      mov r2, #0x43ac
000074  01e00194  a2a2              lsr r2, r2, 0x2
000076  01e00196  1203              rep 0x4, r2
000078  01e00198  1305              lw r3, [r1 ++= 4]
00007a  01e0019a  c305              sw r3, [r4 ++= 4]
00007c  01e0019c  f25c              jnz r2, 0x1e00196

; i2c_busy_wait
010dbe  01e10ede  0482              goto 0x1e10ee4
010dc0  01e10ee0  0000              nop 
010dc2  01e10ee2  f83f              add r0, #-0x1
010dc4  01e10ee4  f05d              jnz r0, 0x1e10ee0
010dc6  01e10ee6  8000              rts 

; i2c_write_word
010f7c  01e1109c  7604              push {rets,r6,r5,r4}
010f7e  01e1109e  2416              mov r4, r2
010f80  01e110a0  1516              mov r5, r1
010f82  01e110a2  0616              mov r6, r0
010f84  01e110a4  bfea20ff          call 0x1e10ee8
010f88  01e110a8  6016              mov r0, r6
010f8a  01e110aa  bfea4eff          call 0x1e10f4a
010f8e  01e110ae  5194              call 0x1e11018
010f90  01e110b0  005e              jz r0, 0x1e110ee
010f92  01e110b2  5016              mov r0, r5
010f94  01e110b4  bfea49ff          call 0x1e10f4a
010f98  01e110b8  518f              call 0x1e11018
010f9a  01e110ba  005f              jz r0, 0x1e110fa
010f9c  01e110bc  70e00044          rev8 r4, r4
010fa0  01e110c0  c0b0              lsr r0, r4, 0x10
010fa2  01e110c2  70e17f0c          and r0, r0, #0xffff00ff
010fa6  01e110c6  bfea40ff          call 0x1e10f4a
010faa  01e110ca  5186              call 0x1e11018
010fac  01e110cc  005c              jz r0, 0x1e11106
010fae  01e110ce  c0b8              lsr r0, r4, 0x18
010fb0  01e110d0  bfea3bff          call 0x1e10f4a
010fb4  01e110d4  5181              call 0x1e11018
010fb6  01e110d6  0416              mov r4, r0
010fb8  01e110d8  bfea75ff          call 0x1e10fc6
010fbc  01e110dc  b4e80010          if (r4 != #0x0) {
010fc0  01e110e0  c0ffe003e201      mov r0, #0x1e203e0
010fc6  01e110e6  c0ffc003e201      mov r0, #0x1e203c0
010fcc  01e110ec  0491              goto 0x1e11110
010fce  01e110ee  bfea6aff          call 0x1e10fc6
010fd2  01e110f2  c0ff6003e201      mov r0, #0x1e20360
010fd8  01e110f8  048b              goto 0x1e11110
010fda  01e110fa  bfea64ff          call 0x1e10fc6
010fde  01e110fe  c0ff8003e201      mov r0, #0x1e20380
010fe4  01e11104  0485              goto 0x1e11110
010fe6  01e11106  bfea5eff          call 0x1e10fc6
010fea  01e1110a  c0ffa003e201      mov r0, #0x1e203a0
010ff0  01e11110  3604              pop {rets, r6,r5,r4}
010ff2  01e11112  ffea72da          goto 0x1e0c5fa

; write_first_75
01b5a6  01e1b6c6  7504              push {rets,r5,r4}
01b5a8  01e1b6c8  c0ffb0420000      mov r0, #0x42b0
01b5ae  01e1b6ce  0841              lb.z r0, [r0 + 0x1]
01b5b0  01e1b6d0  80f80f02          jne r0, #0x1, 0x1e1b6f2
01b5b4  01e1b6d4  4420              mov r4, #0x0
01b5b6  01e1b6d6  c5ff441be201      mov r5, #0x1e21b44
01b5bc  01e1b6dc  5016              mov r0, r5
01b5be  01e1b6de  dcee0014          lb.z r1, [++r0 = r4]
01b5c2  01e1b6e2  0a61              lh.z r2, [r0 + 0x2]
01b5c4  01e1b6e4  5020              mov r0, #0x40
01b5c6  01e1b6e6  bfead9ac          call 0x1e1109c
01b5ca  01e1b6ea  c424              add r4, #0x4
01b5cc  01e1b6ec  a4f8f659          jne r4, #0x12c
01b5d0  01e1b6f0  5504              pop {pc,r5,r4}
01b5d2  01e1b6f2  4420              mov r4, #0x0
01b5d4  01e1b6f4  c5ffe4400000      mov r5, #0x40e4
01b5da  01e1b6fa  d8ed4005          lh.z r0, [r4 + r5]
01b5de  01e1b6fe  004a              jz r0, 0x1e1b714
01b5e0  01e1b700  491d              add r1, r4, r5
01b5e2  01e1b702  71f17f0c          and r1, r0, #0xffff00ff
01b5e6  01e1b706  1a61              lh.z r2, [r1 + 0x2]
01b5e8  01e1b708  5020              mov r0, #0x40
01b5ea  01e1b70a  bfeac7ac          call 0x1e1109c
01b5ee  01e1b70e  c424              add r4, #0x4
01b5f0  01e1b710  a4f8f359          jne r4, #0x12c
01b5f4  01e1b714  5504              pop {pc,r5,r4}

; spi_initialization
01b7c6  01e1b8e6  7904              push {rets,r9,r8,r7,r6,r5,r4}
01b7c8  01e1b8e8  c1ffb0420000      mov r1, #0x42b0
01b7ce  01e1b8ee  40f03020          movz r0, #0x2030
01b7d2  01e1b8f2  1d41              lb.z r5, [r1 + 0x1]
01b7d4  01e1b8f4  c9ffe0700000      mov r9, #0x70e0
01b7da  01e1b8fa  9018              add r0, r9
01b7dc  01e1b8fc  4120              mov r1, #0x0
01b7de  01e1b8fe  42e02410          movz r2, #0x1024
01b7e2  01e1b902  97ea57b7          call 0x21127b4
01b7e6  01e1b906  c4ff604c0000      mov r4, #0x4c60
01b7ec  01e1b90c  4020              mov r0, #0x0
01b7ee  01e1b90e  4120              mov r1, #0x0
01b7f0  01e1b910  50ec4100          sdw r0_r1, [r4 + 0x0]
01b7f4  01e1b914  4820              mov r0, #0x20
01b7f6  01e1b916  b5e80100          if (r5 != #0x1) {
01b7fa  01e1b91a  5020              mov r0, #0x40
01b7fc  01e1b91c  42f00008          movz r2, #0x800
01b800  01e1b920  c862              sh r0, [r4 + 0x4]
01b802  01e1b922  c0ff02000808      mov r0, #0x8080002
01b808  01e1b928  e0f0219d          add r0, r9, 0x2840
01b80c  01e1b92c  c060              sw r0, [r4 + 0x0]
01b80e  01e1b92e  4122              mov r1, #0x2
01b810  01e1b930  0484              goto 0x1e1b93a
01b812  01e1b932  f93f              add r1, #-0x1
01b814  01e1b934  00f11208          add r0, r0, #0x812
01b818  01e1b938  8a60              sh r2, [r0 + 0x0]
01b81a  01e1b93a  f15b              jnz r1, 0x1e1b932
01b81c  01e1b93c  01e16292          add r1, r9, #0x262
01b820  01e1b940  403e              mov r0, #0x1e
01b822  01e1b942  423a              mov r2, #0x1a
01b824  01e1b944  bfeaccf0          call 0x1e19ae0
01b828  01e1b948  0116              mov r1, r0
01b82a  01e1b94a  b1e81a40          if (r1 != #0x1a) {
01b82e  01e1b94e  c0ffe6fbe101      mov r0, #0x1e1fbe6
01b834  01e1b954  bfea1786          call 0x1e0c586
01b838  01e1b958  4c61              lh.z r4, [r4 + 0x2]
01b83a  01e1b95a  50ed9743          sh r4, [r9 + 0x36]
01b83e  01e1b95e  4021              mov r0, #0x1
01b840  01e1b960  4621              mov r6, #0x1
01b842  01e1b962  bfeafafe          call 0x1e1b75a
01b846  01e1b966  4021              mov r0, #0x1
01b848  01e1b968  5193              call 0x1e1b8d0
01b84a  01e1b96a  c2ff3e4be101      mov r2, #0x1e14b3e
01b850  01e1b970  402f              mov r0, #0xf
01b852  01e1b972  4123              mov r1, #0x3
01b854  01e1b974  bfeaef87          call 0x1e0c956
01b858  01e1b978  50ee9700          lb.z r0, [r9 + 0x7]
01b85c  01e1b97c  45e00808          movz r5, #0x808
01b860  01e1b980  501b              mul r0, r5
01b862  01e1b982  c7ff084d0000      mov r7, #0x4d08
01b868  01e1b988  891d              add r1, r0, r7
01b86a  01e1b98a  4021              mov r0, #0x1
01b86c  01e1b98c  4216              mov r2, r4
01b86e  01e1b98e  bfeac7c8          call 0x1e14b20
01b872  01e1b992  4022              mov r0, #0x2
01b874  01e1b994  bfeae1fe          call 0x1e1b75a
01b878  01e1b998  4022              mov r0, #0x2
01b87a  01e1b99a  419a              call 0x1e1b8d0
01b87c  01e1b99c  c2ff804be101      mov r2, #0x1e14b80
01b882  01e1b9a2  482c              mov r0, #0x2c
01b884  01e1b9a4  4123              mov r1, #0x3
01b886  01e1b9a6  bfead687          call 0x1e0c956
01b88a  01e1b9aa  50ee9800          lb.z r0, [r9 + 0x8]
01b88e  01e1b9ae  501b              mul r0, r5
01b890  01e1b9b0  7018              add r0, r7
01b892  01e1b9b2  11e11000          add r1, r0, 0x1010
01b896  01e1b9b6  4022              mov r0, #0x2
01b898  01e1b9b8  4216              mov r2, r4
01b89a  01e1b9ba  bfeab1c8          call 0x1e14b20
01b89e  01e1b9be  00e15890          add r0, r9, #0x58
01b8a2  01e1b9c2  50ee0880          lb.z r8, [r0 + 0x8]
01b8a6  01e1b9c6  14f11095          add r4, r9, 0x1510
01b8aa  01e1b9ca  0f44              lb.z r7, [r0 + 0x4]
01b8ac  01e1b9cc  42f02003          movz r2, #0x320
01b8b0  01e1b9d0  0d40              lb.z r5, [r0 + 0x0]
01b8b2  01e1b9d2  4120              mov r1, #0x0
01b8b4  01e1b9d4  4016              mov r0, r4
01b8b6  01e1b9d6  97eaedb6          call 0x21127b4
01b8ba  01e1b9da  c0ffcdcc4c3e      mov r0, #0x3e4ccccd
01b8c0  01e1b9e0  c1ff9a99993f      mov r1, #0x3f99999a
01b8c6  01e1b9e6  0485              goto 0x1e1b9f2
01b8c8  01e1b9e8  50ec4d03          sdw r0_r1, [r4 + 0x3c]
01b8cc  01e1b9ec  d8ec496c          sw r6, [r4++=0xc8]
01b8d0  01e1b9f0  c621              add r6, #0x1
01b8d2  01e1b9f2  86f8f90b          jne r6, #0x5, 0x1e1b9e8
01b8d6  01e1b9f6  41e098fe          movz r1, #0xfe98
01b8da  01e1b9fa  25ea0100          if ((r5 & #0x1) != 0) {
01b8de  01e1b9fe  4120              mov r1, #0x0
01b8e0  01e1ba00  00e14490          add r0, r9, #0x44
01b8e4  01e1ba04  41f06801          movz r1, #0x168
01b8e8  01e1ba08  8961              sh r1, [r0 + 0x2]
01b8ea  01e1ba0a  27ea0100          if ((r7 & #0x1) != 0) {
01b8ee  01e1ba0e  4120              mov r1, #0x0
01b8f0  01e1ba10  41f02003          movz r1, #0x320
01b8f4  01e1ba14  8960              sh r1, [r0 + 0x0]
01b8f6  01e1ba16  28ea0100          if ((r8 & #0x1) != 0) {
01b8fa  01e1ba1a  4120              mov r1, #0x0
01b8fc  01e1ba1c  8962              sh r1, [r0 + 0x4]
01b8fe  01e1ba1e  5904              pop {pc,r9,r8,r7,r6,r5,r4}

; write_last_5
01b900  01e1ba20  7604              push {rets,r6,r5,r4}
01b902  01e1ba22  4823              mov r0, #0x23
01b904  01e1ba24  bfeaca23          call 0x1e001bc
01b908  01e1ba28  0047              jz r0, 0x1e1ba38
01b90a  01e1ba2a  c1ff00021e00      mov r1, #0x1e0200
01b910  01e1ba30  1260              lw r2, [r1 + 0x0]
01b912  01e1ba32  00ef0800          or [r0+0x0], #0x8
01b916  01e1ba36  1060              lw r0, [r1 + 0x0]
01b918  01e1ba38  40e0e803          movz r0, #0x3e8
01b91c  01e1ba3c  bfea4faa          call 0x1e10ede
01b920  01e1ba40  c0ffb0420000      mov r0, #0x42b0
01b926  01e1ba46  0841              lb.z r0, [r0 + 0x1]
01b928  01e1ba48  80f81304          jne r0, #0x2, 0x1e1ba72
01b92c  01e1ba4c  542b              mov r4, #0x4b
01b92e  01e1ba4e  c5ffe4400000      mov r5, #0x40e4
01b934  01e1ba54  0488              goto 0x1e1ba66
01b936  01e1ba56  5118              add r1, r5
01b938  01e1ba58  71f17f0c          and r1, r0, #0xffff00ff
01b93c  01e1ba5c  1a61              lh.z r2, [r1 + 0x2]
01b93e  01e1ba5e  5020              mov r0, #0x40
01b940  01e1ba60  bfea1cab          call 0x1e1109c
01b944  01e1ba64  c421              add r4, #0x1
01b946  01e1ba66  c017              uxth r0, r4
01b948  01e1ba68  01a2              lsl r1, r0, 0x2
01b94a  01e1ba6a  d8ed5001          lh.z r0, [r5 + r1]
01b94e  01e1ba6e  f053              jnz r0, 0x1e1ba56
01b950  01e1ba70  5604              pop {pc,r6,r5,r4}
01b952  01e1ba72  142c              movs r4, #-0x14
01b954  01e1ba74  c5ff441be201      mov r5, #0x1e21b44
01b95a  01e1ba7a  46e04001          movz r6, #0x140
01b95e  01e1ba7e  0489              goto 0x1e1ba92
01b960  01e1ba80  481d              add r0, r4, r5
01b962  01e1ba82  d8ee0016          lb.z r1, [r0 + r6]
01b966  01e1ba86  51ed0224          lh.z r2, [r0 + 0x142]
01b96a  01e1ba8a  5020              mov r0, #0x40
01b96c  01e1ba8c  bfea06ab          call 0x1e1109c
01b970  01e1ba90  c424              add r4, #0x4
01b972  01e1ba92  f456              jnz r4, 0x1e1ba80
01b974  01e1ba94  5604              pop {pc,r6,r5,r4}

; radar_init_call_order
01b9ca  01e1baea  7504              push {rets,r5,r4}
01b9cc  01e1baec  e29e              add sp, #-0x8
01b9ce  01e1baee  c0ff7002e201      mov r0, #0x1e20270
01b9d4  01e1baf4  bfea8185          call 0x1e0c5fa
01b9d8  01e1baf8  c4fffc23e201      mov r4, #0x1e223fc
01b9de  01e1bafe  10e16f45          add r0, r4, 0x156f
01b9e2  01e1bb02  4121              mov r1, #0x1
01b9e4  01e1bb04  4223              mov r2, #0x3
01b9e6  01e1bb06  bfea3e85          call 0x1e0c586
01b9ea  01e1bb0a  bfea9bc7          call 0x1e14a44
01b9ee  01e1bb0e  bfeaedfa          call 0x1e1b0ec
01b9f2  01e1bb12  bfea2cfb          call 0x1e1b16e
01b9f6  01e1bb16  bfead0fd          call 0x1e1b6ba
01b9fa  01e1bb1a  bfea93c7          call 0x1e14a44
01b9fe  01e1bb1e  bfead2fd          call 0x1e1b6c6
01ba02  01e1bb22  bfea8fc7          call 0x1e14a44
01ba06  01e1bb26  bfeadefe          call 0x1e1b8e6
01ba0a  01e1bb2a  bfea8bc7          call 0x1e14a44
01ba0e  01e1bb2e  bfea77ff          call 0x1e1ba20
01ba12  01e1bb32  bfea87c7          call 0x1e14a44
01ba16  01e1bb36  5199              call 0x1e1baaa

; saved_mode_selection_part
01b04e  01e1b16e  7704              push {rets,r7,r6,r5,r4}
01b050  01e1b170  e29f              add sp, #-0x4
01b052  01e1b172  4020              mov r0, #0x0
01b054  01e1b174  dee90300          sb r0, [sp+0x3]
01b058  01e1b178  8983              add r1, sp, #0x3
01b05a  01e1b17a  4039              mov r0, #0x19
01b05c  01e1b17c  4221              mov r2, #0x1
01b05e  01e1b17e  4521              mov r5, #0x1
01b060  01e1b180  bfeaaef4          call 0x1e19ae0
01b064  01e1b184  c6ffb0420000      mov r6, #0x42b0
01b06a  01e1b18a  c4ffe0700000      mov r4, #0x70e0
01b070  01e1b190  80f81302          jne r0, #0x1, 0x1e1b1ba
01b074  01e1b194  dce90300          lb r0, [sp+0x3]
01b078  01e1b198  41d6              mov r1, r4
01b07a  01e1b19a  e841              sb r0, [r6 + 0x1]

; command_updates_ram_table
0117cc  01e118ec  50eda000          lh.z r0, [r10 + 0x0]
0117d0  01e118f0  d117              uxth r1, r5
0117d2  01e118f2  81f81780          jne r1, #0x40, 0x1e11924
0117d6  01e118f6  50eda210          lh.z r1, [r10 + 0x2]
0117da  01e118fa  4220              mov r2, #0x0
0117dc  01e118fc  bee14020          uextra r14, r2, 0x0, 0x10
0117e0  01e11900  c0e1e230          lsl r3, r14, 0x2
0117e4  01e11904  c6ffe4400000      mov r6, #0x40e4
0117ea  01e1190a  d8ed6063          lh.z r6, [r6 + r3]
0117ee  01e1190e  064a              jz r6, 0x1e11924
0117f0  01e11910  c221              add r2, #0x1
0117f2  01e11912  8ef9f30b          jb r14, 0x5, 0x1e118fc
0117f6  01e11916  80e8f161          jne r6, r0, 0x1e118fc
0117fa  01e1191a  c2ffe4400000      mov r2, #0x40e4
011800  01e11920  3218              add r2, r3
011802  01e11922  a961              sh r1, [r2 + 0x2]
