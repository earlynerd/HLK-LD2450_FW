import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { SpreadsheetFile, Workbook } from '@oai/artifact-tool';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const data = JSON.parse(await fs.readFile(path.join(root, 'output/evb1122_analysis/register_write_table.json'), 'utf8'));
const out = path.join(root, 'outputs/01a1059c-a543-7771-b852-4f55722e6cc0');
const support = path.join(root, 'tmp/evb1122_analysis/workbook');
await fs.mkdir(out, { recursive: true });
await fs.mkdir(support, { recursive: true });

const wb = Workbook.create();
const writes = wb.worksheets.add('Register writes');
const timing = wb.worksheets.add('Timing inference');
const ink = '#202B3B', navy = '#263B56', light = '#F3F6F9';
for (const s of [writes, timing]) { s.showGridLines = false; }
writes.tabColor = navy;

function textStyle(sheet, range) {
  sheet.getRange(range).format = { font: { name: 'Arial', size: 10, color: ink }, verticalAlignment: 'top', wrapText: true };
}
function header(sheet, range) {
  sheet.getRange(range).format = { fill: navy, font: { name: 'Arial', size: 10, bold: true, color: '#FFFFFF' },
    verticalAlignment: 'center', horizontalAlignment: 'center', wrapText: true, rowHeightPx: 40 };
}

textStyle(writes, 'A1:L117');
writes.getRange('A2').values = [['LD2450 register writes']];
writes.getRange('A2').format = { font: { name: 'Arial', size: 15, bold: true }, wrapText: false, rowHeightPx: 28 };
writes.getRange('A3').values = [['Assumption: S5KM312CL and ICL1122 share the register meanings. Values are initial profiles recovered from firmware.']];
writes.getRange('A4').values = [['Both V2.04 and V2.14 contain these same profiles. Mode 1 = ROM. Mode 2 = initial RAM, which saved configuration or runtime writes can modify.']];
writes.getRange('A5').values = [['80 writes, 18 profile differences. First 75 precede SPI setup; final 5 follow it. Hex uses h suffix (4207h = 0x4207). Amber flags an uncertain field; red flags a mismatch.']];
writes.getRange('A3:L5').format.wrapText = false;
writes.getRange('A3:L5').format.rowHeightPx = 22;
const heads = ['#', 'Stage', 'Register', 'Mode 1 hex', 'Mode 2 hex', 'Working interpretation', 'Mode 1 meaning', 'Mode 2 meaning', 'Basis', 'Flag', 'Notes / incompatibilities', 'Source IDs'];
writes.getRange('A7:L7').values = [heads];
const columns = ['sequence','stage','register','mode1_value','mode2_value','function','mode1_meaning','mode2_meaning','basis','flag','notes','sources'];
// The bundled renderer interprets 0x-prefixed strings as decimal even with
// text formatting. Conventional h-suffixed hex stays literal in Excel and
// the preview, without changing the underlying word/address meaning.
const rows = data.rows.map(r => columns.map(k => {
  if (k === 'stage') return r[k] === 'pre_spi' ? 'Before SPI' : 'After SPI';
  if (['register','mode1_value','mode2_value'].includes(k)) return r[k].slice(2) + 'h';
  return r[k];
}));
writes.getRange('A8:L87').values = rows;
const table = writes.tables.add('A7:L87', true, 'RadarRegisterWrites');
table.showFilterButton = true;
header(writes, 'A7:L7');
const widths = [44, 80, 66, 82, 82, 220, 310, 310, 134, 115, 440, 85];
widths.forEach((n,i) => { writes.getRangeByIndexes(0,i,117,1).format.columnWidthPx = n; });
writes.getRange('A8:A87').setNumberFormat('0');
writes.getRange('A8:E87').format.horizontalAlignment = 'center';
writes.getRange('C8:E87').setNumberFormat('@');
writes.getRange('C8:E87').format.font = { name: 'Consolas', size: 10, color: ink };
for (let i=0; i<rows.length; i++) {
  const row = i+8;
  const lines = Math.max(...rows[i].map((s,j) => {
    if (typeof s === 'number') return 1;
    // Conservative line estimation at 10pt, including long identifiers.
    return Math.ceil(String(s).length / Math.max(8, Math.floor((widths[j]-16)/7.0)));
  }));
  writes.getRange(`A${row}:L${row}`).format.rowHeightPx = Math.max(56, 10 + lines*18);
  if (i % 2 === 1) writes.getRange(`A${row}:L${row}`).format.fill = light;
  if (data.rows[i].profile_differs) {
    writes.getRange(`D${row}:E${row}`).format.font = { name: 'Consolas', size: 10, bold: true, color: '#245A9B' };
  }
}
writes.getRange('J8:J87').conditionalFormats.add('containsText', {text: 'Incompatibility', format: {fill: '#FBE3DE', font: {color:'#942B20', bold:true}}});
writes.getRange('J8:J87').conditionalFormats.add('containsText', {text: 'Uncertain', format: {fill: '#FFF0C8', font: {color:'#664A0A'}}});
writes.getRange('A83:L83').format.borders = { top: {style:'medium', color:navy} };
writes.freezePanes.freezeRows(7);
writes.freezePanes.freezeColumns(3);

