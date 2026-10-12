"""Release preview and execution boundaries; external services are never called."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('pipeline', Path(__file__).parents[1] / 'scripts/lib/pipeline.py')
pipeline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pipeline)
COMMIT = 'a' * 40


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.config = {'schemaVersion': 1, 'product': 'SampleApp', 'appName': 'Sample App',
                       'executable': 'SampleApp', 'bundleIdentifier': 'dev.sample.app',
                       'repository': 'mayflies-app/sample-app', 'caskToken': 'sample-app',
                       'description': 'Sample', 'minimumSystemVersion': '14.0',
                       'buildSystem': 'swiftpm', 'architectures': ['arm64', 'x86_64', 'universal'],
                       'versionFile': 'VERSION', 'releaseAdapter': 'scripts/app.py'}
        (self.root / 'macos-app.json').write_text(json.dumps(self.config))
        (self.root / 'VERSION').write_text('1.2.3\n')

    def tearDown(self):
        self.temp.cleanup()

    def call(self, argv):
        with contextlib.redirect_stdout(io.StringIO()):
            return pipeline.main(argv, root=self.root)

    def test_default_and_explicit_preview_never_run_tools_or_write(self):
        before = {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        for args in ([], ['--dry-run'], ['--dry-run', '--publish']):
            with self.subTest(args=args), patch.object(pipeline.contract, 'run', side_effect=AssertionError('tool called')), \
                 patch.object(pipeline.release, 'github_json', side_effect=AssertionError('GitHub called')), \
                 patch.object(pipeline, 'execute', side_effect=AssertionError('execution called')):
                result = self.call(args)
                self.assertFalse(result['executed'])
                self.assertFalse(result['credentialsValidated'])
                self.assertEqual([s['architecture'] for s in result['steps'] if s['step'] == 'package'],
                                 ['arm64', 'x86_64', 'universal'])
                self.assertEqual('update-cask' in [s['step'] for s in result['steps']], '--publish' in args)
                if '--publish' in args:
                    tap = next(s for s in result['steps'] if s['step'] == 'update-cask')
                    self.assertEqual(tap['repository'], 'mayflies-app/homebrew-tap')
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_local_execute_rejected_before_any_tool_or_output(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(pipeline.contract, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'Remote operation'):
                self.call(['--execute'])
            run.assert_not_called()
        self.assertFalse((self.root / 'dist').exists())

    def test_execute_and_dry_run_are_mutually_exclusive(self):
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()), patch.object(pipeline, 'execute') as execute:
            self.call(['--execute', '--dry-run'])
        execute.assert_not_called()

    def test_private_publication_rejected_before_build_sign_or_apple(self):
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GH_TOKEN': 'fixture', 'GITHUB_SHA': COMMIT}
        with patch.dict(os.environ, env, clear=True), \
             patch.object(pipeline.contract, 'source_state', return_value={'commit': COMMIT, 'dirty': False}), \
             patch.object(pipeline.release, 'github_json', return_value={'visibility': 'private'}), \
             patch.object(pipeline.ci_prepare, 'prepare') as prepare, \
             patch.object(pipeline.ci_prepare, 'verify_toolchain') as toolchain:
            with self.assertRaisesRegex(ValueError, 'public release repository'):
                self.call(['--execute', '--publish'])
            prepare.assert_not_called()
            toolchain.assert_not_called()

    def test_dirty_source_rejected_before_apple_or_publication(self):
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GH_TOKEN': 'fixture', 'GITHUB_SHA': COMMIT}
        with patch.dict(os.environ, env, clear=True), \
             patch.object(pipeline.contract, 'source_state', return_value={'commit': COMMIT, 'dirty': True}), \
             patch.object(pipeline.release, 'github_json') as github, \
             patch.object(pipeline.ci_prepare, 'prepare') as prepare:
            with self.assertRaisesRegex(ValueError, 'clean checkout'):
                self.call(['--execute', '--publish'])
            github.assert_not_called()
            prepare.assert_not_called()

    def test_signed_private_artifact_execution_has_no_publication(self):
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GH_TOKEN': 'fixture', 'GITHUB_SHA': COMMIT}
        with patch.dict(os.environ, env, clear=True), \
             patch.object(pipeline.contract, 'source_state', return_value={'commit': COMMIT, 'dirty': False}), \
             patch.object(pipeline.ci_prepare, 'verify_toolchain'), \
             patch.object(pipeline.release, 'main', return_value={'reuse': False}), \
             patch.object(pipeline.ci_prepare, 'prepare') as prepare, \
             patch.object(pipeline.contract, 'collect'), \
             patch.object(pipeline.release, 'publish') as publish, \
             patch.object(pipeline.tap_update, 'remote_update') as tap:
            self.call(['--execute', '--build', '42'])
            self.assertEqual([c.args[3] for c in prepare.call_args_list], ['arm64', 'x86_64', 'universal'])
            self.assertTrue(all(c.kwargs == {'signed': True, 'notarized': True} for c in prepare.call_args_list))
            self.assertTrue(all(c.args[2] == '42' for c in prepare.call_args_list))
            publish.assert_not_called()
            tap.assert_not_called()

    def test_public_reuse_never_rebuilds_and_tap_uses_own_token(self):
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'workflow_dispatch', 'GH_TOKEN': 'app-token',
               'HOMEBREW_TAP_TOKEN': 'tap-token', 'GITHUB_SHA': COMMIT}
        with patch.dict(os.environ, env, clear=True), \
             patch.object(pipeline.contract, 'source_state', return_value={'commit': COMMIT, 'dirty': False}), \
             patch.object(pipeline.release, 'github_json', return_value={'visibility': 'public'}), \
             patch.object(pipeline.ci_prepare, 'verify_toolchain'), \
             patch.object(pipeline.release, 'main', return_value={'reuse': True}), \
             patch.object(pipeline.ci_prepare, 'prepare') as prepare, \
             patch.object(pipeline.release, 'publish'), \
             patch.object(pipeline.release, 'verify_public_release', return_value={'artifact': {'sha256': 'e' * 64}}), \
             patch.object(pipeline.contract, 'run') as run, \
             patch.object(pipeline.tap_update, 'remote_update', side_effect=lambda *a: self.assertEqual(os.environ['GH_TOKEN'], 'tap-token')) as tap:
            self.call(['--execute', '--publish'])
            prepare.assert_not_called()
            self.assertEqual(os.environ['GH_TOKEN'], 'app-token')
            calls = [list(map(str, c.args[0])) for c in run.call_args_list]
            clone = next(c for c in calls if 'clone' in c)
            self.assertEqual(clone[-2], 'https://github.com/mayflies-app/homebrew-tap.git')
            self.assertEqual(tap.call_args.args[-1], 'mayflies-app/homebrew-tap')
            self.assertTrue(any('!gh auth git-credential' in c and 'config' in c for c in calls))
            self.assertFalse(any('tap-token' in ' '.join(c) for c in calls))


if __name__ == '__main__':
    unittest.main()
