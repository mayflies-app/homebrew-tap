#!/usr/bin/env python3
"""Compare or explicitly copy common bytes into registered app checkouts."""
import argparse
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def safe_path(base, relative):
    relative = PurePosixPath(relative)
    if relative.is_absolute() or not relative.parts or any(part in (".", "..") for part in relative.parts):
        raise ValueError(f"Unsafe managed path: {relative}")
    path = base
    if path.is_symlink():
        raise ValueError(f"Symlink root: {base}")
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f"Symlink managed path: {path}")
    if not path.resolve().is_relative_to(base.resolve()):
        raise ValueError(f"Managed path leaves repository: {path}")
    return path


def payloads(root, app):
    template = safe_path(root, "templates/macos-app")
    result = []
    for path in sorted((template / "scripts").rglob("*")):
        source = safe_path(template, path.relative_to(template).as_posix())
        if source.is_file():
            result.append((source, source.relative_to(template).as_posix()))
    if not result:
        raise ValueError("Template scripts are missing")
    result += [(safe_path(template, name), f".github/workflows/{name}") for name in ("ci.yml", "release.yml")]
    if app.get("designDestination"):
        result.append((safe_path(template, "shared/MacAppDesign.swift"), app["designDestination"]))
    if app.get("localizationDestination"):
        result.append((safe_path(template, "shared/LocalizationResources.swift"), app["localizationDestination"]))
    for source, _ in result:
        if not source.is_file():
            raise ValueError(f"Template file missing: {source}")
    return result


def sync(root, app, apply=False):
    clone = root / app["path"]
    if clone.is_symlink() or not clone.is_dir():
        raise ValueError(f"Missing or symlink app checkout: {clone}")
    repo = clone.resolve()
    if repo == root.resolve():
        raise ValueError("An app checkout cannot be the source repository")
    observed = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--show-toplevel"], text=True).strip()
    if Path(observed).resolve() != repo:
        raise ValueError(f"App path is not the repository root: {repo}")
    changes = []
    for source, relative in payloads(root, app):
        target = safe_path(repo, relative)
        if target.exists() and not target.is_file():
            raise ValueError(f"Managed target is not a file: {target}")
        if not target.exists() or source.read_bytes() != target.read_bytes():
            changes.append((source, relative))
    if apply and changes:
        staged = subprocess.check_output(["git", "-C", str(repo), "diff", "--cached", "--name-only", "--", *[relative for _, relative in changes]], text=True).strip()
        if staged:
            raise ValueError(f"Refuse to overwrite staged managed files in {app['name']}:\n{staged}")
        for source, relative in changes:
            target = safe_path(repo, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".sync-", delete=False) as stream:
                    temporary = Path(stream.name)
                    stream.write(source.read_bytes())
                shutil.copymode(source, temporary)
                safe_path(repo, relative)
                os.replace(temporary, target)
            finally:
                if temporary is not None and temporary.exists():
                    temporary.unlink()
    for _, relative in changes:
        print(f"{'copied' if apply else 'differs'} {app['name']}/{relative}")
    if not changes:
        print(f"matches {app['name']}")
    return not changes or apply


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", help="Registered app name; default checks all registered apps")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Readonly byte comparison (default)")
    mode.add_argument("--apply", action="store_true", help="Copy common files; preserve product tools and staged changes")
    args = parser.parse_args()
    try:
        apps = json.loads((ROOT / "catalog/apps.json").read_text())["apps"]
        if args.app:
            apps = [app for app in apps if app["name"] == args.app]
            if not apps:
                raise ValueError(f"Unknown app: {args.app}")
        results = [sync(ROOT, app, args.apply) for app in apps]
        return 0 if all(results) else 1
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(2, f"sync_apps: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