writes.getRange('A90').values = [['Additional gaps and source defects']];
writes.getRange('A90').format = {font:{name:'Arial',size:12,bold:true},wrapText:false};
data.additional_gaps.forEach((g,i) => {
  const row = 92+i;
  writes.getRange(`C${row}`).values = [[g[0]]];
  writes.getRange(`F${row}`).values = [[g[1]]];
  writes.getRange(`G${row}`).values = [[g[2]]];
  writes.getRange(`L${row}`).values = [[g[3]]];
  writes.getRange(`A${row}:L${row}`).format.rowHeightPx = 92;
});
writes.getRange('A99').values = [['Sources for the assumed mapping']];
writes.getRange('A99').format = {font:{name:'Arial',size:12,bold:true},wrapText:false};
writes.getRange('A100').values = [[`EVB source commit: ${data.commit}. Explicit definitions, functional usage and pattern inferences are kept separate in the Basis column.`]];
writes.getRange('A100:L100').format.wrapText = false;
data.sources.forEach((s,i) => {
  const row = 102+i;
  writes.getRange(`C${row}`).values = [[s.id]];
  writes.getRange(`F${row}`).values = [[s.title]];
  writes.getRange(`G${row}`).values = [[s.location]];
  writes.getRange(`H${row}`).values = [[s.url]];
  writes.getRange(`K${row}`).values = [[`SHA256 ${s.sha256}`]];
  writes.getRange(`A${row}:L${row}`).format.rowHeightPx = 120;
});

