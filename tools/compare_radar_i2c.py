"""Compare a decoded Saleae I2C CSV with the extracted, hash-verified radar tables."""
import argparse
import csv
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def analyze(capture, manifest_path):
    transactions = []
    active = None
    with capture.open(newline='', encoding='utf-8-sig') as stream:
        for line, row in enumerate(csv.DictReader(stream), 2):
            kind = row['type']
            if kind == 'start':
                if active is not None:
                    raise ValueError(f'Unclosed transaction before line {line}')
                active = dict(start=Decimal(row['start_time']), line=line, address=[], data=[])
            elif active is None:
                raise ValueError(f'Event outside transaction at line {line}')
            elif kind in ('address', 'data'):
                active[kind].append(row)
            elif kind == 'stop':
                active['stop'] = Decimal(row['start_time'])
                transactions.append(active)
                active = None
            else:
                raise ValueError(f'Unexpected event {kind} at line {line}')
    if active is not None or not transactions:
        raise ValueError('Incomplete or empty capture')

    actual = []
    for i, t in enumerate(transactions):
        if len(t['address']) != 1 or len(t['data']) != 3:
            raise ValueError(f'Unexpected transaction structure at line {t["line"]}')
        a = t['address'][0]
        if int(a['address'], 0) != 0x20 or a['read'].lower() != 'false':
            raise ValueError(f'Unexpected device/direction at line {t["line"]}')
        payload = [int(r['data'], 0) for r in t['data']]
        actual.append(dict(sequence=i+1, address_7bit='0x20', register=f'0x{payload[0]:02X}',
                           value=f'0x{int.from_bytes(bytes(payload[1:]), "big"):04X}',
                           payload_hex=bytes(payload).hex(' '),
                           ack_count=sum(r['ack'].lower() == 'true' for r in t['address']+t['data']),
                           start_seconds=str(t['start']), stop_seconds=str(t['stop']),
                           duration_us=float((t['stop']-t['start'])*1000000),
                           preceding_idle_us=None if not i else
                           float((t['start']-transactions[i-1]['stop'])*1000000)))
    captured = [(int(t['register'], 0), int(t['value'], 0)) for t in actual]
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    comparisons = []
    for source in manifest['sources']:
        ufw = ROOT / (source['stem']+'.ufw')
        app = ROOT / source['application']
        if sha(ufw) != source['ufw_sha256'] or sha(app) != source['app_sha256']:
            raise ValueError(f'Firmware source changed: {source["version"]}')
        app_bytes = app.read_bytes()
        for name, table in source['tables'].items():
            records = b''.join(bytes.fromhex(e['raw_record_hex']) for e in table['entries'])
            offset = table['app_file_offset']
            if hashlib.sha256(records).hexdigest() != table['sha256'] or app_bytes[offset:offset+len(records)] != records:
                raise ValueError(f'Extracted table verification failed: {name}')
            expected = [(e['register'], e['value']) for e in table['entries']]
            differences = [dict(sequence=i+1, captured=f'{a[0]:02X}={a[1]:04X}',
                                expected=f'{b[0]:02X}={b[1]:04X}')
                           for i, (a, b) in enumerate(zip(captured, expected)) if a != b]
            comparisons.append(dict(version=source['version'], profile=name,
                                    expected_count=len(expected), captured_count=len(captured),
                                    exact_match=captured == expected, differences=differences,
                                    missing_count=max(0, len(expected)-len(captured)),
                                    extra_count=max(0, len(captured)-len(expected))))
    gaps = [t['preceding_idle_us'] for t in actual[1:]]
    return dict(capture=str(capture.resolve()), capture_sha256=sha(capture),
                extraction_manifest_sha256=sha(manifest_path),
                transaction_count=len(actual), acknowledged_bytes=sum(t['ack_count'] for t in actual),
                expected_acknowledged_bytes=4*len(actual),
                total_span_ms=float((transactions[-1]['stop']-transactions[0]['start'])*1000),
                median_intertransaction_idle_us=statistics.median(gaps) if gaps else None,
                comparisons=comparisons, transactions=actual,
                timing_scope='Decoder START-to-STOP and STOP-to-START timestamps; no power, bias or SPI channels in this CSV.')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('capture', type=Path)
    p.add_argument('--out', type=Path, default=ROOT/'output/i2c_init_comparison')
    args = p.parse_args()
    result = analyze(args.capture, ROOT/'output/radar_init/manifest.json')
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'manifest.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    lines = [f'Capture SHA-256: {result["capture_sha256"]}',
             f'Transactions: {result["transaction_count"]}; ACKs: {result["acknowledged_bytes"]}/{result["expected_acknowledged_bytes"]}',
             f'Total START-to-final-STOP span: {result["total_span_ms"]:.6f} ms',
             f'Median intertransaction idle: {result["median_intertransaction_idle_us"]:.3f} us']
    for c in result['comparisons']:
        lines.append(f'{c["version"]} {c["profile"]}: exact={c["exact_match"]}, differences={len(c["differences"])}, missing={c["missing_count"]}, extra={c["extra_count"]}')
    lines += ['', result['timing_scope'], '', 'Seq  Register Value  Start (s)    Idle before (us)  ACKs']
    for t in result['transactions']:
        idle = '-' if t['preceding_idle_us'] is None else f'{t["preceding_idle_us"]:.3f}'
        lines.append(f'{t["sequence"]:3}  {t["register"]}     {t["value"]}  {t["start_seconds"]:12}  {idle:>12}      {t["ack_count"]}/4')
    (args.out/'report.txt').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print('\n'.join(lines[:8]))


if __name__ == '__main__':
    main()
