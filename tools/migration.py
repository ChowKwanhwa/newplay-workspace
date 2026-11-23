from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import platform
import re
import shutil
import sys


ROOT = Path(__file__).resolve().parents[1]
CACHE_PARTS = {'.git', '.venv', 'node_modules', '__pycache__', '.cache', '.wrangler', 'telegram-cli-cache'}
SOURCE_DIRS = ('tools', 'scripts', 'docs', 'design', 'wiki', 'newplay-library')
TEXT_SUFFIXES = {'.py', '.js', '.ts', '.sh', '.md', '.json', '.jsonc', '.toml', '.yaml', '.yml', '.html', '.css', '.txt'}
PRIVATE_NAMES = {'.env', 'credentials.json', 'token.json'}


def skipped_asset(path):
    if path.name in PRIVATE_NAMES or path.name.startswith('client_secret') or path.name.startswith('.env.') or path.suffix in {'.session', '.pem', '.key'}:
        return True
    if path.parts[:2] == ('newplay-library', '.cache') and len(path.parts) == 3 and path.suffix == '.json':
        return False
    return any(part in CACHE_PARTS for part in path.parts) or path.name == '.DS_Store' or path.name in PRIVATE_NAMES or path.name.startswith('.env.') or path.suffix in {'.session', '.pem', '.key'} or path.name.endswith('.session-journal')


def digest(path):
    checksum = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            checksum.update(chunk)
    return checksum.hexdigest()


def inspect_text(path, text, secrets):
    issues = []
    patterns = {
        'machine-path': r'/Users/[\w.-]+/[^\s\n\"\x27]+|/private/tmp/[\w.-]+|/Library/Frameworks/|/opt/homebrew/(?:bin|Cellar)/',
        'temporary-input': r'''(?:ROOT|root)\s*/\s*['"]tmp(?:/|['"])''',
        'credential-pattern': r'AIza[\w-]{35}|\bsk-[A-Za-z0-9_-]{32,}|\b\d{8,12}:[A-Za-z0-9_-]{30,}',
    }
    for number, line in enumerate(text.splitlines(), 1):
        for kind, pattern in patterns.items():
            if re.search(pattern, line):
                issues.append({'path': str(path), 'line': number, 'kind': kind})
        if any(value in line for value in secrets):
            issues.append({'path': str(path), 'line': number, 'kind': 'credential-value'})
    return issues


def source_files(root):
    paths = [path for path in root.iterdir() if path.is_file() and (path.name == '.env.example' or not path.name.startswith('.env'))]
    for folder in SOURCE_DIRS:
        base = root / folder
        if base.exists():
            paths.extend(path for path in base.rglob('*') if path.is_file())
    return sorted(path for path in paths if not path.is_symlink() and not any(part in CACHE_PARTS for part in path.relative_to(root).parts) and (path.name == '.env.example' or not skipped_asset(path.relative_to(root))) and (path.suffix in TEXT_SUFFIXES or path.name in {'Brewfile', '.gitignore', '.gitattributes', '.env.example'}))


def audit(root):
    secrets = []
    env_path = root / '.env'
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if '=' in line and not line.lstrip().startswith('#'):
                value = line.split('=', 1)[1].strip().strip('\"\x27')
                if len(value) >= 16:
                    secrets.append(value)
    issues = []
    files = source_files(root)
    for path in files:
        relative = path.relative_to(root)
        if path.stat().st_size > 8 * 1024 * 1024:
            issues.append({'path': str(relative), 'kind': 'scan-size-limit'})
            continue
        issues.extend(inspect_text(relative, path.read_text(errors='replace'), secrets))
    counts = {kind: len({item['path'] for item in issues if item['kind'] == kind}) for kind in sorted({item['kind'] for item in issues})}
    return {'schema': 1, 'filesScanned': len(files), 'affectedFilesByKind': counts, 'issues': issues, 'readyForSeamlessMigration': not issues, 'notes': ['Source audit only; excluded assets require private transfer and manifest verification.', 'Pattern matches need review and may include examples or scanners. No matched values are recorded.']}


