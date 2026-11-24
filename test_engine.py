import contextlib
import copy
import io
import json
import subprocess
import sys
import unittest
from app import create_app
from prime.engine import (PrimeError, STYLES, generate_definition, encode, decode,
    compare_recovery, inspect_python, validate_definition, audit_definition,
    definition_id, prompt_style)
from prime.dataset import CORPUS, run_benchmark

SOURCE = 'value = 42\nprint(value)\n'
def make_definition(source=SOURCE, **kwargs):
    return generate_definition(source=source, **kwargs)


class DefinitionTests(unittest.TestCase):
    def test_aliases_unique_under_all_families(self):
        for family in STYLES:
            with self.subTest(family=family):
                d=make_definition(style=family)
                self.assertEqual(len(set(d['mapping'].values())),len(d['mapping']))
                self.assertEqual(decode(encode(SOURCE,d),d),SOURCE)

    def test_prefix_aliases_remain_unambiguous(self):
        source='x = 1\n';d=make_definition(source)
        for key,alias in zip(d['mapping'],['x','xx','xxx']):d['mapping'][key]=alias
        self.assertEqual(decode(encode(source,d),d),source)

    def test_duplicate_reserved_and_invisible_aliases_rejected(self):
        for code in ['', 'two words', 'x~', '⟦a', 'a\\', 'x\x00', '\u200b']:
            d=make_definition();d['mapping']['NAME:value']=code
            with self.subTest(code=repr(code)),self.assertRaises(PrimeError):validate_definition(d)
        d=make_definition();d['mapping']['NAME:value']=d['mapping']['NAME:print']
        with self.assertRaisesRegex(PrimeError,'share'):validate_definition(d)

    def test_wrong_key_detected(self):
        first=make_definition(seed=1);second=make_definition(seed=2)
        with self.assertRaisesRegex(PrimeError,'do not match'):decode(encode(SOURCE,first),second)

    def test_fingerprint_tracks_rules_but_not_display_name(self):
        d=make_definition();fingerprint=definition_id(d);d['name']='Another name'
        self.assertEqual(definition_id(d),fingerprint)
        d['mapping']['NAME:value']='new-alias'
        self.assertNotEqual(definition_id(d),fingerprint)

    def test_malformed_envelopes_rejected(self):
        d=make_definition();header=encode(SOURCE,d).partition('\n')[0]+'\n'
        for payload in ['⟦missing','⟦not-in-key⟧','⟧','\\q','\\']:
            with self.subTest(payload=payload),self.assertRaises(PrimeError):decode(header+payload,d)
        with self.assertRaises(PrimeError):decode('plain',d)

    def test_locked_codes_survive_regeneration(self):
        d=make_definition(locked={'NAME:value':'keep-value'})
        self.assertEqual(d['mapping']['NAME:value'],'keep-value')
        with self.assertRaises(PrimeError):make_definition(locked={'NAME:value':'x','NAME:print':'x'})
        with self.assertRaises(PrimeError):make_definition(locked={'NAME:missing':'x'})

    def test_pack_and_public_representation_are_separate(self):
        d=make_definition();public=encode(SOURCE,d)
        self.assertNotIn('mapping',public);self.assertNotIn('NAME:value',public)
        self.assertIn('NAME:value',json.dumps(d))
        self.assertEqual(decode(public,json.loads(json.dumps(d))),SOURCE)

    def test_invalid_input_types_limits_and_surrogates(self):
        d=make_definition()
        for source in ['x'*10001,'\ud800',123,None]:
            with self.subTest(source_type=type(source)),self.assertRaises(PrimeError):encode(source,d)

    def test_png_pack_serialisation_and_validation(self):
        d=make_definition()
        d['assets']['NAME:value']='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jVb8AAAAASUVORK5CYII='
        self.assertEqual(audit_definition(d)['attachments'],1)
        self.assertEqual(decode(encode(SOURCE,d),json.loads(json.dumps(d))),SOURCE)
        for value in ['https://example.com/image.png','data:image/svg+xml;base64,AA==','data:image/png;base64,AA==']:
            d['assets']['NAME:value']=value
            with self.assertRaises(PrimeError):validate_definition(d)

    def test_missing_policy_rejected(self):
        d=make_definition();del d['policy']
        with self.assertRaises(PrimeError):validate_definition(d)

    def test_non_program_language_packs_rejected(self):
        d=make_definition();d['kind']='text'
        with self.assertRaisesRegex(PrimeError,'Python source'):validate_definition(d)
        with self.assertRaises(PrimeError):generate_definition(kind='text',source='example')

    def test_prompt_rules_use_code_token_preferences(self):
        for phrase,style in [('compact ASCII','ascii'),('word tokens','syllables'),('geometric tokens','geometry'),('dot patterns','dots'),('frame symbols','pen'),('angular symbols','angular')]:
            self.assertEqual(prompt_style(phrase)[0],style)


