"""Local Flask application. Run python app.py; no message or key is saved by the server."""
import argparse
import csv
import io
import json
import os
import secrets
import threading
import webbrowser
from time import perf_counter
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException
from prime.engine import (PrimeError, STYLES, validate_definition, generate_definition,
    audit_definition, encode, decode, compare_recovery, analyse, prompt_style)
from prime.dataset import CORPUS, run_benchmark


def create_app(testing=False):
    app=Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=4*1024*1024,TESTING=testing)
    csrf=secrets.token_urlsafe(32)

    @app.before_request
    def protect_local_api():
        if request.method=='POST' and not testing and not secrets.compare_digest(request.headers.get('X-Prime-Token',''),csrf):
            return jsonify(error='Refresh ΠRIME before submitting this request.'),403

    @app.after_request
    def headers(response):
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['Referrer-Policy']='no-referrer'
        response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; base-uri 'none'"
        return response

    @app.errorhandler(PrimeError)
    def invalid(e):return jsonify(error=str(e)),400

    @app.errorhandler(HTTPException)
    def http_error(e):return jsonify(error=e.description),e.code

    def body():
        data=request.get_json(silent=True)
        if not isinstance(data,dict):raise PrimeError('Send a JSON object.')
        return data

    def definition(data):
        d=data.get('definition')
        validate_definition(d)
        return d

    @app.get('/')
    def index():return render_template('index.html',csrf=csrf)

    @app.get('/api/catalog')
    def catalog():
        return jsonify(styles=STYLES,examples=[x for x in CORPUS if not x.get('expect_error')],limit=10000)

    @app.post('/api/generate')
    def generate():
        data=body()
        kind=data.get('kind','python');style=data.get('style','ascii')
        if kind!='python':raise PrimeError('ΠRIME accepts supported Python source code only.')
        style,reason=prompt_style(data.get('prompt',''),style)
        candidates=[]
        for index in range(3):
            d=generate_definition(kind,style,data.get('source',''),data.get('policy','full'),data.get('name','My language'),data.get('locked'))
            # Preserve already attached signs when a locked source entry remains in the new definition.
            old_assets=data.get('assets',{})
            if not isinstance(old_assets,dict):raise PrimeError('Invalid sign attachments.')
            d['assets']={k:v for k,v in old_assets.items() if k in (data.get('locked') or {})}
            candidates.append({'definition':d,'audit':audit_definition(d)})
        return jsonify(candidates=candidates,reason=reason)

    @app.post('/api/validate')
    def validate():
        data=body();d=definition(data)
        return jsonify(definition=d,audit=audit_definition(d))

    @app.post('/api/import')
    def import_key():
        data=body();content=data.get('content','')
        if not isinstance(content,str) or len(content)>3500000:raise PrimeError('Import a key file below 3.5 MB.')
        filename=data.get('filename','')
        if not isinstance(filename,str):raise PrimeError('The key filename must be text.')
        if filename.lower().endswith('.csv'):
            try:
                rows=list(csv.reader(io.StringIO(content)))
                if rows and rows[0] and rows[0][0].strip().lower() in ('source','letter'):rows=rows[1:]
                mapping={}
                for row in rows:
                    if not row:continue
                    if len(row)!=2:raise PrimeError('CSV keys need two columns: source and typing_code.')
                    if row[0] in mapping:raise PrimeError('A source entry is duplicated in the CSV.')
                    mapping[row[0]]=row[1]
                kind=data.get('kind','python')
                d={'format':'prime-language','version':1,'name':'Imported code language','kind':kind,'style':'ascii','policy':data.get('policy','full'),'mapping':mapping,'assets':{}}
            except csv.Error as e:raise PrimeError('Could not read this CSV key.') from e
        else:
            try:d=json.loads(content)
            except (json.JSONDecodeError,RecursionError) as e:raise PrimeError('The language pack is not valid JSON.') from e
        validate_definition(d)
        return jsonify(definition=d,audit=audit_definition(d))

    @app.post('/api/encode')
    def encode_text():
        data=body();d=definition(data);source=data.get('source','')
        t=perf_counter();out=encode(source,d);duration=(perf_counter()-t)*1000
        return jsonify(encoded=out,analysis=analyse(source,out,d),encode_ms=round(duration,4),audit=audit_definition(d))

    @app.post('/api/decode')
    def decode_text():
        data=body();d=definition(data);encoded=data.get('encoded','')
        restored=decode(encoded,d)
        return jsonify(restored=restored,analysis=analyse(restored,encoded,d))

    @app.post('/api/verify')
    def verify():
        data=body();d=definition(data);result=compare_recovery(data.get('source',''),data.get('encoded',''),d)
        return jsonify(**result,analysis=analyse(result['restored'],data.get('encoded',''),d))

    @app.post('/api/benchmark')
    def benchmark():return jsonify(run_benchmark(body().get('repetitions',3)))

    @app.get('/api/corpus')
    def corpus():return jsonify(provenance='Synthetic fixtures authored for this prototype. No external collection or user study.',samples=CORPUS)

    return app

app=create_app()
if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Run the local ΠRIME prototype.')
    parser.add_argument('--host',default='127.0.0.1')
    parser.add_argument('--port',type=int,default=int(os.environ.get('PORT','5050')))
    parser.add_argument('--open',action='store_true',help='Open the local website in your browser.')
    parser.add_argument('--strictPort',action='store_true',help=argparse.SUPPRESS)  # Flask already fails when its requested port is occupied.
    args=parser.parse_args()
    if args.open:threading.Timer(1,lambda:webbrowser.open(f'http://127.0.0.1:{args.port}')).start()
    app.run(host=args.host,port=args.port,debug=False)
