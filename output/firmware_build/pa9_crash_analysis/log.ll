; ModuleID = 'output/firmware_build/pa9_crash_analysis/log.c.o'
source_filename = "/jks/workspace/audio_build_release/SDK/lib/system/printf/log.c"
target datalayout = "e-m:e-p:32:32-i1:32-i64:32:32-f64:32:32-n8:16:32-a:0:32"
target triple = "pi32v2"

%struct.logbuf = type { i16, i16, [0 x i8] }
%struct.xSTATIC_QUEUE = type { [3 x i8*], %union.anon, [2 x %struct.xSTATIC_LIST], [3 x i32], [2 x i8], i8, i32, i8 }
%union.anon = type { i8* }
%struct.xSTATIC_LIST = type { i32, i8*, %struct.xSTATIC_MINI_LIST_ITEM }
%struct.xSTATIC_MINI_LIST_ITEM = type { i32, [2 x i8*] }
%struct.lbuff_head = type { i32, %struct.list_head, %struct.list_head, %struct.__spinlock, i8, i16, i32, i32, i8*, i32 }
%struct.list_head = type { %struct.list_head*, %struct.list_head* }
%struct.__spinlock = type { i32 }

@lb_send = internal unnamed_addr global %struct.logbuf* null, align 4, !dbg !0
@send_cnt = internal unnamed_addr global i32 0, align 4, !dbg !106
@jiffies_offset = internal unnamed_addr global i32 0, align 4, !dbg !108
@jiffies_base = internal unnamed_addr global i32 0, align 4, !dbg !110
@.str = private unnamed_addr constant [22 x i8] c"[%02d:%02d:%02d.%03d]\00", align 1
@config_printf_time = external local_unnamed_addr constant i32, align 4
@prev_putbyte = internal unnamed_addr global i8 0, align 1, !dbg !123
@log_mutex = internal global %struct.xSTATIC_QUEUE zeroinitializer, align 4, !dbg !55
@log_bufs = internal unnamed_addr global %struct.lbuff_head* null, align 4, !dbg !53
@log_output_busy = internal unnamed_addr global i1 false, align 4
@g_level = internal unnamed_addr global i8 0, align 1, !dbg !129
@log_str = internal unnamed_addr constant [2 x i8*] [i8* getelementptr inbounds ([9 x i8], [9 x i8]* @.str.1, i32 0, i32 0), i8* getelementptr inbounds ([10 x i8], [10 x i8]* @.str.2, i32 0, i32 0)], align 4, !dbg !131
@.str.1 = private unnamed_addr constant [9 x i8] c"(warn): \00", align 1
@.str.2 = private unnamed_addr constant [10 x i8] c"(error): \00", align 1
@cur_time.3 = internal unnamed_addr global i8 0, align 2
@cur_time.4 = internal unnamed_addr global i8 0, align 2
@cur_time.5 = internal unnamed_addr global i8 0, align 2

; Function Attrs: minsize nounwind optsize
define void @log_flush() local_unnamed_addr #0 section ".system.printf.text" !dbg !141 {
  %1 = load %struct.logbuf*, %struct.logbuf** @lb_send, align 4, !dbg !149, !tbaa !150
  %2 = icmp eq %struct.logbuf* %1, null, !dbg !149
  br i1 %2, label %18, label %3, !dbg !154

; <label>:3:                                      ; preds = %0
  %4 = load i32, i32* @send_cnt, align 4, !dbg !155, !tbaa !156
  tail call void @llvm.dbg.value(metadata i32 %4, i64 0, metadata !145, metadata !158), !dbg !159
  br label %5, !dbg !160

; <label>:5:                                      ; preds = %12, %3
  %6 = phi %struct.logbuf* [ %1, %3 ], [ %16, %12 ], !dbg !161
  %7 = phi i32 [ %4, %3 ], [ %15, %12 ]
  tail call void @llvm.dbg.value(metadata i32 %7, i64 0, metadata !145, metadata !158), !dbg !159
  %8 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %6, i32 0, i32 0, !dbg !164
  %9 = load volatile i16, i16* %8, align 2, !dbg !164, !tbaa !166
  %10 = zext i16 %9 to i32, !dbg !169
  %11 = icmp slt i32 %7, %10, !dbg !170
  br i1 %11, label %12, label %17, !dbg !171

; <label>:12:                                     ; preds = %5
  %13 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %6, i32 0, i32 2, i32 %7, !dbg !173
  %14 = load volatile i8, i8* %13, align 1, !dbg !173, !tbaa !175
  tail call void @putbyte(i8 signext %14) #7, !dbg !176
  %15 = add nsw i32 %7, 1, !dbg !177
  tail call void @llvm.dbg.value(metadata i32 %15, i64 0, metadata !145, metadata !158), !dbg !159
  %16 = load %struct.logbuf*, %struct.logbuf** @lb_send, align 4, !tbaa !150
  br label %5, !dbg !179, !llvm.loop !180

; <label>:17:                                     ; preds = %5
  br label %18, !dbg !183

; <label>:18:                                     ; preds = %17, %0
  tail call fastcc void @logbuf_output() #8, !dbg !184
  ret void, !dbg !186
}

; Function Attrs: argmemonly nounwind
declare void @llvm.lifetime.start(i64, i8* nocapture) #1

; Function Attrs: nounwind readnone
declare void @llvm.dbg.declare(metadata, metadata, metadata) #2

; Function Attrs: minsize optsize
declare void @putbyte(i8 signext) local_unnamed_addr #3

; Function Attrs: argmemonly nounwind
declare void @llvm.lifetime.end(i64, i8* nocapture) #1

; Function Attrs: minsize nounwind optsize
define void @log_set_time_offset(i32) local_unnamed_addr #0 section ".system.printf.text" !dbg !187 {
  tail call void @llvm.dbg.value(metadata i32 %0, i64 0, metadata !191, metadata !158), !dbg !192
  store i32 %0, i32* @jiffies_offset, align 4, !dbg !193, !tbaa !156
  ret void, !dbg !194
}

; Function Attrs: minsize norecurse nounwind optsize readonly
define i32 @log_get_time_offset() local_unnamed_addr #4 section ".system.printf.text" !dbg !195 {
  %1 = load i32, i32* @jiffies_offset, align 4, !dbg !198, !tbaa !156
  ret i32 %1, !dbg !199
}

; Function Attrs: minsize nounwind optsize
define i32 @log_print_time_to_buf(i8* nocapture) local_unnamed_addr #0 section ".system.printf.text" !dbg !200 {
  tail call void @llvm.dbg.value(metadata i8* %0, i64 0, metadata !205, metadata !158), !dbg !208
  %2 = tail call i32 bitcast (i32 (...)* @jiffies_msec to i32 ()*)() #7, !dbg !209
  tail call void @llvm.dbg.value(metadata i32 %2, i64 0, metadata !206, metadata !158), !dbg !210
  %3 = load i32, i32* @jiffies_offset, align 4, !dbg !211, !tbaa !156
  %4 = add i32 %3, %2, !dbg !212
  %5 = load i32, i32* @jiffies_base, align 4, !dbg !213, !tbaa !156
  %6 = sub i32 %4, %5, !dbg !214
  tail call void @llvm.dbg.value(metadata i32 %6, i64 0, metadata !207, metadata !158), !dbg !215
  %7 = icmp slt i32 %6, 0, !dbg !216
  br i1 %7, label %8, label %9, !dbg !218

; <label>:8:                                      ; preds = %1
  store i32 0, i32* @jiffies_base, align 4, !dbg !219, !tbaa !156
  store i8 0, i8* @cur_time.5, align 2, !dbg !221, !tbaa !222
  store i8 0, i8* @cur_time.4, align 2, !dbg !224, !tbaa !225
  store i8 0, i8* @cur_time.3, align 2, !dbg !226, !tbaa !227
  tail call void @llvm.dbg.value(metadata i32 %4, i64 0, metadata !207, metadata !158), !dbg !215
  br label %9, !dbg !228

; <label>:9:                                      ; preds = %8, %1
  %10 = phi i32 [ %4, %8 ], [ %6, %1 ]
  tail call void @llvm.dbg.value(metadata i32 %10, i64 0, metadata !207, metadata !158), !dbg !215
  %11 = icmp sgt i32 %10, 999, !dbg !229
  %12 = load i8, i8* @cur_time.5, align 2, !tbaa !222
  br i1 %11, label %13, label %36, !dbg !231, !llvm.loop !232

; <label>:13:                                     ; preds = %9
  br label %14, !dbg !236

; <label>:14:                                     ; preds = %29, %13
  %15 = phi i8 [ %30, %29 ], [ %12, %13 ], !dbg !238
  %16 = phi i32 [ %17, %29 ], [ %10, %13 ]
  tail call void @llvm.dbg.value(metadata i32 %16, i64 0, metadata !207, metadata !158), !dbg !215
  %17 = add nsw i32 %16, -1000, !dbg !240
  tail call void @llvm.dbg.value(metadata i32 %17, i64 0, metadata !207, metadata !158), !dbg !215
  %18 = add i8 %15, 1, !dbg !242
  %19 = icmp ugt i8 %18, 59, !dbg !244
  br i1 %19, label %20, label %29, !dbg !245

; <label>:20:                                     ; preds = %14
  %21 = load i8, i8* @cur_time.4, align 2, !dbg !246, !tbaa !225
  %22 = add i8 %21, 1, !dbg !246
  store i8 %22, i8* @cur_time.4, align 2, !dbg !246, !tbaa !225
  %23 = icmp ugt i8 %22, 59, !dbg !249
  br i1 %23, label %24, label %29, !dbg !250

; <label>:24:                                     ; preds = %20
  store i8 0, i8* @cur_time.4, align 2, !dbg !251, !tbaa !225
  %25 = load i8, i8* @cur_time.3, align 2, !dbg !253, !tbaa !227
  %26 = add i8 %25, 1, !dbg !253
  %27 = icmp ugt i8 %26, 98, !dbg !255
  %28 = select i1 %27, i8 0, i8 %26, !dbg !256
  store i8 %28, i8* @cur_time.3, align 2, !dbg !257
  br label %29, !dbg !259

; <label>:29:                                     ; preds = %24, %20, %14
  %30 = phi i8 [ %18, %14 ], [ 0, %24 ], [ 0, %20 ]
  %31 = icmp sgt i32 %17, 999, !dbg !260
  br i1 %31, label %14, label %32, !dbg !262, !llvm.loop !232

; <label>:32:                                     ; preds = %29
  store i8 %30, i8* @cur_time.5, align 2, !dbg !264, !tbaa !222
  %33 = sub i32 1000, %16
  %34 = add i32 %33, %2, !dbg !266
  %35 = add i32 %34, %3, !dbg !267
  store i32 %35, i32* @jiffies_base, align 4, !dbg !268, !tbaa !156
  br label %36, !dbg !269

; <label>:36:                                     ; preds = %32, %9
  %37 = phi i8 [ %30, %32 ], [ %12, %9 ], !dbg !270
  %38 = phi i32 [ %17, %32 ], [ %10, %9 ]
  tail call void @llvm.dbg.value(metadata i32 %38, i64 0, metadata !207, metadata !158), !dbg !215
  %39 = load i8, i8* @cur_time.3, align 2, !dbg !271, !tbaa !227
  %40 = zext i8 %39 to i32, !dbg !272
  %41 = load i8, i8* @cur_time.4, align 2, !dbg !273, !tbaa !225
  %42 = zext i8 %41 to i32, !dbg !274
  %43 = zext i8 %37 to i32, !dbg !275
  %44 = tail call i32 (i8*, i8*, ...) @sprintf(i8* %0, i8* getelementptr inbounds ([22 x i8], [22 x i8]* @.str, i32 0, i32 0), i32 %40, i32 %42, i32 %43, i32 %38) #8, !dbg !276
  ret i32 14, !dbg !277
}

; Function Attrs: minsize optsize
declare i32 @jiffies_msec(...) local_unnamed_addr #3

; Function Attrs: minsize nounwind optsize
declare i32 @sprintf(i8* nocapture, i8* nocapture readonly, ...) local_unnamed_addr #5

; Function Attrs: minsize nounwind optsize
define void @log_print_time() local_unnamed_addr #0 section ".system.printf.text" !dbg !278 {
  %1 = alloca [24 x i8], align 1
  %2 = getelementptr inbounds [24 x i8], [24 x i8]* %1, i32 0, i32 0, !dbg !286
  call void @llvm.lifetime.start(i64 24, i8* nonnull %2) #6, !dbg !286
  tail call void @llvm.dbg.declare(metadata [24 x i8]* %1, metadata !280, metadata !158), !dbg !287
  %3 = load i32, i32* @config_printf_time, align 4, !dbg !288, !tbaa !156
  %4 = icmp eq i32 %3, 0, !dbg !288
  br i1 %4, label %5, label %9, !dbg !290

; <label>:5:                                      ; preds = %0
  %6 = load i8, i8* @prev_putbyte, align 1, !dbg !291, !tbaa !175
  %7 = icmp eq i8 %6, 10, !dbg !294
  br i1 %7, label %23, label %8, !dbg !295

; <label>:8:                                      ; preds = %5
  tail call void @log_putbyte(i8 signext 10) #8, !dbg !296
  br label %23, !dbg !298

; <label>:9:                                      ; preds = %0
  %10 = call i32 @log_print_time_to_buf(i8* nonnull %2) #8, !dbg !299
  %11 = load i8, i8* @prev_putbyte, align 1, !dbg !300, !tbaa !175
  %12 = icmp eq i8 %11, 10, !dbg !302
  br i1 %12, label %14, label %13, !dbg !303

; <label>:13:                                     ; preds = %9
  tail call void @log_putbyte(i8 signext 10) #8, !dbg !304
  br label %14, !dbg !306

; <label>:14:                                     ; preds = %13, %9
  br label %15, !dbg !307

; <label>:15:                                     ; preds = %18, %14
  %16 = phi i32 [ %21, %18 ], [ 0, %14 ]
  tail call void @llvm.dbg.value(metadata i32 %16, i64 0, metadata !284, metadata !158), !dbg !307
  %17 = icmp eq i32 %16, 14, !dbg !308
  br i1 %17, label %22, label %18, !dbg !311

