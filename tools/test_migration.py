from pathlib import Path
import tempfile
import unittest

from migration import audit, inspect_text, make_manifest, verify_manifest, skipped_asset


class MigrationTests(unittest.TestCase):
    def test_secret_values_never_appear_in_report(self):
        secret = 'example-credential-value-for-test'
        issues = inspect_text('tools/example.py', f'TOKEN = "{secret}"\n', [secret])
        self.assertTrue(any(item['kind'] == 'credential-value' for item in issues))
        self.assertNotIn(secret, str(issues))

    def test_machine_paths_are_reported(self):
        issues = inspect_text('tools/example.py', 'FONT="/Users/somebody/Library/Fonts/font.ttf"\n', [])
        self.assertEqual(issues[0]['kind'], 'machine-path')

    def test_cache_exclusion_keeps_receipts_and_fonts(self):
        self.assertTrue(skipped_asset(Path('tmp/telegram-cli-cache/archive/data')))
        self.assertFalse(skipped_asset(Path('tmp/task/send-small/receipt.json')))
        self.assertFalse(skipped_asset(Path('tmp/task/fonts/font.ttf')))

    def test_manifest_detects_missing_and_changed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'raw').mkdir()
            (root / 'raw/input.txt').write_text('input')
            manifest = make_manifest(root, ['raw'], hashed=True)
            self.assertEqual(verify_manifest(root, manifest), [])
            (root / 'raw/input.txt').write_text('other')
            self.assertEqual(verify_manifest(root, manifest)[0]['kind'], 'hash-mismatch')
            (root / 'raw/input.txt').unlink()
            self.assertEqual(verify_manifest(root, manifest)[0]['kind'], 'missing')

    def test_manifest_rejects_unsafe_restore_paths(self):
        with tempfile.TemporaryDirectory() as folder:
            issues = verify_manifest(Path(folder), {'files': [{'path': '../escape', 'size': 0}]})
            self.assertEqual(issues[0]['kind'], 'unsafe-path')

    def test_manifest_does_not_follow_symlinks(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'raw').mkdir()
            (root / 'raw/link').symlink_to('/etc/hosts')
            manifest = make_manifest(root, ['raw'], hashed=True)
            self.assertEqual(manifest['files'], [])
            self.assertEqual(manifest['warnings'][0]['kind'], 'symlink-not-copied')

    def test_manifest_does_not_follow_top_level_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'raw').symlink_to('/etc', target_is_directory=True)
            manifest = make_manifest(root, ['raw'], hashed=True)
            self.assertEqual(manifest['files'], [])
            self.assertEqual(manifest['warnings'][0]['kind'], 'symlink-not-copied')

    def test_audit_checks_env_template_against_private_values(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            secret = 'example-private-credential-value'
            (root / '.env').write_text('TOKEN=' + secret)
            (root / '.env.example').write_text('TOKEN=' + secret)
            report = audit(root)
            self.assertEqual(report['affectedFilesByKind']['credential-value'], 1)
            self.assertNotIn(secret, str(report))

    def test_private_operation_cache_is_backed_up_but_not_audited_as_code(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            cache = root / 'newplay-library/.cache'
            cache.mkdir(parents=True)
            (cache / 'uploads.json').write_text('{"path":"/Users/previous/project/input.png"}')
            report = audit(root)
            self.assertEqual(report['filesScanned'], 0)
            self.assertFalse(skipped_asset(Path('newplay-library/.cache/uploads.json')))
            manifest = make_manifest(root, ['newplay-library/.cache'], hashed=True)
            self.assertEqual(manifest['fileCount'], 1)


if __name__ == '__main__':
    unittest.main()
