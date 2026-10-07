'use strict';
const $ = id => document.getElementById(id);
let registerNotes = {}, registerRows = {};
let token = '', version = -1, generation = -1, current = null, iq = null;
let history = [], binTrail = [], paused = false, recording = false, busy = false, messageUntil = 0;
const colors = ['#55e0d4', '#ee85b0', '#f6b86b', '#ad9fff'];
const fmt = n => Number(n || 0).toLocaleString();

function notice(text, error=false, persistent=false) {
  $('notice').textContent = text; $('notice').hidden = !text;
  $('notice').className = error ? 'error' : '';
  messageUntil = persistent ? Infinity : Date.now() + 8000;
}
async function request(path, body, retry=true) {
  const response = await fetch('/api/' + path, {method:'POST',
    headers:{'Content-Type':'application/json','X-Viewer-Token':token},body:JSON.stringify(body || {})});
  const data = await response.json();
  // The token is per server process: after a server restart, fetch the new one and retry once.
  if (response.status === 403 && retry) { await options(); return request(path, body, false); }
  if (!response.ok) throw new Error(data.error || response.statusText);
  return data;
}
function action(id, callback) {
  $(id).addEventListener('click', async () => {
    if (busy) return;
    busy = true; $(id).disabled = true;
    try { await callback(); } catch (err) { notice(err.message, true); }
    finally { busy = false; $(id).disabled = false; }
  });
}
async function options() {
  const response = await fetch('/api/options');
  if (!response.ok) throw new Error('Cannot load viewer options');
  const data = await response.json(); token = data.token; registerNotes = data.register_notes || {};
  const port = $('port').value, replay = $('replay').value;
  $('port').replaceChildren(...(data.ports.length ? data.ports : ['No matching USB device']).map(p => new Option(p,p)));
  if (data.ports.includes(port)) $('port').value = port;
  $('replay').replaceChildren(...data.sources.map(s => new Option(s.name.replace('output\\stream_bench\\','').replace('\\stream.ldf',''),s.id)));
  if (data.sources.some(s => s.id === replay)) $('replay').value = replay;
  else { const preferred = data.sources.find(s => s.name.includes('usb_budget_guard_capture')); if (preferred) $('replay').value = preferred.id; }
}
action('refresh', options);
action('connect', async () => { await request('connect',{port:$('port').value}); resetDisplay(); notice('USB acquisition started.'); });
action('disconnect', async () => { await request('disconnect'); notice('Disconnected. The USB port is released.'); });
action('play', async () => { await request('replay',{id:$('replay').value}); resetDisplay(); notice('Replay started. Recordings loop automatically.'); });
action('reference', async () => { await request('reference',{enabled:true}); notice('Background captured from the latest acquired frame.'); });
action('clear-reference', async () => { await request('reference',{enabled:false}); notice('Background cleared.'); });
action('iq-calibrate', async () => {
  const c = (await request('iq-calibration',{enabled:true})).calibration;
  notice(`I/Q calibrated from frame ${c.frame}: Q gain ${c.q_gain_db.map(v=>v.toFixed(2)).join(' / ')} dB, phase ${c.phase_deg.map(v=>v.toFixed(1)).join(' / ')} deg (RX1 / RX2).`);
});
action('iq-clear', async () => { await request('iq-calibration',{enabled:false}); notice('I/Q correction cleared.'); });
action('record', async () => { await request(recording?'record/stop':'record/start'); await options(); });
action('snapshot', async () => { const data = await request('snapshot'); notice('Saved latest acquired frame: ' + data.path); });
function resetDisplay() { version=-1; current=iq=null; history=[]; binTrail=[]; paused=false; $('pause').textContent='Freeze display'; $('pause').classList.remove('active'); acceptFrame(null); }
$('pause').addEventListener('click', () => {
  paused = !paused; $('pause').textContent = paused ? 'Resume display' : 'Freeze display'; $('pause').classList.toggle('active',paused);
  if (!paused) { version=-1; history=[]; binTrail=[]; }
  notice(paused ? 'Display frozen. USB acquisition and recording continue; chirp selection still works.' : 'Display resumed; history starts fresh.');
});
// Polls issued before a settings change completes carry stale settings; they must not overwrite the controls.
let settingsPending = 0, settingsChangedAt = 0;
for (const id of ['remove_dc','detrend','window','remove_static']) $(id).addEventListener('change', async () => {
  settingsPending++;
  try { await request('settings',{remove_dc:$('remove_dc').checked,detrend:$('detrend').checked,window:$('window').value,remove_static:$('remove_static').checked}); }
  catch (err) { notice(err.message,true); }
  finally { settingsPending--; settingsChangedAt = performance.now(); }
});
for (const id of ['receiver','chirp','mean','color-min','color-max','doppler-min','doppler-max','history-mode','auto-scale','constellation-mode']) $(id).addEventListener('input', draw);
new ResizeObserver(() => draw()).observe(document.querySelector('main'));

