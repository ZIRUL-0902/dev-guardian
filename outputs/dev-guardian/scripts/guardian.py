#!/usr/bin/env python3
"""Local development evidence helper. Python 3.9+, Git; no external packages."""
import argparse
from datetime import datetime, timezone
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import signal
import subprocess
import sys
import tarfile
import threading
import time
import uuid

LIMIT = 65536
LEVELS = ['build', 'unit', 'integration', 'e2e', 'simulator', 'hardware', 'performance', 'manual']
MANAGED = {'.git', '.dev-guardian'}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def write_json(path, value):
    atomic(path, json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        tmp.write_text(text, encoding='utf-8')
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()

def git(root, *args, optional=False):
    p = subprocess.run(['git', '-C', str(root), *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode and not optional:
        raise ValueError('Git command failed: ' + ' '.join(args) + ': ' + p.stderr.decode(errors='replace')[:500])
    return p.stdout if p.returncode == 0 else b''

def excluded(name):
    parts = Path(name).parts
    if name == '.dev-guardian/config.json':
        return False
    return bool(parts) and (parts[0] in MANAGED or '__pycache__' in parts)

def repository(root):
    top = git(root, 'rev-parse', '--show-toplevel').decode().strip()
    if Path(top).resolve() != root:
        raise ValueError('--root must be the Git repository root')

def files(root):
    repository(root)
    names = git(root, 'ls-files', '-z', '--cached', '--others', '--exclude-standard').split(b'\0')
    return sorted({os.fsdecode(n) for n in names if n and not excluded(os.fsdecode(n))})

def snapshot(root):
    h = hashlib.sha256()
    names = files(root)
    config = '.dev-guardian/config.json'
    if (root / config).is_file() and config not in names:
        names.append(config)
        names.sort()
    for name in names:
        path = root / name
        h.update(os.fsencode(name) + b'\0')
        if path.is_symlink():
            h.update(b'link\0' + os.fsencode(os.readlink(path)))
        elif path.is_file():
            h.update(str(path.stat().st_mode & 0o777).encode() + b'\0')
            with path.open('rb') as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b''):
                    h.update(chunk)
        elif path.is_dir():
            raise ValueError('Submodule/nested repository requires separate evidence: ' + name)
        else:
            h.update(b'deleted\0')
    # Index matters even when the worktree content is unchanged.
    h.update(git(root, 'diff', '--cached', '--binary', '--no-ext-diff', '--no-textconv', '--', '.', ':(exclude).dev-guardian'))
    h.update(git(root, 'diff', '--cached', '--binary', '--no-ext-diff', '--no-textconv', '--', '.dev-guardian/config.json', '.dev-guardian/ENVIRONMENT.md'))
    head = git(root, 'rev-parse', '--verify', 'HEAD', optional=True).decode().strip() or 'UNBORN'
    env = {'os': platform.system(), 'release': platform.release(), 'machine': platform.machine(),
           'python': platform.python_version(), 'git': git(root, '--version').decode().strip(),
           'environment_record_sha256': digest((root / '.dev-guardian/ENVIRONMENT.md').read_bytes()) if (root / '.dev-guardian/ENVIRONMENT.md').is_file() else None}
    return {'head': head, 'branch': git(root, 'branch', '--show-current').decode().strip() or 'DETACHED',
            'tree_sha256': h.hexdigest(), 'environment': env,
            'environment_sha256': digest(json.dumps(env, sort_keys=True).encode()), 'files_count': len(names)}

def same(a, b):
    return all(a[k] == b[k] for k in ['head', 'tree_sha256', 'environment_sha256'])

def new_dir(root, category):
    name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ') + '-' + uuid.uuid4().hex[:10]
    path = root / '.dev-guardian' / category / name
    path.mkdir(parents=True, exist_ok=False)
    return path

def scrub(text):
    text = re.sub(r'(?im)(authorization\s*:\s*)[^\r\n]+', r'\1[REDACTED]', text)
    text = re.sub(r'(?i)((?:password|passwd|secret|token|api[_-]?key|authorization)\s*[:=]\s*)([^\s,;]+)', r'\1[REDACTED]', text)
    text = re.sub(r'(?i)(Bearer\s+)[\w.\-]+', r'\1[REDACTED]', text)
    text = re.sub(r'(://)[^\s/@:]+:[^\s/@]+@', r'\1[REDACTED]@', text)
    text = re.sub(r'\b(?:sk-[A-Za-z0-9_-]{12,}|gh[pousr]_[A-Za-z0-9_]+)\b', '[REDACTED]', text)
    return text

def run(root, ident, level, argv, timeout):
    if not argv or timeout <= 0:
        raise ValueError('A command and positive timeout are required')
    before = snapshot(root)
    directory = new_dir(root, 'evidence')
    output = bytearray()
    total = [0]
    # Read bounded lines/chunks while draining the pipe; never keep unbounded output.
    def drain(pipe):
        pending = b''
        dropping = False
        while True:
            chunk = pipe.read(4096)
            if not chunk:
                break
            total[0] += len(chunk)
            if dropping:
                if b'\n' not in chunk:
                    continue
                chunk = chunk.split(b'\n', 1)[1]
                dropping = False
            pending += chunk
            while b'\n' in pending:
                line, pending = pending.split(b'\n', 1)
                if len(line) > 8192:
                    keep(b'[long line omitted]\n')
                else:
                    keep(line + b'\n')
            if len(pending) > 8192:
                # Drop long unsplit lines instead of persisting possible split credentials.
                pending = b''
                dropping = True
                keep(b'[long line omitted]\n')
        if pending:
            keep(pending)
        pipe.close()
    def keep(raw):
        safe = scrub(raw.decode('utf-8', errors='replace')).encode('utf-8')
        output.extend(safe[:max(0, LIMIT - len(output))])
    started = datetime.now(timezone.utc).isoformat()
    tick = time.monotonic()
    status, reason, code = 'FAILED', '', 1
    try:
        proc = subprocess.Popen(argv, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                start_new_session=(os.name == 'posix'))
        reader = threading.Thread(target=drain, args=(proc.stdout,), daemon=True)
        reader.start()
        try:
            code = proc.wait(timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt) as e:
            if os.name == 'posix':
                os.killpg(proc.pid, signal.SIGKILL)
            else:
                proc.kill()
            proc.wait()
            code = 124 if isinstance(e, subprocess.TimeoutExpired) else 130
            reason = 'TIMEOUT' if code == 124 else 'INTERRUPTED'
        reader.join(timeout=2)
        if reader.is_alive():
            if os.name == 'posix':
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            reader.join(timeout=2)
            code, reason = 124, 'OUTPUT_PIPE_NOT_CLOSED'
        status = 'PASSED' if code == 0 else 'FAILED'
    except OSError as e:
        code, status, reason = 127, 'BLOCKED', str(e)
    after = snapshot(root)
    if status == 'PASSED' and not same(before, after):
        code, status, reason = 1, 'FAILED', 'SOURCE_OR_ENVIRONMENT_CHANGED_DURING_TEST'
    log = directory / 'output.log'
    log.write_bytes(bytes(output))
    result = {'schema': 1, 'id': ident, 'level': level, 'status': status, 'exit_code': code,
              'reason': scrub(reason), 'argv': [scrub(x) for x in argv], 'cwd': '.',
              'started_utc': started, 'duration_seconds': round(time.monotonic() - tick, 3),
              'before': before, 'after': after, 'log': log.relative_to(root).as_posix(),
              'log_sha256': digest(bytes(output)), 'output_bytes': total[0],
              'log_truncated': total[0] > len(output)}
    write_json(directory / 'result.json', result)
    print(json.dumps({'status': status, 'evidence': str(directory.relative_to(root)), 'reason': reason}))
    return code if 0 <= code <= 255 else 1

def load_config(root):
    cfg = json.loads((root / '.dev-guardian/config.json').read_text())
    tests = cfg['tests']
    ids = set()
    for t in tests:
        if t['id'] in ids or t['level'] not in LEVELS or not t.get('argv') or not all(isinstance(x, str) for x in t['argv']):
            raise ValueError('Invalid or duplicate test configuration')
        ids.add(t['id'])
    return tests

def required_ids(root):
    ids = json.loads((root / '.dev-guardian/config.json').read_text()).get('required_ids', [])
    if not isinstance(ids, list) or not all(isinstance(i, str) and i for i in ids):
        raise ValueError('required_ids must be a list of nonempty acceptance IDs')
    return ids

def plan(root, base=None):
    names = files(root)
    changed = set()
    for args in [('diff', '--cached', '--no-renames', '--name-only', '-z'), ('diff', '--no-renames', '--name-only', '-z'), ('ls-files', '--others', '--exclude-standard', '-z')]:
        if args[0] == 'diff' and not git(root, 'rev-parse', '--verify', 'HEAD', optional=True):
            changed.update(names)
        else:
            changed.update(os.fsdecode(n) for n in git(root, *args).split(b'\0') if n)
    if base:
        changed.update(os.fsdecode(n) for n in git(root, 'diff', '--no-renames', '--name-only', '-z', base, 'HEAD').split(b'\0') if n)
    changed = sorted(n for n in changed if not excluded(n))
    tests = load_config(root)
    matches = {n: [t['id'] for t in tests if any(fnmatch.fnmatchcase(n, p) for p in t.get('paths', []))] for n in changed}
    unknown = [n for n, ids in matches.items() if not ids]
    # No diff may mean a clean commit being resumed: run all, never infer no work.
    all_tests = not changed or bool(unknown)
    selected = [t['id'] for t in tests if all_tests or t['id'] in required_ids(root) or any(t['id'] in ids for ids in matches.values())]
    return {'changed': changed, 'unknown_impact': unknown, 'selected': selected, 'required_ids': required_ids(root),
            'reason': 'all: clean tree or unknown impact' if all_tests else 'configured path matches; agent must inspect callers too'}

def check(root, ids):
    current = snapshot(root)
    if not ids:
        ids = list(dict.fromkeys([t['id'] for t in load_config(root)] + required_ids(root)))
    if not ids:
        raise ValueError('No required tests configured: NOT TESTED')
    latest = {}
    for p in sorted((root / '.dev-guardian/evidence').glob('*/result.json')):
        r = json.loads(p.read_text())
        latest[r['id']] = r
    errors = []
    for ident in ids:
        r = latest.get(ident)
        if not r:
            errors.append(ident + ': NOT TESTED')
            continue
        if r['status'] != 'PASSED' or r.get('exit_code') != 0:
            errors.append(ident + ': ' + r['status'])
            continue
        if not same(current, r['before']) or not same(current, r['after']):
            errors.append(ident + ': STALE (rerun)')
        p = (root / r['log']).resolve()
        if not p.is_relative_to((root / '.dev-guardian/evidence').resolve()) or not p.is_file() or digest(p.read_bytes()) != r['log_sha256']:
            errors.append(ident + ': INVALID LOG')
    print(json.dumps({'gate': 'FAILED' if errors else 'PASSED', 'errors': errors, 'required': ids}))
    return 1 if errors else 0

def safe_paths(root, names):
    result = []
    for name in names:
        p = Path(name)
        if p.is_absolute() or '..' in p.parts or not p.parts or excluded(name):
            raise ValueError('Unsafe checkpoint path: ' + name)
        if any((root / Path(*p.parts[:i])).is_symlink() for i in range(1, len(p.parts) + 1)):
            raise ValueError('Symlink checkpoint rejected: ' + name)
        lower = p.name.lower()
        if lower.startswith('.env') or lower.endswith(('.pem', '.key', '.p12', '.pfx')) or lower in ['credentials', 'credentials.json', 'id_rsa', 'id_ed25519']:
            raise ValueError('Potential secret file rejected: ' + name)
        if (root / p).is_dir():
            raise ValueError('Select individual files, not directories: ' + name)
        if git(root, 'check-ignore', '--', str(p), optional=True):
            raise ValueError('Ignored checkpoint path rejected: ' + name)
        if not (root / p).exists() and not git(root, 'ls-files', '--', ':(literal)' + p.as_posix()):
            raise ValueError('No such tracked or existing file: ' + name)
        result.append(p.as_posix())
    return result

def checkpoint(root, names):
    before = snapshot(root)
    names = safe_paths(root, names)
    cp = new_dir(root, 'checkpoints')
    try:
        for filename, args in [('staged.patch', ['diff', '--cached']), ('unstaged.patch', ['diff'])]:
            data = git(root, *args, '--binary', '--no-ext-diff', '--no-textconv', '--', *[':(literal)' + n for n in names])
            (cp / filename).write_bytes(data)
        with tarfile.open(cp / 'working.tar', 'w') as archive:
            for name in names:
                if (root / name).is_file():
                    archive.add(root / name, arcname=name, recursive=False)
        if not same(before, snapshot(root)):
            raise ValueError('Concurrent source change; checkpoint is incomplete')
        write_json(cp / 'manifest.json', {'schema': 1, 'snapshot': before, 'files': names,
                   'deleted': [n for n in names if not (root / n).exists()],
                   'sha256': {p.name: digest(p.read_bytes()) for p in cp.iterdir() if p.is_file()}})
    except BaseException:
        # Keep incomplete artifacts for inspection; absence of manifest means invalid.
        raise
    print(str(cp))
    return 0

def initialize(root):
    directory = root / '.dev-guardian'
    directory.mkdir(exist_ok=True)
    assets = Path(__file__).resolve().parents[1] / 'assets'
    for name in ['STATE.md', 'DECISIONS.md', 'ENVIRONMENT.md', 'config.json']:
        path = directory / name
        try:
            with path.open('x', encoding='utf-8') as f:
                f.write((assets / name).read_text(encoding='utf-8'))
        except FileExistsError:
            pass
    block = (assets / 'AGENTS.fragment.md').read_text()
    rules = root / 'AGENTS.md'
    old = rules.read_text() if rules.exists() else ''
    if '<!-- dev-guardian:start -->' not in old:
        atomic(rules, old.rstrip() + '\n\n' + block)
    print('Initialized without overwriting existing memory or rules.')
    return 0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('init')
    sub.add_parser('snapshot')
    for action in ['plan', 'verify']:
        s = sub.add_parser(action)
        s.add_argument('--base', help='Explicit trusted Git ref to include committed changes')
    s = sub.add_parser('run')
    s.add_argument('--id', required=True)
    s.add_argument('--level', choices=LEVELS, required=True)
    s.add_argument('--timeout', type=float, default=300)
    s.add_argument('argv', nargs=argparse.REMAINDER)
    s = sub.add_parser('record')
    s.add_argument('--id', required=True)
    s.add_argument('--level', choices=LEVELS, required=True)
    s.add_argument('--status', choices=['NOT TESTED', 'BLOCKED', 'FAILED'], required=True)
    s.add_argument('--reason', required=True)
    s = sub.add_parser('check')
    s.add_argument('--ids', nargs='+')
    s = sub.add_parser('checkpoint')
    s.add_argument('--files', nargs='+', required=True)
    a = parser.parse_args()
    root = a.root.resolve()
    try:
        if a.action == 'init':
            return initialize(root)
        if a.action == 'snapshot':
            print(json.dumps(snapshot(root), indent=2))
            return 0
        if a.action in ['plan', 'verify']:
            p = plan(root, a.base)
            print(json.dumps(p, indent=2))
            if a.action == 'plan':
                return 0
            if not p['selected']:
                raise ValueError('NOT TESTED: configure real test commands first')
            tests = {t['id']: t for t in load_config(root)}
            codes = [run(root, i, tests[i]['level'], tests[i]['argv'], tests[i].get('timeout', 300)) for i in p['selected']]
            return 1 if any(codes) else check(root, list(dict.fromkeys(p['selected'] + p['required_ids'])))
        if a.action == 'run':
            return run(root, a.id, a.level, a.argv[1:] if a.argv[:1] == ['--'] else a.argv, a.timeout)
        if a.action == 'record':
            d = new_dir(root, 'evidence')
            write_json(d / 'result.json', {'schema': 1, 'id': a.id, 'level': a.level, 'status': a.status,
                'reason': scrub(a.reason), 'before': snapshot(root), 'recorded_utc': datetime.now(timezone.utc).isoformat()})
            print(json.dumps({'status': a.status, 'evidence': str(d.relative_to(root))}))
            return 1
        if a.action == 'check':
            return check(root, a.ids)
        return checkpoint(root, a.files)
    except (ValueError, OSError, KeyError, TypeError) as e:
        print('dev-guardian: ' + scrub(str(e)), file=sys.stderr)
        return 2

if __name__ == '__main__':
    sys.exit(main())
