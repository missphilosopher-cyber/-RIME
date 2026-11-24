"""Export a real repeatable experiment with only Python's standard library.

No fixture or uploaded source is executed. Rerunning replaces generated outputs.
"""
import argparse
import csv
import html
import json
from pathlib import Path
from prime.dataset import CORPUS, run_benchmark


def write_chart(result, target):
    """Render labelled SVG bars from measured family medians."""
    families = {'ascii': 'ASCII tokens', 'syllables': 'Word tokens', 'geometry': 'Geometric tokens'}
    panels = [('median_encode_ms', 'Median encode duration (ms)', '#d9f786', 4),
              ('median_byte_ratio', 'Median output / input bytes', '#c5b7ed', 2)]
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="620" viewBox="0 0 1400 620" role="img" aria-labelledby="title desc">',
             '<title id="title">ΠRIME measured synthetic experiment</title>',
             '<desc id="desc">Family medians for conversion time and byte expansion. Exact values are printed beside each bar. This is not a cryptographic strength chart.</desc>',
             '<rect width="1400" height="620" fill="#101820"/>',
             '<g font-family="Arial,Helvetica,sans-serif" fill="#f5f4ee">',
             '<text x="36" y="48" font-size="28">ΠRIME · Measured synthetic experiment</text>',
             f'<text x="36" y="80" font-size="16" fill="#acb8bf">{html.escape(result["generated_at"])} · Python {html.escape(result["python"])} · {len(result["rows"])} trials</text>']
    for panel_index, (field, title, color, decimals) in enumerate(panels):
        x = 36 + panel_index * 690
        maximum = max((r[field] or 0 for r in result['summary']), default=0) or 1
        parts.append(f'<text x="{x}" y="145" font-size="23">{html.escape(title)}</text>')
        for index, row in enumerate(result['summary']):
            y = 203 + index * 103
            value = row[field] or 0
            width = 455 * value / maximum
            parts.extend([f'<text x="{x}" y="{y}" font-size="19" fill="#acb8bf">{html.escape(families[row["family"]])}</text>',
                          f'<rect x="{x}" y="{y+16}" width="455" height="24" fill="#27333e"/>',
                          f'<rect x="{x}" y="{y+16}" width="{width:.2f}" height="24" fill="{color}"/>',
                          f'<text x="{x+475}" y="{y+36}" font-size="20">{value:.{decimals}f}</text>'])
    parts.extend([f'<text x="36" y="545" font-size="18">{result["exact_trials"]} / {result["valid_trials"]} valid trials recovered exactly; {result["correct_rejections"]} / {result["negative_trials"]} negative trials rejected.</text>',
                  '<text x="36" y="578" font-size="16" fill="#acb8bf">Synthetic fixtures · machine-dependent timings · empty input excluded from size ratios · no program execution</text>',
                  '</g></svg>'])
    target.write_text('\n'.join(parts), encoding='utf-8')


def export_experiment(root, repetitions=3):
    """Save dataset, raw measurements, metadata, readable summary and chart."""
    root = Path(root)
    data = root / 'data'
    reports = root / 'reports'
    data.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    result = run_benchmark(repetitions)
    corpus = {'provenance': result['provenance'], 'samples': CORPUS}
    (data/'synthetic_corpus.json').write_text(json.dumps(corpus, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (reports/'experiment.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    with (reports/'measured_trials.csv').open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(result['rows'][0]))
        writer.writeheader()
        writer.writerows(result['rows'])
    write_chart(result, reports/'experiment_charts.svg')
    lines = ['# Measured experiment results', '', f'Generated: {result["generated_at"]} (UTC).', '',
             f'Environment: Python {result["python"]}, {result["platform"]}.', '',
             f'{result["samples"]} fixtures × applicable configurations × {repetitions} repetitions = {len(result["rows"])} actual trials.', '',
             f'- Valid trials: {result["valid_trials"]}; exact recoveries: {result["exact_trials"]}.',
             f'- Deliberate negative trials: {result["negative_trials"]}; correct rejections: {result["correct_rejections"]}.', '',
             '| Family | Valid trials | Exact | Median encode (ms) | Median byte expansion |',
             '|---|---:|---:|---:|---:|']
    for row in result['summary']:
        lines.append(f'| {row["family"]} | {row["trials"]} | {row["exact"]} | {row["median_encode_ms"]:.5f} | {row["median_byte_ratio"]:.2f}× |')
    lines += ['', '![Measured conversion and size charts](experiment_charts.svg)', '',
              result['provenance'], '', result['execution'], '',
              'Encode time includes validation and conversion. Decode time includes recovery/comparison and Python AST checks. Total trial time also includes key creation. All are Python-side durations; browser/network overhead is excluded.', '',
              'Byte expansion includes the version header, escaping and token frames. Zero-byte inputs are excluded from ratios. Family medians mix fixture categories and policies. A three-repetition run is a demonstration, not a statistically rigorous performance study.', '',
              'No user study, handwriting-speed result, security strength or external benchmark comparison is inferred from these measurements. Rerun on your own machine before preparing the final report.', '']
    (reports/'experiment_summary.md').write_text('\n'.join(lines), encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repetitions', type=int, choices=(1, 3, 5), default=3)
    parser.add_argument('--out-root', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    result = export_experiment(args.out_root, args.repetitions)
    print(f'Saved {len(result["rows"])} measured trials to {args.out_root.resolve()/"reports"}.')
    print(f'Exact recovery: {result["exact_trials"]}/{result["valid_trials"]}; expected rejections: {result["correct_rejections"]}/{result["negative_trials"]}.')
