from pathlib import Path
import argparse
import hashlib
import json

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_FONTS = {'homeChinese': 'home', 'homeLatin': 'latin', 'gameTitle': 'game', 'body': 'body'}
EXPECTED_FRAMES = {'home': ('61:2', '62:2'), 'lieflat': ('602:126', '602:252')}


def validate(root, contract=None):
    path = root / 'design/contract.json'
    if contract is None and not path.is_file():
        return {'verified': False, 'checkedFiles': 0, 'issues': [{'kind': 'missing-contract'}]}
    contract = contract if contract is not None else json.loads(path.read_text())
    issues = []
    checked = 0
    resolved_root = root.resolve()
    for row in contract['files']:
        relative = Path(row['path'])
        target = root / relative
        if relative.is_absolute() or '..' in relative.parts or target.is_symlink() or not target.resolve().is_relative_to(resolved_root):
            issues.append({'kind': 'unsafe-path', 'path': row['path']})
            continue
        if not target.is_file():
            issues.append({'kind': 'missing-file', 'path': row['path']})
            continue
        checked += 1
        if hashlib.sha256(target.read_bytes()).hexdigest() != row['sha256']:
            issues.append({'kind': 'hash-mismatch', 'path': row['path']})
    for role, font_id in EXPECTED_FONTS.items():
        if contract['typography'][role]['fontId'] != font_id:
            issues.append({'kind': 'font-role-mismatch', 'role': role})
    for page, frames in EXPECTED_FRAMES.items():
        if tuple(contract['pages'][page][mode] for mode in ['desktop', 'mobile']) != frames:
            issues.append({'kind': 'frame-mismatch', 'page': page})
    for font_id, spec in contract['fonts'].items():
        target = root / spec['path']
        relative = Path(spec['path'])
        if relative.is_absolute() or '..' in relative.parts or target.is_symlink() or not target.resolve().is_relative_to(resolved_root):
            issues.append({'kind': 'unsafe-path', 'font': font_id})
            continue
        if not target.is_file():
            issues.append({'kind': 'missing-font', 'font': font_id})
            continue
        try:
            with TTFont(target) as font:
                if font['name'].getDebugName(6) != spec['postscriptName']:
                    issues.append({'kind': 'font-identity-mismatch', 'font': font_id})
                missing = sorted({character for character in spec['requiredText'] if not character.isspace() and ord(character) not in font.getBestCmap()})
                if missing:
                    issues.append({'kind': 'missing-glyphs', 'font': font_id, 'characters': ''.join(missing)})
                if spec.get('axisRange'):
                    axes = {axis.axisTag: [axis.minValue, axis.maxValue] for axis in font['fvar'].axes} if 'fvar' in font else {}
                    if axes.get('wght') != spec['axisRange']:
                        issues.append({'kind': 'font-axis-mismatch', 'font': font_id})
        except Exception as error:
            issues.append({'kind': 'invalid-font', 'font': font_id, 'errorType': type(error).__name__})
    return {'verified': not issues, 'checkedFiles': checked, 'issues': issues, 'figmaSnapshotDate': contract['verifiedAt'], 'scope': 'Bundled design files and typography contract, not all Figma pages or backend readiness.'}


def main():
    parser = argparse.ArgumentParser(description='Verify the bundled Figma implementation baseline without network or external writes')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    report = validate(args.root.resolve())
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['verified'] else 2)


if __name__ == '__main__':
    main()
