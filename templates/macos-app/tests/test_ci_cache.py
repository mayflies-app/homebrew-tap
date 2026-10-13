"""Input-cache behavior in real Git checkouts; no compiler or remote services."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts/lib/release"))
import ci_prepare


@contextlib.contextmanager
def checkout():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td).resolve()
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        (root / "Sources").mkdir()
        (root / "Sources/A.swift").write_bytes(b"let a = 1\n")
        (root / "Sources/B.swift").write_bytes(b"let b = 2\n")
        (root / ".gitignore").write_text(".build/\n")
        subprocess.run(["git", "-C", str(root), "add", "."], check=True)
        subprocess.run(["git", "-C", str(root), "-c", "user.name=Cache Test", "-c",
                        "user.email=cache@example.invalid", "commit", "-qm", "fixture"], check=True)
        previous = Path.cwd()
        os.chdir(root)
        try:
            yield root, root / ".build/app/debug/arm64"
        finally:
            os.chdir(previous)


def git_state(root):
    return tuple(subprocess.check_output(["git", "-C", str(root), *args]) for args in
                 (("status", "--porcelain=v1", "-z"), ("diff", "--binary"), ("diff", "--cached", "--binary")))


def touch(path):
    timestamp = path.stat().st_mtime_ns + 10_000_000_000
    os.utime(path, ns=(path.stat().st_atime_ns, timestamp))
    return timestamp


def invoke(action, cache):
    stream = io.StringIO()
    with contextlib.redirect_stdout(stream):
        result = ci_prepare.main(["cache-inputs", action, "--cache-dir", str(cache)])
    assert json.loads(stream.getvalue()) == result
    return result


class InputCacheTests(unittest.TestCase):
    def test_restore_same_bytes_preserves_contents_atime_and_git_state(self):
        with checkout() as (root, cache):
            source = root / "Sources/A.swift"
            original = source.stat().st_mtime_ns
            contents = source.read_bytes()
            self.assertEqual(invoke("save", cache)["saved"], 3)
            touch(source)
            before = git_state(root)
            atime = source.stat().st_atime_ns
            result = invoke("restore", cache)
            self.assertEqual(result["restored"], 3)
            self.assertEqual(source.stat().st_mtime_ns, original)
            self.assertEqual(source.stat().st_atime_ns, atime)
            self.assertEqual(source.read_bytes(), contents)
            self.assertEqual(git_state(root), before)

    def test_changed_mode_content_new_deleted_and_untracked_keep_current_mtime(self):
        with checkout() as (root, cache):
            invoke("save", cache)
            changed = root / "Sources/A.swift"
            changed.write_bytes(b"let a = 3\n")
            changed_time = touch(changed)
            (root / "Sources/B.swift").unlink()
            new = root / "Sources/New.swift"
            new.write_bytes(b"let n = 4\n")
            subprocess.run(["git", "add", "Sources"], check=True)
            subprocess.run(["git", "-c", "user.name=Cache Test", "-c", "user.email=cache@example.invalid",
                            "commit", "-qm", "next head"], check=True)
            new_time = touch(new)
            untracked = root / "private.txt"
            untracked.write_bytes(b"user data")
            untracked_time = touch(untracked)
            before = git_state(root)
            result = invoke("restore", cache)
            self.assertEqual(result["restored"], 1)
            self.assertEqual(changed.stat().st_mtime_ns, changed_time)
            self.assertEqual(new.stat().st_mtime_ns, new_time)
            self.assertEqual(untracked.stat().st_mtime_ns, untracked_time)
            self.assertEqual(git_state(root), before)
            self.assertEqual(invoke("save", cache)["saved"], 3)
            touch(changed)
            touch(new)
            invoke("restore", cache)
            self.assertEqual(changed.stat().st_mtime_ns, changed_time)
            self.assertEqual(new.stat().st_mtime_ns, new_time)
            changed.chmod(0o755)
            changed_time = touch(changed)
            invoke("restore", cache)
            self.assertEqual(changed.stat().st_mtime_ns, changed_time)

    def test_symlink_source_and_parent_never_touch_external_files(self):
        with checkout() as (root, cache), tempfile.TemporaryDirectory() as external:
            invoke("save", cache)
            outside = Path(external) / "A.swift"
            outside.write_bytes(b"let a = 1\n")
            outside_time = touch(outside)
            source = root / "Sources/A.swift"
            source.unlink()
            source.symlink_to(outside)
            before = git_state(root)
            invoke("restore", cache)
            self.assertEqual(outside.stat().st_mtime_ns, outside_time)
            self.assertEqual(git_state(root), before)
            self.assertEqual(invoke("save", cache)["saved"], 2)
            source.unlink()
            (root / "Sources/B.swift").unlink()
            (root / "Sources").rmdir()
            (root / "Sources").symlink_to(external, target_is_directory=True)
            invoke("restore", cache)
            self.assertEqual(outside.stat().st_mtime_ns, outside_time)
            self.assertEqual(invoke("save", cache)["saved"], 1)

    def test_missing_and_invalid_metadata_are_optional_safe_misses(self):
        with checkout() as (root, cache):
            self.assertEqual(invoke("restore", cache)["status"], "missing")
            self.assertFalse(cache.exists())
            invoke("save", cache)
            metadata = cache / ".source-inputs.json"
            valid = json.loads(metadata.read_text())
            invalid_cases = ["not json", {}, dict(valid, root="/different-checkout"),
                             dict(valid, schemaVersion=True), dict(valid, files=[{}])]
            for field, value in (("mtimeNs", True), ("mtimeNs", -1), ("mtimeNs", 2**64),
                                 ("sha256", "invalid"), ("mode", True), ("mode", 0o10000)):
                invalid = json.loads(json.dumps(valid))
                invalid["files"][0][field] = value
                invalid_cases.append(invalid)
            for invalid in invalid_cases:
                with self.subTest(invalid=invalid):
                    source = root / "Sources/A.swift"
                    fresh = touch(source)
                    metadata.write_text(invalid if isinstance(invalid, str) else json.dumps(invalid))
                    before = git_state(root)
                    self.assertEqual(invoke("restore", cache)["status"], "rejected")
                    self.assertEqual(source.stat().st_mtime_ns, fresh)
                    self.assertEqual(git_state(root), before)

    def test_bad_paths_reject_entire_metadata_before_restoring_any_file(self):
        with checkout() as (root, cache), tempfile.TemporaryDirectory() as external:
            invoke("save", cache)
            metadata = cache / ".source-inputs.json"
            valid = json.loads(metadata.read_text())
            outside = Path(external) / "outside.swift"
            outside.write_bytes(b"let a = 1\n")
            outside_time = touch(outside)
            for bad_path in (str(outside), "../outside.swift", "Sources/../A.swift", ".", "", ".build/app/debug/arm64/.source-inputs.json"):
                with self.subTest(path=bad_path):
                    malformed = json.loads(json.dumps(valid))
                    malformed["files"].append(dict(valid["files"][0], path=bad_path))
                    metadata.write_text(json.dumps(malformed))
                    source = root / "Sources/A.swift"
                    fresh = touch(source)
                    self.assertEqual(invoke("restore", cache)["status"], "rejected")
                    self.assertEqual(source.stat().st_mtime_ns, fresh)
                    self.assertEqual(outside.stat().st_mtime_ns, outside_time)

    def test_valid_record_cannot_restore_an_untracked_file(self):
        with checkout() as (root, cache):
            invoke("save", cache)
            source = root / "Sources/A.swift"
            subprocess.run(["git", "rm", "--cached", "Sources/A.swift"], check=True)
            fresh = touch(source)
            before = git_state(root)
            invoke("restore", cache)
            self.assertEqual(source.stat().st_mtime_ns, fresh)
            self.assertEqual(git_state(root), before)

    def test_debug_and_release_paths_allowed_but_unsafe_cache_paths_fail(self):
        with checkout() as (root, cache), tempfile.TemporaryDirectory() as external:
            for allowed in (cache, root / ".build/app/release", Path(".build/app/debug/x86_64")):
                with self.subTest(cache=allowed):
                    self.assertEqual(invoke("save", allowed)["saved"], 3)
            for invalid in (root, root / ".build/app", root / "dist/release", Path(".build/app/../elsewhere"), Path(external)):
                with self.subTest(cache=invalid), self.assertRaises(ValueError):
                    invoke("restore", invalid)
            (root / ".build/app/linked").symlink_to(external, target_is_directory=True)
            with self.assertRaises(ValueError):
                invoke("save", root / ".build/app/linked/cache")
            metadata = cache / ".source-inputs.json"
            metadata.unlink()
            outside = Path(external) / "metadata.json"
            outside.write_bytes(b"private contents")
            outside_time = touch(outside)
            metadata.symlink_to(outside)
            for action in ("restore", "save"):
                self.assertEqual(invoke(action, cache)["status"], "rejected")
            self.assertEqual(outside.read_bytes(), b"private contents")
            self.assertEqual(outside.stat().st_mtime_ns, outside_time)

    def test_cli_reports_safe_cache_miss_and_rejects_invalid_argument_path(self):
        script = Path(ci_prepare.__file__).resolve()
        with checkout() as (root, cache):
            command = [sys.executable, "-B", str(script), "cache-inputs", "restore", "--cache-dir"]
            miss = subprocess.run([*command, str(cache)], cwd=root, capture_output=True, text=True)
            self.assertEqual(miss.returncode, 0, miss.stderr)
            self.assertEqual(json.loads(miss.stdout)["status"], "missing")
            invalid = subprocess.run([*command, str(root)], cwd=root, capture_output=True, text=True)
            self.assertNotEqual(invalid.returncode, 0)
            self.assertIn("Input cache", invalid.stderr)


if __name__ == "__main__":
    unittest.main()
