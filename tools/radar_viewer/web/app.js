'use strict';
const $ = id => document.getElementById(id);
let registerNotes = {}, registerRows = {};
let token = '', version = -1, generation = -1, current = null, bins = null;
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
function resetDisplay() { version=-1; current=bins=null; history=[]; binTrail=[]; paused=false; $('pause').textContent='Freeze display'; $('pause').classList.remove('active'); acceptFrame(null); }
$('pause').addEventListener('click', () => {
  paused = !paused; $('pause').textContent = paused ? 'Resume display' : 'Freeze display'; $('pause').classList.toggle('active',paused);
  if (!paused) { version=-1; history=[]; binTrail=[]; }
  notice(paused ? 'Display frozen. USB acquisition and recording continue; chirp selection still works.' : 'Display resumed; history starts fresh.');
});
// Polls issued before a settings change completes carry stale settings; they must not overwrite the controls.
let settingsPending = 0, settingsChangedAt = 0;
for (const id of ['remove_dc','window','remove_static']) $(id).addEventListener('change', async () => {
  settingsPending++;
  try { await request('settings',{remove_dc:$('remove_dc').checked,window:$('window').value,remove_static:$('remove_static').checked}); }
  catch (err) { notice(err.message,true); }
  finally { settingsPending--; settingsChangedAt = performance.now(); }
});
for (const id of ['receiver','color-min','color-max','doppler-min','doppler-max','history-mode','auto-scale','phase-bin']) $(id).addEventListener('input', draw);
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
// Every product carries its own signed bin range; slice a requested span out of it.
function sliceBins(values,range,s){return values.slice(s.min-range[0],s.max-range[0]+1);}
// Spans are clamped to the bins the frame carries (range bins -(K-1)..(K-1)).
function spectrumSpan(){
  const r=current?.bin_range||[-39,39],h=r[1];
  const spans={center:{min:-16,max:16},positive:{min:0,max:32},full:{min:r[0],max:r[1]}};
  const s=spans[$('spectrum-span').value],min=Math.max(s.min,r[0]),max=Math.min(s.max,r[1]);
  const ticks=$('spectrum-span').value==='full'?[min,Math.round(min/2),0,Math.round(max/2),max]:[min,min+(max-min)/4,min+(max-min)/2,min+3*(max-min)/4,max].map(Math.round);
  return {min,max,ticks:[...new Set(ticks)]};
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
  const range=current.products.spectrum.bins;
  const rows=(history.length?history.map(h=>h.spectrum):[current.products.spectrum.db]).flatMap(rx=>rx.map(v=>sliceBins(v,range,s)));
  const [lo,hi]=percentileRange(rows,0,1,20);
  return [Math.floor((lo-3)/10)*10,Math.ceil((hi+3)/10)*10];
}
function spectrum(){const p=setup('spectrum');const data=current?.products.spectrum;if(!data){empty(p);return;}const s=spectrumSpan(),[ymin,ymax]=spectrumRange(s);axes(p,s.min,s.max,ymin,ymax,s.ticks,niceTicks(ymin,ymax));data.db.forEach((v,i)=>line(p,sliceBins(v,data.bins,s),ymin,ymax,colors[i*2]));$('spectrum-span-detail').textContent=`Bins ${s.min} to ${s.max} · ${ymin} to ${ymax} dB re 1 count`;}
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
  const s=spectrumSpan(),range=current.products.spectrum.bins,visible=rows.map(r=>sliceBins(r,range,s)),[min,max]=heatRange(visible,'color-min','color-max');
  heat(p,visible,min,max);axes(p,s.min-.5,s.max+.5,0,rows.length,s.ticks,[0,Math.round(rows.length/2),rows.length],false);
  $('history-count').textContent=rows.length+' displayed frames · age in rows';
  $('history-detail').textContent=`Signed range bin · colour ${min.toFixed(0)} to ${max.toFixed(0)} dB`;
}
function doppler(){const p=setup('doppler');const data=current?.products.doppler;if(!data){empty(p);return;}const rx=Number($('receiver').value),rows=[...data.db[rx]].reverse(),[min,max]=heatRange(rows,'doppler-min','doppler-max');heat(p,rows,min,max);const ymin=data.hz[0],ymax=data.hz.at(-1),bound=Math.floor(Math.min(-ymin,ymax)/100)*100;const [b0,b1]=data.fast_bins;axes(p,b0-.5,b1+.5,ymin,ymax,[b0,Math.round(b0/2),0,Math.round(b1/2),b1],[-bound,-bound/2,0,bound/2,bound],false);
  // Detections: circles at their interpolated range bin and Doppler frequency.
  const step=(data.hz[1]-data.hz[0])||1,{ctx}=p;ctx.save();ctx.strokeStyle='#ffffff';ctx.lineWidth=1.5;
  for(const t of current.products.targets?.targets||[]){const xx=p.x+(t.range_bin-(b0-.5))/(b1-b0+1)*p.pw,yy=p.y+p.ph-(t.doppler_hz-(ymin-step/2))/(ymax-ymin+step)*p.ph;ctx.beginPath();ctx.arc(xx,yy,7,0,2*Math.PI);ctx.stroke();}
  ctx.restore();const quality=current.products.quality;$('doppler-detail').textContent=(quality?`${quality.chirp_interval_us} µs / chirp · ${(1e6/quality.chirp_interval_us/current.chirps).toFixed(1)} Hz / bin${quality.timing_outliers?' · timing outliers':''} · `:'')+`colour ${min.toFixed(0)} to ${max.toFixed(0)} dB`;}
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
// Complex value of one signed range bin per chirp, from the server's processed bins
// (background, I/Q correction, DC and window settings applied).
function binValues(frame,data,k){
  const [rx,chirps,width]=frame.bins_shape,lo=frame.bin_range[0],out=[];
  if(k<lo||k>frame.bin_range[1])return null;
  for(let r=0;r<rx;r++){const points=[];for(let c=0;c<chirps;c++){const b=((r*chirps+c)*width+(k-lo))*2;points.push([data[b],data[b+1]]);}out.push(points);}
  return out;
}
function constellation(){
  const p=setup('constellation',{l:48,r:12,t:12,b:29}),k=Number($('constellation-bin').value);
  $('constellation-bin-label').textContent=k;
  if(!bins||!current){empty(p);return;}
  const sets=[0,1].map(rx=>binTrail.filter(t=>t.k===k).map(t=>t.points[rx]));
  $('constellation-subtitle').textContent=`Range bin ${k} per chirp · last ${sets[0].length} frames, oldest faded · motion appears as rotation`;
  let r=1;for(const rx of sets)for(const pts of rx)for(const [i,q] of pts)r=Math.max(r,Math.abs(i),Math.abs(q));
  r=constellationRange(r*1.08,'bin'+k);
  const side=Math.min(p.pw,p.ph),sq={...p,x:p.x+(p.pw-side)/2,pw:side,ph:side};
  const t=Math.pow(10,Math.floor(Math.log10(r))),step=r/t>=5?t*2:r/t>=2?t:t/2,ticks=[];for(let v=-Math.floor(r/step)*step;v<=r;v+=step)ticks.push(Number(v.toPrecision(6)));
  axes(sq,-r,r,-r,r,ticks.length>7?ticks.filter((_,i)=>i%2===0):ticks,ticks.length>7?ticks.filter((_,i)=>i%2===0):ticks);
  const {ctx}=p;ctx.save();ctx.beginPath();ctx.rect(sq.x,sq.y,side,side);ctx.clip();
  sets.forEach((frames,rx)=>frames.forEach((pts,f)=>{ctx.globalAlpha=frames.length>1?.12+.88*(f+1)/frames.length:.8;ctx.fillStyle=colors[rx*2];
    for(const [i,q] of pts){ctx.fillRect(sq.x+(i+r)/(2*r)*side-1.25,sq.y+side-(q+r)/(2*r)*side-1.25,2.5,2.5);}}));
  ctx.restore();
  $('constellation-detail').textContent=`±${Number(r.toPrecision(3))} counts (range bin, window-normalized)`;
}
$('constellation-bin').addEventListener('input',()=>{binTrail=[];const k=Number($('constellation-bin').value),points=current&&bins?binValues(current,bins,k):null;if(points)binTrail.push({k,points});draw();});
// Top view: radar at bottom centre, y forward, x to the side (positive per the angle calibration sign).
function targetsView(){
  const p=setup('targets',{l:12,r:12,t:16,b:22}),data=current?.products.targets;
  if(!data){empty(p);$('target-rows').replaceChildren();return;}
  const R=data.max_range_m,fov=Math.PI/3,X=R*Math.sin(fov)*1.08,s=Math.min(p.pw/(2*X),p.ph/(R*1.04));
  const cx=p.x+p.pw/2,cy=p.y+p.ph,px=x=>cx+x*s,py=y=>cy-y*s,{ctx}=p;
  ctx.save();ctx.strokeStyle='#28364a';ctx.fillStyle='#8195af';ctx.lineWidth=1;ctx.textAlign='left';ctx.textBaseline='middle';
  for(let r=1;r<=Math.floor(R);r++){ctx.beginPath();ctx.arc(cx,cy,r*s,-Math.PI/2-fov,-Math.PI/2+fov);ctx.stroke();ctx.fillText(r+' m',px(r*Math.sin(fov))+4,py(r*Math.cos(fov)));}
  ctx.setLineDash([4,4]);for(const a of [-fov,0,fov]){ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(px(R*Math.sin(a)),py(R*Math.cos(a)));ctx.stroke();}ctx.setLineDash([]);
  ctx.beginPath();ctx.rect(p.x,p.y,p.pw,p.ph);ctx.clip();
  // This frame's raw detections: small dots. Tracks: trail, marker, id and a 1 s velocity arrow.
  ctx.fillStyle='#8195af';for(const t of data.targets)ctx.fillRect(px(t.x_m)-1.5,py(t.y_m)-1.5,3,3);
  const tracks=current.products.tracks?.tracks||[];ctx.textAlign='left';ctx.textBaseline='bottom';ctx.lineWidth=2;
  for(const t of tracks){const color=t.in_place?'#8195af':t.doppler_mps>=0?colors[0]:colors[2];ctx.strokeStyle=ctx.fillStyle=color;
    ctx.globalAlpha=.6;ctx.beginPath();t.trail.forEach(([x,y],i)=>i?ctx.lineTo(px(x),py(y)):ctx.moveTo(px(x),py(y)));ctx.stroke();
    ctx.globalAlpha=t.coasting?.5:1;ctx.beginPath();ctx.arc(px(t.x_m),py(t.y_m),7,0,2*Math.PI);t.in_place?ctx.stroke():ctx.fill();
    if(!t.in_place){ctx.beginPath();ctx.moveTo(px(t.x_m),py(t.y_m));ctx.lineTo(px(t.x_m+t.vx_mps),py(t.y_m+t.vy_mps));ctx.stroke();}
    ctx.globalAlpha=1;ctx.fillStyle='#e5edf7';ctx.fillText(String(t.id),px(t.x_m)+10,py(t.y_m)-4);}
  ctx.restore();
  const fmt2=(v,d)=>v==null?'—':Number(v).toFixed(d);
  $('target-rows').replaceChildren(...tracks.map(t=>{const row=document.createElement('tr');
    row.innerHTML=`<td>${t.id}</td><td>${fmt2(t.range_m,2)}</td><td>${fmt2(t.angle_deg,1)}</td><td>${fmt2(t.doppler_mps,2)}</td><td>${fmt2(t.range_rate_mps,2)}</td><td>${fmt2(t.age_s,1)}</td><td>${t.in_place?'in place':'moving'}${t.coasting?' · coasting':''}</td>`;return row;}));
  const unc=Object.entries(data.calibrated).filter(([,v])=>!v).map(([k])=>k),tk=current.products.tracks;
  $('targets-subtitle').textContent=`${data.moving_only?'Moving targets (static removal on)':'All targets (static removal off; capture a background to suppress clutter)'} · CFAR ${data.threshold_db} dB`+(data.clutter_tau_s>0?(tk?.clutter_learning?` · learning persistent clutter (${(tk.clutter_age_s??0).toFixed(0)} of ~${data.clutter_tau_s} s)`:` · clutter map ${data.clutter_tau_s} s`):'')+` · up to ${R} m · ${(data.m_per_bin*100).toFixed(1)} cm/bin`+(data.sweep_step?` (rise step ${data.sweep_step})`:'');
  $('targets-detail').textContent=`${tracks.length} track${tracks.length===1?'':'s'}`+(tk?` (${tk.tentative} tentative)`:'')+` · ${data.targets.length} detection${data.targets.length===1?'':'s'} this frame · noise ${data.noise_db} dB`+(unc.length?` · uncalibrated: ${unc.join(', ')} (see tools/radar_viewer/calibration.json)`:'');
}
// Slow-time phase: the server keeps each bin's chirp-mean value over the last 20 s as a strip
// chart (samples are never revised). The axes stay put until the data leaves them or fills
// under 40% of them, so the past also stays still on screen.
const phaseView={key:null,cx:0,cy:0,r:0,peak:0};
function symTicks(r){const t=Math.pow(10,Math.floor(Math.log10(r))),step=r/t>=5?t*2:r/t>=2?t:t/2,ticks=[];for(let v=-Math.floor(r/step)*step;v<=r+1e-12;v+=step)ticks.push(Number(v.toPrecision(6)));return ticks.length>7?ticks.filter((_,i)=>i%2===0):ticks;}
function phaseOptions(data){
  const select=$('phase-bin'),want=['auto',...data.range_bins.map(String)];
  if([...select.options].map(o=>o.value).join()===want.join())return;
  const value=select.value;
  select.replaceChildren(new Option('Auto · most slow motion','auto'),...data.range_bins.map((k,i)=>new Option(`Bin ${k} · ${data.range_m[i].toFixed(2)} m`,String(k))));
  select.value=want.includes(value)?value:'auto';
}
function phaseViews(){
  const data=current?.products.phase,maps=setup('phase-map'),iqp=setup('phase-iq',{l:12,r:12,t:12,b:12}),disp=setup('phase-disp');
  if(!data||data.filling){
    const text=data?`Collecting history: ${data.window_s.toFixed(1)} of ${data.target_window_s} s`:'Waiting for a complete frame';
    for(const p of [maps,iqp,disp]){p.ctx.fillStyle='#708299';p.ctx.textAlign='center';p.ctx.fillText(text,p.w/2,p.h/2);}
    $('phase-state').textContent='';return;
  }
  phaseOptions(data);
  const chosen=$('phase-bin').value==='auto'?data.auto_bin:Number($('phase-bin').value),i=Math.max(0,data.range_bins.indexOf(chosen)),k=data.range_bins[i],b=data.bins[i];
  $('phase-state').textContent=`auto: bin ${data.auto_bin} · ${data.window_s.toFixed(0)} s window · ${data.frames} frames`;
  // Map: range bin across, slow-time Hz up; breathing sits near ±0.2–0.5 Hz.
  const rows=[...data.map_db].reverse(),[min,max]=percentileRange(rows,.05,.999,20),b0=data.range_bins[0],b1=data.range_bins.at(-1),f=data.hz.at(-1);
  heat(maps,rows,min,max);axes(maps,b0-.5,b1+.5,-f,f,data.range_bins.filter((_,j)=>data.range_bins.length<14||j%2===0),[-3,-2,-1,0,1,2,3].filter(v=>Math.abs(v)<=f),false);
  {const {ctx}=maps,w=maps.pw/(b1-b0+1);ctx.strokeStyle='#ffffff';ctx.lineWidth=1.5;ctx.strokeRect(maps.x+(k-b0)*w,maps.y,w,maps.ph);}
  // I/Q path about the fitted centre; equal axes.
  const v=phaseView,key=k+':'+current.generation;if(v.key!==key){v.key=key;v.r=v.peak=0;}
  const pts=data.iq[i],[cx,cy]=data.centre[i];let x0=Infinity,x1=-Infinity,y0=Infinity,y1=-Infinity;
  for(const [a,q] of pts){x0=Math.min(x0,a);x1=Math.max(x1,a);y0=Math.min(y0,q);y1=Math.max(y1,q);}
  const half=Math.max(x1-x0,y1-y0,1e-9)/2;
  if(x0<v.cx-v.r||x1>v.cx+v.r||y0<v.cy-v.r||y1>v.cy+v.r||half<.4*v.r){v.cx=(x0+x1)/2;v.cy=(y0+y1)/2;v.r=half*1.3;}
  const mx=v.cx,my=v.cy,r=v.r;
  const side=Math.min(iqp.pw,iqp.ph),sq={...iqp,x:iqp.x+(iqp.pw-side)/2,pw:side,ph:side},X=a=>sq.x+(a-mx+r)/(2*r)*side,Y=q=>sq.y+side-(q-my+r)/(2*r)*side;
  {const {ctx}=iqp;ctx.strokeStyle='#40516a';ctx.strokeRect(sq.x,sq.y,side,side);ctx.save();ctx.beginPath();ctx.rect(sq.x,sq.y,side,side);ctx.clip();
    for(let j=1;j<pts.length;j++){ctx.globalAlpha=.15+.85*j/pts.length;ctx.strokeStyle=colors[0];ctx.beginPath();ctx.moveTo(X(pts[j-1][0]),Y(pts[j-1][1]));ctx.lineTo(X(pts[j][0]),Y(pts[j][1]));ctx.stroke();}
    ctx.globalAlpha=1;const last=pts.at(-1);ctx.fillStyle='#ffffff';ctx.fillRect(X(last[0])-2.5,Y(last[1])-2.5,5,5);
    ctx.strokeStyle=colors[2];ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(X(cx)-5,Y(cy));ctx.lineTo(X(cx)+5,Y(cy));ctx.moveTo(X(cx),Y(cy)-5);ctx.lineTo(X(cx),Y(cy)+5);ctx.stroke();
    ctx.globalAlpha=.4;ctx.setLineDash([3,3]);ctx.beginPath();ctx.moveTo(X(cx),Y(cy));ctx.lineTo(X(last[0]),Y(last[1]));ctx.stroke();ctx.restore();
    ctx.fillStyle='#8195af';ctx.textAlign='left';ctx.textBaseline='top';ctx.fillText(`±${Number(r.toPrecision(2))} counts`,sq.x+4,sq.y+4);}
  // Displacement at the frames' own times (frames arrive with gaps), fixed 20 s axis.
  const trace=data.disp_mm[i],ts=data.t_s,t0=-data.target_window_s;let m=1e-3;for(const d of trace)m=Math.max(m,Math.abs(d));
  if(m>v.peak||m<.4*v.peak)v.peak=m*1.3;
  const peak=v.peak,tt=[];for(let s=t0;s<=0;s+=5)tt.push(s);
  axes(disp,t0,0,-peak,peak,tt,symTicks(peak));
  {const {ctx,x,y,pw,ph}=disp;ctx.save();ctx.beginPath();ctx.rect(x,y,pw,ph);ctx.clip();ctx.strokeStyle=colors[0];ctx.lineWidth=1.15;ctx.beginPath();
    trace.forEach((d,j)=>{const xx=x+(ts[j]-t0)/-t0*pw,yy=y+ph-(d+peak)/(2*peak)*ph;j?ctx.lineTo(xx,yy):ctx.moveTo(xx,yy);});ctx.stroke();ctx.restore();}
  const bpm=(hz,ratio)=>hz==null?'—':`${(hz*60).toFixed(0)}/min (${hz.toFixed(2)} Hz, ${ratio}× band median)`;
  $('phase-detail').textContent=`Bin ${k} · ${data.range_m[i].toFixed(2)} m · static ${b.static_db} dB · slow motion ${b.motion_db} dB · phase swept ${b.arc_deg.toFixed(0)}° · ${b.disp_pp_mm.toFixed(2)} mm peak to peak · strongest breathing-band line ${bpm(b.breath_hz,b.breath_ratio)} · strongest heart-band line ${bpm(b.heart_hz,b.heart_ratio)}. Rates are only meaningful while someone holds still in this bin; a breathing harmonic can fall in the heart band.`;
}
function draw(){
  for(const id of ['color-min','color-max','doppler-min','doppler-max'])$(id+'-value').textContent=$(id).value+' dB';
  $('manual-scale').hidden=$('auto-scale').checked;
  document.querySelectorAll('.rx-label').forEach(e=>e.textContent='RX'+(Number($('receiver').value)+1));
  targetsView();spectrum();waterfall();doppler();constellation();phaseViews();
}
function acceptFrame(frame){
  current=frame;if(!frame){bins=null;$('frame-id').textContent='—';$('frame-detail').textContent='Waiting for capture dimensions';$('residual').textContent='—';$('config').textContent='Configuration identity: waiting';$('history-count').textContent='0 displayed frames';$('doppler-detail').textContent='Waiting for timing';draw();return;}
  $('doppler-tag').textContent=frame.chirps+' CHIRP FFT';
  $('constellation-bin').min=frame.bin_range[0];$('constellation-bin').max=frame.bin_range[1];
  const bytes=Uint8Array.from(atob(frame.bins_base64),c=>c.charCodeAt(0));
  // Explicit little-endian interpretation also works on a big-endian browser host.
  const view=new DataView(bytes.buffer);bins=new Float32Array(bytes.length/4);for(let i=0;i<bins.length;i++)bins[i]=view.getFloat32(i*4,true);
  const k=Number($('constellation-bin').value),points=binValues(frame,bins,k);if(points)binTrail.push({k,points});if(binTrail.length>40)binTrail.shift();
  // History rows share one bin axis; a different range (new firmware/format) restarts it.
  if(history.length&&String(history.at(-1).bins)!==String(frame.bin_range))history=[];
  if(frame.products.spectrum){history.push({bins:frame.bin_range,spectrum:frame.products.spectrum.db,change:frame.products.change?.db});if(history.length>160)history.shift();}
  $('frame-id').textContent=fmt(frame.frame_id);
  $('frame-detail').textContent=`${frame.chirps} chirps / RX · bins ${frame.bin_range[0]}..${frame.bin_range[1]} (${frame.bins_source==='device'?'device FFT':'host FFT of raw'}) · ${frame.processing_ms.toFixed(1)} ms DSP`;
  const quality=frame.products.quality;
  $('residual').textContent=quality?quality.residual_percent.map(v=>v.toFixed(1)+'%').join(' / '):'—';
  $('config').textContent='Configuration: '+frame.config_sha256;
  const balance=frame.products.iq_balance, cal=frame.iq_calibration;
  const mirror=balance?`Mirror now ${balance.image_db.map(v=>v.toFixed(1)).join(' / ')} dB (RX1 / RX2, fit residual ${balance.fit_residual.map(v=>v.toFixed(2)).join(' / ')}).`:'';
  $('iq-state').textContent=cal
    ?`Correcting: Q gain ${cal.q_gain_db.map(v=>v.toFixed(2)).join(' / ')} dB, phase ${cal.phase_deg.map(v=>v.toFixed(1)).join(' / ')} deg from frame ${cal.frame} (was ${cal.image_before_db.map(v=>v.toFixed(1)).join(' / ')} dB). ${mirror} Cleared when settings or registers change.`
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
// Sweep width: the server enforces minimum power, the revert timer and restore on disconnect.
const sweepName=mhz=>mhz>=1000?mhz/1000+' GHz':mhz+' MHz';
$('sweep').addEventListener('change',()=>{$('sweep-oob').hidden=$('sweep').value==='240';});
action('sweep-apply',async()=>{
  const mhz=Number($('sweep').value),accept=$('sweep-ack').checked;
  if(mhz!==240&&!accept)throw new Error('Tick the acknowledgement to transmit outside 24.0–24.25 GHz.');
  await request('sweep',{mhz,minutes:Number($('sweep-minutes').value),accept});
  $('sweep-ack').checked=false;   // Acknowledge each out-of-band run.
  notice(mhz===240?'Restoring the in-band build profile…':`Applying the ${sweepName(mhz)} sweep at minimum power…`);
});
action('sweep-restore',async()=>{await request('sweep',{mhz:240});notice('Restoring the in-band build profile…');});
function updateSweep(w){
  const badge=$('sweep-badge');
  if(!w){badge.hidden=true;return;}
  const a=w.active,last=w.last?` Last out-of-band sweep (${sweepName(w.last.mhz)}) ended at ${new Date(w.last.at*1000).toLocaleTimeString()}: ${w.last.reason}.`:'';
  badge.hidden=!a&&w.in_band;
  if(a){
    const left=`${Math.floor(a.remaining_s/60)}:${String(a.remaining_s%60).padStart(2,'0')}`;
    badge.textContent=`OUT OF BAND · ${sweepName(a.mhz)} · ${left}`;
    $('sweep-state').textContent={applying:'Applying',active:'Active',failed:'A write failed; restoring',restoring:'Restoring in band'}[a.phase]+
      `: ${sweepName(a.mhz)} sweep, 24.005–${a.top_ghz.toFixed(3)} GHz, minimum power. Returns to in band in ${left}`+
      (a.restore_attempts>1?` (restore attempt ${a.restore_attempts})`:'')+'.';
  }else if(!w.in_band){
    badge.textContent='RADAR NOT IN BAND';
    $('sweep-state').textContent=`The radar reports rise step ${w.live_step} (in band is 20), set before this connection. Use Restore in band now.`;
  }else $('sweep-state').textContent='In band: 240 MHz sweep (24.005–24.245 GHz), stock power.'+last;
}
function updateState(state,polledAt=Infinity){
  updateRegisters(state.registers);
  updateSweep(state.status==='live'?state.sweep:null);
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
    $('remove_dc').checked=state.settings.remove_dc;$('window').value=state.settings.window;$('remove_static').checked=state.settings.remove_static;
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
// Long poll: the server replies as soon as a newer frame is processed (or after 0.5 s),
// so every frame is drawn while the browser keeps up; otherwise it draws the newest.
async function poll(){
  let retry=0;
  try {const polledAt=performance.now(),response=await fetch('/api/state?since='+version+'&wait=0.5');if(!response.ok)throw new Error('Viewer server returned '+response.status);updateState(await response.json(),polledAt);}
  catch(err){$('status').textContent='SERVER OFFLINE';$('status').className='badge error';notice(err.message,true);retry=1000;}
  setTimeout(poll,retry);
}
options().then(poll).catch(err=>{notice(err.message,true);setTimeout(()=>location.reload(),3000);});