class ProgramTests(unittest.TestCase):
    def test_valid_corpus_exact_recovery_and_ast_under_all_families_and_policies(self):
        for fixture in CORPUS:
            if fixture.get('expect_error'):continue
            for policy in ('full','names'):
                for style in STYLES:
                    with self.subTest(sample=fixture['id'],policy=policy,style=style):
                        d=make_definition(fixture['source'],style=style,policy=policy)
                        result=compare_recovery(fixture['source'],encode(fixture['source'],d),d)
                        self.assertTrue(result['matches']);self.assertTrue(result['ast_matches'])

    def test_new_tokens_need_updated_definition(self):
        d=make_definition('x = 1\n')
        with self.assertRaisesRegex(PrimeError,'no entry'):encode('y = 9\n',d)

    def test_full_policy_conceals_selected_literals_and_comments(self):
        source='# internal-comment\nsecret_name = "internal-value"\nprint(secret_name, 123456)\n'
        d=make_definition(source);public=encode(source,d)
        for value in ['internal-comment','secret_name','internal-value','123456','print']:
            self.assertNotIn(value,public)
        self.assertEqual(decode(public,d),source)

    def test_names_policy_keeps_literals_visible(self):
        source='x = "visible literal" # visible comment\n'
        d=make_definition(source,policy='names');public=encode(source,d)
        self.assertIn('visible literal',public);self.assertIn('visible comment',public)
        self.assertEqual(decode(public,d),source)

    def test_escaped_markers_and_unicode_literal_boundaries(self):
        for separator in ['\u2028','\u2029','\u0085','\x0b','\x0c']:
            source='s = "ΠRIME नमस्ते ⟦x⟧ ~ '+separator+'"\nprint(s)\n'
            for policy in ('full','names'):
                d=make_definition(source,policy=policy)
                self.assertEqual(decode(encode(source,d),d),source)

    def test_edited_document_is_compared_without_regeneration(self):
        d=make_definition();encoded=encode(SOURCE,d)+'\n'
        result=compare_recovery(SOURCE,encoded,d)
        self.assertFalse(result['matches']);self.assertEqual(result['first_difference'],len(SOURCE)+1)
        self.assertTrue(result['ast_matches'])

    def test_negative_corpus_rejected(self):
        for sample in CORPUS:
            if sample.get('expect_error'):
                with self.subTest(sample=sample['id']),self.assertRaises(PrimeError):inspect_python(sample['source'])

    def test_only_fixed_trusted_repository_demos_execute(self):
        # Test fixtures only: source equality is checked before launching Python.
        for sample in CORPUS:
            if 'expected' not in sample:continue
            d=make_definition(sample['source']);restored=decode(encode(sample['source'],d),d)
            self.assertEqual(restored,sample['source'])
            process=subprocess.run([sys.executable,'-I','-S','-c',restored],capture_output=True,text=True,timeout=2)
            self.assertEqual(process.returncode,0,process.stderr)
            self.assertEqual(process.stdout,sample['expected'])

    def test_api_does_not_execute_uploaded_source(self):
        source='print("SHOULD_NOT_EXECUTE")\n';d=make_definition(source)
        client=create_app(testing=True).test_client();capture=io.StringIO()
        with contextlib.redirect_stdout(capture):response=client.post('/api/encode',json={'definition':d,'source':source})
        self.assertEqual(response.status_code,200);self.assertEqual(capture.getvalue(),'')


