"""Real CLI + Git integration; no process or filesystem mocks."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'guardian.py'

class GuardianTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.git('init', '-q')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'user.name', 'Guardian Test')
        (self.root / 'app.py').write_text('value = 1\n')
        self.git('add', 'app.py')
        self.git('commit', '-qm', 'fixture')
    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args])
    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root), *args], capture_output=True, text=True)
    def init(self):
        p = self.cli('init')
        self.assertEqual(p.returncode, 0, p.stderr)
    def result(self):
        files = sorted((self.root / '.dev-guardian/evidence').glob('*/result.json'))
        return json.loads(files[-1].read_text())
    def run_test(self, code, ident='unit', timeout='5'):
        return self.cli('run', '--id', ident, '--level', 'unit', '--timeout', timeout, '--', sys.executable, '-c', code)
    def test_init_preserves_memory_and_existing_rules(self):
        (self.root / 'AGENTS.md').write_text('# Existing rules\nKeep me\n')
        self.init()
        state = self.root / '.dev-guardian/STATE.md'
        state.write_text('user checkpoint\n')
        self.init()
        self.assertEqual(state.read_text(), 'user checkpoint\n')
        rules = (self.root / 'AGENTS.md').read_text()
        self.assertTrue(rules.startswith('# Existing rules\nKeep me\n'))
        self.assertEqual(rules.count('<!-- dev-guardian:start -->'), 1)
    def test_success_is_traceable_and_stale_after_change(self):
        self.init()
        p = self.run_test("print('real check')")
        self.assertEqual(p.returncode, 0, p.stderr)
        r = self.result()
        self.assertEqual(r['status'], 'PASSED')
        self.assertEqual(r['before']['head'], self.git('rev-parse', 'HEAD').decode().strip())
        self.assertEqual(self.cli('check', '--ids', 'unit').returncode, 0)
        (self.root / 'app.py').write_text('value = 2\n')
        self.assertNotEqual(self.cli('check', '--ids', 'unit').returncode, 0)
    def test_failure_timeout_and_missing_executable(self):
        self.init()
        self.assertEqual(self.run_test("print('failure'); raise SystemExit(7)").returncode, 7)
        self.assertEqual(self.result()['status'], 'FAILED')
        self.assertEqual(self.run_test('import time; time.sleep(10)', timeout='0.1').returncode, 124)
        self.assertEqual(self.result()['status'], 'FAILED')
        self.assertEqual(self.cli('run', '--id', 'missing', '--level', 'integration', '--', '/no/such/executable').returncode, 127)
        self.assertEqual(self.result()['status'], 'BLOCKED')
    def test_unrun_cannot_be_claimed_passed(self):
        self.init()
        self.assertNotEqual(self.cli('check', '--ids', 'hardware').returncode, 0)
        p = self.cli('record', '--id', 'hardware', '--level', 'hardware', '--status', 'BLOCKED', '--reason', 'No reader connected')
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.result()['status'], 'BLOCKED')
        self.assertNotEqual(self.cli('check', '--ids', 'hardware').returncode, 0)
    def test_mutating_test_does_not_pass_gate(self):
        self.init()
        p = self.run_test("from pathlib import Path; Path('app.py').write_text('changed')")
        self.assertNotEqual(p.returncode, 0)
        self.assertEqual(self.result()['status'], 'FAILED')
    def test_tampered_log_is_rejected(self):
        self.init()
        self.run_test("print('ok')")
        r = self.result()
        log = self.root / r['log']
        log.write_text('forged')
        self.assertNotEqual(self.cli('check', '--ids', 'unit').returncode, 0)
    def test_output_is_bounded_and_common_secrets_redacted(self):
        self.init()
        p = self.run_test("print('token=super-secret-value'); print('x'*200000)")
        self.assertEqual(p.returncode, 0, p.stderr)
        r = self.result()
        data = (self.root / r['log']).read_bytes()
        self.assertNotIn(b'super-secret-value', data)
        self.assertLessEqual(len(data), 65536)
        self.assertTrue(r['log_truncated'])
    def test_checkpoint_preserves_index_and_can_be_recovered(self):
        self.init()
        (self.root / 'app.py').write_text('staged\n')
        self.git('add', 'app.py')
        (self.root / 'app.py').write_text('unstaged\n')
        (self.root / 'notes.txt').write_text('untracked\n')
        before = self.git('diff', '--cached', '--binary')
        p = self.cli('checkpoint', '--files', 'app.py', 'notes.txt')
        self.assertEqual(p.returncode, 0, p.stderr)
        cp = Path(p.stdout.strip())
        self.assertEqual(before, self.git('diff', '--cached', '--binary'))
        self.assertEqual((self.root / 'app.py').read_text(), 'unstaged\n')
        with tarfile.open(cp / 'working.tar') as t:
            self.assertEqual(t.extractfile('app.py').read(), b'unstaged\n')
            self.assertEqual(t.extractfile('notes.txt').read(), b'untracked\n')
        recovery = self.root / 'recovery'
        self.git('worktree', 'add', '--detach', str(recovery), 'HEAD')
        subprocess.run(['git', '-C', str(recovery), 'apply', '--index', str(cp / 'staged.patch')], check=True)
        subprocess.run(['git', '-C', str(recovery), 'apply', str(cp / 'unstaged.patch')], check=True)
        self.assertEqual((recovery / 'app.py').read_text(), 'unstaged\n')
    def test_checkpoint_rejects_secrets_traversal_symlink(self):
        self.init()
        (self.root / '.env').write_text('PRIVATE=must-not-copy')
        (self.root / 'link').symlink_to(self.root / 'app.py')
        for name in ['.env', '../outside', 'link']:
            self.assertNotEqual(self.cli('checkpoint', '--files', name).returncode, 0)
    def test_concurrent_runs_keep_distinct_evidence(self):
        self.init()
        argv = [sys.executable, str(SCRIPT), '--root', str(self.root), 'run', '--id', 'parallel', '--level', 'unit', '--', sys.executable, '-c', 'print(1)']
        jobs = [subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(3)]
        for j in jobs:
            out, err = j.communicate(timeout=15)
            self.assertEqual(j.returncode, 0, err)
        self.assertEqual(len(list((self.root / '.dev-guardian/evidence').glob('*/result.json'))), 3)
    def test_impact_selects_matching_tests_and_unknown_changes_all(self):
        self.init()
        self.git('add', 'AGENTS.md')
        self.git('commit', '-qm', 'rules baseline')
        cfg = {'tests': [
            {'id': 'unit', 'level': 'unit', 'paths': ['app.py'], 'argv': [sys.executable, '-c', 'print(1)']},
            {'id': 'e2e', 'level': 'e2e', 'paths': ['web/*'], 'argv': [sys.executable, '-c', 'print(2)']} ]}
        (self.root / '.dev-guardian/config.json').write_text(json.dumps(cfg))
        self.git('add', '.dev-guardian/config.json')
        self.git('commit', '-qm', 'test configuration baseline')
        (self.root / 'app.py').write_text('change')
        plan = json.loads(self.cli('plan').stdout)
        self.assertEqual(plan['selected'], ['unit'])
        (self.root / 'unknown.txt').write_text('unknown impact')
        plan = json.loads(self.cli('plan').stdout)
        self.assertEqual(plan['selected'], ['unit', 'e2e'])
    def test_configuration_change_invalidates_old_evidence(self):
        self.init()
        self.run_test("print('ok')")
        cfg = self.root / '.dev-guardian/config.json'
        cfg.write_text('{"tests": [], "note": "new configuration"}')
        self.assertNotEqual(self.cli('check', '--ids', 'unit').returncode, 0)
    @unittest.skipUnless(os.name == 'posix', 'POSIX process group cleanup')
    def test_timeout_kills_descendant_before_side_effect(self):
        self.init()
        child = "import time; from pathlib import Path; time.sleep(0.5); Path('survivor').write_text('bad')"
        code = "import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', " + repr(child) + "]); time.sleep(10)"
        self.assertEqual(self.run_test(code, timeout='0.15').returncode, 124)
        import time
        time.sleep(0.65)
        self.assertFalse((self.root / 'survivor').exists())
    def test_checkpoint_paths_are_literal(self):
        self.init()
        (self.root / 'a*.txt').write_text('selected')
        (self.root / 'another.txt').write_text('private-not-selected')
        self.git('add', 'a*.txt', 'another.txt')
        p = self.cli('checkpoint', '--files', 'a*.txt')
        self.assertEqual(p.returncode, 0, p.stderr)
        patch = (Path(p.stdout.strip()) / 'staged.patch').read_text()
        self.assertNotIn('private-not-selected', patch)
    def test_required_external_acceptance_cannot_be_hidden_by_green_unit(self):
        self.init()
        cfg = {'required_ids': ['reader'], 'tests': [
            {'id': 'unit', 'level': 'unit', 'paths': ['*'], 'argv': [sys.executable, '-c', 'print(1)']}]}
        (self.root / '.dev-guardian/config.json').write_text(json.dumps(cfg))
        p = self.cli('verify')
        self.assertNotEqual(p.returncode, 0)
        self.cli('record', '--id', 'reader', '--level', 'hardware', '--status', 'BLOCKED', '--reason', 'No reader')
        self.assertNotEqual(self.cli('verify').returncode, 0)
        self.assertNotEqual(self.cli('check').returncode, 0)
        self.assertEqual(self.cli('check', '--ids', 'unit').returncode, 0)
    def test_portable_copy_works_without_private_runtime(self):
        import shutil
        local = self.root / '.agents/skills/dev-guardian'
        shutil.copytree(SCRIPT.parents[1], local, ignore=shutil.ignore_patterns('__pycache__'))
        for command in [['init'], ['run', '--id', 'portable', '--level', 'unit', '--', sys.executable, '-c', 'print(1)']]:
            p = subprocess.run([sys.executable, str(local / 'scripts/guardian.py'), '--root', str(self.root), *command], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
    def test_authorization_and_long_line_secrets_do_not_leak(self):
        self.init()
        for code, forbidden in [
            ("print('Authorization: Bearer EXAMPLE_ACCESS_CREDENTIAL_123')", b'EXAMPLE_ACCESS_CREDENTIAL_123'),
            ("print('Authorization: Basic EXAMPLE_BASIC_CREDENTIAL_456')", b'EXAMPLE_BASIC_CREDENTIAL_456'),
            ("print('token=' + 'A'*17000 + 'SECRETTAIL')", b'SECRETTAIL')]:
            self.assertEqual(self.run_test(code).returncode, 0)
            r = self.result()
            self.assertNotIn(forbidden, (self.root / r['log']).read_bytes())
    def test_staged_config_is_part_of_provenance(self):
        self.init()
        self.git('add', '.dev-guardian/config.json')
        self.git('commit', '-qm', 'config')
        self.run_test("print('ok')")
        p = self.root / '.dev-guardian/config.json'
        old = p.read_text()
        p.write_text('{"tests":[],"new":true}')
        self.git('add', '.dev-guardian/config.json')
        p.write_text(old)
        self.assertNotEqual(self.cli('check', '--ids', 'unit').returncode, 0)
    def test_impact_unions_staged_and_unstaged(self):
        self.init()
        (self.root / 'web.py').write_text('original')
        cfg = {'tests': [
            {'id': 'unit', 'level': 'unit', 'paths': ['app.py'], 'argv': [sys.executable, '-c', 'print(1)']},
            {'id': 'web', 'level': 'e2e', 'paths': ['web.py'], 'argv': [sys.executable, '-c', 'print(2)']} ]}
        (self.root / '.dev-guardian/config.json').write_text(json.dumps(cfg))
        self.git('add', 'AGENTS.md', '.dev-guardian/config.json', 'web.py')
        self.git('commit', '-qm', 'baseline')
        (self.root / 'web.py').write_text('staged')
        self.git('add', 'web.py')
        (self.root / 'web.py').write_text('original')
        (self.root / 'app.py').write_text('changed')
        self.assertEqual(json.loads(self.cli('plan').stdout)['selected'], ['unit', 'web'])
    def test_rename_preserves_old_and_new_impact(self):
        self.init()
        (self.root / 'web.py').write_text('original')
        cfg = {'tests': [
            {'id': 'old', 'level': 'integration', 'paths': ['web.py'], 'argv': [sys.executable, '-c', 'print(1)']},
            {'id': 'new', 'level': 'unit', 'paths': ['new.py'], 'argv': [sys.executable, '-c', 'print(2)']}]}
        (self.root / '.dev-guardian/config.json').write_text(json.dumps(cfg))
        self.git('add', 'AGENTS.md', '.dev-guardian/config.json', 'web.py')
        self.git('commit', '-qm', 'baseline')
        self.git('mv', 'web.py', 'new.py')
        self.assertEqual(json.loads(self.cli('plan').stdout)['selected'], ['old', 'new'])
    def test_no_git_fails_without_fabricated_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            p = subprocess.run([sys.executable, str(SCRIPT), '--root', d, 'snapshot'], capture_output=True)
            self.assertNotEqual(p.returncode, 0)

if __name__ == '__main__':
    unittest.main()
