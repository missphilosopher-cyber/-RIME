"""Lossless custom representations of Python source. No uploaded code is executed.

A definition is a private translation dictionary, not an encryption key.
The public PRIME/1 envelope contains its dictionary fingerprint, never the key.
"""
from __future__ import annotations
import ast
import base64
import hashlib
import io
import json
import random
import re
import secrets
import tokenize
import unicodedata
from collections import Counter
from time import perf_counter

MAX_TEXT = 10000
MAX_UNITS = 256
STYLES = {
    'ascii': {'name': 'ASCII tokens', 'description': 'Compact aliases using standard keyboard characters.', 'category': 'type'},
    'syllables': {'name': 'Word tokens', 'description': 'Pronounceable aliases for a custom code vocabulary.', 'category': 'type'},
    'geometry': {'name': 'Geometric tokens', 'description': 'Distinct geometric sequences assigned to source tokens.', 'category': 'visual'},
    'dots': {'name': 'Dot patterns', 'description': 'Dot sequences as alternate token spellings.', 'category': 'visual'},
    'pen': {'name': 'Frame symbols', 'description': 'Frame-and-dot notation with short digital aliases.', 'category': 'visual'},
    'angular': {'name': 'Angular symbols', 'description': 'Stroke sequences assigned to source tokens.', 'category': 'visual'},
}
RESERVED = re.compile(r'[\s\\⟦⟧~]')

class PrimeError(ValueError):
    """An actionable validation or translation error."""

def check_text(text):
    if not isinstance(text, str):
        raise PrimeError('Text must be a string.')
    if len(text) > MAX_TEXT:
        raise PrimeError(f'Keep the input to {MAX_TEXT:,} characters for this prototype.')
    try:
        text.encode('utf-8')
    except UnicodeEncodeError as e:
        raise PrimeError('The input contains an invalid Unicode surrogate.') from e
    return text

_ALLOWED = (
    ast.Module, ast.Assign, ast.AugAssign, ast.Name, ast.Load, ast.Store,
    ast.Constant, ast.Expr, ast.BinOp, ast.UnaryOp, ast.BoolOp, ast.Compare,
    ast.If, ast.For, ast.While, ast.Call, ast.keyword, ast.FunctionDef,
    ast.arguments, ast.arg, ast.Return, ast.Break, ast.Continue, ast.Pass,
    ast.List, ast.Tuple, ast.Dict, ast.Set, ast.Subscript, ast.Slice, ast.IfExp,
    ast.operator, ast.unaryop, ast.boolop, ast.cmpop,
)

def inspect_python(source):
    """Validate a declared subset; return its AST without executing it."""
    check_text(source)
    if not source.strip():
        raise PrimeError('Enter a Python program before creating a code language.')
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, RecursionError) as e:
        line = getattr(e, 'lineno', None)
        raise PrimeError(f'Python syntax error{f" on line {line}" if line else ""}: {getattr(e, "msg", str(e))}') from e
    nodes = list(ast.walk(tree))
    if len(nodes) > 2500:
        raise PrimeError('This program is too complex for the prototype.')
    stack = [(tree, 0)]
    while stack:
        item, depth = stack.pop()
        if depth > 100:
            raise PrimeError('Use a program with shallower expressions for this prototype.')
        stack.extend((child, depth + 1) for child in ast.iter_child_nodes(item))
    for node in nodes:
        if not isinstance(node, _ALLOWED):
            raise PrimeError(f'{type(node).__name__} is not in the supported Python subset. Use assignments, arithmetic, conditions, loops, basic functions and calls. Imports, attributes, classes and f-strings are not supported yet.')
        if isinstance(node, ast.Constant) and not isinstance(node.value, (str, int, float, bool, type(None))):
            raise PrimeError('This constant type is not supported yet.')
    return tree


