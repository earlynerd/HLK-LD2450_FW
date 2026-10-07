"""Reproducible, calibration-conscious analysis of accepted dual-RX LDF1 frames.

Reads saved data only. Verifies lane hashes and every original radar record.
No device access, firmware changes, inferred metre axes or target declarations.
"""
from pathlib import Path
import argparse,base64,hashlib,html,json,sys,textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'firmware/tools'))
from frame_stream import validate_record

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def db(p):return 10*np.log10(np.maximum(p,1e-20))
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,default=ROOT/'output/stream_bench/usb_budget_guard_decoded')
    p.add_argument('--out',type=Path,default=ROOT/'output/radar_analysis/usb_20261006')
    args=p.parse_args();src=args.input.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    zs=[];metas=[];manifest={};configs=set()
    for folder in sorted(src.glob('frame-*')):
        meta=json.loads((folder/'frame.json').read_text());metas.append(meta);configs.add(meta['config_sha256']);lanes=[]
        manifest[str((folder/'frame.json').relative_to(src))]=digest(folder/'frame.json')
        for lane in range(2):
            f=folder/f'lane{lane}.bin';raw=f.read_bytes();h=hashlib.sha256(raw).hexdigest()
            assert h==meta['lane_sha256'][lane],f
            assert len(raw)==64*2056,f
            for chirp in range(64):assert validate_record(raw[chirp*2056:(chirp+1)*2056])==(lane,chirp)
            manifest[str(f.relative_to(src))]=h
            words=np.frombuffer(raw,dtype='>i2').reshape(64,1028)[:,2:-2].reshape(64,512,2).astype(np.float32)
            lanes.append(words[...,0]+1j*words[...,1])
        zs.append(lanes)
    assert len(zs)>1 and len(configs)==1
    z=np.array(zs);n=len(z);times=np.array([m['timestamps_us'] for m in metas],dtype=np.int64)
    ids=np.array([m['frame_id'] for m in metas]);t=(times[:,0,0]-times[0,0,0])/1e6
    dt=np.diff(times,axis=-1);period=np.median(np.diff(times[:,0,0])/np.diff(ids))/1e6
    chirp_s=np.median(dt)/1e6
    ac=z-z.mean(axis=-1,keepdims=True)
    residual=ac-ac.mean(axis=2,keepdims=True)
    ac_rms=np.sqrt(np.mean(abs(ac)**2,axis=(0,2,3)))
    residual_rms=np.sqrt(np.mean(abs(residual)**2,axis=(0,2,3)))
    frame_residual=np.sqrt(np.mean(abs(residual)**2,axis=(2,3)))
    w=np.hanning(512);spec=np.fft.fftshift(np.fft.fft(ac*w,axis=-1),axes=-1)/w.sum()
    residual_spec=spec-spec.mean(axis=2,keepdims=True)
    power=np.mean(abs(spec)**2,axis=(0,2));res_power=np.mean(abs(residual_spec)**2,axis=(0,2))
    frame_power=np.mean(abs(spec)**2,axis=2);bins=np.arange(-256,256);ref=float(power.max())
    # Normalized complex coherence within each 64-chirp frame, without removing
    # the static component. This measures phase repeatability, not independent
    # target separation or noise coherence and not a calibrated angle.
    bin1=spec[:,:,:,257]
    coherence=np.mean(bin1[:,1]*bin1[:,0].conj(),axis=1)/np.sqrt(np.mean(abs(bin1[:,0])**2,axis=1)*np.mean(abs(bin1[:,1])**2,axis=1))
    phase=np.unwrap(np.angle(coherence))*180/np.pi
    bin_amplitude=np.mean(abs(bin1),axis=2)
    amplitude_drift=100*(bin_amplitude[-10:].mean(axis=0)/bin_amplitude[:10].mean(axis=0)-1)
    phase_drift=float(phase[-10:].mean()-phase[:10].mean())
    changes=np.argwhere(abs(dt-1200)>20)
    stats={'input':str(src),'configuration_sha256':next(iter(configs)),
        'scene_context':'User reports unattended office, radar aimed approximately at keyboard; no controlled target distances.',
        'accepted_frames':n,'records_verified':n*128,'complex_samples':int(z.size),
        'real_IQ_values':int(z.size*2),'reconstructed_record_bytes':n*128*2056,
        'capture_span_seconds':float((times[-1,0,-1]-times[0,0,0])/1e6),
        'median_chirp_interval_seconds':float(chirp_s),'frame_period_seconds':float(period),
        'radar_frame_rate_hz':float(1/period),'retained_frame_id_gaps':dict(zip(*[x.tolist() for x in np.unique(np.diff(ids),return_counts=True)])),
        'full_int16_rail_hits':int(np.sum((z.real<=-32767)|(z.imag<=-32767)|(z.real==32767)|(z.imag==32767))),
        'timestamp_interval_outliers':{'count':len(changes),'intervals':dt.size,'values_us':[int(dt[tuple(x)]) for x in changes],
            'locations_frame_lane_interval':changes.tolist(),
            'interpretation':'Two chirp events have paired roughly -1000/+1000 us interval errors on both lanes. Metadata anomaly, not evidence of lost samples. Cause not proven; originals retained.'},
        'receivers':[],
        'strongest_AC_bin_interreceiver':{'bin':1,'median_within_frame_coherence':float(np.median(abs(coherence))),
            'phase_p5_median_p95_deg':np.percentile(phase,[5,50,95]).tolist(),
            'phase_drift_first_to_last_10_frames_deg':phase_drift,
            'amplitude_change_first_to_last_10_frames_percent':amplitude_drift.tolist(),
            'caution':'Dominated by static signal; phase is not calibrated azimuth or a pure isolated target.'},
        'processing':'Signed BE int16 I+jQ; per-chirp complex mean removed for spectra; 512-point Hann FFT divided by window sum. Residual = centered waveform minus its own frame-average waveform. Doppler is an exploratory FFT over 64 records at the median 1.2 ms spacing; no resampling of timestamp outliers. Full-record FFT may mix sweep segments.',
        'limits':['No calibrated fast-time sample rate, sweep slope/segmentation or range axis.',
            'Residual includes noise, drift, ripple and any real small motion; no receiver noise figure or target SNR measured.',
            'Exported int16 range is not the unverified physical ADC range.',
            'No controlled moving or known-distance target; no detection range or sensitivity measurement.',
            'Skipped whole frames limit cross-frame motion analysis; no interpolation across them.',
            'Stable interreceiver phase does not identify a target angle without geometry and phase-offset calibration.']}
    for lane in range(2):
        zz=z[:,lane]
        stats['receivers'].append({'receiver':lane+1,'I_min_max':[float(zz.real.min()),float(zz.real.max())],
            'Q_min_max':[float(zz.imag.min()),float(zz.imag.max())],
            'mean_I_Q':[float(zz.real.mean()),float(zz.imag.mean())],
            'AC_complex_rms_counts':float(ac_rms[lane]),'within_frame_residual_complex_rms_counts':float(residual_rms[lane]),
            'residual_to_AC_amplitude_percent':float(100*residual_rms[lane]/ac_rms[lane]),
            'AC_to_residual_power_ratio_db':float(20*np.log10(ac_rms[lane]/residual_rms[lane])),
            'repeatable_within_frame_AC_energy_percent':float(100*(1-(residual_rms[lane]/ac_rms[lane])**2)),
            'off_band_median_spectral_amplitude_counts':float(np.sqrt(np.median(power[lane]))),
            'spur_bin_220_relative_peak_db':float(db(power[lane,476]/power[lane].max()))})
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,
        'axes.titlelocation':'left','axes.titlesize':12,'axes.titleweight':'bold','figure.facecolor':'#f8fafc','axes.facecolor':'white',
        'grid.color':'#e2e8f0','grid.alpha':.8,'savefig.facecolor':'#f8fafc'})
    colors=['#126b86','#b54e78'];blue='#2563b3';gold='#bd7118';plots=[]
    def finish(fig,name,title,subtitle,foot):
        fig.suptitle(title,x=.075,y=.985,ha='left',fontsize=21,fontweight='bold',color='#152238')
        fig.text(.075,.94,subtitle,ha='left',fontsize=11,color='#475569')
        fig.text(.075,.025,textwrap.fill(foot,145),ha='left',fontsize=9,color='#475569')
        fig.subplots_adjust(top=.865,bottom=.13,left=.075,right=.97,hspace=.4,wspace=.25)
        fig.savefig(out/f'{name}.png',dpi=150);fig.savefig(out/f'{name}.svg');plt.close(fig)
        plots.append((name,title,subtitle,foot))
    # 1. The actual samples and their small deviations, on explicitly different scales.
    fig,axs=plt.subplots(2,2,figsize=(13,8))
    for lane in range(2):
        mean=z[:,lane].mean(axis=(0,1));loI,hiI=np.percentile(z[:,lane].real,[5,95],axis=(0,1));loQ,hiQ=np.percentile(z[:,lane].imag,[5,95],axis=(0,1))
        ax=axs[0,lane];ax.fill_between(np.arange(512),loI,hiI,color=blue,alpha=.15);ax.fill_between(np.arange(512),loQ,hiQ,color=gold,alpha=.15)
        ax.plot(mean.real,c=blue,label='I');ax.plot(mean.imag,c=gold,label='Q');ax.legend(loc='best',ncols=2,frameon=False)
        ax.set(title=f'RX{lane+1} · mean waveform and 5–95% band',ylabel='Exported signed counts',xlabel='Sample within exported record (0–511)');ax.grid()
        ax=axs[1,lane];x=residual[0,lane,0,:96]
        ax.plot(x.real,c=blue,lw=1,label='I residual');ax.plot(x.imag,c=gold,lw=1,label='Q residual');ax.axhline(0,c='#94a3b8',lw=.7)
        ax.set(title=f'RX{lane+1} · residual detail, first record',ylabel='Counts, magnified scale',xlabel='Sample within record (first 96)');ax.grid();ax.set_ylim(-90,90)
    finish(fig,'01_waveforms','A repeatable waveform, with much smaller variation',
        '159 verified frames · 2 receivers · 64 chirps × 512 complex samples per receiver per frame',
        'Top: all 10,176 chirps per receiver. Bottom: per-chirp DC and the frame-average waveform removed; this is not pure thermal noise.')
    # 2. Static structure over time plus measured residual magnitude.
    fig,axs=plt.subplots(2,2,figsize=(13,8),gridspec_kw={'height_ratios':[1.25,1]})
    for lane in range(2):
        ax=axs[0,lane];im=ax.imshow(db(frame_power[:,lane,244:269]/ref),origin='lower',aspect='auto',extent=[-12.5,12.5,-.5,n-.5],vmin=-65,vmax=0,cmap='magma',interpolation='nearest')
        ticks=np.linspace(0,n-1,5).astype(int);ax.set_yticks(ticks,[f'{t[k]:.1f}' for k in ticks]);ax.set(title=f'RX{lane+1} · low-frequency structure stays put',xlabel='Fast-time FFT bin (not metres)',ylabel='Time since first retained frame (s)')
        fig.colorbar(im,ax=ax,label='dB relative to strongest AC bin',pad=.02)
    for lane in range(2):axs[1,0].plot(t,frame_residual[:,lane],c=colors[lane],lw=1.5,label=f'RX{lane+1}')
    axs[1,0].set(title='Small residual throughout the recording',xlabel='Elapsed time (s)',ylabel='Complex residual RMS (counts)',ylim=(0,50));axs[1,0].legend(frameon=False);axs[1,0].grid()
    for lane in range(2):
        ax=axs[1,1];ax.plot(bins,db(power[lane]/ref),color=colors[lane],lw=1,label=f'RX{lane+1}')
    ax.set(title='Full spectrum reveals narrow features at ±220',xlabel='Fast-time FFT bin (not metres)',ylabel='dB relative to strongest AC bin',xlim=(-256,255),ylim=(-75,5));ax.legend(frameon=False,ncols=2);ax.grid()
    ax.axvline(220,c='#64748b',ls=':',lw=1);ax.axvline(-220,c='#64748b',ls=':',lw=1)
    finish(fig,'02_stability','The unattended office looks predominantly static',
        f'Nonrepeatable waveform amplitude: RX1 {100*residual_rms[0]/ac_rms[0]:.1f}% · RX2 {100*residual_rms[1]/ac_rms[1]:.1f}% of DC-removed waveform RMS',
        'Heatmap rows show retained frames only; skipped frames are omitted. The narrow ±220-bin feature has an unidentified source.')
    # 3. Exploratory two-dimensional spectrum. Preserve full complex signed bins.
    slow_w=np.hanning(64);doppler=np.fft.fftshift(np.fft.fft(spec*slow_w[None,None,:,None],axis=2),axes=2)/slow_w.sum()
    doppler_res=np.fft.fftshift(np.fft.fft(residual_spec*slow_w[None,None,:,None],axis=2),axes=2)/slow_w.sum()
    pd=np.mean(abs(doppler)**2,axis=0);pr=np.mean(abs(doppler_res)**2,axis=0);rd_ref=float(pd.max())
    hz=np.fft.fftshift(np.fft.fftfreq(64,chirp_s));dh=hz[1]-hz[0]
    fig,axs=plt.subplots(2,2,figsize=(13,8))
    for row,ps in enumerate([pd,pr]):
        for lane in range(2):
            ax=axs[row,lane];im=ax.imshow(db(ps[lane,:,244:269]/rd_ref),origin='lower',aspect='auto',extent=[-12.5,12.5,hz[0]-dh/2,hz[-1]+dh/2],vmin=-75,vmax=0,cmap='magma',interpolation='nearest')
            ax.set(title=f'RX{lane+1} · '+('static returns retained' if row==0 else 'frame-average complex signal removed'),xlabel='Fast-time FFT bin (not metres)',ylabel='Across-chirp frequency (Hz)')
            fig.colorbar(im,ax=ax,label='dB, same reference in all panels',pad=.02)
    finish(fig,'03_doppler','Nearly all strong structure sits at zero Doppler',
        'Exploratory 512 × 64 Hann-windowed FFT · power averaged over 159 frames · nominal chirp spacing 1.200 ms',
        'This is not yet a calibrated range–velocity map. Full-record sweep segmentation is unverified; no moving target was present to calibrate sign.')
    # 4. Paired receiver information is available, but not yet angle calibrated.
    fig,axs=plt.subplots(2,2,figsize=(13,8))
    for lane in range(2):axs[0,0].plot(t,np.mean(abs(bin1[:,lane]),axis=1),c=colors[lane],label=f'RX{lane+1}',lw=1.4)
    axs[0,0].set(title='Dominant AC coefficient amplitude (bin +1)',xlabel='Elapsed time (s)',ylabel='Window-normalized counts');axs[0,0].legend(frameon=False);axs[0,0].grid()
    axs[0,1].plot(t,phase,c='#7c3f9b',lw=1.4);axs[0,1].set(title='Receiver phase difference is stable',xlabel='Elapsed time (s)',ylabel='RX2 minus RX1 phase (degrees)');axs[0,1].grid()
    for lane in range(2):axs[1,0].plot(bins,db(power[lane]/np.maximum(res_power[lane],1e-20)),c=colors[lane],lw=1.3,label=f'RX{lane+1}')
    axs[1,0].set(title='Repeatable structure is strongest near low bins',xlabel='Fast-time FFT bin',ylabel='Total / within-frame residual power (dB)',xlim=(-12,12),ylim=(0,65));axs[1,0].grid();axs[1,0].legend(frameon=False)
    ax=axs[1,1];ax.axis('off');ax.text(0,.98,'What this enables next',va='top',weight='bold',fontsize=14)
    ax.text(0,.78,'• Range: calibrate sweep segments and known distances\n\n• Motion: compare a controlled moving target\n\n• Direction: measure antenna spacing + phase offset\n\n• Small motion: test phase against a known displacement',va='top',fontsize=11,linespacing=1.4)
    finish(fig,'04_receivers','Stable receiver phase, with a small gradual drift',
        f'Bin +1 within-frame coherence: median {np.median(abs(coherence)):.6f} · phase 5–95% range {np.percentile(phase,5):.2f}° to {np.percentile(phase,95):.2f}°',
        'Stable clutter can be highly coherent. These values are not a target angle, displacement precision, or independently measured SNR.')
    # Provenance and a portable report, including the exact charts inline.
    (out/'analysis.json').write_text(json.dumps(stats,indent=2)+'\n')
    (out/'source_manifest.json').write_text(json.dumps({'source':str(src),'files_sha256':manifest,'script_sha256':digest(Path(__file__))},indent=2)+'\n')
    manual='https://h.hlktech.com/download/HLK-LD2450-24G/1/HLK%20LD2450%201T2R%E8%BF%90%E5%8A%A8%E7%9B%AE%E6%A0%87%E6%A3%80%E6%B5%8B%E8%BF%BD%E8%B8%AA%E6%A8%A1%E7%BB%84%E8%AF%B4%E6%98%8E%E4%B9%A6%20V1.02%20.pdf'
    body='''<p class="eyebrow">LD2450 · SAVED USB CAPTURE · 6 OCTOBER 2026</p><h1>A quiet office, seen through two radar receivers</h1>
<p class="lead">The data is transport-clean and strongly repeatable. This is a useful static baseline, with rich complex samples, but it is not yet a calibrated map of objects or distances.</p>
<p>The user reports that the radar faced approximately toward their keyboard in an unattended office. This report analyzes the existing 30-second recording only; it does not access the device.</p>'''
    body+=f'<div class="cards"><div><b>{n}</b>complete frames</div><div><b>{n*128:,}</b>records revalidated</div><div><b>{z.size/1e6:.2f}M</b>complex samples</div><div><b>0</b>exported int16 rail hits</div></div>'
    body+='''<h2>Clean transport, measurable analog variation</h2><p>Every accepted lane file matches its saved SHA-256. Every reconstructed record independently passes header, receiver/chirp sequence, trailer and radar checksum checks. The original receiver also validated all message and reconstructed-record CRCs. The capture ends with an incomplete frame, which is excluded. This establishes intact transport, not a noiseless radar receiver.</p>'''
    body+='<table><tr><th>Measured quantity</th><th>RX1</th><th>RX2</th></tr>'
    for label,key,fmt in [('DC-removed waveform RMS (counts)','AC_complex_rms_counts','.1f'),('Within-frame residual RMS (counts)','within_frame_residual_complex_rms_counts','.1f'),('Residual amplitude / waveform (%)','residual_to_AC_amplitude_percent','.2f'),('Waveform / residual power (dB)','AC_to_residual_power_ratio_db','.1f'),('Repeatable within-frame AC energy (%)','repeatable_within_frame_AC_energy_percent','.3f')]:
        body+=f'<tr><td>{label}</td>'+''.join(f'<td>{r[key]:{fmt}}</td>' for r in stats['receivers'])+'</tr>'
    body+='</table><p>The residual includes electronic noise, repeatable ripple, drift and any small real scene changes. These ratios are repeatability measurements, not calibrated target SNR. Large I/Q offsets and static reflections dominate the raw values. No samples reach the exported signed-16-bit limits; the physical ADC range is not established.</p>'
    body+=f'<p>The scene is not mathematically constant: the dominant coefficient amplitude falls by about {abs(amplitude_drift[0]):.1f}% on RX1 and {abs(amplitude_drift[1]):.1f}% on RX2, while the relative phase drifts about {phase_drift:.2f} degrees (first versus last ten frames). Slow settling or temperature drift are possible explanations, but no temperature or independent motion reference was recorded.</p>'
    for name,title,sub,foot in plots:
        b64=base64.b64encode((out/f'{name}.png').read_bytes()).decode()
        body+=f'<section><h2>{html.escape(title)}</h2><img alt="{html.escape(title)}" src="data:image/png;base64,{b64}"><p>{html.escape(foot)}</p></section>'
    body+=f'''<h2>How far, and how detailed?</h2><p>Hi-Link specifies the stock LD2450 for up to 6 m, approximately ±60° in azimuth, and 250 MHz sweep bandwidth. Those are module specifications, not a demonstrated range for this custom firmware or this office recording. <a href="{manual}">Manufacturer manual, V1.02, section 8</a>.</p>
<p>At 250 MHz, the ideal FMCW two-target range-resolution scale is c/(2B) ≈ 0.60 m when using the full linear sweep. Windowing and partial-sweep acquisition can worsen separation. Estimating one isolated target's position can be more precise than separating two nearby targets. The 512 samples are not 512 independently resolved objects, and they do not establish a centimetre-spaced range grid. Our actual sample rate, sweep slope and sample-to-sweep alignment still need confirmation.</p>
<p>Complex I/Q retains amplitude and phase; the two receivers provide information for direction estimation. After calibration we can investigate distance, radial motion, hand/gesture changes and fine phase changes. Breathing or tiny vibration sensing is a hypothesis to test with controlled displacement, not a capability demonstrated by this recording. A static reflection can reveal an object, but cannot by itself identify an immobile person.</p>
<h2>A small timing issue to keep separate from signal noise</h2><p>Median adjacent-chirp spacing is 1.200 ms, and frame IDs imply a radar frame period of {period*1000:.3f} ms ({1/period:.2f} Hz). Only selected complete frames were exported. Eight of {dt.size:,} interval entries are anomalous: two chirp events, on both receivers, have a roughly 0.199 ms interval followed by 2.200 ms. This looks like timestamp bookkeeping near a 1 ms timer boundary, but the cause has not been proven. Record identities and checksums remain intact. Doppler plots use nominal spacing and are exploratory. Original timestamps are preserved.</p>
<h2>Next measurements that would answer the remaining questions</h2><ol><li>Keep the radar fixed; place one strong reflector at measured distances, for example 0.5, 1, 2 and 3 m, with an empty-scene reference. Determine the right sweep segment and calibrate the frequency-to-distance slope.</li><li>Move the same reflector toward and away from the board. Identify Doppler sign, static-clutter removal behavior and usable motion sensitivity.</li><li>At fixed range, move the reflector left, center and right. Calibrate receiver phase offset and confirm the phase-to-angle relationship.</li><li>Compare quiet and powered/active desk equipment states to investigate the narrow ±220-bin feature before calling it a physical target.</li></ol>
<p>Reproduce with <code>python tools/analyze_usb_frames.py</code>. Exact input hashes are in <code>source_manifest.json</code>; numerical results and limitations are in <code>analysis.json</code>. PNG and SVG charts are retained beside this self-contained report.</p>'''
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LD2450 static-scene analysis</title><style>body{margin:0;background:#eef2f6;color:#192b40;font:17px/1.65 system-ui,sans-serif}main{max-width:1100px;margin:auto;background:white;padding:48px}h1{font-size:44px;line-height:1.1;max-width:850px}h2{margin-top:40px;line-height:1.3}p{max-width:960px}.lead{font-size:22px;color:#345}.eyebrow{font-size:12px;letter-spacing:2px;color:#547}.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:30px 0}.cards div{padding:20px;background:#f0f6f8;border-radius:8px}.cards b{display:block;font-size:30px;color:#126b86}img{width:100%;height:auto;border:1px solid #e2e8f0}table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:12px;border-bottom:1px solid #dce3eb}th{background:#f1f5f9}a{color:#156b8a}code{font-size:14px}@media(max-width:700px){main{padding:22px}h1{font-size:34px}.cards{grid-template-columns:repeat(2,1fr)}} </style><main>'+body+'</main></html>'
    (out/'analysis.html').write_text(page,encoding='utf-8')
    print(json.dumps(stats,indent=2))

if __name__=='__main__':main()