class ApiAndDatasetTests(unittest.TestCase):
    def setUp(self):self.client=create_app(testing=True).test_client()

    def test_source_workspace_and_catalog(self):
        page=self.client.get('/');self.assertEqual(page.status_code,200)
        self.assertNotIn(b'data-purpose',page.data)
        self.assertNotIn(b'symbol-keyboard',page.data)
        self.assertIn(b'Original Python source',page.data)
        self.assertEqual(len(self.client.get('/api/catalog').json['styles']),6)
        samples=self.client.get('/api/corpus').json['samples']
        self.assertEqual(len(samples),16);self.assertTrue(all(x['kind']=='python' for x in samples))

    def test_page_nonce_required_in_real_app(self):
        client=create_app().test_client()
        self.assertEqual(client.post('/api/generate',json={'source':SOURCE}).status_code,403)
        self.assertIn("default-src 'self'",client.get('/').headers['Content-Security-Policy'])

    def test_generate_apply_encode_verify(self):
        response=self.client.post('/api/generate',json={'source':SOURCE,'style':'syllables'})
        self.assertEqual(response.status_code,200);self.assertEqual(len(response.json['candidates']),3)
        d=response.json['candidates'][0]['definition'];self.assertEqual(d['kind'],'python')
        self.assertEqual(self.client.post('/api/validate',json={'definition':d}).status_code,200)
        encoded=self.client.post('/api/encode',json={'source':SOURCE,'definition':d}).json['encoded']
        result=self.client.post('/api/verify',json={'source':SOURCE,'encoded':encoded,'definition':d}).json
        self.assertTrue(result['matches']);self.assertTrue(result['ast_matches'])

    def test_json_csv_import_and_atomic_failure(self):
        import csv
        d=make_definition();stream=io.StringIO();writer=csv.writer(stream)
        writer.writerow(['source','typing_code']);writer.writerows(d['mapping'].items())
        for filename,content in [('key.csv',stream.getvalue()),('key.json',json.dumps(d))]:
            response=self.client.post('/api/import',json={'filename':filename,'content':content})
            self.assertEqual(response.status_code,200);self.assertEqual(response.json['definition']['mapping'],d['mapping'])
        for content in ['not JSON','{}','{"format":"prime-language","version":8}']:
            self.assertEqual(self.client.post('/api/import',json={'content':content}).status_code,400)
        self.assertEqual(decode(encode(SOURCE,d),d),SOURCE)

    def test_non_source_requests_rejected(self):
        self.assertEqual(self.client.post('/api/generate',json={'kind':'text','source':'example'}).status_code,400)
        self.assertEqual(self.client.post('/api/generate',json={'source':'not valid Python source'}).status_code,400)
        bare=json.dumps({chr(65+i):str(i) for i in range(26)})
        self.assertEqual(self.client.post('/api/import',json={'content':bare}).status_code,400)

    def test_bad_requests_report_validation_errors(self):
        for route in ['generate','validate','encode','decode','verify','import']:
            response=self.client.post('/api/'+route,data='null',content_type='application/json')
            self.assertEqual(response.status_code,400)
        for style in [[],{},None,42]:
            d=make_definition();d['style']=style
            self.assertEqual(self.client.post('/api/validate',json={'definition':d}).status_code,400)
            self.assertEqual(self.client.post('/api/generate',json={'style':style,'source':SOURCE}).status_code,400)
        self.assertEqual(self.client.post('/api/import',json={'filename':None,'content':'{}'}).status_code,400)

    def test_verify_requires_valid_original_input(self):
        d=make_definition();encoded=encode(SOURCE,d)
        for value in [None,12,{},'x'*10001]:
            self.assertEqual(self.client.post('/api/verify',json={'definition':d,'encoded':encoded,'source':value}).status_code,400)

    def test_actual_benchmark_has_separate_negative_denominator(self):
        result=run_benchmark(1)
        self.assertEqual(result['samples'],16);self.assertEqual(len(result['rows']),78)
        self.assertEqual(result['valid_trials'],60);self.assertEqual(result['exact_trials'],60)
        self.assertEqual(result['negative_trials'],18);self.assertEqual(result['correct_rejections'],18)
        self.assertTrue(all(r['ast_matches'] is True and r['encode_ms']>=0 for r in result['rows'] if not r['expected_rejection']))
        self.assertTrue(all(r['recovered'] is None for r in result['rows'] if r['expected_rejection']))
        self.assertIn('No program was executed',result['execution'])

if __name__=='__main__':unittest.main()