def python_spans(source, policy='full'):
    """Find token spans in valid Python, preserving every gap and original byte spelling."""
    inspect_python(source)
    if policy not in ('full', 'names'):
        raise PrimeError('Choose names or full token concealment.')
    # Tokenizer rows follow LF, not every Unicode character splitlines recognises.
    lines = source.split('\n')
    offsets = [0]
    for line in lines[:-1]:
        offsets.append(offsets[-1] + len(line) + 1)
    def position(point):
        row, col = point
        return offsets[min(row - 1, len(offsets) - 1)] + col
    selected = {tokenize.NAME, tokenize.OP}
    if policy == 'full':
        selected |= {tokenize.STRING, tokenize.NUMBER, tokenize.COMMENT}
    spans = []
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for t in tokens:
            if t.type in selected and t.string:
                start, end = position(t.start), position(t.end)
                spans.append((start, end, f'{tokenize.tok_name[t.type]}:{source[start:end]}'))
    except (tokenize.TokenError, IndentationError) as e:
        raise PrimeError(f'Could not read this Python program: {e}') from e
    return spans


def required_units(kind, source='', policy='full'):
    if kind != 'python':
        raise PrimeError('ΠRIME accepts supported Python source code only.')
    units = list(dict.fromkeys(s[2] for s in python_spans(source, policy)))
    if len(units) > MAX_UNITS:
        raise PrimeError(f'Use a smaller example: at most {MAX_UNITS} different code tokens.')
    return units