; <label>:18:                                     ; preds = %15
  %19 = getelementptr inbounds [24 x i8], [24 x i8]* %1, i32 0, i32 %16, !dbg !313
  %20 = load i8, i8* %19, align 1, !dbg !313, !tbaa !175
  tail call void @log_putbyte(i8 signext %20) #8, !dbg !315
  %21 = add nuw nsw i32 %16, 1, !dbg !316
  tail call void @llvm.dbg.value(metadata i32 %21, i64 0, metadata !284, metadata !158), !dbg !307
  br label %15, !dbg !318, !llvm.loop !319

; <label>:22:                                     ; preds = %15
  br label %23, !dbg !322

; <label>:23:                                     ; preds = %22, %8, %5
  call void @llvm.lifetime.end(i64 24, i8* nonnull %2) #6, !dbg !322
  ret void, !dbg !323
}

; Function Attrs: minsize nounwind optsize
define weak void @log_putbyte(i8 signext) local_unnamed_addr #0 section ".system.printf.text" !dbg !325 {
  tail call void @llvm.dbg.value(metadata i8 %0, i64 0, metadata !329, metadata !158), !dbg !330
  tail call void @putbyte(i8 signext %0) #7, !dbg !331
  store i8 %0, i8* @prev_putbyte, align 1, !dbg !332, !tbaa !175
  ret void, !dbg !333
}

; Function Attrs: minsize nounwind optsize
define i32 @log_output_lock() local_unnamed_addr #0 section ".system.printf.text" !dbg !334 {
  %1 = tail call i32 @os_mutex_pend(%struct.xSTATIC_QUEUE* nonnull @log_mutex, i32 0) #7, !dbg !337
  tail call void @llvm.dbg.value(metadata i32 %1, i64 0, metadata !336, metadata !158), !dbg !338
  %2 = load %struct.lbuff_head*, %struct.lbuff_head** @log_bufs, align 4, !dbg !339, !tbaa !150
  %3 = icmp eq %struct.lbuff_head* %2, null, !dbg !341
  br i1 %3, label %11, label %4, !dbg !342

; <label>:4:                                      ; preds = %0
  tail call void @llvm.dbg.value(metadata %struct.__spinlock* null, i64 0, metadata !343, metadata !158) #6, !dbg !349
  tail call void bitcast (void (...)* @local_irq_disable to void ()*)() #7, !dbg !351
  %5 = load i1, i1* @log_output_busy, align 4
  br i1 %5, label %6, label %10, !dbg !352

; <label>:6:                                      ; preds = %4
  %7 = icmp eq i32 %1, 0, !dbg !353
  tail call void @llvm.dbg.value(metadata %struct.__spinlock* null, i64 0, metadata !357, metadata !158) #6, !dbg !360
  tail call void bitcast (void (...)* @local_irq_enable to void ()*)() #7, !dbg !363
  br i1 %7, label %8, label %11, !dbg !364

; <label>:8:                                      ; preds = %6
  %9 = tail call i32 @os_mutex_post(%struct.xSTATIC_QUEUE* nonnull @log_mutex) #7, !dbg !365
  br label %11, !dbg !366

; <label>:10:                                     ; preds = %4
  store i1 true, i1* @log_output_busy, align 4
  tail call void @llvm.dbg.value(metadata %struct.__spinlock* null, i64 0, metadata !357, metadata !158) #6, !dbg !367
  tail call void bitcast (void (...)* @local_irq_enable to void ()*)() #7, !dbg !369
  br label %11, !dbg !371

; <label>:11:                                     ; preds = %10, %8, %6, %0
  %12 = phi i32 [ 0, %10 ], [ 0, %0 ], [ -16, %6 ], [ -16, %8 ]
  ret i32 %12, !dbg !372
}

; Function Attrs: minsize optsize
declare i32 @os_mutex_pend(%struct.xSTATIC_QUEUE*, i32) local_unnamed_addr #3

; Function Attrs: minsize optsize
declare i32 @os_mutex_post(%struct.xSTATIC_QUEUE*) local_unnamed_addr #3

; Function Attrs: minsize nounwind optsize
define void @log_output_unlock() local_unnamed_addr #0 section ".system.printf.text" !dbg !373 {
  tail call fastcc void @logbuf_output() #8, !dbg !374
  store i1 false, i1* @log_output_busy, align 4
  %1 = tail call i32 @os_mutex_post(%struct.xSTATIC_QUEUE* nonnull @log_mutex) #7, !dbg !375
  ret void, !dbg !376
}

; Function Attrs: minsize nounwind optsize
define weak void @log_print(i32, i8*, i8*, ...) local_unnamed_addr #0 section ".system.printf.text" !dbg !377 {
  %4 = alloca i8*, align 4
  %5 = alloca i8*, align 4
  tail call void @llvm.dbg.value(metadata i32 %0, i64 0, metadata !381, metadata !158), !dbg !392
  tail call void @llvm.dbg.value(metadata i8* %1, i64 0, metadata !382, metadata !158), !dbg !393
  tail call void @llvm.dbg.value(metadata i8* %2, i64 0, metadata !383, metadata !158), !dbg !394
  %6 = bitcast i8** %4 to i8*, !dbg !395
  call void @llvm.lifetime.start(i64 4, i8* nonnull %6) #6, !dbg !395
  %7 = bitcast i8** %5 to i8*, !dbg !396
  call void @llvm.lifetime.start(i64 4, i8* nonnull %7) #6, !dbg !396
  tail call void @llvm.dbg.value(metadata i32 0, i64 0, metadata !389, metadata !158), !dbg !397
  %8 = load i8, i8* @g_level, align 1, !dbg !398, !tbaa !175
  %9 = sext i8 %8 to i32, !dbg !398
  %10 = icmp sgt i32 %9, %0, !dbg !400
  br i1 %10, label %105, label %11, !dbg !401

; <label>:11:                                     ; preds = %3
  call void @llvm.va_start(i8* nonnull %7), !dbg !402
  %12 = call i32 @log_output_lock() #8, !dbg !403
  %13 = icmp eq i32 %12, 0, !dbg !405
  br i1 %13, label %14, label %15, !dbg !406

; <label>:14:                                     ; preds = %11
  br label %71, !dbg !394

; <label>:15:                                     ; preds = %11
  %16 = call %struct.logbuf* @log_output_start(i32 256) #8, !dbg !407
  call void @llvm.dbg.value(metadata %struct.logbuf* %16, i64 0, metadata !390, metadata !158), !dbg !409
  %17 = icmp eq %struct.logbuf* %16, null, !dbg !410
  br i1 %17, label %105, label %18, !dbg !412

; <label>:18:                                     ; preds = %15
  br label %19, !dbg !413

; <label>:19:                                     ; preds = %23, %18
  %20 = phi i32 [ %25, %23 ], [ 0, %18 ]
  %21 = phi i8* [ %24, %23 ], [ %2, %18 ]
  call void @llvm.dbg.value(metadata i8* %21, i64 0, metadata !383, metadata !158), !dbg !394
  call void @llvm.dbg.value(metadata i32 %20, i64 0, metadata !389, metadata !158), !dbg !397
  %22 = load i8, i8* %21, align 1, !dbg !415, !tbaa !175
  switch i8 %22, label %29 [
    i8 13, label %23
    i8 10, label %23
    i8 0, label %26
  ], !dbg !417

; <label>:23:                                     ; preds = %19, %19
  call void @log_putchar(%struct.logbuf* nonnull %16, i8 signext %22) #8, !dbg !418
  %24 = getelementptr inbounds i8, i8* %21, i32 1, !dbg !420
  call void @llvm.dbg.value(metadata i8* %24, i64 0, metadata !383, metadata !158), !dbg !394
  %25 = add nuw nsw i32 %20, 1, !dbg !421
  call void @llvm.dbg.value(metadata i32 %25, i64 0, metadata !389, metadata !158), !dbg !397
  br label %19, !dbg !422, !llvm.loop !423

; <label>:26:                                     ; preds = %19
  %27 = bitcast %struct.logbuf* %16 to i8*, !dbg !426
  %28 = call i32 @lbuf_free(i8* %27) #7, !dbg !429
  br label %105, !dbg !430

; <label>:29:                                     ; preds = %19
  %30 = icmp sgt i32 %0, 2, !dbg !431
  br i1 %30, label %31, label %48, !dbg !433

; <label>:31:                                     ; preds = %29
  br label %32, !dbg !397

; <label>:32:                                     ; preds = %35, %31
  %33 = phi i32 [ %36, %35 ], [ %20, %31 ]
  call void @llvm.dbg.value(metadata i32 %33, i64 0, metadata !389, metadata !158), !dbg !397
  call void @llvm.dbg.value(metadata i32 %36, i64 0, metadata !389, metadata !158), !dbg !397
  %34 = icmp slt i32 %33, 1, !dbg !434
  br i1 %34, label %35, label %37, !dbg !437

; <label>:35:                                     ; preds = %32
  %36 = add nsw i32 %33, 1, !dbg !438
  call void @log_putchar(%struct.logbuf* nonnull %16, i8 signext 10) #8, !dbg !439
  br label %32, !dbg !437, !llvm.loop !441

; <label>:37:                                     ; preds = %32
  %38 = add nsw i32 %0, -3, !dbg !444
  %39 = getelementptr inbounds [2 x i8*], [2 x i8*]* @log_str, i32 0, i32 %38, !dbg !445
  %40 = load i8*, i8** %39, align 4, !dbg !445, !tbaa !150
  call void @llvm.dbg.value(metadata i8* %40, i64 0, metadata !391, metadata !158), !dbg !446
  br label %41, !dbg !447

; <label>:41:                                     ; preds = %45, %37
  %42 = phi i8* [ %40, %37 ], [ %46, %45 ]
  call void @llvm.dbg.value(metadata i8* %42, i64 0, metadata !391, metadata !158), !dbg !446
  %43 = load i8, i8* %42, align 1, !dbg !448, !tbaa !175
  %44 = icmp eq i8 %43, 0, !dbg !449
  br i1 %44, label %47, label %45, !dbg !450

; <label>:45:                                     ; preds = %41
  call void @log_putchar(%struct.logbuf* nonnull %16, i8 signext %43) #8, !dbg !451
  %46 = getelementptr inbounds i8, i8* %42, i32 1, !dbg !453
  call void @llvm.dbg.value(metadata i8* %46, i64 0, metadata !391, metadata !158), !dbg !446
  br label %41, !dbg !454, !llvm.loop !456

; <label>:47:                                     ; preds = %41
  br label %48, !dbg !458

; <label>:48:                                     ; preds = %47, %29
  %49 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %16, i32 0, i32 0, !dbg !459
  %50 = load i16, i16* %49, align 2, !dbg !459, !tbaa !166
  %51 = zext i16 %50 to i32, !dbg !460
  %52 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %16, i32 0, i32 2, i32 %51, !dbg !460
  call void @llvm.dbg.value(metadata i8* %52, i64 0, metadata !384, metadata !158), !dbg !461
  store i8* %52, i8** %4, align 4, !dbg !462, !tbaa !150
  %53 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %16, i32 0, i32 2, i32 0, !dbg !463
  %54 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %16, i32 0, i32 1, !dbg !464
  %55 = load i16, i16* %54, align 2, !dbg !464, !tbaa !465
  %56 = zext i16 %55 to i32, !dbg !466
  %57 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %16, i32 0, i32 2, i32 %56, !dbg !467
  %58 = load i8*, i8** %5, align 4, !dbg !468, !tbaa !150
  call void @llvm.dbg.value(metadata i8* %58, i64 0, metadata !385, metadata !158), !dbg !469
  call void @llvm.dbg.value(metadata i8** %4, i64 0, metadata !384, metadata !470), !dbg !461
  %59 = call i32 @print(i8** nonnull %4, i8* %57, i8* %21, i8* %58) #7, !dbg !471
  br i1 %30, label %60, label %65, !dbg !472

; <label>:60:                                     ; preds = %48
  %61 = load i8*, i8** %4, align 4, !dbg !473, !tbaa !150
  call void @llvm.dbg.value(metadata i8* %61, i64 0, metadata !384, metadata !158), !dbg !461
  %62 = getelementptr inbounds i8, i8* %61, i32 1, !dbg !473
  call void @llvm.dbg.value(metadata i8* %62, i64 0, metadata !384, metadata !158), !dbg !461
  store i8* %62, i8** %4, align 4, !dbg !473, !tbaa !150
  store i8 13, i8* %61, align 1, !dbg !476, !tbaa !175
  %63 = load i8*, i8** %4, align 4, !dbg !477, !tbaa !150
  call void @llvm.dbg.value(metadata i8* %63, i64 0, metadata !384, metadata !158), !dbg !461
  %64 = getelementptr inbounds i8, i8* %63, i32 1, !dbg !477
  call void @llvm.dbg.value(metadata i8* %64, i64 0, metadata !384, metadata !158), !dbg !461
  store i8* %64, i8** %4, align 4, !dbg !477, !tbaa !150
  store i8 10, i8* %63, align 1, !dbg !478, !tbaa !175
  br label %65, !dbg !479

; <label>:65:                                     ; preds = %60, %48
  %66 = bitcast i8** %4 to i32*, !dbg !480
  %67 = load i32, i32* %66, align 4, !dbg !480, !tbaa !150
  %68 = ptrtoint i8* %53 to i32, !dbg !481
  %69 = sub i32 %67, %68, !dbg !481
  %70 = trunc i32 %69 to i16, !dbg !480
  store i16 %70, i16* %49, align 2, !dbg !482, !tbaa !166
  call void @log_output_end(%struct.logbuf* nonnull %16) #8, !dbg !483
  br label %104, !dbg !484

; <label>:71:                                     ; preds = %75, %14
  %72 = phi i32 [ %77, %75 ], [ 0, %14 ]
  %73 = phi i8* [ %76, %75 ], [ %2, %14 ]
  call void @llvm.dbg.value(metadata i8* %73, i64 0, metadata !383, metadata !158), !dbg !394
  call void @llvm.dbg.value(metadata i32 %72, i64 0, metadata !389, metadata !158), !dbg !397
  %74 = load i8, i8* %73, align 1, !dbg !485, !tbaa !175
  switch i8 %74, label %78 [
    i8 13, label %75
    i8 10, label %75
    i8 0, label %102
  ], !dbg !488