textStyle(timing, 'A1:G35');
const tw = [245,155,155,150,150,470,105];
tw.forEach((n,i) => { timing.getRangeByIndexes(0,i,35,1).format.columnWidthPx=n; });
timing.getRange('A2').values = [['Chirp timing inference']];
timing.getRange('A2').format={font:{name:'Arial',size:15,bold:true},wrapText:false,rowHeightPx:28};
timing.getRange('A3').values = [['The count arithmetic is exact. Phase names and conversion to microseconds are inferred.']];
timing.getRange('A3:G3').format.wrapText=false;
timing.getRange('A5:B5').values=[['Assumed counts per microsecond',200]];
timing.getRange('A5:B5').format.rowHeightPx=38;
timing.getRange('B5').setNumberFormat('0');
timing.getRange('F5').values=[['200 comes from the SDK calibration factor 410*200. ICL1122 datasheet labels PLLsys as 50 MHz; a separate timer/scaling is not documented. Changing B5 changes only the conditional duration calculations.']];
timing.getRange('G5').values=[['G, I']];
timing.getRange('A5:G5').format.rowHeightPx=76;
timing.getRange('A7:G7').values=[['Parameter','Mode 1 counts','Mode 2 counts','Mode 1 (us)','Mode 2 (us)','Interpretation / evidence','Source IDs']];
header(timing,'A7:G7');
const t1=data.timing_evidence[0],t2=data.timing_evidence[1];
const phaseNames=['T0 at 45/46','T1 at 47/48','T2 at 49/4A','T3 at 4B/4C'];
const desc=['Candidate startup/preparation duration.','SDK T_FSM01 pair. Candidate rising-sweep duration.','Candidate falling-sweep duration.','Candidate stop/idle duration.'];
for(let i=0;i<4;i++) {
  const r=i+9;
  timing.getRange(`A${r}:C${r}`).values=[[phaseNames[i],t1.segments_counts[i],t2.segments_counts[i]]];
  timing.getRange(`D${r}:E${r}`).formulas=[[`=B${r}/$B$5`,`=C${r}/$B$5`]];
  timing.getRange(`F${r}:G${r}`).values=[[desc[i],'P, G, U']];
}
timing.getRange('A13').values=[['Sum of four phases']];
timing.getRange('B13:E13').formulas=[['=SUM(B9:B12)','=SUM(C9:C12)','=SUM(D9:D12)','=SUM(E9:E12)']];
timing.getRange('A14:C14').values=[['Total at 42/43',t1.total_counts,t2.total_counts]];
timing.getRange('D14:E14').formulas=[['=B14/$B$5','=C14/$B$5']];
timing.getRange('F14:G14').values=[['Each total exactly equals its four phase counts. The EVB example also satisfies this relationship.','P']];
timing.getRange('A15').values=[['Sum minus stored total']];
timing.getRange('B15:E15').formulas=[['=B13-B14','=C13-C14','=D13-D14','=E13-E14']];
timing.getRange('F15').values=[['Zero verifies count closure. It does not establish the timer clock.']];
timing.getRange('A18:C18').values=[['Rising-step code',t1.up_step,t2.up_step]];
timing.getRange('A19:C19').values=[['Falling-step code (signed candidate)',t1.down_step_candidate_signed,t2.down_step_candidate_signed]];
timing.getRange('F18:G18').values=[['SDK packs 55/56 as Step01. Physical frequency units are unknown.','G']];
timing.getRange('F19:G19').values=[['SDK packs 57/58 as Step10. Negative values assume two\'s complement.','G']];
timing.getRange('A20').values=[['Up-step × rising count']];
timing.getRange('B20:C20').formulas=[['=B18*B10','=C18*C10']];
timing.getRange('A21').values=[['Down-step magnitude × falling count']];
timing.getRange('B21:C21').formulas=[['=-B19*B11','=-C19*C11']];
timing.getRange('A22').values=[['Relative up/down sweep difference']];
timing.getRange('B22:C22').formulas=[['=(B21-B20)/B20','=(C21-C20)/C20']];
timing.getRange('F22').values=[['About 1.77% in mode 1, zero in mode 2. Supports the phase/step interpretation. Integer rounding is one possible explanation for the small mode 1 difference.']];
timing.getRange('B22:C22').setNumberFormat('0.00%');
timing.getRange('A25:C25').values=[['EVB example phase counts', 'Count', 'Candidate us']];
header(timing,'A25:C25');
const evb=data.timing_evidence[2];
for(let i=0;i<4;i++) {
  const r=i+26;
  timing.getRange(`A${r}:B${r}`).values=[[phaseNames[i],evb.segments_counts[i]]];
  timing.getRange(`C${r}`).formulas=[[`=B${r}/$B$5`]];
}
timing.getRange('A30:B30').values=[['Total at 42/43', evb.total_counts]];
timing.getRange('C30').formulas=[['=B30/$B$5']];
timing.getRange('F26').values=[['Source P supplies the example values. The same four-phase sum works here, independently of the time conversion.']];
timing.getRange('A33').values=[['Source IDs resolve at the bottom of Register writes.']];
timing.getRange('A33:G33').format.wrapText=false;
timing.getRange('A35:C35').values=[['Measured SPI chirp spacing (us)',null,data.capture_cross_check.median_interval_us]];
timing.getRange('C35').setNumberFormat('#,##0.000');
timing.getRange('F35:G35').values=[[`${data.capture_cross_check.adjacent_chirp_intervals} adjacent-chirp intervals, checksum/framing-valid packets. RAM total at proposed scale: 1200 us. Agreement within 0.013% supports the conversion. Individual RF phase durations are not measured.`, 'C']];
timing.getRange('A35:G35').format.rowHeightPx=94;
timing.getRange('B9:C21').setNumberFormat('#,##0');
timing.getRange('D9:E15').setNumberFormat('#,##0.00');
timing.getRange('B26:B30').setNumberFormat('#,##0');
timing.getRange('C26:C30').setNumberFormat('#,##0.00');
timing.getRange('B9:E22').format.horizontalAlignment='right';
timing.getRange('A9:G30').format.rowHeightPx=44;
for(const r of [13,14,15]) timing.getRange(`A${r}:G${r}`).format.fill=light;
timing.getRange('A22:G22').format.rowHeightPx=84;
timing.getRange('A18:G19').format.rowHeightPx=58;
timing.getRange('A15:G15').format.rowHeightPx=58;
timing.getRange('A14:G14').format.rowHeightPx=66;
timing.getRange('A26:G26').format.rowHeightPx=70;