def _pool(style, count):
    if style == 'pen':
        base = [str(i) + suffix for suffix in ('', '.', ':') for i in range(1, 10)]
        return base if count <= len(base) else [f'{base[i % 27]}-{i // 27 + 1}' for i in range(count)]
    if style == 'syllables':
        return [a + b for a in ('ka','mi','no','ra','se','tu','vi','zo','lu','pe','da','fi','bo','ye','hu','wa') for b in ('ka','mi','no','ra','se','tu','vi','zo','lu','pe','da','fi','bo','ye','hu','wa')]
    if style == 'dots':
        return [chr(0x2800 + 1 + i % 63) + (chr(0x2801 + i // 63) if count > 63 else '') for i in range(max(count, 26))]
    alphabet = {'geometry': '◇△○□☆⬡', 'angular': '┌┐└┘├┤┬┴┼', 'ascii': '23456789abcdefghjkmnpqrstuvwxyz'}.get(style)
    if not alphabet:
        raise PrimeError('Choose a supported language family.')
    width = 1
    while len(alphabet) ** width < max(count, 26):
        width += 1
    tokens = []
    for i in range(max(count, 26)):
        value, token = i, ''
        for _ in range(width):
            token = alphabet[value % len(alphabet)] + token
            value //= len(alphabet)
        tokens.append(token)
    return tokens


def generate_definition(kind='python', style='ascii', source='', policy='full', name='Research language', locked=None, seed=None):
    units = required_units(kind, source, policy)
    if not isinstance(style, str) or style not in STYLES:
        raise PrimeError('Unknown language family.')
    if not isinstance(name, str) or len(name) > 80:
        raise PrimeError('Use a language name of at most 80 characters.')
    if locked is None:
        locked = {}
    if not isinstance(locked, dict) or any(k not in units for k in locked):
        raise PrimeError('Locked entries must belong to the current program.')
    for v in locked.values():
        _check_token(v)
    if len(set(locked.values())) != len(locked):
        raise PrimeError('Locked entries must have different typing codes.')
    pool = _pool(style, len(units))
    rng = random.Random(seed) if seed is not None else secrets.SystemRandom()
    rng.shuffle(pool)
    available = [x for x in pool if x not in locked.values()]
    while len(available) < len(units) - len(locked):
        token = 'p' + secrets.token_hex(3)
        if token not in available and token not in locked.values():
            available.append(token)
    iterator = iter(available)
    mapping = {unit: locked[unit] if unit in locked else next(iterator) for unit in units}
    result = {'format': 'prime-language', 'version': 1, 'name': name.strip() or 'Research language', 'kind': 'python', 'style': style, 'policy': policy, 'mapping': mapping, 'assets': {}}
    validate_definition(result)
    return result


def _check_token(token):
    if not isinstance(token, str) or not 1 <= len(token) <= 24 or RESERVED.search(token) or any(unicodedata.category(c).startswith('C') for c in token):
        raise PrimeError('Typing codes need 1–24 characters without spaces, backslashes, ⟦, ⟧ or ~.')
    check_text(token)


def validate_definition(d):
    """Validate private packs completely before accepting a replacement."""
    if not isinstance(d, dict) or d.get('format') != 'prime-language' or d.get('version') != 1:
        raise PrimeError('This is not a supported ΠRIME language pack (version 1).')
    if d.get('kind') != 'python':
        raise PrimeError('ΠRIME accepts Python source language packs only.')
    if not isinstance(d.get('style'), str) or d['style'] not in STYLES:
        raise PrimeError('The pack has an unsupported language type or family.')
    if not isinstance(d.get('name'), str) or len(d['name']) > 80:
        raise PrimeError('The language needs a name of at most 80 characters.')
    d.setdefault('assets', {})
    mapping = d.get('mapping')
    if not isinstance(mapping, dict) or not 1 <= len(mapping) <= MAX_UNITS:
        raise PrimeError('Supply a nonempty mapping with at most 256 entries.')
    if d.get('policy') not in ('names', 'full'):
        raise PrimeError('The Python token policy is missing.')
    seen = {}
    for unit, token in mapping.items():
        if not isinstance(unit, str) or len(unit) > MAX_TEXT:
            raise PrimeError('Invalid source entry.')
        if not re.match(r'^(NAME|OP|STRING|NUMBER|COMMENT):.+', unit, re.S):
            raise PrimeError('A Python mapping has an invalid token category.')
        _check_token(token)
        if token in seen:
            raise PrimeError(f'{seen[token]} and {unit} share “{token}”. Give every entry a unique typing code.')
        seen[token] = unit
    assets = d.get('assets', {})
    if not isinstance(assets, dict) or len(assets) > MAX_UNITS:
        raise PrimeError('Invalid sign attachments.')
    total_bytes = 0
    for unit, value in assets.items():
        if unit not in mapping or not isinstance(value, str) or not value.startswith('data:image/png;base64,'):
            raise PrimeError('Attached signs must be PNG images assigned to a mapped entry.')
        try:
            data = base64.b64decode(value.split(',', 1)[1], validate=True)
        except (ValueError, TypeError) as e:
            raise PrimeError('An attached sign is not valid base64.') from e
        if len(data) > 80000 or not data.startswith(b'\x89PNG\r\n\x1a\n'):
            raise PrimeError('Each sign must be a PNG smaller than 80 KB.')
        total_bytes += len(data)
    if total_bytes > 2_000_000:
        raise PrimeError('Keep the total sign attachments below 2 MB.')
    return d


def definition_id(d):
    validate_definition(d)
    core = {k: d[k] for k in ('kind', 'policy', 'mapping')}
    return hashlib.sha256(json.dumps(core, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]


def audit_definition(d):
    validate_definition(d)
    warnings = []
    long = sum(len(v) > 6 for v in d['mapping'].values())
    if long:
        warnings.append(f'{long} aliases are longer than six characters. Consider shorter aliases to reduce representation size.')
    if d['assets'] and len(set(d['assets'].values())) < len(d['assets']):
        warnings.append('Some entries use identical pictures. Their typing codes differ, but the pictures may be ambiguous.')
    warnings.append('The Python key is specific to its listed tokens. A program containing new tokens needs an updated key.')
    warnings.append('Repeated tokens and layout can reveal patterns. This is reversible encoding, not secure encryption.')
    return {'id': definition_id(d), 'entries': len(d['mapping']), 'unique': len(set(d['mapping'].values())), 'attachments': len(d['assets']), 'warnings': warnings}


def _escape(text):
    return ''.join('\\' + c if c in '\\⟦⟧' else c for c in text)


def encode(source, d):
    check_text(source)
    validate_definition(d)
    parts, end = [], 0
    for start, stop, unit in python_spans(source, d['policy']):
        if unit not in d['mapping']:
            raise PrimeError(f'This key has no entry for {unit[:60]}. Generate an updated code language for this program.')
        parts.extend((_escape(source[end:start]), '⟦' + d['mapping'][unit] + '⟧'))
        end = stop
    parts.append(_escape(source[end:]))
    payload = ''.join(parts)
    return f'PRIME/1 {d["kind"]} {definition_id(d)}\n{payload}'


def read_payload(encoded, d):
    if not isinstance(encoded, str) or len(encoded) > 600000:
        raise PrimeError('The disguised document is too large.')
    first, sep, payload = encoded.partition('\n')
    expected = f'PRIME/1 {d["kind"]} {definition_id(d)}'
    if not sep or first != expected:
        raise PrimeError('Document and language key do not match. Import the matching private pack, and keep the PRIME/1 header intact.')
    return payload


def representation_parts(encoded, d):
    """Read framed tokens and escaped literals without evaluating them."""
    validate_definition(d)
    payload = read_payload(encoded, d)
    reverse = {v: k for k, v in d['mapping'].items()}
    pieces, literal = [], []
    def flush():
        if literal:
            pieces.append({'literal': ''.join(literal)})
            literal.clear()
    i = 0
    while i < len(payload):
        c = payload[i]
        if c == '\\':
            i += 1
            if i >= len(payload) or payload[i] not in '\\⟦⟧':
                raise PrimeError('Malformed literal escape in the disguised document.')
            literal.append(payload[i])
        elif c == '⟦':
            flush()
            end = payload.find('⟧', i + 1)
            if end == -1:
                raise PrimeError('A disguised token is missing its closing ⟧.')
            token = payload[i + 1:end]
            raw = token
            if raw not in reverse:
                raise PrimeError(f'Unknown code “{raw[:30]}”. Check the token or use the matching language key.')
            unit = reverse[raw]
            value = unit.split(':', 1)[1]
            pieces.append({'unit': unit, 'token': raw, 'value': value})
            i = end
        elif c == '⟧':
            raise PrimeError('Unexpected closing ⟧ in the disguised document.')
        else:
            literal.append(c)
        i += 1
    flush()
    return pieces


def decode(encoded, d):
    pieces = representation_parts(encoded, d)
    source = ''.join(p.get('literal', p.get('value', '')) for p in pieces)
    check_text(source)
    inspect_python(source)
    return source


def compare_recovery(source, encoded, d):
    check_text(source)
    started = perf_counter()
    restored = decode(encoded, d)
    match = source == restored
    first = next((i + 1 for i, (a, b) in enumerate(zip(source, restored)) if a != b), None)
    if first is None and len(source) != len(restored):
        first = min(len(source), len(restored)) + 1
    syntax_match = ast.dump(inspect_python(source), include_attributes=False) == ast.dump(inspect_python(restored), include_attributes=False)
    return {'restored': restored, 'matches': match, 'first_difference': first, 'ast_matches': syntax_match, 'decode_ms': round((perf_counter() - started) * 1000, 4), 'original_characters': len(source), 'restored_characters': len(restored)}


def analyse(source, encoded, d):
    pieces = representation_parts(encoded, d)
    counts = Counter(p['token'] for p in pieces if 'token' in p)
    literal = ''.join(p.get('literal', '') for p in pieces)
    return {'input_characters': len(source), 'input_bytes': len(source.encode()), 'output_bytes': len(encoded.encode()), 'token_count': sum(counts.values()), 'distinct_used': len(counts), 'literal_characters': len(literal), 'frequencies': [{'token': k, 'count': v} for k, v in counts.most_common(12)], 'pieces': pieces[:1800], 'preview_truncated': len(pieces) > 1800}


def prompt_style(prompt, fallback='ascii'):
    """Small transparent preference parser; no external model or hidden transmission."""
    prompt = str(prompt).lower()[:500]
    rules = [('syllables', ('word', 'pronounc', 'syllab')), ('ascii', ('keyboard', 'ascii', 'compact')), ('dots', ('dot',)), ('angular', ('angular', 'corner', 'stroke')), ('geometry', ('geometr',)), ('pen', ('frame',))]
    for style, keywords in rules:
        if any(x in prompt for x in keywords):
            return style, f'Matched {STYLES[style]["name"]} from your token preferences. Generation uses local rules, not an AI model.'
    return fallback, 'Using the selected family. Supported preferences: ASCII, words, geometric, dots, angular and frames.'