; <label>:75:                                     ; preds = %71, %71
  call void @log_putbyte(i8 signext %74) #8, !dbg !490
  %76 = getelementptr inbounds i8, i8* %73, i32 1, !dbg !492
  call void @llvm.dbg.value(metadata i8* %76, i64 0, metadata !383, metadata !158), !dbg !394
  %77 = add nuw nsw i32 %72, 1, !dbg !493
  call void @llvm.dbg.value(metadata i32 %77, i64 0, metadata !389, metadata !158), !dbg !397
  br label %71, !dbg !494, !llvm.loop !495

; <label>:78:                                     ; preds = %71
  %79 = icmp sgt i32 %0, 2, !dbg !498
  br i1 %79, label %80, label %96, !dbg !502

; <label>:80:                                     ; preds = %78
  br label %81, !dbg !503

; <label>:81:                                     ; preds = %84, %80
  %82 = phi i32 [ %85, %84 ], [ %72, %80 ]
  call void @llvm.dbg.value(metadata i32 %82, i64 0, metadata !389, metadata !158), !dbg !397
  call void @llvm.dbg.value(metadata i32 %85, i64 0, metadata !389, metadata !158), !dbg !397
  %83 = icmp slt i32 %82, 1, !dbg !504
  br i1 %83, label %84, label %86, !dbg !507

; <label>:84:                                     ; preds = %81
  %85 = add nsw i32 %82, 1, !dbg !508
  call void @log_putbyte(i8 signext 10) #8, !dbg !509
  br label %81, !dbg !507, !llvm.loop !511

; <label>:86:                                     ; preds = %81
  call void @log_print_time() #8, !dbg !514
  %87 = add nsw i32 %0, -3, !dbg !515
  %88 = getelementptr inbounds [2 x i8*], [2 x i8*]* @log_str, i32 0, i32 %87, !dbg !518
  %89 = load i8*, i8** %88, align 4, !dbg !518, !tbaa !150
  call void @llvm.dbg.value(metadata i8* %89, i64 0, metadata !391, metadata !158), !dbg !446
  br label %90, !dbg !519

; <label>:90:                                     ; preds = %94, %86
  %91 = phi i8* [ %89, %86 ], [ %95, %94 ]
  call void @llvm.dbg.value(metadata i8* %91, i64 0, metadata !391, metadata !158), !dbg !446
  %92 = load i8, i8* %91, align 1, !dbg !520, !tbaa !175
  %93 = icmp eq i8 %92, 0, !dbg !522
  br i1 %93, label %99, label %94, !dbg !523

; <label>:94:                                     ; preds = %90
  call void @log_putbyte(i8 signext %92) #8, !dbg !524
  %95 = getelementptr inbounds i8, i8* %91, i32 1, !dbg !526
  call void @llvm.dbg.value(metadata i8* %95, i64 0, metadata !391, metadata !158), !dbg !446
  br label %90, !dbg !527, !llvm.loop !529

; <label>:96:                                     ; preds = %78
  call void @log_print_time() #8, !dbg !531
  %97 = load i8*, i8** %5, align 4, !dbg !533, !tbaa !150
  call void @llvm.dbg.value(metadata i8* %100, i64 0, metadata !385, metadata !158), !dbg !469
  %98 = call i32 @print(i8** null, i8* null, i8* %73, i8* %97) #7, !dbg !534
  br label %103, !dbg !535

; <label>:99:                                     ; preds = %90
  %100 = load i8*, i8** %5, align 4, !dbg !536, !tbaa !150
  call void @llvm.dbg.value(metadata i8* %100, i64 0, metadata !385, metadata !158), !dbg !469
  %101 = call i32 @print(i8** null, i8* null, i8* %73, i8* %100) #7, !dbg !537
  call void @log_putbyte(i8 signext 10) #8, !dbg !538
  br label %103, !dbg !541

; <label>:102:                                    ; preds = %71
  br label %103, !dbg !542

; <label>:103:                                    ; preds = %102, %99, %96
  call void @log_output_unlock() #8, !dbg !543
  br label %104

; <label>:104:                                    ; preds = %103, %65
  call void @llvm.va_end(i8* nonnull %7), !dbg !544
  br label %105, !dbg !545

; <label>:105:                                    ; preds = %104, %26, %15, %3
  call void @llvm.lifetime.end(i64 4, i8* nonnull %7) #6, !dbg !545
  call void @llvm.lifetime.end(i64 4, i8* nonnull %6) #6, !dbg !545
  ret void, !dbg !546
}

; Function Attrs: nounwind
declare void @llvm.va_start(i8*) #6

; Function Attrs: minsize nounwind optsize
define %struct.logbuf* @log_output_start(i32) local_unnamed_addr #0 section ".system.printf.text" !dbg !547 {
  tail call void @llvm.dbg.value(metadata i32 %0, i64 0, metadata !551, metadata !158), !dbg !553
  tail call void @llvm.dbg.value(metadata %struct.logbuf* null, i64 0, metadata !552, metadata !158), !dbg !554
  %2 = icmp eq i32 %0, 0, !dbg !555
  tail call void @llvm.dbg.value(metadata i32 252, i64 0, metadata !551, metadata !158), !dbg !553
  %3 = select i1 %2, i32 252, i32 %0, !dbg !557
  tail call void @llvm.dbg.value(metadata i32 %3, i64 0, metadata !551, metadata !158), !dbg !553
  %4 = load %struct.lbuff_head*, %struct.lbuff_head** @log_bufs, align 4, !dbg !558, !tbaa !150
  %5 = add i32 %3, 4, !dbg !559
  %6 = tail call i8* @lbuf_alloc(%struct.lbuff_head* %4, i32 %5) #7, !dbg !560
  %7 = bitcast i8* %6 to %struct.logbuf*, !dbg !561
  tail call void @llvm.dbg.value(metadata %struct.logbuf* %7, i64 0, metadata !552, metadata !158), !dbg !554
  %8 = icmp eq i8* %6, null, !dbg !562
  br i1 %8, label %14, label %9, !dbg !564

; <label>:9:                                      ; preds = %1
  %10 = bitcast i8* %6 to i16*, !dbg !565
  store i16 0, i16* %10, align 2, !dbg !567, !tbaa !166
  %11 = trunc i32 %3 to i16, !dbg !568
  %12 = getelementptr inbounds i8, i8* %6, i32 2, !dbg !569
  %13 = bitcast i8* %12 to i16*, !dbg !569
  store i16 %11, i16* %13, align 2, !dbg !570, !tbaa !465
  br label %14, !dbg !571

; <label>:14:                                     ; preds = %9, %1
  ret %struct.logbuf* %7, !dbg !572
}

; Function Attrs: minsize nounwind optsize
define void @log_putchar(%struct.logbuf* nocapture, i8 signext) local_unnamed_addr #0 section ".system.printf.text" !dbg !573 {
  tail call void @llvm.dbg.value(metadata %struct.logbuf* %0, i64 0, metadata !577, metadata !158), !dbg !579
  tail call void @llvm.dbg.value(metadata i8 %1, i64 0, metadata !578, metadata !158), !dbg !580
  %3 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %0, i32 0, i32 0, !dbg !581
  %4 = load i16, i16* %3, align 2, !dbg !581, !tbaa !166
  %5 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %0, i32 0, i32 1, !dbg !583
  %6 = load i16, i16* %5, align 2, !dbg !583, !tbaa !465
  %7 = icmp ult i16 %4, %6, !dbg !584
  br i1 %7, label %8, label %12, !dbg !585

; <label>:8:                                      ; preds = %2
  %9 = zext i16 %4 to i32, !dbg !586
  %10 = add i16 %4, 1, !dbg !588
  store i16 %10, i16* %3, align 2, !dbg !588, !tbaa !166
  %11 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %0, i32 0, i32 2, i32 %9, !dbg !590
  store i8 %1, i8* %11, align 1, !dbg !591, !tbaa !175
  br label %12, !dbg !592

; <label>:12:                                     ; preds = %8, %2
  ret void, !dbg !593
}

; Function Attrs: minsize optsize
declare i32 @lbuf_free(i8*) local_unnamed_addr #3

; Function Attrs: minsize optsize
declare i32 @print(i8**, i8*, i8*, i8*) local_unnamed_addr #3

; Function Attrs: minsize nounwind optsize
define void @log_output_end(%struct.logbuf*) local_unnamed_addr #0 section ".system.printf.text" !dbg !594 {
  tail call void @llvm.dbg.value(metadata %struct.logbuf* %0, i64 0, metadata !598, metadata !158), !dbg !599
  %2 = icmp eq %struct.logbuf* %0, null, !dbg !600
  br i1 %2, label %18, label %3, !dbg !602

; <label>:3:                                      ; preds = %1
  %4 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %0, i32 0, i32 0, !dbg !603
  %5 = load i16, i16* %4, align 2, !dbg !603, !tbaa !166
  %6 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %0, i32 0, i32 1, !dbg !606
  %7 = load i16, i16* %6, align 2, !dbg !606, !tbaa !465
  %8 = icmp ult i16 %5, %7, !dbg !607
  br i1 %8, label %11, label %9, !dbg !608

; <label>:9:                                      ; preds = %3
  %10 = bitcast %struct.logbuf* %0 to i8*, !dbg !609
  br label %16, !dbg !610

; <label>:11:                                     ; preds = %3
  %12 = zext i16 %5 to i32, !dbg !612
  %13 = bitcast %struct.logbuf* %0 to i8*, !dbg !614
  %14 = add nuw nsw i32 %12, 4, !dbg !616
  %15 = tail call i8* @lbuf_realloc(i8* %13, i32 %14) #7, !dbg !617
  br label %16, !dbg !618

; <label>:16:                                     ; preds = %11, %9
  %17 = phi i8* [ %10, %9 ], [ %13, %11 ], !dbg !619
  tail call void @lbuf_push(i8* %17, i8 zeroext 1) #7, !dbg !620
  br label %18, !dbg !621

; <label>:18:                                     ; preds = %16, %1
  %19 = tail call i32 @log_output_lock() #8, !dbg !622
  %20 = icmp eq i32 %19, 0, !dbg !624
  br i1 %20, label %21, label %22, !dbg !625

; <label>:21:                                     ; preds = %18
  tail call void @log_output_unlock() #8, !dbg !626
  br label %22, !dbg !628

; <label>:22:                                     ; preds = %21, %18
  ret void, !dbg !629
}

; Function Attrs: nounwind
declare void @llvm.va_end(i8*) #6

; Function Attrs: minsize nounwind optsize
define void @log_level(i32) local_unnamed_addr #0 section ".system.printf.text" !dbg !630 {
  tail call void @llvm.dbg.value(metadata i32 %0, i64 0, metadata !632, metadata !158), !dbg !633
  %2 = trunc i32 %0 to i8, !dbg !634
  store i8 %2, i8* @g_level, align 1, !dbg !635, !tbaa !175
  ret void, !dbg !636
}

; Function Attrs: minsize optsize
declare i8* @lbuf_alloc(%struct.lbuff_head*, i32) local_unnamed_addr #3

; Function Attrs: minsize optsize
declare i8* @lbuf_realloc(i8*, i32) local_unnamed_addr #3

; Function Attrs: minsize optsize
declare void @lbuf_push(i8*, i8 zeroext) local_unnamed_addr #3

; Function Attrs: minsize nounwind optsize
define void @log_put_u4hex(%struct.logbuf* nocapture, i8 zeroext) local_unnamed_addr #0 section ".system.printf.text" !dbg !637 {
  tail call void @llvm.dbg.value(metadata %struct.logbuf* %0, i64 0, metadata !641, metadata !158), !dbg !643
  tail call void @llvm.dbg.value(metadata i8 %1, i64 0, metadata !642, metadata !158), !dbg !644
  %3 = and i8 %1, 15, !dbg !645
  tail call void @llvm.dbg.value(metadata i8 %3, i64 0, metadata !642, metadata !158), !dbg !644
  %4 = icmp ugt i8 %3, 9, !dbg !646
  br i1 %4, label %5, label %7, !dbg !648

; <label>:5:                                      ; preds = %2
  %6 = add nuw nsw i8 %3, 55, !dbg !649
  tail call void @log_putchar(%struct.logbuf* %0, i8 signext %6) #8, !dbg !651
  br label %9, !dbg !652

; <label>:7:                                      ; preds = %2
  %8 = or i8 %3, 48, !dbg !653
  tail call void @log_putchar(%struct.logbuf* %0, i8 signext %8) #8, !dbg !655
  br label %9

; <label>:9:                                      ; preds = %7, %5
  ret void, !dbg !656
}

; Function Attrs: minsize nounwind optsize
define void @log_put_u8hex(%struct.logbuf* nocapture, i8 zeroext) local_unnamed_addr #0 section ".system.printf.text" !dbg !657 {
  tail call void @llvm.dbg.value(metadata %struct.logbuf* %0, i64 0, metadata !659, metadata !158), !dbg !661
  tail call void @llvm.dbg.value(metadata i8 %1, i64 0, metadata !660, metadata !158), !dbg !662
  %3 = lshr i8 %1, 4, !dbg !663
  tail call void @log_put_u4hex(%struct.logbuf* %0, i8 zeroext %3) #8, !dbg !664
  tail call void @log_put_u4hex(%struct.logbuf* %0, i8 zeroext %1) #8, !dbg !665
  tail call void @log_putchar(%struct.logbuf* %0, i8 signext 32) #8, !dbg !666
  ret void, !dbg !667
}

; Function Attrs: minsize nounwind optsize
define void @log_early_init(i32) local_unnamed_addr #0 section ".system.printf.text" !dbg !668 {
  tail call void @llvm.dbg.value(metadata i32 %0, i64 0, metadata !670, metadata !158), !dbg !671
  %2 = tail call i32 @os_mutex_create(%struct.xSTATIC_QUEUE* nonnull @log_mutex) #7, !dbg !672
  %3 = tail call i8* @malloc(i32 %0) #8, !dbg !673
  store i8* %3, i8** bitcast (%struct.lbuff_head** @log_bufs to i8**), align 4, !dbg !674, !tbaa !150
  %4 = tail call %struct.lbuff_head* @lbuf_init(i8* %3, i32 %0, i32 4, i32 0) #7, !dbg !675
  ret void, !dbg !676
}

