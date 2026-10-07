"""Plot decoded, checksum-valid records without assuming RF calibration."""
import argparse
import json
from pathlib import Path
import struct
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p=argparse.ArgumentParser();p.add_argument('directory',type=Path);a=p.parse_args()
r=json.loads((a.directory/'report.json').read_text())
fig,axes=plt.subplots(2,2,figsize=(12,7),sharex=True)
stats={}
for lane in (0,1):
    raw=(a.directory/f'lane{lane}.bin').read_bytes()
    recs=r['lanes'][str(lane)]['valid_records']
    if not recs: raise ValueError(f'No valid records for lane {lane}')
    iq=np.array([struct.unpack('>'+str(rec['pairs']*2)+'h',raw[rec['offset']+4:rec['offset']+rec['size']-4]) for rec in recs],dtype=float)
    z=iq[:,::2]+1j*iq[:,1::2]
    for k in range(len(recs)):
        axes[lane,0].plot(z[k].real,color='#2563eb',alpha=.25,lw=.7)
        axes[lane,0].plot(z[k].imag,color='#ea580c',alpha=.25,lw=.7)
    axes[lane,0].plot(z[0].real,color='#2563eb',lw=1,label='I, first chirp')
    axes[lane,0].plot(z[0].imag,color='#ea580c',lw=1,label='Q, first chirp')
    axes[lane,0].set_title(f'RX{lane}: {len(recs)} verified chirps overlaid',loc='left')
    axes[lane,0].set_ylabel('Signed sample value');axes[lane,0].legend(fontsize=8)
    axes[lane,0].grid(alpha=.2)
    delta=np.abs(z-z[0])
    im=axes[lane,1].imshow(delta,aspect='auto',origin='lower',interpolation='nearest',extent=[0,z.shape[1]-1,-.5,len(recs)-.5],cmap='viridis')
    axes[lane,1].set_title('I/Q difference magnitude from first chirp',loc='left')
    axes[lane,1].set_ylabel('Record order');fig.colorbar(im,ax=axes[lane,1],label='Sample units')
    stats[lane]={'records':len(recs),'chirps':[rec['chirp'] for rec in recs],
                 'adjacent_iq_rms_difference':np.sqrt(np.mean(np.abs(np.diff(z,axis=0))**2,axis=1)).tolist(),
                 'contiguous':all(b['offset']==c['offset']+c['size'] for c,b in zip(recs,recs[1:]))}
for ax in axes[1]:ax.set_xlabel('Sample index (uncalibrated)')
fig.suptitle('Dual-receiver capture: waveforms and chirp-to-chirp variation')
fig.tight_layout();fig.savefig(a.directory/'chirp-comparison.png',dpi=150)
(a.directory/'sequence-summary.json').write_text(json.dumps(stats,indent=2)+'\n')
print(json.dumps(stats,indent=2))
