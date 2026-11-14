"""One-click, loopback-only static demo server; Python standard library only."""
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import argparse, hashlib, hmac, json, os, secrets, subprocess, sys, threading, time, urllib.error, urllib.parse, urllib.request, webbrowser

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / '.tmp' / 'preview-server.json'
IDENTITY = hashlib.sha256(str(ROOT).encode()).hexdigest()[:16]
PUBLIC_ROOT_FILES = {'index.html', 'styles.css', 'app.js', 'engine.js', 'movement-map.js', 'movement-map.css', 'insights.js', 'locations.html', 'location-explorer.js', 'location-explorer.css', 'favicon.svg', 'companion-signals.js', 'tour.js'}
PUBLIC_DIRS = {'data', 'vendor'}
EXTENSIONS = {'.html', '.js', '.css', '.json', '.svg', '.png', '.jpg', '.jpeg', '.ico', '.woff', '.woff2', '.ttf'}


def public_file(url):
    path = urllib.parse.unquote(urllib.parse.urlsplit(url).path)
    if path == '/': path = '/index.html'
    candidate = (ROOT / path.lstrip('/')).resolve()
    try: relative = candidate.relative_to(ROOT)
    except ValueError: return None
    if '\\' in path or any(part.startswith('.') for part in relative.parts): return None
    if relative.as_posix() not in PUBLIC_ROOT_FILES and (not relative.parts or relative.parts[0] not in PUBLIC_DIRS): return None
    if candidate.suffix.lower() not in EXTENSIONS or not candidate.is_file(): return None
    return candidate


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs): super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args): pass
    def valid_host(self):
        return self.headers.get('Host', '') in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    def do_GET(self):
        if not self.valid_host(): return self.send_error(403)
        if self.path == '/__within_health':
            content = json.dumps({'app': 'within-demo', 'workspace': IDENTITY}).encode()
            self.send_response(200); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(content))); self.end_headers(); self.wfile.write(content); return
        if not public_file(self.path): return self.send_error(404)
        super().do_GET()
    def do_HEAD(self):
        if not self.valid_host(): return self.send_error(403)
        if not public_file(self.path): return self.send_error(404)
        super().do_HEAD()
    def do_POST(self):
        if not self.valid_host() or self.path != '/__within_stop' or not hmac.compare_digest(self.headers.get('X-Within-Token',''), self.server.stop_token): return self.send_error(403)
        self.send_response(204); self.end_headers()
        threading.Thread(target=self.server.shutdown, daemon=True).start()
    def translate_path(self, path):
        candidate = public_file(path)
        return str(candidate) if candidate else str(ROOT / '__not_public__')
    def list_directory(self, path): return self.send_error(404)


def health(port):
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/__within_health', timeout=.5) as r:
            return json.load(r) == {'app':'within-demo', 'workspace':IDENTITY}
    except (OSError, ValueError): return False


def serve(port):
    server = ThreadingHTTPServer(('127.0.0.1',port), Handler)
    server.stop_token = secrets.token_urlsafe(32)
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps({'port':server.server_port,'token':server.stop_token,'workspace':IDENTITY}), encoding='utf-8')
    print(f'WITHIN street map preview: http://127.0.0.1:{server.server_port}', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally:
        server.server_close()
        try:
            if json.loads(STATE.read_text()).get('token') == server.stop_token: STATE.unlink()
        except (OSError, ValueError): pass


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serve',action='store_true'); parser.add_argument('--stop',action='store_true'); parser.add_argument('--no-browser',action='store_true'); parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    if not 1024<=args.port<=65535: parser.error('port must be 1024–65535')
    if args.serve: serve(args.port); return
    if args.stop:
        try: state=json.loads(STATE.read_text())
        except (OSError, ValueError): print('The demo server is not running.'); return
        if state.get('workspace') != IDENTITY or not health(state['port']): print('No matching demo server is running.'); return
        request=urllib.request.Request(f"http://127.0.0.1:{state['port']}/__within_stop",data=b'',headers={'X-Within-Token':state['token']},method='POST')
        urllib.request.urlopen(request, timeout=3).close(); print('Demo server stopped.'); return
    port=args.port
    if not health(port):
        child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--serve','--port',str(port)], cwd=ROOT, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0, start_new_session=os.name!='nt')
        for _ in range(50):
            if health(port): break
            if child.poll() is not None: raise SystemExit(f'Port {port} is occupied or the server could not start. Try START-DEMO.cmd --port 8766.')
            time.sleep(.1)
        else: raise SystemExit('The local preview did not start. No browser was opened.')
    url=f'http://127.0.0.1:{port}'
    print('Open '+url+' — use STOP-DEMO.cmd when finished.')
    if not args.no_browser: webbrowser.open(url)

if __name__ == '__main__': main()