; Function Attrs: minsize optsize
declare i32 @os_mutex_create(%struct.xSTATIC_QUEUE*) local_unnamed_addr #3

; Function Attrs: minsize nounwind optsize
declare noalias i8* @malloc(i32) local_unnamed_addr #5

; Function Attrs: minsize optsize
declare %struct.lbuff_head* @lbuf_init(i8*, i32, i32, i32) local_unnamed_addr #3

; Function Attrs: minsize nounwind optsize
define internal fastcc void @logbuf_output() unnamed_addr #0 section ".system.printf.text" !dbg !677 {
  %1 = load %struct.lbuff_head*, %struct.lbuff_head** @log_bufs, align 4, !dbg !680, !tbaa !150
  %2 = icmp eq %struct.lbuff_head* %1, null, !dbg !682
  br i1 %2, label %57, label %3, !dbg !683

; <label>:3:                                      ; preds = %0
  br label %4, !dbg !684

; <label>:4:                                      ; preds = %52, %3
  %5 = phi %struct.lbuff_head* [ %55, %52 ], [ %1, %3 ], !dbg !686
  %6 = tail call i8* @lbuf_pop(%struct.lbuff_head* %5, i8 zeroext 1) #7, !dbg !688
  store i8* %6, i8** bitcast (%struct.logbuf** @lb_send to i8**), align 4, !dbg !689, !tbaa !150
  %7 = icmp eq i8* %6, null, !dbg !690
  br i1 %7, label %56, label %8, !dbg !692

; <label>:8:                                      ; preds = %4
  %9 = bitcast i8* %6 to %struct.logbuf*, !dbg !693
  br label %10, !dbg !694

; <label>:10:                                     ; preds = %25, %8
  %11 = phi %struct.logbuf* [ %29, %25 ], [ %9, %8 ], !dbg !695
  %12 = phi i32 [ %28, %25 ], [ 0, %8 ]
  tail call void @llvm.dbg.value(metadata i32 %12, i64 0, metadata !679, metadata !158), !dbg !694
  %13 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %11, i32 0, i32 0, !dbg !701
  %14 = load volatile i16, i16* %13, align 2, !dbg !701, !tbaa !166
  %15 = zext i16 %14 to i32, !dbg !703
  %16 = icmp slt i32 %12, %15, !dbg !704
  br i1 %16, label %17, label %30, !dbg !705

; <label>:17:                                     ; preds = %10
  %18 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %11, i32 0, i32 2, i32 %12, !dbg !707
  %19 = load volatile i8, i8* %18, align 1, !dbg !707, !tbaa !175
  %20 = icmp eq i8 %19, 13, !dbg !708
  br i1 %20, label %25, label %21, !dbg !709

; <label>:21:                                     ; preds = %17
  %22 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %11, i32 0, i32 2, i32 %12, !dbg !710
  %23 = load volatile i8, i8* %22, align 1, !dbg !710, !tbaa !175
  %24 = icmp eq i8 %23, 10, !dbg !712
  br i1 %24, label %25, label %30, !dbg !713

; <label>:25:                                     ; preds = %21, %17
  %26 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %11, i32 0, i32 2, i32 %12, !dbg !715
  %27 = load volatile i8, i8* %26, align 1, !dbg !715, !tbaa !175
  tail call void @log_putbyte(i8 signext %27) #8, !dbg !717
  store i32 %12, i32* @send_cnt, align 4, !dbg !718, !tbaa !156
  %28 = add nuw nsw i32 %12, 1, !dbg !719
  tail call void @llvm.dbg.value(metadata i32 %28, i64 0, metadata !679, metadata !158), !dbg !694
  %29 = load %struct.logbuf*, %struct.logbuf** @lb_send, align 4, !tbaa !150
  br label %10, !dbg !720, !llvm.loop !721

; <label>:30:                                     ; preds = %21, %10
  %31 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %11, i32 0, i32 0, !dbg !724
  %32 = load volatile i16, i16* %31, align 2, !dbg !724, !tbaa !166
  %33 = zext i16 %32 to i32, !dbg !726
  %34 = icmp slt i32 %12, %33, !dbg !727
  br i1 %34, label %35, label %40, !dbg !728

; <label>:35:                                     ; preds = %30
  %36 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %11, i32 0, i32 0, !dbg !729
  %37 = load volatile i16, i16* %36, align 2, !dbg !729, !tbaa !166
  %38 = icmp ugt i16 %37, 1, !dbg !731
  br i1 %38, label %39, label %40, !dbg !732

; <label>:39:                                     ; preds = %35
  tail call void @log_print_time() #8, !dbg !733
  br label %40, !dbg !735

; <label>:40:                                     ; preds = %39, %35, %30
  br label %41, !dbg !736

; <label>:41:                                     ; preds = %48, %40
  %42 = phi i32 [ %51, %48 ], [ %12, %40 ]
  tail call void @llvm.dbg.value(metadata i32 %42, i64 0, metadata !679, metadata !158), !dbg !694
  %43 = load %struct.logbuf*, %struct.logbuf** @lb_send, align 4, !dbg !738, !tbaa !150
  %44 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %43, i32 0, i32 0, !dbg !742
  %45 = load volatile i16, i16* %44, align 2, !dbg !742, !tbaa !166
  %46 = zext i16 %45 to i32, !dbg !738
  %47 = icmp slt i32 %42, %46, !dbg !743
  br i1 %47, label %48, label %52, !dbg !744

; <label>:48:                                     ; preds = %41
  %49 = getelementptr inbounds %struct.logbuf, %struct.logbuf* %43, i32 0, i32 2, i32 %42, !dbg !746
  %50 = load volatile i8, i8* %49, align 1, !dbg !746, !tbaa !175
  tail call void @log_putbyte(i8 signext %50) #8, !dbg !748
  store i32 %42, i32* @send_cnt, align 4, !dbg !749, !tbaa !156
  %51 = add nsw i32 %42, 1, !dbg !750
  tail call void @llvm.dbg.value(metadata i32 %51, i64 0, metadata !679, metadata !158), !dbg !694
  br label %41, !dbg !751, !llvm.loop !752

; <label>:52:                                     ; preds = %41
  %53 = bitcast %struct.logbuf* %43 to i8*, !dbg !755
  %54 = tail call i32 @lbuf_free(i8* %53) #7, !dbg !756
  store %struct.logbuf* null, %struct.logbuf** @lb_send, align 4, !dbg !757, !tbaa !150
  store i32 0, i32* @send_cnt, align 4, !dbg !758, !tbaa !156
  %55 = load %struct.lbuff_head*, %struct.lbuff_head** @log_bufs, align 4, !tbaa !150
  br label %4, !dbg !759, !llvm.loop !761

; <label>:56:                                     ; preds = %4
  br label %57, !dbg !764

; <label>:57:                                     ; preds = %56, %0
  ret void, !dbg !765
}

; Function Attrs: minsize optsize
declare i8* @lbuf_pop(%struct.lbuff_head*, i8 zeroext) local_unnamed_addr #3

; Function Attrs: minsize optsize
declare void @local_irq_disable(...) local_unnamed_addr #3

; Function Attrs: minsize optsize
declare void @local_irq_enable(...) local_unnamed_addr #3

; Function Attrs: nounwind readnone
declare void @llvm.dbg.value(metadata, i64, metadata, metadata) #2

attributes #0 = { minsize nounwind optsize "allow-nullptr-deref" "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="r3" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { argmemonly nounwind }
attributes #2 = { nounwind readnone }
attributes #3 = { minsize optsize "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="r3" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #4 = { minsize norecurse nounwind optsize readonly "allow-nullptr-deref" "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="r3" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #5 = { minsize nounwind optsize "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="r3" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #6 = { nounwind }
attributes #7 = { minsize nounwind optsize }
attributes #8 = { minsize optsize }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!138, !139}
!llvm.ident = !{!140}