function setup(id, margins={l:48,r:12,t:12,b:29}) {
  const canvas = $(id), rect = canvas.getBoundingClientRect(), dpr = window.devicePixelRatio || 1;
  const width = Math.max(1,Math.round(rect.width*dpr)), height=Math.max(1,Math.round(rect.height*dpr));
  if (canvas.width!==width || canvas.height!==height) {canvas.width=width;canvas.height=height;}
  const ctx=canvas.getContext('2d'); ctx.setTransform(dpr,0,0,dpr,0,0); ctx.clearRect(0,0,rect.width,rect.height);
  ctx.font='10px system-ui';
  return {ctx,w:rect.width,h:rect.height,x:margins.l,y:margins.t,pw:Math.max(1,rect.width-margins.l-margins.r),ph:Math.max(1,rect.height-margins.t-margins.b)};
}
function axes(p,xmin,xmax,ymin,ymax,xTicks,yTicks,grid=true) {
  const {ctx,x,y,pw,ph}=p;
  ctx.strokeStyle='#28364a';ctx.fillStyle='#8195af';ctx.lineWidth=1;
  ctx.textAlign='center';ctx.textBaseline='top';
  for(const val of xTicks){const xx=x+(val-xmin)/(xmax-xmin)*pw; if(grid){ctx.beginPath();ctx.moveTo(xx,y);ctx.lineTo(xx,y+ph);ctx.stroke();}ctx.fillText(String(val),xx,y+ph+8);}
  ctx.textAlign='right';ctx.textBaseline='middle';
  for(const val of yTicks){const yy=y+ph-(val-ymin)/(ymax-ymin)*ph;if(grid){ctx.beginPath();ctx.moveTo(x,yy);ctx.lineTo(x+pw,yy);ctx.stroke();}ctx.fillText(String(val),x-7,yy);}
  ctx.strokeStyle='#40516a';ctx.strokeRect(x,y,pw,ph);
}
function line(p,values,ymin,ymax,color){
  const {ctx,x,y,pw,ph}=p;ctx.save();ctx.beginPath();ctx.rect(x,y,pw,ph);ctx.clip();ctx.strokeStyle=color;ctx.lineWidth=1.15;ctx.beginPath();
  values.forEach((v,i)=>{const xx=x+i/(values.length-1)*pw,yy=y+ph-(v-ymin)/(ymax-ymin)*ph;i?ctx.lineTo(xx,yy):ctx.moveTo(xx,yy);});ctx.stroke();ctx.restore();
}
function empty(p){p.ctx.fillStyle='#708299';p.ctx.textAlign='center';p.ctx.fillText('Waiting for a complete frame',p.w/2,p.h/2);}
const TREND_NORM=Array.from({length:512},(_,n)=>(n-255.5)**2).reduce((a,b)=>a+b,0);
// Applies the frame's DC and linear-trend settings to one real 512-sample part in place.
function clean(values,settings){
  if(!settings.remove_dc&&!settings.detrend)return values;
  let mean=0;for(let n=0;n<512;n++)mean+=values[n];mean/=512;
  let slope=0;if(settings.detrend){for(let n=0;n<512;n++)slope+=(values[n]-mean)*(n-255.5);slope/=TREND_NORM;}
  for(let n=0;n<512;n++)values[n]-=mean+slope*(n-255.5);
  return values;
}
function wave(){
  const p=setup('wave');if(!iq || !current){empty(p);return;}
  const chirps=current.chirps, chirp=Number($('chirp').value), mean=$('mean').checked, traces=[];
  $('chirp-label').textContent=mean?'mean':chirp; $('chirp').disabled=mean;
  for(let rx=0;rx<2;rx++)for(let part=0;part<2;part++){
    const values=new Float32Array(512);
    for(let n=0;n<512;n++){if(mean){for(let c=0;c<chirps;c++)values[n]+=iq[((rx*chirps+c)*512+n)*2+part]/chirps;}else values[n]=iq[((rx*chirps+chirp)*512+n)*2+part];}
    traces.push(clean(values,current.settings));
  }
  let lo=Infinity,hi=-Infinity;for(const values of traces)for(const v of values){lo=Math.min(lo,v);hi=Math.max(hi,v);}
  const span=Math.max(hi-lo,10),step=Math.pow(10,Math.floor(Math.log10(span/4))),ymin=Math.floor((lo-span*.08)/step)*step,ymax=Math.ceil((hi+span*.08)/step)*step;
  const ticks=Array.from({length:5},(_,i)=>Math.round(ymin+(ymax-ymin)*i/4));
  axes(p,0,511,ymin,ymax,[0,128,256,384,511],ticks);traces.forEach((v,i)=>line(p,v,ymin,ymax,colors[i]));
}
function spectrumSpan(){
  const spans={center:{min:-16,max:16,ticks:[-16,-8,0,8,16]},positive:{min:0,max:32,ticks:[0,8,16,24,32]},full:{min:-256,max:255,ticks:[-256,-128,0,128,255]}};
  return spans[$('spectrum-span').value];
}
$('spectrum-span').addEventListener('change',draw);
// Auto ranges follow the visible bins; the spectrum axis uses the whole history so it does not jitter.
function percentileRange(rows,lo=.02,hi=.995,minSpan=10){
  const values=Float32Array.from(rows.flat()).sort();if(!values.length)return [0,minSpan];
  let a=values[Math.floor(lo*(values.length-1))],b=values[Math.ceil(hi*(values.length-1))];
  if(b-a<minSpan){const mid=(a+b)/2;a=mid-minSpan/2;b=mid+minSpan/2;}
  return [a,b];
}
function niceTicks(min,max){const step=[5,10,20,30,50].find(s=>(max-min)/s<=6)||100,ticks=[];for(let v=Math.ceil(min/step)*step;v<=max;v+=step)ticks.push(v);return ticks;}
function spectrumRange(s){
  if(!$('auto-scale').checked)return [-60,90];
  const rows=(history.length?history.map(h=>h.spectrum):[current.products.spectrum.db]).flatMap(rx=>rx.map(v=>v.slice(s.min+256,s.max+257)));
  const [lo,hi]=percentileRange(rows,0,1,20);
  return [Math.floor((lo-3)/10)*10,Math.ceil((hi+3)/10)*10];
}
function spectrum(){const p=setup('spectrum');const data=current?.products.spectrum;if(!data){empty(p);return;}const s=spectrumSpan(),[ymin,ymax]=spectrumRange(s);axes(p,s.min,s.max,ymin,ymax,s.ticks,niceTicks(ymin,ymax));data.db.forEach((v,i)=>line(p,v.slice(s.min+256,s.max+257),ymin,ymax,colors[i*2]));$('spectrum-span-detail').textContent=`Bins ${s.min} to ${s.max} · ${ymin} to ${ymax} dB re 1 count`;}
const stops=[[16,24,45],[35,69,108],[36,143,158],[99,214,178],[239,225,139],[255,151,102]];
function heatColor(v,min,max){const t=Math.max(0,Math.min(.99999,(v-min)/(max-min)))*(stops.length-1),i=Math.floor(t),f=t-i;return stops[i].map((a,c)=>Math.round(a+(stops[i+1][c]-a)*f));}
function heat(p,rows,min,max){
  if(!rows.length)return;
  const height=rows.length,width=rows[0].length,canvas=document.createElement('canvas');canvas.width=width;canvas.height=height;
  const ctx=canvas.getContext('2d'),pixels=ctx.createImageData(width,height);
  const palette=Array.from({length:256},(_,i)=>heatColor(min+(max-min)*i/255,min,max));
  for(let r=0;r<height;r++)for(let c=0;c<width;c++){const offset=(r*width+c)*4,col=palette[Math.max(0,Math.min(255,Math.round((rows[r][c]-min)/(max-min)*255)))];pixels.data[offset]=col[0];pixels.data[offset+1]=col[1];pixels.data[offset+2]=col[2];pixels.data[offset+3]=255;}
  ctx.putImageData(pixels,0,0);p.ctx.imageSmoothingEnabled=false;p.ctx.drawImage(canvas,p.x,p.y,p.pw,p.ph);
}
function heatRange(rows,minId,maxId){
  if($('auto-scale').checked)return percentileRange(rows);
  const min=Number($(minId).value),max=Number($(maxId).value);return max>min?[min,max]:[min,min+5];
}
function waterfall(){
  const p=setup('waterfall');let mode=$('history-mode').value;
  // A viewer server started before the change stage existed publishes no change product.
  const fallback=mode==='change' && history.length>0 && !history.some(h=>h.change);if(fallback)mode='spectrum';
  $('history-subtitle').textContent=(fallback?'Absolute spectrum (restart the viewer server for change mode)':mode==='change'?'Change from running average':'Absolute spectrum')+' · newest at the bottom · last 160 views';
  const rows=history.filter(h=>h[mode]).map(h=>h[mode][Number($('receiver').value)]);
  if(!rows.length){empty(p);return;}
  const s=spectrumSpan(),visible=rows.map(r=>r.slice(s.min+256,s.max+257)),[min,max]=heatRange(visible,'color-min','color-max');
  heat(p,visible,min,max);axes(p,s.min-.5,s.max+.5,0,rows.length,s.ticks,[0,Math.round(rows.length/2),rows.length],false);
  $('history-count').textContent=rows.length+' displayed frames · age in rows';
  $('history-detail').textContent=`Signed FFT bin · colour ${min.toFixed(0)} to ${max.toFixed(0)} dB`;
}
function doppler(){const p=setup('doppler');const data=current?.products.doppler;if(!data){empty(p);return;}const rx=Number($('receiver').value),rows=[...data.db[rx]].reverse(),[min,max]=heatRange(rows,'doppler-min','doppler-max');heat(p,rows,min,max);const ymin=data.hz[0],ymax=data.hz.at(-1),bound=Math.floor(Math.min(-ymin,ymax)/100)*100;axes(p,-64,64,ymin,ymax,[-64,-32,0,32,64],[-bound,-bound/2,0,bound/2,bound],false);const quality=current.products.quality;$('doppler-detail').textContent=(quality?`${quality.chirp_interval_us} µs / chirp · ${(1e6/quality.chirp_interval_us/current.chirps).toFixed(1)} Hz / bin${quality.timing_outliers?' · timing outliers':''} · `:'')+`colour ${min.toFixed(0)} to ${max.toFixed(0)} dB`;}
// Complex value of one signed FFT bin per chirp, matching the server's window/DC settings (no background).
function binValues(frame,samples,k){
  const chirps=frame.chirps,hann=frame.settings.window==='hann',out=[];let wsum=0;const w=new Float32Array(512);
  for(let n=0;n<512;n++){w[n]=hann?.5-.5*Math.cos(2*Math.PI*n/511):1;wsum+=w[n];}
  for(let rx=0;rx<2;rx++){const points=[];for(let c=0;c<chirps;c++){
    const base=(rx*chirps+c)*512*2,I=new Float32Array(512),Q=new Float32Array(512);
    for(let n=0;n<512;n++){I[n]=samples[base+2*n];Q[n]=samples[base+2*n+1];}clean(I,frame.settings);clean(Q,frame.settings);
    let re=0,im=0;for(let n=0;n<512;n++){const a=-2*Math.PI*k*n/512,i=I[n]*w[n],q=Q[n]*w[n];re+=i*Math.cos(a)-q*Math.sin(a);im+=i*Math.sin(a)+q*Math.cos(a);}
    points.push([re/wsum,im/wsum]);}out.push(points);}
  return out;
}
// Constellation scale grows at once so no point leaves the plot, then shrinks slowly.
// Shrinking is per new frame (about 8/s), not per redraw: 4% per frame, roughly 3 s to halve.
let constellationScale={key:null,frame:null,r:0};
function constellationRange(peak,key){
  const s=constellationScale;
  if(s.key!==key){s.key=key;s.frame=current.frame_id;s.r=peak;return s.r;}
  if(peak>=s.r)s.r=peak;
  else if(s.frame!==current.frame_id)s.r=Math.max(peak,s.r*.96);
  s.frame=current.frame_id;
  return s.r;
}
function constellation(){
  const p=setup('constellation',{l:48,r:12,t:12,b:29}),mode=$('constellation-mode').value,k=Number($('constellation-bin').value);
  $('constellation-bin-label').textContent=k;$('constellation-bin').disabled=mode!=='bin';
  if(!iq||!current){empty(p);return;}
  let sets;
  if(mode==='raw'){
    const chirps=current.chirps,chirp=Number($('chirp').value),mean=$('mean').checked;
    sets=[0,1].map(rx=>{const pts=[];for(let n=0;n<512;n++){let i=0,q=0;if(mean){for(let c=0;c<chirps;c++){const b=((rx*chirps+c)*512+n)*2;i+=iq[b]/chirps;q+=iq[b+1]/chirps;}}else{const b=((rx*chirps+chirp)*512+n)*2;i=iq[b];q=iq[b+1];}pts.push([i,q]);}
      const I=clean(Float32Array.from(pts,v=>v[0]),current.settings),Q=clean(Float32Array.from(pts,v=>v[1]),current.settings);
      return [Array.from(I,(v,n)=>[v,Q[n]])];});
    $('constellation-subtitle').textContent=`Raw I versus Q · ${mean?'mean of chirps':'chirp '+chirp} · DC/trend follow settings`;
  } else {
    sets=[0,1].map(rx=>binTrail.filter(t=>t.k===k).map(t=>t.points[rx]));
    $('constellation-subtitle').textContent=`Bin ${k} per chirp · last ${sets[0].length} frames, oldest faded · motion appears as rotation`;
  }
  let r=1;for(const rx of sets)for(const pts of rx)for(const [i,q] of pts)r=Math.max(r,Math.abs(i),Math.abs(q));
  r=constellationRange(r*1.08,mode+(mode==='bin'?k:''));
  const side=Math.min(p.pw,p.ph),sq={...p,x:p.x+(p.pw-side)/2,pw:side,ph:side};
  const t=Math.pow(10,Math.floor(Math.log10(r))),step=r/t>=5?t*2:r/t>=2?t:t/2,ticks=[];for(let v=-Math.floor(r/step)*step;v<=r;v+=step)ticks.push(Number(v.toPrecision(6)));
  axes(sq,-r,r,-r,r,ticks.length>7?ticks.filter((_,i)=>i%2===0):ticks,ticks.length>7?ticks.filter((_,i)=>i%2===0):ticks);
  const {ctx}=p;ctx.save();ctx.beginPath();ctx.rect(sq.x,sq.y,side,side);ctx.clip();
  sets.forEach((frames,rx)=>frames.forEach((pts,f)=>{ctx.globalAlpha=frames.length>1?.12+.88*(f+1)/frames.length:.8;ctx.fillStyle=colors[rx*2];
    for(const [i,q] of pts){ctx.fillRect(sq.x+(i+r)/(2*r)*side-1.25,sq.y+side-(q+r)/(2*r)*side-1.25,2.5,2.5);}}));
  ctx.restore();
  $('constellation-detail').textContent=`±${Number(r.toPrecision(3))} ${mode==='raw'?'exported counts':'counts (FFT, window-normalized)'}`;
}
$('constellation-bin').addEventListener('input',()=>{binTrail=[];if(current&&iq)binTrail.push({k:Number($('constellation-bin').value),points:binValues(current,iq,Number($('constellation-bin').value))});draw();});
function spectrogram(){
  const p=setup('spectrogram');const data=current?.products.spectrogram;if(!data){empty(p);return;}
  // The published STFT covers bins -64..64; wider spans are clamped to it.
  const s=spectrumSpan(),lo=Math.max(s.min,data.bins[0]),hi=Math.min(s.max,data.bins[1]);
  const ticks=s.ticks.filter(t=>t>=lo&&t<=hi);if(lo!==s.min||hi!==s.max)ticks.splice(0,ticks.length,lo,lo/2,0,hi/2,hi);
  const rows=data.db[Number($('receiver').value)].map(r=>r.slice(lo-data.bins[0],hi-data.bins[0]+1));
  // Auto: the strongest 40 dB only, so the dominant structure stands out instead of saturating.
  let [min,max]=heatRange(rows,'color-min','color-max');if($('auto-scale').checked){max=percentileRange(rows,.999,.999,0)[1];min=max-40;}
  heat(p,rows,min,max);
  const c=data.centers,half=data.hop/2,ymin=c.at(-1)+half,ymax=c[0]-half;
  axes(p,lo-.5,hi+.5,ymin,ymax,ticks,[c[0],256,c.at(-1)],false);
  // Peak trace: strongest bin per row, ignoring |bin| < 2 (DC residue), parabolic sub-bin estimate.
  const peaks=rows.map(r=>{let best=-1;r.forEach((v,i)=>{if(Math.abs(lo+i)>=2&&(best<0||v>r[best]))best=i;});
    const d=best>0&&best<r.length-1?(r[best-1]-r[best+1])/(2*(r[best-1]-2*r[best]+r[best+1])||1):0;return lo+best+(Number.isFinite(d)?Math.max(-.5,Math.min(.5,d)):0);});
  const {ctx}=p,px=b=>p.x+(b-(lo-.5))/(hi-lo+1)*p.pw,py=v=>p.y+p.ph-(v-ymin)/(ymax-ymin)*p.ph;
  ctx.save();ctx.strokeStyle='#ffffff';ctx.fillStyle='#ffffff';ctx.lineWidth=1.5;ctx.beginPath();
  peaks.forEach((b,i)=>i?ctx.lineTo(px(b),py(c[i])):ctx.moveTo(px(b),py(c[i])));ctx.stroke();
  peaks.forEach((b,i)=>{ctx.beginPath();ctx.arc(px(b),py(c[i]),2.5,0,2*Math.PI);ctx.fill();});ctx.restore();
  const mc=c.reduce((a,b)=>a+b,0)/c.length,mb=peaks.reduce((a,b)=>a+b,0)/peaks.length;
  const slope=c.reduce((a,x,i)=>a+(x-mc)*(peaks[i]-mb),0)/c.reduce((a,x)=>a+(x-mc)**2,0);
  const spread=Math.sqrt(peaks.reduce((a,b)=>a+(b-mb)**2,0)/peaks.length);
  $('spectrogram-subtitle').textContent=`Beat frequency along each chirp · ${data.segment}-sample Hann segments every ${data.hop} · a steady reflector gives a straight vertical white trace`;
  $('spectrogram-detail').textContent=`White trace: peak at bin ${mb.toFixed(1)} · tilt ${(slope*(c.at(-1)-c[0])).toFixed(1)} bins start→end · scatter ±${spread.toFixed(1)} · resolution ${data.resolution_bins} bins · colour ${min.toFixed(0)}–${max.toFixed(0)} dB${lo!==s.min||hi!==s.max?' · clamped to ±64':''}`;
}
function draw(){
  for(const id of ['color-min','color-max','doppler-min','doppler-max'])$(id+'-value').textContent=$(id).value+' dB';
  $('manual-scale').hidden=$('auto-scale').checked;
  document.querySelectorAll('.rx-label').forEach(e=>e.textContent='RX'+(Number($('receiver').value)+1));
  wave();spectrum();waterfall();doppler();constellation();spectrogram();
}
function acceptFrame(frame){
  current=frame;if(!frame){iq=null;$('frame-id').textContent='—';$('frame-detail').textContent='Waiting for capture dimensions';$('residual').textContent='—';$('config').textContent='Configuration identity: waiting';$('history-count').textContent='0 displayed frames';$('doppler-detail').textContent='Waiting for timing';draw();return;}
  $('chirp').max=frame.chirps-1; $('chirp').value=Math.min(Number($('chirp').value),frame.chirps-1);
  $('mean-label').textContent='Mean of '+frame.chirps; $('doppler-tag').textContent=frame.chirps+' CHIRP FFT';
  const bytes=Uint8Array.from(atob(frame.iq_base64),c=>c.charCodeAt(0));
  // Explicit little-endian interpretation also works on a big-endian browser host.
  const view=new DataView(bytes.buffer);iq=new Int16Array(bytes.length/2);for(let i=0;i<iq.length;i++)iq[i]=view.getInt16(i*2,true);
  const k=Number($('constellation-bin').value);binTrail.push({k,points:binValues(frame,iq,k)});if(binTrail.length>40)binTrail.shift();
  if(frame.products.spectrum){history.push({spectrum:frame.products.spectrum.db,change:frame.products.change?.db});if(history.length>160)history.shift();}
  $('frame-id').textContent=fmt(frame.frame_id);
  $('frame-detail').textContent=`${frame.chirps} chirps / RX - ${frame.processing_ms.toFixed(1)} ms DSP`;
  const quality=frame.products.quality;
  $('residual').textContent=quality?quality.residual_percent.map(v=>v.toFixed(1)+'%').join(' / '):'—';
  $('config').textContent='Configuration: '+frame.config_sha256;
  const balance=frame.products.iq_balance, cal=frame.iq_calibration;
  const mirror=balance?`Mirror now ${balance.image_db.map(v=>v.toFixed(1)).join(' / ')} dB (RX1 / RX2, fit residual ${balance.fit_residual.map(v=>v.toFixed(2)).join(' / ')}).`:'';
  $('iq-state').textContent=cal
    ?`Correcting: Q gain ${cal.q_gain_db.map(v=>v.toFixed(2)).join(' / ')} dB, phase ${cal.phase_deg.map(v=>v.toFixed(1)).join(' / ')} deg from frame ${cal.frame} (was ${cal.image_before_db.map(v=>v.toFixed(1)).join(' / ')} dB). ${mirror} Cleared when settings or registers change. Raw waveform and constellation stay uncorrected.`
    :`No I/Q correction. ${mirror} Calibrate on a static scene with a strong reflector; the fit uses the latest frame.`;
  draw();
}
// Radar registers. Rows are created once and only their value cells refresh,
// so values typed into a row survive the 180 ms state polling.
const hex = (n, width) => n.toString(16).toUpperCase().padStart(width, '0');
function parseHex(text, max, what) {
  const clean = String(text).trim().replace(/^0x/i, '');
  const n = /^[0-9a-f]+$/i.test(clean) ? parseInt(clean, 16) : NaN;
  if (!(n >= 0 && n <= max)) throw new Error(`${what} must be hex 0-${hex(max, max > 255 ? 4 : 2)}`);
  return n;
}
function registerRow(reg) {
  if (registerRows[reg]) return registerRows[reg];
  const note = registerNotes[reg] || {}, row = document.createElement('tr');
  const stock = note.stock === undefined ? 'not written' : hex(note.stock, 4) + (note.writes && note.writes.length > 1 ? ' *' : '');
  row.innerHTML = `<td class="mono">0x${reg.toUpperCase()}</td><td></td><td class="mono">${stock}</td><td class="mono current">—</td>` +
    `<td class="set"><input class="hex" maxlength="4"><button>Write</button><button>Read</button></td>`;
  const cell = row.children[1];
  cell.textContent = note.function ? note.function + (note.meaning ? ' · ' + note.meaning : '') : '';
  if (note.finding) {
    const bench = document.createElement('div');
    bench.className = 'finding'; bench.textContent = 'Bench: ' + note.finding;
    bench.title = note.evidence ? 'Evidence: ' + note.evidence : '';
    cell.append(bench);
  }
  row.title = note.writes && note.writes.length > 1 ? 'Written several times at startup: ' + note.writes.map(v => hex(v, 4)).join(', ') : '';
  const [input, write, read] = row.querySelectorAll('input,button');
  write.addEventListener('click', () => registerAction(() => request('register/write', {register: parseInt(reg, 16), value: parseHex(input.value, 0xFFFF, 'Value')})));
  read.addEventListener('click', () => registerAction(() => request('register/read', {register: parseInt(reg, 16), count: 1})));
  registerRows[reg] = row;
  const rows = $('register-rows'), after = Object.keys(registerRows).sort().find(k => k > reg);
  rows.insertBefore(row, after ? registerRows[after] : null);
  return row;
}
async function registerAction(callback) {
  try { await callback(); } catch (err) { notice(err.message, true); }
}
$('register-dump').addEventListener('click', () => registerAction(() => request('register/read', {register: 0, count: 128})));
$('register-stock').addEventListener('click', () => registerAction(async () => {
  for (const [reg, note] of Object.entries(registerNotes))
    if (note.stock !== undefined) await request('register/read', {register: parseInt(reg, 16), count: 1});
}));
$('register-reinit').addEventListener('click', () => registerAction(() => request('register/reinit')));
$('register-read-one').addEventListener('click', () => registerAction(() => request('register/read', {register: parseHex($('register-address').value, 255, 'Register'), count: 1})));
$('register-write-one').addEventListener('click', () => registerAction(() => request('register/write', {register: parseHex($('register-address').value, 255, 'Register'), value: parseHex($('register-value').value, 0xFFFF, 'Value')})));
const opNames = {1: 'READ', 2: 'WRITE', 3: 'REINIT'};
let registerLogKey = '';
function updateRegisters(r) {
  if (!r) return;
  for (const reg of Object.keys(registerNotes)) registerRow(reg);
  for (const [reg, entry] of Object.entries(r.values)) {
    const row = registerRow(reg), note = registerNotes[reg];
    row.querySelector('.current').textContent = hex(entry.value, 4) + (entry.op === 'write' ? ' (written)' : '');
    row.classList.toggle('changed', note !== undefined && note.stock !== entry.value);
    row.classList.toggle('failed', !entry.ok);
  }
  for (const [reg, row] of Object.entries(registerRows)) if (!(reg in r.values)) {
    row.querySelector('.current').textContent = '—'; row.classList.remove('changed', 'failed');
  }
  $('register-summary').textContent = `Register generation ${r.generation === null ? '— (no reply yet)' : r.generation} · ` +
    `${Object.keys(r.values).length} registers known · ${r.pending} pending` + (r.timed_out ? ` · ${r.timed_out} unanswered (firmware without register control?)` : '');
  const key = r.log.length ? r.log.at(-1).tag + ':' + r.log.length : '';
  if (key !== registerLogKey) {
    registerLogKey = key;
    $('register-log').replaceChildren(...[...r.log].reverse().map(e => {
      const li = document.createElement('li');
      const values = e.values.map(v => hex(v, 4)).join(' ');
      li.textContent = `${new Date(e.at * 1000).toLocaleTimeString()} ${opNames[e.op] || e.op} 0x${hex(e.register, 2)}` +
        `${values ? ' = ' + values : ''} · ${e.status}${e.driver_error ? ' (' + e.driver_error + ')' : ''} · gen ${e.generation}` +
        `${e.latency_s !== null ? ' · ' + Math.round(e.latency_s * 1000) + ' ms' : ''}`;
      return li;
    }));
  }
}
function updateState(state,polledAt=Infinity){
  updateRegisters(state.registers);
  const s=state.stats,stale=state.last_frame_age_s===null || state.last_frame_age_s>2;
  const limited=stale && state.last_abort_age_s!==null && state.last_abort_age_s<3;
  $('status').textContent=state.status==='live'?(limited?'LIVE · EXPORT LIMITED':stale?'LIVE · WAITING':'LIVE · USB'):state.status.toUpperCase();
  $('status').className='badge '+(state.status==='error'?'error':stale&&state.status==='live'?'warn':state.status);
  $('source').textContent=state.source || 'Waiting for a source';
  $('rate').textContent=Number(s.wire_kbps).toFixed(0);$('fps').textContent=Number(s.frames_per_second).toFixed(1);
  $('frames').textContent=fmt(s.complete_frames)+' total complete frames';
  for(const [id,key] of Object.entries({'parser-errors':'parser_errors','protocol-errors':'protocol_errors',rejected:'rejected_frames',resync:'discarded_bytes','device-skips':'device_skipped','device-rejects':'device_rejected','queue-aborts':'queue_aborts','cpu-aborts':'cpu_aborts','other-aborts':'other_aborts','invalid-frames':'invalid_frames',drops:'processing_drops',timing:'timing_outliers'}))$(id).textContent=fmt(s[key]);
  const reasons={1:'prior frame incomplete',2:'invalid radar record or sequence',3:'output buffer full',4:'timeout',5:'acquisition or USB gap',6:'CPU backlog guard'};
  $('abort-detail').textContent=s.last_abort?`Last device abort: ${reasons[s.last_abort.reason] || 'reason '+s.last_abort.reason} · frame ${fmt(s.last_abort.frame_id)} · ${s.last_abort.received_records}/${s.last_abort.expected_records} records arrived. This candidate is not displayed.`:'No firmware abort observed in this connection.';
  $('health-summary').textContent=`${state.last_frame_age_s===null?'No frame yet':'Last processed frame '+state.last_frame_age_s.toFixed(1)+' s ago'} · ${fmt(s.received_bytes)} wire bytes · ${s.replay_loops} replay loops${s.truncated_tail?' · partial recording tail discarded':''}${paused?' · display frozen':''}`;
  recording=!!state.recording;$('record').textContent=recording?'Stop recording':'Start raw recording';$('record').classList.toggle('active',recording);
  $('record-state').textContent=recording?`${(state.recording.bytes/1e6).toFixed(1)} MB recorded · ${state.recording.path}`:state.last_recording?'Saved: '+state.last_recording:'Original USB bytes and SHA-256 manifest. Recording stops automatically at 1 GiB.';
  $('reference-state').textContent=state.reference_frame===null?'No background reference. Subtraction affects spectrum and Doppler.':'Background: frame '+state.reference_frame+'. Applied to spectrum and Doppler.';
  if(!busy && !settingsPending && polledAt>settingsChangedAt && document.activeElement!==$('window')){
    $('remove_dc').checked=state.settings.remove_dc;$('detrend').checked=!!state.settings.detrend;$('window').value=state.settings.window;$('remove_static').checked=state.settings.remove_static;
  }
  if(state.error) notice(state.error,true,true);
  else if(state.frame && Object.keys(state.frame.stage_errors).length)notice('Processing stage error: '+JSON.stringify(state.frame.stage_errors),true,true);
  else if(Date.now()>messageUntil)$('notice').hidden=true;
  if(!paused){
    if(generation!==state.generation){history=[];binTrail=[];generation=state.generation;}
    if(Object.hasOwn(state,'frame') && (!state.frame || state.frame.generation===state.generation))acceptFrame(state.frame);
  }
  version=state.version;
}
async function poll(){
  try {const polledAt=performance.now(),response=await fetch('/api/state?since='+version);if(!response.ok)throw new Error('Viewer server returned '+response.status);updateState(await response.json(),polledAt);}
  catch(err){$('status').textContent='SERVER OFFLINE';$('status').className='badge error';notice(err.message,true);}
  setTimeout(poll,180);
}
options().then(poll).catch(err=>{notice(err.message,true);setTimeout(()=>location.reload(),3000);});
