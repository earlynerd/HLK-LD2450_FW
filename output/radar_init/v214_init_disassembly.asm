; Static PI32v2 decoding; offsets refer to extracted app.bin.
; This is disassembly evidence, not validated firmware emulation.

; copy_initial_data_to_ram
000062  01e00182  c4ff00000000      mov r4, #0x0
000068  01e00188  c1ffe486e201      mov r1, #0x1e286e4
00006e  01e0018e  c2fffc430000      mov r2, #0x43fc
000074  01e00194  a2a2              lsr r2, r2, 0x2
000076  01e00196  1203              rep 0x4, r2
000078  01e00198  1305              lw r3, [r1 ++= 4]
00007a  01e0019a  c305              sw r3, [r4 ++= 4]
00007c  01e0019c  f25c              jnz r2, 0x1e00196

; i2c_busy_wait
010e2e  01e10f4e  0482              goto 0x1e10f54
010e30  01e10f50  0000              nop 
010e32  01e10f52  f83f              add r0, #-0x1
010e34  01e10f54  f05d              jnz r0, 0x1e10f50
010e36  01e10f56  8000              rts 

; i2c_write_word
010fec  01e1110c  7604              push {rets,r6,r5,r4}
010fee  01e1110e  2416              mov r4, r2
010ff0  01e11110  1516              mov r5, r1
010ff2  01e11112  0616              mov r6, r0
010ff4  01e11114  bfea20ff          call 0x1e10f58
010ff8  01e11118  6016              mov r0, r6
010ffa  01e1111a  bfea4eff          call 0x1e10fba
010ffe  01e1111e  5194              call 0x1e11088
011000  01e11120  005e              jz r0, 0x1e1115e
011002  01e11122  5016              mov r0, r5
011004  01e11124  bfea49ff          call 0x1e10fba
011008  01e11128  518f              call 0x1e11088
01100a  01e1112a  005f              jz r0, 0x1e1116a
01100c  01e1112c  70e00044          rev8 r4, r4
011010  01e11130  c0b0              lsr r0, r4, 0x10
011012  01e11132  70e17f0c          and r0, r0, #0xffff00ff
011016  01e11136  bfea40ff          call 0x1e10fba
01101a  01e1113a  5186              call 0x1e11088
01101c  01e1113c  005c              jz r0, 0x1e11176
01101e  01e1113e  c0b8              lsr r0, r4, 0x18
011020  01e11140  bfea3bff          call 0x1e10fba
011024  01e11144  5181              call 0x1e11088
011026  01e11146  0416              mov r4, r0
011028  01e11148  bfea75ff          call 0x1e11036
01102c  01e1114c  b4e80010          if (r4 != #0x0) {
011030  01e11150  c0ff4010e201      mov r0, #0x1e21040
011036  01e11156  c0ff2010e201      mov r0, #0x1e21020
01103c  01e1115c  0491              goto 0x1e11180
01103e  01e1115e  bfea6aff          call 0x1e11036
011042  01e11162  c0ffc00fe201      mov r0, #0x1e20fc0
011048  01e11168  048b              goto 0x1e11180
01104a  01e1116a  bfea64ff          call 0x1e11036
01104e  01e1116e  c0ffe00fe201      mov r0, #0x1e20fe0
011054  01e11174  0485              goto 0x1e11180
011056  01e11176  bfea5eff          call 0x1e11036
01105a  01e1117a  c0ff0010e201      mov r0, #0x1e21000
011060  01e11180  3604              pop {rets, r6,r5,r4}
011062  01e11182  ffea48da          goto 0x1e0c616

; write_first_75
011368  01e11488  7504              push {rets,r5,r4}
01136a  01e1148a  c0fff0420000      mov r0, #0x42f0
011370  01e11490  0841              lb.z r0, [r0 + 0x1]
011372  01e11492  80f80f02          jne r0, #0x1, 0x1e114b4
011376  01e11496  4420              mov r4, #0x0
011378  01e11498  c5ffa427e201      mov r5, #0x1e227a4
01137e  01e1149e  5016              mov r0, r5
011380  01e114a0  dcee0014          lb.z r1, [++r0 = r4]
011384  01e114a4  0a61              lh.z r2, [r0 + 0x2]
011386  01e114a6  5020              mov r0, #0x40
011388  01e114a8  bfea30fe          call 0x1e1110c
01138c  01e114ac  c424              add r4, #0x4
01138e  01e114ae  a4f8f659          jne r4, #0x12c
011392  01e114b2  5504              pop {pc,r5,r4}
011394  01e114b4  4420              mov r4, #0x0
011396  01e114b6  c5ff24410000      mov r5, #0x4124
01139c  01e114bc  d8ed4005          lh.z r0, [r4 + r5]
0113a0  01e114c0  004a              jz r0, 0x1e114d6
0113a2  01e114c2  491d              add r1, r4, r5
0113a4  01e114c4  71f17f0c          and r1, r0, #0xffff00ff
0113a8  01e114c8  1a61              lh.z r2, [r1 + 0x2]
0113aa  01e114ca  5020              mov r0, #0x40
0113ac  01e114cc  bfea1efe          call 0x1e1110c
0113b0  01e114d0  c424              add r4, #0x4
0113b2  01e114d2  a4f8f359          jne r4, #0x12c
0113b6  01e114d6  5504              pop {pc,r5,r4}

; spi_initialization
01163c  01e1175c  7904              push {rets,r9,r8,r7,r6,r5,r4}
01163e  01e1175e  c0fff0420000      mov r0, #0x42f0
011644  01e11764  c9ff40730000      mov r9, #0x7340
01164a  01e1176a  10f13c9f          add r0, r9, 0x1f3c
01164e  01e1176e  0c41              lb.z r4, [r0 + 0x1]
011650  01e11770  4120              mov r1, #0x0
011652  01e11772  42e02410          movz r2, #0x1024
011656  01e11776  98ea1d08          call 0x21127b4
01165a  01e1177a  c0ffa04c0000      mov r0, #0x4ca0
011660  01e11780  4220              mov r2, #0x0
011662  01e11782  4320              mov r3, #0x0
011664  01e11784  50ec0120          sdw r2_r3, [r0 + 0x0]
011668  01e11788  4920              mov r1, #0x20
01166a  01e1178a  b4e80100          if (r4 != #0x1) {
01166e  01e1178e  5120              mov r1, #0x40
011670  01e11790  42f00008          movz r2, #0x800
011674  01e11794  8962              sh r1, [r0 + 0x4]
011676  01e11796  c1ff02000808      mov r1, #0x8080002
01167c  01e1179c  40f04c27          movz r0, #0x274c
011680  01e117a0  8160              sw r1, [r0 + 0x0]
011682  01e117a2  9018              add r0, r9
011684  01e117a4  4122              mov r1, #0x2
011686  01e117a6  0484              goto 0x1e117b0
011688  01e117a8  f93f              add r1, #-0x1
01168a  01e117aa  00f11208          add r0, r0, #0x812
01168e  01e117ae  8a60              sh r2, [r0 + 0x0]
011690  01e117b0  f15b              jnz r1, 0x1e117a8
011692  01e117b2  4621              mov r6, #0x1
011694  01e117b4  52ee9c66          sb r6, [r9 + 0x6c]
011698  01e117b8  4021              mov r0, #0x1
01169a  01e117ba  bfeabafe          call 0x1e11532
01169e  01e117be  4021              mov r0, #0x1
0116a0  01e117c0  4121              mov r1, #0x1
0116a2  01e117c2  518c              call 0x1e1171c
0116a4  01e117c4  c2ff9a57e101      mov r2, #0x1e1579a
0116aa  01e117ca  402f              mov r0, #0xf
0116ac  01e117cc  4123              mov r1, #0x3
0116ae  01e117ce  bfea7ed8          call 0x1e0c8ce
0116b2  01e117d2  50ee9900          lb.z r0, [r9 + 0x9]
0116b6  01e117d6  44e00808          movz r4, #0x808
0116ba  01e117da  401b              mul r0, r4
0116bc  01e117dc  c5ff484d0000      mov r5, #0x4d48
0116c2  01e117e2  091d              add r1, r0, r5
0116c4  01e117e4  4021              mov r0, #0x1
0116c6  01e117e6  4216              mov r2, r4
0116c8  01e117e8  518a              call 0x1e1173e
0116ca  01e117ea  4022              mov r0, #0x2
0116cc  01e117ec  bfeaa1fe          call 0x1e11532
0116d0  01e117f0  4022              mov r0, #0x2
0116d2  01e117f2  4121              mov r1, #0x1
0116d4  01e117f4  4193              call 0x1e1171c
0116d6  01e117f6  c2ffe457e101      mov r2, #0x1e157e4
0116dc  01e117fc  482c              mov r0, #0x2c
0116de  01e117fe  4123              mov r1, #0x3
0116e0  01e11800  bfea65d8          call 0x1e0c8ce
0116e4  01e11804  50ee9a00          lb.z r0, [r9 + 0xa]
0116e8  01e11808  401b              mul r0, r4
0116ea  01e1180a  5018              add r0, r5
0116ec  01e1180c  11e11000          add r1, r0, 0x1010
0116f0  01e11810  4022              mov r0, #0x2
0116f2  01e11812  4216              mov r2, r4
0116f4  01e11814  4194              call 0x1e1173e
0116f6  01e11816  00e15c90          add r0, r9, #0x5c
0116fa  01e1181a  50ee0880          lb.z r8, [r0 + 0x8]
0116fe  01e1181e  14f1ec93          add r4, r9, 0x13ec
011702  01e11822  0f44              lb.z r7, [r0 + 0x4]
011704  01e11824  42f05003          movz r2, #0x350
011708  01e11828  0d40              lb.z r5, [r0 + 0x0]
01170a  01e1182a  4120              mov r1, #0x0
01170c  01e1182c  4016              mov r0, r4
01170e  01e1182e  98eac107          call 0x21127b4
011712  01e11832  c0ffcdcc4c3e      mov r0, #0x3e4ccccd
011718  01e11838  c1ff9a99993f      mov r1, #0x3f99999a
01171e  01e1183e  0485              goto 0x1e1184a
011720  01e11840  50ec4d03          sdw r0_r1, [r4 + 0x3c]
011724  01e11844  d8ec456d          sw r6, [r4++=0xd4]
011728  01e11848  c621              add r6, #0x1
01172a  01e1184a  86f8f90b          jne r6, #0x5, 0x1e11840
01172e  01e1184e  41e098fe          movz r1, #0xfe98
011732  01e11852  25ea0100          if ((r5 & #0x1) != 0) {
011736  01e11856  4120              mov r1, #0x0
011738  01e11858  00e14490          add r0, r9, #0x44
01173c  01e1185c  41f06801          movz r1, #0x168
011740  01e11860  8961              sh r1, [r0 + 0x2]
011742  01e11862  27ea0100          if ((r7 & #0x1) != 0) {
011746  01e11866  4120              mov r1, #0x0
011748  01e11868  41f02003          movz r1, #0x320
01174c  01e1186c  8960              sh r1, [r0 + 0x0]
01174e  01e1186e  28ea0100          if ((r8 & #0x1) != 0) {
011752  01e11872  4120              mov r1, #0x0
011754  01e11874  8962              sh r1, [r0 + 0x4]
011756  01e11876  5904              pop {pc,r9,r8,r7,r6,r5,r4}

; write_last_5
011758  01e11878  7604              push {rets,r6,r5,r4}
01175a  01e1187a  4823              mov r0, #0x23
01175c  01e1187c  bfea9e74          call 0x1e001bc
011760  01e11880  0047              jz r0, 0x1e11890
011762  01e11882  c1ff00021e00      mov r1, #0x1e0200
011768  01e11888  1260              lw r2, [r1 + 0x0]
01176a  01e1188a  00ef0800          or [r0+0x0], #0x8
01176e  01e1188e  1060              lw r0, [r1 + 0x0]
011770  01e11890  40e0e803          movz r0, #0x3e8
011774  01e11894  bfea5bfb          call 0x1e10f4e
011778  01e11898  c0fff0420000      mov r0, #0x42f0
01177e  01e1189e  0841              lb.z r0, [r0 + 0x1]
011780  01e118a0  80f81304          jne r0, #0x2, 0x1e118ca
011784  01e118a4  542b              mov r4, #0x4b
011786  01e118a6  c5ff24410000      mov r5, #0x4124
01178c  01e118ac  0488              goto 0x1e118be
01178e  01e118ae  5118              add r1, r5
011790  01e118b0  71f17f0c          and r1, r0, #0xffff00ff
011794  01e118b4  1a61              lh.z r2, [r1 + 0x2]
011796  01e118b6  5020              mov r0, #0x40
011798  01e118b8  bfea28fc          call 0x1e1110c
01179c  01e118bc  c421              add r4, #0x1
01179e  01e118be  c017              uxth r0, r4
0117a0  01e118c0  01a2              lsl r1, r0, 0x2
0117a2  01e118c2  d8ed5001          lh.z r0, [r5 + r1]
0117a6  01e118c6  f053              jnz r0, 0x1e118ae
0117a8  01e118c8  5604              pop {pc,r6,r5,r4}
0117aa  01e118ca  142c              movs r4, #-0x14
0117ac  01e118cc  c5ffa427e201      mov r5, #0x1e227a4
0117b2  01e118d2  46e04001          movz r6, #0x140
0117b6  01e118d6  0489              goto 0x1e118ea
0117b8  01e118d8  481d              add r0, r4, r5
0117ba  01e118da  d8ee0016          lb.z r1, [r0 + r6]
0117be  01e118de  51ed0224          lh.z r2, [r0 + 0x142]
0117c2  01e118e2  5020              mov r0, #0x40
0117c4  01e118e4  bfea12fc          call 0x1e1110c
0117c8  01e118e8  c424              add r4, #0x4
0117ca  01e118ea  f456              jnz r4, 0x1e118d8
0117cc  01e118ec  5604              pop {pc,r6,r5,r4}

; radar_init_call_order
01c620  01e1c740  bfeae1c6          call 0x1e15506
01c624  01e1c744  bfeaa0a6          call 0x1e11488
01c628  01e1c748  bfeaddc6          call 0x1e15506
01c62c  01e1c74c  bfea06a8          call 0x1e1175c
01c630  01e1c750  bfead9c6          call 0x1e15506
01c634  01e1c754  bfea90a8          call 0x1e11878
01c638  01e1c758  bfead5c6          call 0x1e15506