!0 = !DIGlobalVariableExpression(var: !1)
!1 = distinct !DIGlobalVariable(name: "lb_send", scope: !2, file: !3, line: 13, type: !136, isLocal: true, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C99, file: !3, producer: "clang version 4.0.1 () ()", isOptimized: true, runtimeVersion: 0, emissionKind: FullDebug, enums: !4, retainedTypes: !5, globals: !52)
!3 = !DIFile(filename: "/jks/workspace/audio_build_release/SDK/lib/system/printf/log.c", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!4 = !{}
!5 = !{!6, !7, !21}
!6 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 32)
!7 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !8, size: 32)
!8 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "logbuf", file: !9, line: 14, size: 32, elements: !10)
!9 = !DIFile(filename: "/jks/workspace/audio_build_release/SDK/include_lib/system/generic/log.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!10 = !{!11, !15, !16}
!11 = !DIDerivedType(tag: DW_TAG_member, name: "len", scope: !8, file: !9, line: 15, baseType: !12, size: 16)
!12 = !DIDerivedType(tag: DW_TAG_typedef, name: "u16", file: !13, line: 13, baseType: !14)
!13 = !DIFile(filename: "/jks/workspace/audio_build_release/SDK/include_lib/driver/cpu/br23/asm/cpu.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!14 = !DIBasicType(name: "unsigned short", size: 16, encoding: DW_ATE_unsigned)
!15 = !DIDerivedType(tag: DW_TAG_member, name: "buf_len", scope: !8, file: !9, line: 16, baseType: !12, size: 16, offset: 16)
!16 = !DIDerivedType(tag: DW_TAG_member, name: "buf", scope: !8, file: !9, line: 17, baseType: !17, offset: 32)
!17 = !DICompositeType(tag: DW_TAG_array_type, baseType: !18, elements: !19)
!18 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!19 = !{!20}
!20 = !DISubrange(count: 0)
!21 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !22, size: 32)
!22 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "lbuff_head", file: !23, line: 10, size: 352, elements: !24)
!23 = !DIFile(filename: "/jks/workspace/audio_build_release/SDK/include_lib/system/generic/lbuf.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!24 = !{!25, !27, !34, !35, !44, !47, !48, !49, !50, !51}
!25 = !DIDerivedType(tag: DW_TAG_member, name: "magic_a", scope: !22, file: !23, line: 11, baseType: !26, size: 32)
!26 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!27 = !DIDerivedType(tag: DW_TAG_member, name: "head", scope: !22, file: !23, line: 12, baseType: !28, size: 64, offset: 32)
!28 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "list_head", file: !29, line: 25, size: 64, elements: !30)
!29 = !DIFile(filename: "/jks/workspace/audio_build_release/SDK/include_lib/system/generic/list.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!30 = !{!31, !33}
!31 = !DIDerivedType(tag: DW_TAG_member, name: "next", scope: !28, file: !29, line: 26, baseType: !32, size: 32)
!32 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !28, size: 32)
!33 = !DIDerivedType(tag: DW_TAG_member, name: "prev", scope: !28, file: !29, line: 26, baseType: !32, size: 32, offset: 32)
!34 = !DIDerivedType(tag: DW_TAG_member, name: "free", scope: !22, file: !23, line: 13, baseType: !28, size: 64, offset: 96)
!35 = !DIDerivedType(tag: DW_TAG_member, name: "lock", scope: !22, file: !23, line: 14, baseType: !36, size: 32, offset: 160)
!36 = !DIDerivedType(tag: DW_TAG_typedef, name: "spinlock_t", file: !37, line: 13, baseType: !38)
!37 = !DIFile(filename: "/jks/workspace/audio_build_release/SDK/include_lib/system/spinlock.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!38 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "__spinlock", file: !37, line: 9, size: 32, elements: !39)
!39 = !{!40}
!40 = !DIDerivedType(tag: DW_TAG_member, name: "rwlock", scope: !38, file: !37, line: 10, baseType: !41, size: 32)
!41 = !DIDerivedType(tag: DW_TAG_volatile_type, baseType: !42)
!42 = !DIDerivedType(tag: DW_TAG_typedef, name: "u32", file: !13, line: 15, baseType: !43)
!43 = !DIBasicType(name: "unsigned int", size: 32, encoding: DW_ATE_unsigned)
!44 = !DIDerivedType(tag: DW_TAG_member, name: "align", scope: !22, file: !23, line: 15, baseType: !45, size: 8, offset: 192)
!45 = !DIDerivedType(tag: DW_TAG_typedef, name: "u8", file: !13, line: 11, baseType: !46)
!46 = !DIBasicType(name: "unsigned char", size: 8, encoding: DW_ATE_unsigned_char)
!47 = !DIDerivedType(tag: DW_TAG_member, name: "priv_len", scope: !22, file: !23, line: 16, baseType: !12, size: 16, offset: 208)
!48 = !DIDerivedType(tag: DW_TAG_member, name: "total_size", scope: !22, file: !23, line: 17, baseType: !42, size: 32, offset: 224)
!49 = !DIDerivedType(tag: DW_TAG_member, name: "last_addr", scope: !22, file: !23, line: 18, baseType: !42, size: 32, offset: 256)
!50 = !DIDerivedType(tag: DW_TAG_member, name: "priv", scope: !22, file: !23, line: 19, baseType: !6, size: 32, offset: 288)
!51 = !DIDerivedType(tag: DW_TAG_member, name: "magic_b", scope: !22, file: !23, line: 20, baseType: !26, size: 32, offset: 320)
!52 = !{!53, !55, !0, !106, !108, !110, !112, !123, !125, !127, !129, !131}
!53 = !DIGlobalVariableExpression(var: !54)
!54 = distinct !DIGlobalVariable(name: "log_bufs", scope: !2, file: !3, line: 12, type: !21, isLocal: true, isDefinition: true)
!55 = !DIGlobalVariableExpression(var: !56)
!56 = distinct !DIGlobalVariable(name: "log_mutex", scope: !2, file: !3, line: 17, type: !57, isLocal: true, isDefinition: true)
!57 = !DIDerivedType(tag: DW_TAG_typedef, name: "OS_MUTEX", file: !58, line: 31, baseType: !59)
!58 = !DIFile(filename: "/jks/workspace/audio_build_release/SDK/include_lib/system/os/os_type.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!59 = !DIDerivedType(tag: DW_TAG_typedef, name: "StaticSemaphore_t", file: !60, line: 991, baseType: !61)
!60 = !DIFile(filename: "/jks/workspace/audio_build_release/SDK/include_lib/system/os/FreeRTOS/FreeRTOS.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!61 = !DIDerivedType(tag: DW_TAG_typedef, name: "StaticQueue_t", file: !60, line: 990, baseType: !62)
!62 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "xSTATIC_QUEUE", file: !60, line: 965, size: 640, elements: !63)
!63 = !{!64, !68, !76, !97, !99, !103, !104, !105}
!64 = !DIDerivedType(tag: DW_TAG_member, name: "pvDummy1", scope: !62, file: !60, line: 966, baseType: !65, size: 96)
!65 = !DICompositeType(tag: DW_TAG_array_type, baseType: !6, size: 96, elements: !66)
!66 = !{!67}
!67 = !DISubrange(count: 3)
!68 = !DIDerivedType(tag: DW_TAG_member, name: "u", scope: !62, file: !60, line: 971, baseType: !69, size: 32, offset: 96)
!69 = distinct !DICompositeType(tag: DW_TAG_union_type, scope: !62, file: !60, line: 968, size: 32, elements: !70)
!70 = !{!71, !72}
!71 = !DIDerivedType(tag: DW_TAG_member, name: "pvDummy2", scope: !69, file: !60, line: 969, baseType: !6, size: 32)
!72 = !DIDerivedType(tag: DW_TAG_member, name: "uxDummy2", scope: !69, file: !60, line: 970, baseType: !73, size: 32)
!73 = !DIDerivedType(tag: DW_TAG_typedef, name: "UBaseType_t", file: !74, line: 89, baseType: !75)
!74 = !DIFile(filename: "/jks/workspace/audio_build_release/SDK/include_lib/system/os/FreeRTOS/pi32v2/portmacro.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!75 = !DIBasicType(name: "long unsigned int", size: 32, encoding: DW_ATE_unsigned)
!76 = !DIDerivedType(tag: DW_TAG_member, name: "xDummy3", scope: !62, file: !60, line: 973, baseType: !77, size: 320, offset: 128)
!77 = !DICompositeType(tag: DW_TAG_array_type, baseType: !78, size: 320, elements: !95)
!78 = !DIDerivedType(tag: DW_TAG_typedef, name: "StaticList_t", file: !60, line: 892, baseType: !79)
!79 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "xSTATIC_LIST", file: !60, line: 888, size: 160, elements: !80)
!80 = !{!81, !82, !83}
!81 = !DIDerivedType(tag: DW_TAG_member, name: "uxDummy1", scope: !79, file: !60, line: 889, baseType: !73, size: 32)
!82 = !DIDerivedType(tag: DW_TAG_member, name: "pvDummy2", scope: !79, file: !60, line: 890, baseType: !6, size: 32, offset: 32)
!83 = !DIDerivedType(tag: DW_TAG_member, name: "xDummy3", scope: !79, file: !60, line: 891, baseType: !84, size: 96, offset: 64)
!84 = !DIDerivedType(tag: DW_TAG_typedef, name: "StaticMiniListItem_t", file: !60, line: 885, baseType: !85)
!85 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "xSTATIC_MINI_LIST_ITEM", file: !60, line: 881, size: 96, elements: !86)
!86 = !{!87, !93}
!87 = !DIDerivedType(tag: DW_TAG_member, name: "xDummy1", scope: !85, file: !60, line: 882, baseType: !88, size: 32)
!88 = !DIDerivedType(tag: DW_TAG_typedef, name: "TickType_t", file: !74, line: 96, baseType: !89)
!89 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint32_t", file: !90, line: 32, baseType: !91)
!90 = !DIFile(filename: "/opt/pi32v2/newlib/include/sys/_stdint.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!91 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint32_t", file: !92, line: 65, baseType: !43)
!92 = !DIFile(filename: "/opt/pi32v2/newlib/include/machine/_default_types.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!93 = !DIDerivedType(tag: DW_TAG_member, name: "pvDummy2", scope: !85, file: !60, line: 883, baseType: !94, size: 64, offset: 32)
!94 = !DICompositeType(tag: DW_TAG_array_type, baseType: !6, size: 64, elements: !95)
!95 = !{!96}
!96 = !DISubrange(count: 2)
!97 = !DIDerivedType(tag: DW_TAG_member, name: "uxDummy4", scope: !62, file: !60, line: 974, baseType: !98, size: 96, offset: 448)
!98 = !DICompositeType(tag: DW_TAG_array_type, baseType: !73, size: 96, elements: !66)
!99 = !DIDerivedType(tag: DW_TAG_member, name: "ucDummy5", scope: !62, file: !60, line: 975, baseType: !100, size: 16, offset: 544)
!100 = !DICompositeType(tag: DW_TAG_array_type, baseType: !101, size: 16, elements: !95)
!101 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint8_t", file: !90, line: 20, baseType: !102)
!102 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint8_t", file: !92, line: 29, baseType: !46)
!103 = !DIDerivedType(tag: DW_TAG_member, name: "ucDummy6", scope: !62, file: !60, line: 978, baseType: !101, size: 8, offset: 560)
!104 = !DIDerivedType(tag: DW_TAG_member, name: "uxDummy8", scope: !62, file: !60, line: 986, baseType: !73, size: 32, offset: 576)
!105 = !DIDerivedType(tag: DW_TAG_member, name: "ucDummy9", scope: !62, file: !60, line: 987, baseType: !101, size: 8, offset: 608)
!106 = !DIGlobalVariableExpression(var: !107)
!107 = distinct !DIGlobalVariable(name: "send_cnt", scope: !2, file: !3, line: 10, type: !26, isLocal: true, isDefinition: true)
!108 = !DIGlobalVariableExpression(var: !109)
!109 = distinct !DIGlobalVariable(name: "jiffies_offset", scope: !2, file: !3, line: 16, type: !42, isLocal: true, isDefinition: true)
!110 = !DIGlobalVariableExpression(var: !111)
!111 = distinct !DIGlobalVariable(name: "jiffies_base", scope: !2, file: !3, line: 15, type: !42, isLocal: true, isDefinition: true)
!112 = !DIGlobalVariableExpression(var: !113)
!113 = distinct !DIGlobalVariable(name: "cur_time", scope: !2, file: !3, line: 14, type: !114, isLocal: true, isDefinition: true)
!114 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "sys_time", file: !115, line: 7, size: 64, elements: !116)
!115 = !DIFile(filename: "/jks/workspace/audio_build_release/SDK/include_lib/system/sys_time.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!116 = !{!117, !118, !119, !120, !121, !122}
!117 = !DIDerivedType(tag: DW_TAG_member, name: "year", scope: !114, file: !115, line: 8, baseType: !12, size: 16)
!118 = !DIDerivedType(tag: DW_TAG_member, name: "month", scope: !114, file: !115, line: 9, baseType: !45, size: 8, offset: 16)
!119 = !DIDerivedType(tag: DW_TAG_member, name: "day", scope: !114, file: !115, line: 10, baseType: !45, size: 8, offset: 24)
!120 = !DIDerivedType(tag: DW_TAG_member, name: "hour", scope: !114, file: !115, line: 11, baseType: !45, size: 8, offset: 32)
!121 = !DIDerivedType(tag: DW_TAG_member, name: "min", scope: !114, file: !115, line: 12, baseType: !45, size: 8, offset: 40)
!122 = !DIDerivedType(tag: DW_TAG_member, name: "sec", scope: !114, file: !115, line: 13, baseType: !45, size: 8, offset: 48)
!123 = !DIGlobalVariableExpression(var: !124)
!124 = distinct !DIGlobalVariable(name: "prev_putbyte", scope: !2, file: !3, line: 8, type: !18, isLocal: true, isDefinition: true)
!125 = !DIGlobalVariableExpression(var: !126)
!126 = distinct !DIGlobalVariable(name: "lock", scope: !2, file: !3, line: 18, type: !36, isLocal: true, isDefinition: true)
!127 = !DIGlobalVariableExpression(var: !128)
!128 = distinct !DIGlobalVariable(name: "log_output_busy", scope: !2, file: !3, line: 9, type: !45, isLocal: true, isDefinition: true)
!129 = !DIGlobalVariableExpression(var: !130)
!130 = distinct !DIGlobalVariable(name: "g_level", scope: !2, file: !3, line: 11, type: !18, isLocal: true, isDefinition: true)
!131 = !DIGlobalVariableExpression(var: !132)
!132 = distinct !DIGlobalVariable(name: "log_str", scope: !2, file: !3, line: 19, type: !133, isLocal: true, isDefinition: true)
!133 = !DICompositeType(tag: DW_TAG_array_type, baseType: !134, size: 64, elements: !95)
!134 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !135, size: 32)
!135 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !18)
!136 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !137, size: 32)
!137 = !DIDerivedType(tag: DW_TAG_volatile_type, baseType: !8)
!138 = !{i32 2, !"Dwarf Version", i32 4}
!139 = !{i32 2, !"Debug Info Version", i32 3}
!140 = !{!"clang version 4.0.1 () ()"}
!141 = distinct !DISubprogram(name: "log_flush", scope: !3, file: !3, line: 59, type: !142, isLocal: false, isDefinition: true, scopeLine: 60, isOptimized: true, unit: !2, variables: !144)
!142 = !DISubroutineType(types: !143)
!143 = !{null}
!144 = !{!145}
!145 = !DILocalVariable(name: "i", scope: !146, file: !3, line: 62, type: !26)
!146 = distinct !DILexicalBlock(scope: !147, file: !3, line: 62, column: 9)
!147 = distinct !DILexicalBlock(scope: !148, file: !3, line: 61, column: 18)
!148 = distinct !DILexicalBlock(scope: !141, file: !3, line: 61, column: 9)
!149 = !DILocation(line: 61, column: 9, scope: !148)
!150 = !{!151, !151, i64 0}
!151 = !{!"any pointer", !152, i64 0}
!152 = !{!"omnipotent char", !153, i64 0}
!153 = !{!"Simple C/C++ TBAA"}
!154 = !DILocation(line: 61, column: 9, scope: !141)
!155 = !DILocation(line: 62, column: 22, scope: !146)
!156 = !{!157, !157, i64 0}
!157 = !{!"int", !152, i64 0}
!158 = !DIExpression()
!159 = !DILocation(line: 62, column: 18, scope: !146)
!160 = !DILocation(line: 62, column: 14, scope: !146)
!161 = !DILocation(line: 63, column: 21, scope: !162)
!162 = distinct !DILexicalBlock(scope: !163, file: !3, line: 62, column: 55)
!163 = distinct !DILexicalBlock(scope: !146, file: !3, line: 62, column: 9)
!164 = !DILocation(line: 62, column: 45, scope: !165)
!165 = !DILexicalBlockFile(scope: !163, file: !3, discriminator: 1)
!166 = !{!167, !168, i64 0}
!167 = !{!"logbuf", !168, i64 0, !168, i64 2, !152, i64 4}
!168 = !{!"short", !152, i64 0}
!169 = !DILocation(line: 62, column: 36, scope: !165)
!170 = !DILocation(line: 62, column: 34, scope: !165)
!171 = !DILocation(line: 62, column: 9, scope: !172)
!172 = !DILexicalBlockFile(scope: !146, file: !3, discriminator: 1)
!173 = !DILocation(line: 63, column: 21, scope: !174)
!174 = !DILexicalBlockFile(scope: !162, file: !3, discriminator: 1)
!175 = !{!152, !152, i64 0}
!176 = !DILocation(line: 63, column: 13, scope: !174)
!177 = !DILocation(line: 62, column: 51, scope: !178)
!178 = !DILexicalBlockFile(scope: !163, file: !3, discriminator: 2)
!179 = !DILocation(line: 62, column: 9, scope: !178)
!180 = distinct !{!180, !181, !182}
!181 = !DILocation(line: 62, column: 9, scope: !146)
!182 = !DILocation(line: 64, column: 9, scope: !146)
!183 = !DILocation(line: 66, column: 5, scope: !141)
!184 = !DILocation(line: 66, column: 5, scope: !185)
!185 = !DILexicalBlockFile(scope: !141, file: !3, discriminator: 1)
!186 = !DILocation(line: 67, column: 1, scope: !141)
!187 = distinct !DISubprogram(name: "log_set_time_offset", scope: !3, file: !3, line: 136, type: !188, isLocal: false, isDefinition: true, scopeLine: 137, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !190)
!188 = !DISubroutineType(types: !189)
!189 = !{null, !26}
!190 = !{!191}
!191 = !DILocalVariable(name: "offset", arg: 1, scope: !187, file: !3, line: 136, type: !26)
!192 = !DILocation(line: 136, column: 30, scope: !187)
!193 = !DILocation(line: 138, column: 20, scope: !187)
!194 = !DILocation(line: 139, column: 1, scope: !187)
!195 = distinct !DISubprogram(name: "log_get_time_offset", scope: !3, file: !3, line: 141, type: !196, isLocal: false, isDefinition: true, scopeLine: 142, isOptimized: true, unit: !2, variables: !4)
!196 = !DISubroutineType(types: !197)
!197 = !{!26}
!198 = !DILocation(line: 143, column: 12, scope: !195)
!199 = !DILocation(line: 143, column: 5, scope: !195)
!200 = distinct !DISubprogram(name: "log_print_time_to_buf", scope: !3, file: !3, line: 149, type: !201, isLocal: false, isDefinition: true, scopeLine: 150, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !204)
!201 = !DISubroutineType(types: !202)
!202 = !{!26, !203}
!203 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !18, size: 32)
!204 = !{!205, !206, !207}
!205 = !DILocalVariable(name: "time", arg: 1, scope: !200, file: !3, line: 149, type: !203)
!206 = !DILocalVariable(name: "current_msec", scope: !200, file: !3, line: 151, type: !26)
!207 = !DILocalVariable(name: "msec", scope: !200, file: !3, line: 153, type: !26)
!208 = !DILocation(line: 149, column: 33, scope: !200)
!209 = !DILocation(line: 151, column: 24, scope: !200)
!210 = !DILocation(line: 151, column: 9, scope: !200)
!211 = !DILocation(line: 153, column: 31, scope: !200)
!212 = !DILocation(line: 153, column: 29, scope: !200)
!213 = !DILocation(line: 153, column: 48, scope: !200)
!214 = !DILocation(line: 153, column: 46, scope: !200)
!215 = !DILocation(line: 153, column: 9, scope: !200)
!216 = !DILocation(line: 155, column: 14, scope: !217)
!217 = distinct !DILexicalBlock(scope: !200, file: !3, line: 155, column: 9)
!218 = !DILocation(line: 155, column: 9, scope: !200)
!219 = !DILocation(line: 157, column: 22, scope: !220)
!220 = distinct !DILexicalBlock(scope: !217, file: !3, line: 155, column: 19)
!221 = !DILocation(line: 159, column: 22, scope: !220)
!222 = !{!223, !152, i64 6}
!223 = !{!"sys_time", !168, i64 0, !152, i64 2, !152, i64 3, !152, i64 4, !152, i64 5, !152, i64 6}
!224 = !DILocation(line: 161, column: 22, scope: !220)
!225 = !{!223, !152, i64 5}
!226 = !DILocation(line: 163, column: 23, scope: !220)
!227 = !{!223, !152, i64 4}
!228 = !DILocation(line: 167, column: 5, scope: !220)
!229 = !DILocation(line: 170, column: 14, scope: !230)
!230 = distinct !DILexicalBlock(scope: !200, file: !3, line: 170, column: 9)
!231 = !DILocation(line: 170, column: 9, scope: !200)
!232 = distinct !{!232, !233, !235}
!233 = !DILocation(line: 171, column: 9, scope: !234)
!234 = distinct !DILexicalBlock(scope: !230, file: !3, line: 170, column: 23)
!235 = !DILocation(line: 182, column: 30, scope: !234)
!236 = !DILocation(line: 153, column: 9, scope: !237)
!237 = !DILexicalBlockFile(scope: !200, file: !3, discriminator: 1)
!238 = !DILocation(line: 153, column: 9, scope: !239)
!239 = !DILexicalBlockFile(scope: !200, file: !3, discriminator: 2)
!240 = !DILocation(line: 172, column: 18, scope: !241)
!241 = distinct !DILexicalBlock(scope: !234, file: !3, line: 171, column: 12)
!242 = !DILocation(line: 173, column: 17, scope: !243)
!243 = distinct !DILexicalBlock(scope: !241, file: !3, line: 173, column: 17)
!244 = !DILocation(line: 173, column: 32, scope: !243)
!245 = !DILocation(line: 173, column: 17, scope: !241)
!246 = !DILocation(line: 175, column: 21, scope: !247)
!247 = distinct !DILexicalBlock(scope: !248, file: !3, line: 175, column: 21)
!248 = distinct !DILexicalBlock(scope: !243, file: !3, line: 173, column: 39)
!249 = !DILocation(line: 175, column: 36, scope: !247)
!250 = !DILocation(line: 175, column: 21, scope: !248)
!251 = !DILocation(line: 176, column: 34, scope: !252)
!252 = distinct !DILexicalBlock(scope: !247, file: !3, line: 175, column: 43)
!253 = !DILocation(line: 177, column: 25, scope: !254)
!254 = distinct !DILexicalBlock(scope: !252, file: !3, line: 177, column: 25)
!255 = !DILocation(line: 177, column: 41, scope: !254)
!256 = !DILocation(line: 177, column: 25, scope: !252)
!257 = !DILocation(line: 178, column: 39, scope: !258)
!258 = distinct !DILexicalBlock(scope: !254, file: !3, line: 177, column: 48)
!259 = !DILocation(line: 180, column: 17, scope: !252)
!260 = !DILocation(line: 182, column: 23, scope: !261)
!261 = !DILexicalBlockFile(scope: !234, file: !3, discriminator: 1)
!262 = !DILocation(line: 182, column: 9, scope: !263)
!263 = !DILexicalBlockFile(scope: !241, file: !3, discriminator: 1)
!264 = !DILocation(line: 173, column: 17, scope: !265)
!265 = !DILexicalBlockFile(scope: !243, file: !3, discriminator: 1)
!266 = !DILocation(line: 184, column: 37, scope: !234)
!267 = !DILocation(line: 184, column: 54, scope: !234)
!268 = !DILocation(line: 184, column: 22, scope: !234)
!269 = !DILocation(line: 185, column: 5, scope: !234)
!270 = !DILocation(line: 188, column: 22, scope: !200)
!271 = !DILocation(line: 187, column: 53, scope: !200)
!272 = !DILocation(line: 187, column: 44, scope: !200)
!273 = !DILocation(line: 187, column: 68, scope: !200)
!274 = !DILocation(line: 187, column: 59, scope: !200)
!275 = !DILocation(line: 188, column: 13, scope: !200)
!276 = !DILocation(line: 187, column: 5, scope: !200)
!277 = !DILocation(line: 190, column: 5, scope: !200)
!278 = distinct !DISubprogram(name: "log_print_time", scope: !3, file: !3, line: 193, type: !142, isLocal: false, isDefinition: true, scopeLine: 194, isOptimized: true, unit: !2, variables: !279)
!279 = !{!280, !284}
!280 = !DILocalVariable(name: "time", scope: !278, file: !3, line: 195, type: !281)
!281 = !DICompositeType(tag: DW_TAG_array_type, baseType: !18, size: 192, elements: !282)
!282 = !{!283}
!283 = !DISubrange(count: 24)
!284 = !DILocalVariable(name: "i", scope: !285, file: !3, line: 209, type: !26)
!285 = distinct !DILexicalBlock(scope: !278, file: !3, line: 209, column: 5)
!286 = !DILocation(line: 195, column: 5, scope: !278)
!287 = !DILocation(line: 195, column: 10, scope: !278)
!288 = !DILocation(line: 197, column: 10, scope: !289)
!289 = distinct !DILexicalBlock(scope: !278, file: !3, line: 197, column: 9)
!290 = !DILocation(line: 197, column: 9, scope: !278)
!291 = !DILocation(line: 198, column: 13, scope: !292)
!292 = distinct !DILexicalBlock(scope: !293, file: !3, line: 198, column: 13)
!293 = distinct !DILexicalBlock(scope: !289, file: !3, line: 197, column: 30)
!294 = !DILocation(line: 198, column: 26, scope: !292)
!295 = !DILocation(line: 198, column: 13, scope: !293)
!296 = !DILocation(line: 199, column: 13, scope: !297)
!297 = distinct !DILexicalBlock(scope: !292, file: !3, line: 198, column: 35)
!298 = !DILocation(line: 200, column: 9, scope: !297)
!299 = !DILocation(line: 204, column: 5, scope: !278)
!300 = !DILocation(line: 206, column: 9, scope: !301)
!301 = distinct !DILexicalBlock(scope: !278, file: !3, line: 206, column: 9)
!302 = !DILocation(line: 206, column: 22, scope: !301)
!303 = !DILocation(line: 206, column: 9, scope: !278)
!304 = !DILocation(line: 207, column: 9, scope: !305)
!305 = distinct !DILexicalBlock(scope: !301, file: !3, line: 206, column: 31)
!306 = !DILocation(line: 208, column: 5, scope: !305)
!307 = !DILocation(line: 209, column: 14, scope: !285)
!308 = !DILocation(line: 209, column: 23, scope: !309)
!309 = !DILexicalBlockFile(scope: !310, file: !3, discriminator: 1)
!310 = distinct !DILexicalBlock(scope: !285, file: !3, line: 209, column: 5)
!311 = !DILocation(line: 209, column: 5, scope: !312)
!312 = !DILexicalBlockFile(scope: !285, file: !3, discriminator: 1)
!313 = !DILocation(line: 210, column: 21, scope: !314)
!314 = distinct !DILexicalBlock(scope: !310, file: !3, line: 209, column: 34)
!315 = !DILocation(line: 210, column: 9, scope: !314)
!316 = !DILocation(line: 209, column: 30, scope: !317)
!317 = !DILexicalBlockFile(scope: !310, file: !3, discriminator: 2)
!318 = !DILocation(line: 209, column: 5, scope: !317)
!319 = distinct !{!319, !320, !321}
!320 = !DILocation(line: 209, column: 5, scope: !285)
!321 = !DILocation(line: 211, column: 5, scope: !285)
!322 = !DILocation(line: 212, column: 1, scope: !278)
!323 = !DILocation(line: 212, column: 1, scope: !324)
!324 = !DILexicalBlockFile(scope: !278, file: !3, discriminator: 1)
!325 = distinct !DISubprogram(name: "log_putbyte", scope: !3, file: !3, line: 413, type: !326, isLocal: false, isDefinition: true, scopeLine: 414, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !328)
!326 = !DISubroutineType(types: !327)
!327 = !{null, !18}
!328 = !{!329}
!329 = !DILocalVariable(name: "c", arg: 1, scope: !325, file: !3, line: 413, type: !18)
!330 = !DILocation(line: 413, column: 45, scope: !325)
!331 = !DILocation(line: 415, column: 5, scope: !325)
!332 = !DILocation(line: 416, column: 18, scope: !325)
!333 = !DILocation(line: 417, column: 1, scope: !325)
!334 = distinct !DISubprogram(name: "log_output_lock", scope: !3, file: !3, line: 215, type: !196, isLocal: false, isDefinition: true, scopeLine: 216, isOptimized: true, unit: !2, variables: !335)
!335 = !{!336}
!336 = !DILocalVariable(name: "err", scope: !334, file: !3, line: 217, type: !26)
!337 = !DILocation(line: 219, column: 11, scope: !334)
!338 = !DILocation(line: 217, column: 9, scope: !334)
!339 = !DILocation(line: 221, column: 9, scope: !340)
!340 = distinct !DILexicalBlock(scope: !334, file: !3, line: 221, column: 9)
!341 = !DILocation(line: 221, column: 18, scope: !340)
!342 = !DILocation(line: 221, column: 9, scope: !334)
!343 = !DILocalVariable(name: "lock", arg: 1, scope: !344, file: !37, line: 75, type: !347)
!344 = distinct !DISubprogram(name: "spin_lock", scope: !37, file: !37, line: 75, type: !345, isLocal: true, isDefinition: true, scopeLine: 76, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !348)
!345 = !DISubroutineType(types: !346)
!346 = !{null, !347}
!347 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !36, size: 32)
!348 = !{!343}
!349 = !DILocation(line: 75, column: 42, scope: !344, inlinedAt: !350)
!350 = distinct !DILocation(line: 224, column: 5, scope: !334)
!351 = !DILocation(line: 77, column: 5, scope: !344, inlinedAt: !350)
!352 = !DILocation(line: 226, column: 9, scope: !334)
!353 = !DILocation(line: 227, column: 17, scope: !354)
!354 = distinct !DILexicalBlock(scope: !355, file: !3, line: 227, column: 13)
!355 = distinct !DILexicalBlock(scope: !356, file: !3, line: 226, column: 26)
!356 = distinct !DILexicalBlock(scope: !334, file: !3, line: 226, column: 9)
!357 = !DILocalVariable(name: "lock", arg: 1, scope: !358, file: !37, line: 84, type: !347)
!358 = distinct !DISubprogram(name: "spin_unlock", scope: !37, file: !37, line: 84, type: !345, isLocal: true, isDefinition: true, scopeLine: 85, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !359)
!359 = !{!357}
!360 = !DILocation(line: 84, column: 44, scope: !358, inlinedAt: !361)
!361 = distinct !DILocation(line: 228, column: 13, scope: !362)
!362 = distinct !DILexicalBlock(scope: !354, file: !3, line: 227, column: 23)
!363 = !DILocation(line: 88, column: 5, scope: !358, inlinedAt: !361)
!364 = !DILocation(line: 227, column: 13, scope: !355)
!365 = !DILocation(line: 229, column: 13, scope: !362)
!366 = !DILocation(line: 230, column: 9, scope: !362)
!367 = !DILocation(line: 84, column: 44, scope: !358, inlinedAt: !368)
!368 = distinct !DILocation(line: 238, column: 5, scope: !334)
!369 = !DILocation(line: 88, column: 5, scope: !370, inlinedAt: !368)
!370 = !DILexicalBlockFile(scope: !358, file: !37, discriminator: 1)
!371 = !DILocation(line: 240, column: 5, scope: !334)
!372 = !DILocation(line: 241, column: 1, scope: !334)
!373 = distinct !DISubprogram(name: "log_output_unlock", scope: !3, file: !3, line: 243, type: !142, isLocal: false, isDefinition: true, scopeLine: 244, isOptimized: true, unit: !2, variables: !4)
!374 = !DILocation(line: 245, column: 5, scope: !373)
!375 = !DILocation(line: 247, column: 5, scope: !373)
!376 = !DILocation(line: 248, column: 1, scope: !373)
!377 = distinct !DISubprogram(name: "log_print", scope: !3, file: !3, line: 250, type: !378, isLocal: false, isDefinition: true, scopeLine: 251, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !380)
!378 = !DISubroutineType(types: !379)
!379 = !{null, !26, !134, !134, null}
!380 = !{!381, !382, !383, !384, !385, !389, !390, !391}
!381 = !DILocalVariable(name: "level", arg: 1, scope: !377, file: !3, line: 250, type: !26)
!382 = !DILocalVariable(name: "tag", arg: 2, scope: !377, file: !3, line: 250, type: !134)
!383 = !DILocalVariable(name: "format", arg: 3, scope: !377, file: !3, line: 250, type: !134)
!384 = !DILocalVariable(name: "p", scope: !377, file: !3, line: 252, type: !203)
!385 = !DILocalVariable(name: "args", scope: !377, file: !3, line: 253, type: !386)
!386 = !DIDerivedType(tag: DW_TAG_typedef, name: "va_list", file: !387, line: 30, baseType: !388)
!387 = !DIFile(filename: "/opt/pi32v2/pi32v2-uclinux-toolchains/../lib/clang/4.0.1/include/stdarg.h", directory: "/jks/workspace/audio_build_release/SDK/lib/system/printf")
!388 = !DIDerivedType(tag: DW_TAG_typedef, name: "__builtin_va_list", file: !3, line: 253, baseType: !203)
!389 = !DILocalVariable(name: "ent_cnt", scope: !377, file: !3, line: 254, type: !26)
!390 = !DILocalVariable(name: "lb", scope: !377, file: !3, line: 255, type: !7)
!391 = !DILocalVariable(name: "pref", scope: !377, file: !3, line: 256, type: !134)
!392 = !DILocation(line: 250, column: 42, scope: !377)
!393 = !DILocation(line: 250, column: 61, scope: !377)
!394 = !DILocation(line: 250, column: 78, scope: !377)
!395 = !DILocation(line: 252, column: 5, scope: !377)
!396 = !DILocation(line: 253, column: 5, scope: !377)
!397 = !DILocation(line: 254, column: 9, scope: !377)
!398 = !DILocation(line: 258, column: 17, scope: !399)
!399 = distinct !DILexicalBlock(scope: !377, file: !3, line: 258, column: 9)
!400 = !DILocation(line: 258, column: 15, scope: !399)
!401 = !DILocation(line: 258, column: 9, scope: !377)
!402 = !DILocation(line: 262, column: 5, scope: !377)
!403 = !DILocation(line: 264, column: 9, scope: !404)
!404 = distinct !DILexicalBlock(scope: !377, file: !3, line: 264, column: 9)
!405 = !DILocation(line: 264, column: 27, scope: !404)
!406 = !DILocation(line: 264, column: 9, scope: !377)
!407 = !DILocation(line: 266, column: 14, scope: !408)
!408 = distinct !DILexicalBlock(scope: !404, file: !3, line: 264, column: 33)
!409 = !DILocation(line: 255, column: 20, scope: !377)
!410 = !DILocation(line: 267, column: 14, scope: !411)
!411 = distinct !DILexicalBlock(scope: !408, file: !3, line: 267, column: 13)
!412 = !DILocation(line: 267, column: 13, scope: !408)
!413 = !DILocation(line: 250, column: 78, scope: !414)
!414 = !DILexicalBlockFile(scope: !377, file: !3, discriminator: 1)
!415 = !DILocation(line: 271, column: 16, scope: !416)
!416 = !DILexicalBlockFile(scope: !408, file: !3, discriminator: 1)
!417 = !DILocation(line: 271, column: 32, scope: !416)
!418 = !DILocation(line: 272, column: 13, scope: !419)
!419 = distinct !DILexicalBlock(scope: !408, file: !3, line: 271, column: 52)
!420 = !DILocation(line: 273, column: 19, scope: !419)
!421 = !DILocation(line: 274, column: 20, scope: !419)
!422 = !DILocation(line: 271, column: 9, scope: !416)
!423 = distinct !{!423, !424, !425}
!424 = !DILocation(line: 271, column: 9, scope: !408)
!425 = !DILocation(line: 275, column: 9, scope: !408)
!426 = !DILocation(line: 278, column: 23, scope: !427)
!427 = distinct !DILexicalBlock(scope: !428, file: !3, line: 277, column: 30)
!428 = distinct !DILexicalBlock(scope: !408, file: !3, line: 277, column: 13)
!429 = !DILocation(line: 278, column: 13, scope: !427)
!430 = !DILocation(line: 279, column: 13, scope: !427)
!431 = !DILocation(line: 282, column: 19, scope: !432)
!432 = distinct !DILexicalBlock(scope: !408, file: !3, line: 282, column: 13)
!433 = !DILocation(line: 282, column: 13, scope: !408)
!434 = !DILocation(line: 283, column: 30, scope: !435)
!435 = !DILexicalBlockFile(scope: !436, file: !3, discriminator: 1)
!436 = distinct !DILexicalBlock(scope: !432, file: !3, line: 282, column: 34)
!437 = !DILocation(line: 283, column: 13, scope: !435)
!438 = !DILocation(line: 283, column: 27, scope: !435)
!439 = !DILocation(line: 284, column: 17, scope: !440)
!440 = distinct !DILexicalBlock(scope: !436, file: !3, line: 283, column: 35)
!441 = distinct !{!441, !442, !443}
!442 = !DILocation(line: 283, column: 13, scope: !436)
!443 = !DILocation(line: 285, column: 13, scope: !436)
!444 = !DILocation(line: 287, column: 34, scope: !436)
!445 = !DILocation(line: 287, column: 20, scope: !436)
!446 = !DILocation(line: 256, column: 17, scope: !377)
!447 = !DILocation(line: 289, column: 13, scope: !436)
!448 = !DILocation(line: 289, column: 20, scope: !435)
!449 = !DILocation(line: 289, column: 26, scope: !435)
!450 = !DILocation(line: 289, column: 13, scope: !435)
!451 = !DILocation(line: 290, column: 17, scope: !452)
!452 = distinct !DILexicalBlock(scope: !436, file: !3, line: 289, column: 35)
!453 = !DILocation(line: 291, column: 21, scope: !452)
!454 = !DILocation(line: 289, column: 13, scope: !455)
!455 = !DILexicalBlockFile(scope: !436, file: !3, discriminator: 2)
!456 = distinct !{!456, !447, !457}
!457 = !DILocation(line: 292, column: 13, scope: !436)
!458 = !DILocation(line: 295, column: 26, scope: !408)
!459 = !DILocation(line: 295, column: 26, scope: !416)
!460 = !DILocation(line: 295, column: 14, scope: !416)
!461 = !DILocation(line: 252, column: 11, scope: !377)
!462 = !DILocation(line: 295, column: 11, scope: !416)
!463 = !DILocation(line: 297, column: 19, scope: !408)
!464 = !DILocation(line: 297, column: 33, scope: !408)
!465 = !{!167, !168, i64 2}
!466 = !DILocation(line: 297, column: 29, scope: !408)
!467 = !DILocation(line: 297, column: 27, scope: !408)
!468 = !DILocation(line: 297, column: 50, scope: !408)
!469 = !DILocation(line: 253, column: 13, scope: !377)
!470 = !DIExpression(DW_OP_deref)
!471 = !DILocation(line: 297, column: 9, scope: !408)
!472 = !DILocation(line: 299, column: 13, scope: !408)
!473 = !DILocation(line: 300, column: 15, scope: !474)
!474 = distinct !DILexicalBlock(scope: !475, file: !3, line: 299, column: 34)
!475 = distinct !DILexicalBlock(scope: !408, file: !3, line: 299, column: 13)
!476 = !DILocation(line: 300, column: 18, scope: !474)
!477 = !DILocation(line: 301, column: 15, scope: !474)
!478 = !DILocation(line: 301, column: 18, scope: !474)
!479 = !DILocation(line: 302, column: 9, scope: !474)
!480 = !DILocation(line: 303, column: 19, scope: !408)
!481 = !DILocation(line: 303, column: 21, scope: !408)
!482 = !DILocation(line: 303, column: 17, scope: !408)
!483 = !DILocation(line: 305, column: 9, scope: !408)
!484 = !DILocation(line: 307, column: 5, scope: !408)
!485 = !DILocation(line: 309, column: 16, scope: !486)
!486 = !DILexicalBlockFile(scope: !487, file: !3, discriminator: 1)
!487 = distinct !DILexicalBlock(scope: !404, file: !3, line: 307, column: 12)
!488 = !DILocation(line: 309, column: 9, scope: !489)
!489 = !DILexicalBlockFile(scope: !487, file: !3, discriminator: 3)
!490 = !DILocation(line: 310, column: 13, scope: !491)
!491 = distinct !DILexicalBlock(scope: !487, file: !3, line: 309, column: 52)
!492 = !DILocation(line: 311, column: 19, scope: !491)
!493 = !DILocation(line: 312, column: 20, scope: !491)
!494 = !DILocation(line: 309, column: 9, scope: !486)
!495 = distinct !{!495, !496, !497}
!496 = !DILocation(line: 309, column: 9, scope: !487)
!497 = !DILocation(line: 313, column: 9, scope: !487)
!498 = !DILocation(line: 315, column: 23, scope: !499)
!499 = distinct !DILexicalBlock(scope: !500, file: !3, line: 315, column: 17)
!500 = distinct !DILexicalBlock(scope: !501, file: !3, line: 314, column: 30)
!501 = distinct !DILexicalBlock(scope: !487, file: !3, line: 314, column: 13)
!502 = !DILocation(line: 315, column: 17, scope: !500)
!503 = !DILocation(line: 254, column: 9, scope: !414)
!504 = !DILocation(line: 316, column: 34, scope: !505)
!505 = !DILexicalBlockFile(scope: !506, file: !3, discriminator: 1)
!506 = distinct !DILexicalBlock(scope: !499, file: !3, line: 315, column: 38)
!507 = !DILocation(line: 316, column: 17, scope: !505)
!508 = !DILocation(line: 316, column: 31, scope: !505)
!509 = !DILocation(line: 317, column: 21, scope: !510)
!510 = distinct !DILexicalBlock(scope: !506, file: !3, line: 316, column: 39)
!511 = distinct !{!511, !512, !513}
!512 = !DILocation(line: 316, column: 17, scope: !506)
!513 = !DILocation(line: 318, column: 17, scope: !506)
!514 = !DILocation(line: 321, column: 13, scope: !500)
!515 = !DILocation(line: 325, column: 38, scope: !516)
!516 = distinct !DILexicalBlock(scope: !517, file: !3, line: 323, column: 38)
!517 = distinct !DILexicalBlock(scope: !500, file: !3, line: 323, column: 17)
!518 = !DILocation(line: 325, column: 24, scope: !516)
!519 = !DILocation(line: 327, column: 17, scope: !516)
!520 = !DILocation(line: 327, column: 24, scope: !521)
!521 = !DILexicalBlockFile(scope: !516, file: !3, discriminator: 1)
!522 = !DILocation(line: 327, column: 30, scope: !521)
!523 = !DILocation(line: 327, column: 17, scope: !521)
!524 = !DILocation(line: 328, column: 21, scope: !525)
!525 = distinct !DILexicalBlock(scope: !516, file: !3, line: 327, column: 39)
!526 = !DILocation(line: 329, column: 25, scope: !525)
!527 = !DILocation(line: 327, column: 17, scope: !528)
!528 = !DILexicalBlockFile(scope: !516, file: !3, discriminator: 2)
!529 = distinct !{!529, !519, !530}
!530 = !DILocation(line: 330, column: 17, scope: !516)
!531 = !DILocation(line: 321, column: 13, scope: !532)
!532 = !DILexicalBlockFile(scope: !500, file: !3, discriminator: 1)
!533 = !DILocation(line: 333, column: 36, scope: !500)
!534 = !DILocation(line: 333, column: 13, scope: !500)
!535 = !DILocation(line: 335, column: 17, scope: !500)
!536 = !DILocation(line: 333, column: 36, scope: !532)
!537 = !DILocation(line: 333, column: 13, scope: !532)
!538 = !DILocation(line: 336, column: 17, scope: !539)
!539 = distinct !DILexicalBlock(scope: !540, file: !3, line: 335, column: 38)
!540 = distinct !DILexicalBlock(scope: !500, file: !3, line: 335, column: 17)
!541 = !DILocation(line: 337, column: 13, scope: !539)
!542 = !DILocation(line: 340, column: 9, scope: !487)
!543 = !DILocation(line: 340, column: 9, scope: !486)
!544 = !DILocation(line: 344, column: 5, scope: !377)
!545 = !DILocation(line: 345, column: 1, scope: !377)
!546 = !DILocation(line: 345, column: 1, scope: !414)
!547 = distinct !DISubprogram(name: "log_output_start", scope: !3, file: !3, line: 354, type: !548, isLocal: false, isDefinition: true, scopeLine: 355, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !550)
!548 = !DISubroutineType(types: !549)
!549 = !{!7, !26}
!550 = !{!551, !552}
!551 = !DILocalVariable(name: "len", arg: 1, scope: !547, file: !3, line: 354, type: !26)
!552 = !DILocalVariable(name: "lb", scope: !547, file: !3, line: 356, type: !7)
!553 = !DILocation(line: 354, column: 37, scope: !547)
!554 = !DILocation(line: 356, column: 20, scope: !547)
!555 = !DILocation(line: 358, column: 13, scope: !556)
!556 = distinct !DILexicalBlock(scope: !547, file: !3, line: 358, column: 9)
!557 = !DILocation(line: 358, column: 9, scope: !547)
!558 = !DILocation(line: 362, column: 38, scope: !547)
!559 = !DILocation(line: 362, column: 70, scope: !547)
!560 = !DILocation(line: 362, column: 27, scope: !547)
!561 = !DILocation(line: 362, column: 10, scope: !547)
!562 = !DILocation(line: 363, column: 9, scope: !563)
!563 = distinct !DILexicalBlock(scope: !547, file: !3, line: 363, column: 9)
!564 = !DILocation(line: 363, column: 9, scope: !547)
!565 = !DILocation(line: 364, column: 13, scope: !566)
!566 = distinct !DILexicalBlock(scope: !563, file: !3, line: 363, column: 13)
!567 = !DILocation(line: 364, column: 17, scope: !566)
!568 = !DILocation(line: 365, column: 23, scope: !566)
!569 = !DILocation(line: 365, column: 13, scope: !566)
!570 = !DILocation(line: 365, column: 21, scope: !566)
!571 = !DILocation(line: 366, column: 5, scope: !566)
!572 = !DILocation(line: 368, column: 5, scope: !547)
!573 = distinct !DISubprogram(name: "log_putchar", scope: !3, file: !3, line: 387, type: !574, isLocal: false, isDefinition: true, scopeLine: 388, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !576)
!574 = !DISubroutineType(types: !575)
!575 = !{null, !7, !18}
!576 = !{!577, !578}
!577 = !DILocalVariable(name: "lb", arg: 1, scope: !573, file: !3, line: 387, type: !7)
!578 = !DILocalVariable(name: "c", arg: 2, scope: !573, file: !3, line: 387, type: !18)
!579 = !DILocation(line: 387, column: 33, scope: !573)
!580 = !DILocation(line: 387, column: 42, scope: !573)
!581 = !DILocation(line: 389, column: 13, scope: !582)
!582 = distinct !DILexicalBlock(scope: !573, file: !3, line: 389, column: 9)
!583 = !DILocation(line: 389, column: 23, scope: !582)
!584 = !DILocation(line: 389, column: 17, scope: !582)
!585 = !DILocation(line: 389, column: 9, scope: !573)
!586 = !DILocation(line: 389, column: 9, scope: !587)
!587 = !DILexicalBlockFile(scope: !582, file: !3, discriminator: 1)
!588 = !DILocation(line: 390, column: 24, scope: !589)
!589 = distinct !DILexicalBlock(scope: !582, file: !3, line: 389, column: 32)
!590 = !DILocation(line: 390, column: 9, scope: !589)
!591 = !DILocation(line: 390, column: 28, scope: !589)
!592 = !DILocation(line: 391, column: 5, scope: !589)
!593 = !DILocation(line: 392, column: 1, scope: !573)
!594 = distinct !DISubprogram(name: "log_output_end", scope: !3, file: !3, line: 372, type: !595, isLocal: false, isDefinition: true, scopeLine: 373, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !597)
!595 = !DISubroutineType(types: !596)
!596 = !{null, !7}
!597 = !{!598}
!598 = !DILocalVariable(name: "lb", arg: 1, scope: !594, file: !3, line: 372, type: !7)
!599 = !DILocation(line: 372, column: 36, scope: !594)
!600 = !DILocation(line: 374, column: 9, scope: !601)
!601 = distinct !DILexicalBlock(scope: !594, file: !3, line: 374, column: 9)
!602 = !DILocation(line: 374, column: 9, scope: !594)
!603 = !DILocation(line: 375, column: 17, scope: !604)
!604 = distinct !DILexicalBlock(scope: !605, file: !3, line: 375, column: 13)
!605 = distinct !DILexicalBlock(scope: !601, file: !3, line: 374, column: 13)
!606 = !DILocation(line: 375, column: 27, scope: !604)
!607 = !DILocation(line: 375, column: 21, scope: !604)
!608 = !DILocation(line: 375, column: 13, scope: !605)
!609 = !DILocation(line: 378, column: 19, scope: !605)
!610 = !DILocation(line: 375, column: 13, scope: !611)
!611 = !DILexicalBlockFile(scope: !605, file: !3, discriminator: 1)
!612 = !DILocation(line: 375, column: 13, scope: !613)
!613 = !DILexicalBlockFile(scope: !604, file: !3, discriminator: 2)
!614 = !DILocation(line: 376, column: 26, scope: !615)
!615 = distinct !DILexicalBlock(scope: !604, file: !3, line: 375, column: 36)
!616 = !DILocation(line: 376, column: 42, scope: !615)
!617 = !DILocation(line: 376, column: 13, scope: !615)
!618 = !DILocation(line: 377, column: 9, scope: !615)
!619 = !DILocation(line: 378, column: 19, scope: !611)
!620 = !DILocation(line: 378, column: 9, scope: !611)
!621 = !DILocation(line: 379, column: 5, scope: !605)
!622 = !DILocation(line: 380, column: 9, scope: !623)
!623 = distinct !DILexicalBlock(scope: !594, file: !3, line: 380, column: 9)
!624 = !DILocation(line: 380, column: 27, scope: !623)
!625 = !DILocation(line: 380, column: 9, scope: !594)
!626 = !DILocation(line: 381, column: 9, scope: !627)
!627 = distinct !DILexicalBlock(scope: !623, file: !3, line: 380, column: 33)
!628 = !DILocation(line: 382, column: 5, scope: !627)
!629 = !DILocation(line: 384, column: 1, scope: !594)
!630 = distinct !DISubprogram(name: "log_level", scope: !3, file: !3, line: 348, type: !188, isLocal: false, isDefinition: true, scopeLine: 349, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !631)
!631 = !{!632}
!632 = !DILocalVariable(name: "level", arg: 1, scope: !630, file: !3, line: 348, type: !26)
!633 = !DILocation(line: 348, column: 20, scope: !630)
!634 = !DILocation(line: 350, column: 15, scope: !630)
!635 = !DILocation(line: 350, column: 13, scope: !630)
!636 = !DILocation(line: 351, column: 1, scope: !630)
!637 = distinct !DISubprogram(name: "log_put_u4hex", scope: !3, file: !3, line: 395, type: !638, isLocal: false, isDefinition: true, scopeLine: 396, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !640)
!638 = !DISubroutineType(types: !639)
!639 = !{null, !7, !46}
!640 = !{!641, !642}
!641 = !DILocalVariable(name: "lb", arg: 1, scope: !637, file: !3, line: 395, type: !7)
!642 = !DILocalVariable(name: "dat", arg: 2, scope: !637, file: !3, line: 395, type: !46)
!643 = !DILocation(line: 395, column: 35, scope: !637)
!644 = !DILocation(line: 395, column: 53, scope: !637)
!645 = !DILocation(line: 397, column: 15, scope: !637)
!646 = !DILocation(line: 399, column: 13, scope: !647)
!647 = distinct !DILexicalBlock(scope: !637, file: !3, line: 399, column: 9)
!648 = !DILocation(line: 399, column: 9, scope: !637)
!649 = !DILocation(line: 400, column: 34, scope: !650)
!650 = distinct !DILexicalBlock(scope: !647, file: !3, line: 399, column: 18)
!651 = !DILocation(line: 400, column: 9, scope: !650)
!652 = !DILocation(line: 401, column: 5, scope: !650)
!653 = !DILocation(line: 402, column: 29, scope: !654)
!654 = distinct !DILexicalBlock(scope: !647, file: !3, line: 401, column: 12)
!655 = !DILocation(line: 402, column: 9, scope: !654)
!656 = !DILocation(line: 404, column: 1, scope: !637)
!657 = distinct !DISubprogram(name: "log_put_u8hex", scope: !3, file: !3, line: 406, type: !638, isLocal: false, isDefinition: true, scopeLine: 407, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !658)
!658 = !{!659, !660}
!659 = !DILocalVariable(name: "lb", arg: 1, scope: !657, file: !3, line: 406, type: !7)
!660 = !DILocalVariable(name: "dat", arg: 2, scope: !657, file: !3, line: 406, type: !46)
!661 = !DILocation(line: 406, column: 35, scope: !657)
!662 = !DILocation(line: 406, column: 53, scope: !657)
!663 = !DILocation(line: 408, column: 27, scope: !657)
!664 = !DILocation(line: 408, column: 5, scope: !657)
!665 = !DILocation(line: 409, column: 5, scope: !657)
!666 = !DILocation(line: 410, column: 5, scope: !657)
!667 = !DILocation(line: 411, column: 1, scope: !657)
!668 = distinct !DISubprogram(name: "log_early_init", scope: !3, file: !3, line: 421, type: !188, isLocal: false, isDefinition: true, scopeLine: 422, flags: DIFlagPrototyped, isOptimized: true, unit: !2, variables: !669)
!669 = !{!670}
!670 = !DILocalVariable(name: "size", arg: 1, scope: !668, file: !3, line: 421, type: !26)
!671 = !DILocation(line: 421, column: 25, scope: !668)
!672 = !DILocation(line: 423, column: 5, scope: !668)
!673 = !DILocation(line: 424, column: 37, scope: !668)
!674 = !DILocation(line: 424, column: 14, scope: !668)
!675 = !DILocation(line: 426, column: 5, scope: !668)
!676 = !DILocation(line: 427, column: 1, scope: !668)
!677 = distinct !DISubprogram(name: "logbuf_output", scope: !3, file: !3, line: 25, type: !142, isLocal: true, isDefinition: true, scopeLine: 26, isOptimized: true, unit: !2, variables: !678)
!678 = !{!679}
!679 = !DILocalVariable(name: "i", scope: !677, file: !3, line: 27, type: !26)
!680 = !DILocation(line: 29, column: 9, scope: !681)
!681 = distinct !DILexicalBlock(scope: !677, file: !3, line: 29, column: 9)
!682 = !DILocation(line: 29, column: 18, scope: !681)
!683 = !DILocation(line: 29, column: 9, scope: !677)
!684 = !DILocation(line: 33, column: 36, scope: !685)
!685 = distinct !DILexicalBlock(scope: !677, file: !3, line: 32, column: 15)
!686 = !DILocation(line: 33, column: 45, scope: !687)
!687 = !DILexicalBlockFile(scope: !685, file: !3, discriminator: 1)
!688 = !DILocation(line: 33, column: 36, scope: !687)
!689 = !DILocation(line: 33, column: 17, scope: !687)
!690 = !DILocation(line: 34, column: 14, scope: !691)
!691 = distinct !DILexicalBlock(scope: !685, file: !3, line: 34, column: 13)
!692 = !DILocation(line: 34, column: 13, scope: !685)
!693 = !DILocation(line: 34, column: 13, scope: !687)
!694 = !DILocation(line: 27, column: 9, scope: !677)
!695 = !DILocation(line: 39, column: 29, scope: !696)
!696 = distinct !DILexicalBlock(scope: !697, file: !3, line: 38, column: 69)
!697 = distinct !DILexicalBlock(scope: !698, file: !3, line: 38, column: 17)
!698 = distinct !DILexicalBlock(scope: !699, file: !3, line: 37, column: 44)
!699 = distinct !DILexicalBlock(scope: !700, file: !3, line: 37, column: 9)
!700 = distinct !DILexicalBlock(scope: !685, file: !3, line: 37, column: 9)
!701 = !DILocation(line: 37, column: 34, scope: !702)
!702 = !DILexicalBlockFile(scope: !699, file: !3, discriminator: 1)
!703 = !DILocation(line: 37, column: 25, scope: !702)
!704 = !DILocation(line: 37, column: 23, scope: !702)
!705 = !DILocation(line: 37, column: 9, scope: !706)
!706 = !DILexicalBlockFile(scope: !700, file: !3, discriminator: 1)
!707 = !DILocation(line: 38, column: 17, scope: !697)
!708 = !DILocation(line: 38, column: 33, scope: !697)
!709 = !DILocation(line: 38, column: 41, scope: !697)
!710 = !DILocation(line: 38, column: 44, scope: !711)
!711 = !DILexicalBlockFile(scope: !697, file: !3, discriminator: 1)
!712 = !DILocation(line: 38, column: 60, scope: !711)
!713 = !DILocation(line: 38, column: 17, scope: !714)
!714 = !DILexicalBlockFile(scope: !698, file: !3, discriminator: 1)
!715 = !DILocation(line: 39, column: 29, scope: !716)
!716 = !DILexicalBlockFile(scope: !696, file: !3, discriminator: 1)
!717 = !DILocation(line: 39, column: 17, scope: !716)
!718 = !DILocation(line: 40, column: 26, scope: !696)
!719 = !DILocation(line: 37, column: 40, scope: !702)
!720 = !DILocation(line: 37, column: 9, scope: !702)
!721 = distinct !{!721, !722, !723}
!722 = !DILocation(line: 37, column: 9, scope: !700)
!723 = !DILocation(line: 44, column: 9, scope: !700)
!724 = !DILocation(line: 45, column: 26, scope: !725)
!725 = distinct !DILexicalBlock(scope: !685, file: !3, line: 45, column: 13)
!726 = !DILocation(line: 45, column: 17, scope: !725)
!727 = !DILocation(line: 45, column: 15, scope: !725)
!728 = !DILocation(line: 45, column: 30, scope: !725)
!729 = !DILocation(line: 45, column: 42, scope: !730)
!730 = !DILexicalBlockFile(scope: !725, file: !3, discriminator: 1)
!731 = !DILocation(line: 45, column: 46, scope: !730)
!732 = !DILocation(line: 45, column: 13, scope: !687)
!733 = !DILocation(line: 46, column: 13, scope: !734)
!734 = distinct !DILexicalBlock(scope: !725, file: !3, line: 45, column: 52)
!735 = !DILocation(line: 47, column: 9, scope: !734)
!736 = !DILocation(line: 27, column: 9, scope: !737)
!737 = !DILexicalBlockFile(scope: !677, file: !3, discriminator: 1)
!738 = !DILocation(line: 48, column: 20, scope: !739)
!739 = !DILexicalBlockFile(scope: !740, file: !3, discriminator: 1)
!740 = distinct !DILexicalBlock(scope: !741, file: !3, line: 48, column: 9)
!741 = distinct !DILexicalBlock(scope: !685, file: !3, line: 48, column: 9)
!742 = !DILocation(line: 48, column: 29, scope: !739)
!743 = !DILocation(line: 48, column: 18, scope: !739)
!744 = !DILocation(line: 48, column: 9, scope: !745)
!745 = !DILexicalBlockFile(scope: !741, file: !3, discriminator: 1)
!746 = !DILocation(line: 49, column: 25, scope: !747)
!747 = distinct !DILexicalBlock(scope: !740, file: !3, line: 48, column: 39)
!748 = !DILocation(line: 49, column: 13, scope: !747)
!749 = !DILocation(line: 50, column: 22, scope: !747)
!750 = !DILocation(line: 48, column: 35, scope: !739)
!751 = !DILocation(line: 48, column: 9, scope: !739)
!752 = distinct !{!752, !753, !754}
!753 = !DILocation(line: 48, column: 9, scope: !741)
!754 = !DILocation(line: 51, column: 9, scope: !741)
!755 = !DILocation(line: 52, column: 19, scope: !685)
!756 = !DILocation(line: 52, column: 9, scope: !685)
!757 = !DILocation(line: 53, column: 17, scope: !685)
!758 = !DILocation(line: 54, column: 18, scope: !685)
!759 = !DILocation(line: 32, column: 5, scope: !760)
!760 = !DILexicalBlockFile(scope: !677, file: !3, discriminator: 2)
!761 = distinct !{!761, !762, !763}
!762 = !DILocation(line: 32, column: 5, scope: !677)
!763 = !DILocation(line: 55, column: 5, scope: !677)
!764 = !DILocation(line: 56, column: 1, scope: !760)
!765 = !DILocation(line: 56, column: 1, scope: !737)