def make_manifest(root, folders, hashed=False):
    files = []
    warnings = []
    for folder in folders:
        base = root / folder
        if base.is_symlink():
            warnings.append({'path': folder, 'kind': 'symlink-not-copied'})
            continue
        if not base.exists():
            warnings.append({'path': folder, 'kind': 'folder-missing'})
            continue
        for directory, subfolders, names in os.walk(base, followlinks=False):
            current = Path(directory)
            for name in list(subfolders):
                path = current / name
                if path.is_symlink() and not skipped_asset(path.relative_to(root)):
                    warnings.append({'path': str(path.relative_to(root)), 'kind': 'symlink-not-copied'})
            subfolders[:] = [name for name in subfolders if not (current / name).is_symlink() and not skipped_asset((current / name).relative_to(root))]
            for name in sorted(names):
                path = current / name
                relative = path.relative_to(root)
                if path.is_symlink():
                    warnings.append({'path': str(relative), 'kind': 'symlink-not-copied'})
                    continue
                if skipped_asset(relative):
                    continue
                size = path.stat().st_size
                row = {'path': str(relative), 'size': size}
                if hashed:
                    row['sha256'] = digest(path)
                    if path.stat().st_size != size:
                        raise RuntimeError('Source changed during hashing; rerun manifest.')
                files.append(row)
    return {'schema': 1, 'hashed': hashed, 'files': sorted(files, key=lambda item: item['path']), 'warnings': warnings, 'fileCount': len(files), 'totalBytes': sum(item['size'] for item in files)}


def verify_manifest(root, manifest):
    issues = []
    resolved_root = root.resolve()
    for row in manifest['files']:
        relative = Path(row['path'])
        path = root / relative
        if relative.is_absolute() or '..' in relative.parts or not path.resolve().is_relative_to(resolved_root) or path.is_symlink():
            issues.append({'path': row['path'], 'kind': 'unsafe-path'})
        elif not path.is_file():
            issues.append({'path': row['path'], 'kind': 'missing'})
        elif path.stat().st_size != row['size']:
            issues.append({'path': row['path'], 'kind': 'size-mismatch'})
        elif row.get('sha256') and digest(path) != row['sha256']:
            issues.append({'path': row['path'], 'kind': 'hash-mismatch'})
    return issues


def doctor(root):
    modules = ['PIL', 'fontTools', 'playwright', 'fitz', 'pypdf', 'reportlab', 'docx', 'pptx', 'telethon', 'bs4', 'lxml', 'qrcode', 'openpyxl']
    packages = {name: importlib.util.find_spec(name) is not None for name in modules}
    commands = {name: shutil.which(name) is not None for name in ['git', 'git-lfs', 'gh', 'uv', 'node', 'ffmpeg', 'pdftoppm', 'gws', 'wrangler']}
    chrome = Path('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome').is_file() or (Path.home() / 'Applications/Google Chrome.app/Contents/MacOS/Google Chrome').is_file()
    ready = all(packages.values()) and all(commands[name] for name in ['git', 'uv', 'node', 'ffmpeg', 'pdftoppm']) and chrome
    return {'python': platform.python_version(), 'architecture': platform.machine(), 'packages': packages, 'commands': commands, 'chromePresent': chrome, 'readyForBuildDependencies': ready, 'privateFoldersPresent': {name: (root / name).is_dir() for name in ['raw', 'output', 'tmp']}, 'envPresent': (root / '.env').is_file(), 'safeCheckOnly': True, 'notes': ['No login, network request, credential output, send, build or deployment performed.', 'Service authorization and asset integrity require separate explicit verification.']}


def main():
    parser = argparse.ArgumentParser(description='Read-only private workspace migration checks')
    parser.add_argument('command', choices=['audit', 'manifest', 'verify', 'doctor'])
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--hash', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == 'audit':
        result = audit(root)
        status = 2 if result['issues'] else 0
    elif args.command == 'manifest':
        result = make_manifest(root, ['raw', 'output', 'tmp', 'newplay-library/.cache'], args.hash)
        status = 2 if result['warnings'] else 0
    elif args.command == 'verify':
        if not args.manifest:
            parser.error('verify requires --manifest')
        issues = verify_manifest(root, json.loads(args.manifest.read_text()))
        result = {'verified': not issues, 'issues': issues}
        status = 2 if issues else 0
    else:
        result = doctor(root)
        status = 0 if result['readyForBuildDependencies'] else 2
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == 'manifest':
            args.out.with_suffix('.files0').write_bytes(b''.join(item['path'].encode() + b'\0' for item in result['files']))
        summary = {key: value for key, value in result.items() if key not in {'files', 'issues'}}
        summary['issueCount'] = len(result.get('issues', []))
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(status)


if __name__ == '__main__':
    main()
