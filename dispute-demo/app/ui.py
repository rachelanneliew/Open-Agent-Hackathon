"""Local synthetic analyst console: python -m app.ui [--no-memory]."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
from urllib.parse import parse_qs, urlsplit

from integration.fresh_reads import _json
from . import runtime_io
from .orchestrator import Budgets, Controller
from .ui_jobs import JobError, Jobs

ROOT = Path(__file__).resolve().parents[1]
STATIC = Path(__file__).with_name('web')


def browser_value(value):
    """Preserve BIGINT money/revisions past JavaScript's exact number range."""
    if type(value) is int and abs(value) > 2**53 - 1:
        return str(value)
    if type(value) is dict:
        return {key: browser_value(item) for key, item in value.items()}
    if type(value) is list:
        return [browser_value(item) for item in value]
    return value


class LazyInvestigator:
    def step(self, *args, **kwargs):
        from .investigator import Investigator
        from .nightshift import NightshiftClient, NightshiftConfig
        return Investigator(NightshiftClient(NightshiftConfig.from_environment())).step(*args, **kwargs)


class LazyReviewer:
    def review(self, *args, **kwargs):
        from .reviewer import Reviewer
        from .nightshift import NightshiftClient, NightshiftConfig
        return Reviewer(NightshiftClient(NightshiftConfig.from_environment())).review(*args, **kwargs)


def handler_for(jobs, *, inventory=runtime_io.read_inventory, snapshot=runtime_io.read_snapshot,
                memory_enabled=True):
    token = secrets.token_urlsafe(32)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Do not put untrusted URLs, data or credentials into logs.

        def reply(self, code, value, content_type='application/json; charset=utf-8'):
            data = json.dumps(browser_value(value), allow_nan=False).encode() if isinstance(value, (dict, list)) else value
            self.send_response(code)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
            self.end_headers()
            self.wfile.write(data)

        def local_request(self, *, write=False):
            expected = '127.0.0.1:' + str(self.server.server_port)
            if self.headers.get('Host') != expected:
                return False
            origin = self.headers.get('Origin')
            if origin is not None and origin != 'http://' + expected:
                return False
            if self.headers.get('Sec-Fetch-Site') == 'cross-site':
                return False
            return not write or secrets.compare_digest(self.headers.get('X-Analyst-Token', ''), token)

        def do_GET(self):
            if not self.local_request():
                return self.reply(403, {'error': 'local_origin_required'})
            try:
                url = urlsplit(self.path)
                assets = {'/': ('index.html', 'text/html; charset=utf-8'),
                          '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
                          '/style.css': ('style.css', 'text/css; charset=utf-8')}
                if url.path in assets:
                    name, mime = assets[url.path]
                    return self.reply(200, (STATIC / name).read_bytes(), mime)
                if url.path == '/api/config':
                    return self.reply(200, dict(token=token, mode='live', synthetic=True,
                        memory_mode='verified_advisory' if memory_enabled else 'no_memory'))
                if url.path == '/api/inventory':
                    return self.reply(200, inventory(timeout_seconds=45))
                query = parse_qs(url.query, strict_parsing=True)
                if set(query) != {'id'} or len(query['id']) != 1:
                    raise ValueError()
                identifier = query['id'][0]
                if url.path == '/api/case':
                    value = snapshot(identifier, timeout_seconds=45)
                    return self.reply(200, dict(snapshot=value.to_dict(), recoveries=jobs.recoveries(identifier)))
                if url.path == '/api/job':
                    return self.reply(200, jobs.get(identifier))
                return self.reply(404, {'error': 'not_found'})
            except (ValueError, FileNotFoundError, KeyError, TypeError):
                return self.reply(400, {'error': 'invalid_or_unavailable_record'})
            except Exception:
                return self.reply(503, {'error': 'source_unavailable_refresh_to_retry'})

        def do_POST(self):
            if not self.local_request(write=True):
                return self.reply(403, {'error': 'local_origin_token_required'})
            if self.path != '/api/job':
                return self.reply(404, {'error': 'not_found'})
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if not 0 < length <= 4096 or self.headers.get('Content-Type') != 'application/json':
                    raise ValueError()
                value = _json(self.rfile.read(length).decode('utf-8'))
                if value.get('kind') == 'memory' and not memory_enabled:
                    raise ValueError()
                return self.reply(202, jobs.submit(value))
            except JobError as error:
                return self.reply(409, {'error': str(error)})
            except (ValueError, FileNotFoundError, KeyError, TypeError, UnicodeError):
                return self.reply(400, {'error': 'invalid_operation_or_saved_request'})
            except Exception:
                return self.reply(503, {'error': 'operation_unavailable'})
    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8931)
    parser.add_argument('--no-memory', action='store_true')
    parser.add_argument('--memory-dir', type=Path)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535 or (args.no_memory and args.memory_dir):
        parser.error('Use port 1024–65535; --no-memory excludes --memory-dir')
    memory_factory = None
    if not args.no_memory:
        from agent.hmem_client import HmemClient, DEFAULT_PERSIST
        from agent.memory_service import DisputeMemory
        memory_factory = lambda seconds: DisputeMemory(HmemClient(args.memory_dir or DEFAULT_PERSIST, timeout=seconds))
    def controller(journal):
        return Controller(investigator=LazyInvestigator(), reviewer=LazyReviewer(), read_snapshot=runtime_io.read_snapshot,
            commit=runtime_io.commit, journal=journal, memory_factory=memory_factory)
    def retry(path):
        from .memory_workflow import retry_memory
        return retry_memory(path, read_snapshot=runtime_io.read_snapshot,
            memory_factory=memory_factory, budgets=Budgets())
    jobs = Jobs(ROOT / 'outputs/ui', ROOT / 'outputs/runs', controller_factory=controller, memory_retry=retry)
    try:
        server = ThreadingHTTPServer(('127.0.0.1', args.port), handler_for(jobs, memory_enabled=not args.no_memory))
        print(f'Analyst console: http://127.0.0.1:{args.port} (live integrations, synthetic actions)', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    finally:
        jobs.close()


if __name__ == '__main__':
    main()
