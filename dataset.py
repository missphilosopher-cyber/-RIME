"""Synthetic team-authored fixtures and reproducible experimental measurements.

These are samples for software testing, not a survey or evidence of cryptographic security.
Teacher acceptance of a constructed dataset is still required.
"""
import ast
import csv
import io
import platform
from datetime import datetime, timezone
from statistics import median
from time import perf_counter
from .engine import PrimeError, generate_definition, encode, decode, compare_recovery

CORPUS = [
 {'id':'P01','kind':'python','label':'output','source':'print("Hello, world!")\n','expected':'Hello, world!\n'},
 {'id':'P02','kind':'python','label':'condition','source':'score = 72\nif score >= 50:\n    print("Passed")\nelse:\n    print("Try again")\n','expected':'Passed\n'},
 {'id':'P03','kind':'python','label':'loop','source':'total = 0\nfor n in range(5):\n    total += n\nprint(total)\n','expected':'10\n'},
 {'id':'P04','kind':'python','label':'function','source':'def square(x):\n    return x * x\n\nprint(square(7))\n','expected':'49\n'},
 {'id':'P05','kind':'python','label':'strings and comments','source':'# if print should stay inside this comment\ntext = "if print \\\"quoted\\\""\nprint(text)\n','expected':'if print "quoted"\n'},
 {'id':'P06','kind':'python','label':'while','source':'n = 3\nwhile n > 0:\n    print(n)\n    n -= 1\n','expected':'3\n2\n1\n'},
 {'id':'P07','kind':'python','label':'collections','source':'items = [2, 4, 6]\nprint(sum(items))\n','expected':'12\n'},
 {'id':'P08','kind':'python','label':'unicode and brackets','source':'नाम = "ΠRIME ⟦x⟧"\nprint(नाम)\n','expected':'ΠRIME ⟦x⟧\n'},
 {'id':'P09','kind':'python','label':'spacing and CRLF','source':'value  =  3\r\nprint(value) # comment\r\n','expected':'3\n'},
 {'id':'P10','kind':'python','label':'multiline literal','source':'note = """line one\nline two"""\nprint(note)\n','expected':'line one\nline two\n'},
 {'id':'N01','kind':'python','label':'syntax error','source':'if True\n  print(1)','expect_error':True},
 {'id':'N02','kind':'python','label':'unsupported import','source':'import os\nprint(1)\n','expect_error':True},
 {'id':'N03','kind':'python','label':'unsupported attribute','source':'print("hi".upper())\n','expect_error':True},
 {'id':'N04','kind':'python','label':'unsupported f-string','source':'x = 2\nprint(f"value {x}")\n','expect_error':True},
 {'id':'N05','kind':'python','label':'unsupported class','source':'class Example:\n    pass\n','expect_error':True},
 {'id':'N06','kind':'python','label':'empty program','source':'  \n','expect_error':True},
]

def run_benchmark(repetitions=3):
    """Measure each synthetic input across three families and applicable policies."""
    if repetitions not in (1, 3, 5):
        raise PrimeError('Choose one, three or five timing repetitions.')
    rows=[]
    for sample in CORPUS:
        for style in ('ascii','syllables','geometry'):
            policies = ('full','names') if not sample.get('expect_error') else ('full',)
            for policy in policies:
                for repeat in range(1,repetitions+1):
                    trial_started=perf_counter()
                    row={'sample_id':sample['id'],'kind':sample['kind'],'feature':sample['label'],'family':style,'policy':policy,'repeat':repeat,'input_characters':len(sample['source']),'input_bytes':len(sample['source'].encode()),'output_bytes':None,'recovered':None,'ast_matches':None,'expected_rejection':bool(sample.get('expect_error')),'error':''}
                    try:
                        d=generate_definition(sample['kind'],style,sample['source'],policy,seed=repeat)
                        # Measure conversion separately from key generation and validation setup.
                        start=perf_counter()
                        encoded=encode(sample['source'],d)
                        row['encode_ms']=round((perf_counter()-start)*1000,5)
                        t=perf_counter();result=compare_recovery(sample['source'],encoded,d)
                        row['decode_ms']=round((perf_counter()-t)*1000,5)
                        row.update(output_bytes=len(encoded.encode()),recovered=result['matches'],ast_matches=result['ast_matches'])
                        row['status']='unexpected_acceptance' if row['expected_rejection'] else ('exact' if result['matches'] else 'mismatch')
                    except PrimeError as e:
                        row.update(status='expected_rejection' if row['expected_rejection'] else 'error',error=str(e),encode_ms=None,decode_ms=None)
                    row['trial_ms']=round((perf_counter()-trial_started)*1000,5)
                    rows.append(row)
    valid=[r for r in rows if not r['expected_rejection']]
    summary=[]
    for family in ('ascii','syllables','geometry'):
        subset=[r for r in valid if r['family']==family]
        elapsed=[r['encode_ms'] for r in subset if r['encode_ms'] is not None]
        ratios=[r['output_bytes']/r['input_bytes'] for r in subset if r['input_bytes'] and r['output_bytes'] is not None]
        summary.append({'family':family,'trials':len(subset),'exact':sum(r['recovered'] is True for r in subset),'median_encode_ms':round(median(elapsed),5) if elapsed else None,'median_byte_ratio':round(median(ratios),2) if ratios else None})
    return {'generated_at':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),'platform':platform.system(),'provenance':'16 synthetic Python fixtures authored for this ΠRIME prototype; no proprietary source code. Teacher acceptance of this constructed dataset is pending.','samples':len(CORPUS),'repetitions':repetitions,'valid_trials':len(valid),'exact_trials':sum(r['recovered'] is True for r in valid),'negative_trials':sum(r['expected_rejection'] for r in rows),'correct_rejections':sum(r['status']=='expected_rejection' for r in rows),'execution':'No program was executed by this benchmark. Exact recovery and Python AST equality are measured. Trusted demonstration execution is tested separately by the automated test suite.','rows':rows,'summary':summary}