// Verify all 80 values/order/stages against the immutable annotation input.
if(JSON.stringify(writes.getRange('A8:L87').values)!==JSON.stringify(rows)) throw Error('Register rows changed during authoring');
// Verify the conditional clock calculation responds to a changed assumption,
// then restore the proposed factor before the required final recalculation.
timing.getRange('B5').values=[[100]];
wb.recalculate();
if(timing.getRange('D10:E10').values[0].join(',')!=='420,840') throw Error('Clock conversion did not recalculate');
timing.getRange('B5').values=[[200]];
wb.recalculate();
if(timing.getRange('D10:E10').values[0].join(',')!=='210,420') throw Error('Clock conversion not restored');
if(timing.getRange('B15:E15').values[0].some(n => n!==0)) throw Error('Chirp phase sum mismatch');
const inspection = await wb.inspect({kind:'table',range:'Timing inference!A9:G22',include:'values,formulas',tableMaxRows:14,tableMaxCols:7,maxChars:7000});
await fs.writeFile(path.join(support,'timing_inspection.ndjson'), inspection.ndjson);
const errorScan = await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},maxChars:2000});
await fs.writeFile(path.join(support,'error_scan.ndjson'),errorScan.ndjson);
const rendered=[];
for(const [name,sheetName,range] of [
  ['writes_top','Register writes','A1:L13'],
  ['writes_count_mismatch','Register writes','A57:L65'],
  ['writes_spi_boundary','Register writes','A79:L87'],
  ['timing','Timing inference','A1:G35'],
]) {
  const preview=await wb.render({sheetName,range,scale:1,format:'png'});
  const target=path.join(support,`${name}.png`);
  await fs.writeFile(target,new Uint8Array(await preview.arrayBuffer()));
  rendered.push(target);
}
const file=await SpreadsheetFile.exportXlsx(wb);
const target=path.join(out,'ld2450_register_writes.xlsx');
await file.save(target);
await fs.writeFile(path.join(support,'verification.json'),JSON.stringify({
  all80RowsMatch:true,profileDifferences:18,clockInputChangeVerified:true,
  countClosure:timing.getRange('B15:E15').values[0],
  candidatePhaseUsMode1:timing.getRange('D9:D12').values.flat(),
  candidatePhaseUsMode2:timing.getRange('E9:E12').values.flat(),
  sweepResidual:timing.getRange('B22:C22').values[0],rendered,
},null,2));
console.log(JSON.stringify({file:target,rows:80,rendered,errorScan:errorScan.ndjson}));
