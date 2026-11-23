from pathlib import Path
import copy
import json
import tempfile
import unittest

from design_baseline import validate
from check_design_fonts import actual_font_matches
from build_figma_title_outlines_20261123 import FONT, outline_spec


ROOT = Path(__file__).resolve().parents[1]


class DesignBaselineTests(unittest.TestCase):
    def test_figma_outline_builder_uses_bundled_approved_font(self):
        self.assertEqual(FONT, ROOT / 'design/fonts/DouyinSansBold.ttf')
        for mobile in [False, True]:
            spec = outline_spec(mobile)
            self.assertEqual(spec['sourceSha256'], 'fbecfacdfac33982774e301073a8d357a09c698cd3134bb6ddec0f5bfc268fa1')
            self.assertLessEqual(max(spec['rowWidths']), spec['width'])

    def test_variable_bold_platform_alias_is_not_a_font_substitution(self):
        spec = {'postscriptName': 'SpaceGrotesk-Light', 'axisRange': [300, 700]}
        rendered = [{'postScriptName': 'SpaceGrotesk-Light_Bold', 'isCustomFont': True}]
        self.assertTrue(actual_font_matches(rendered, spec, '700'))
        self.assertFalse(actual_font_matches(rendered, spec, '400'))

    def test_system_fallback_and_wrong_font_are_rejected(self):
        spec = {'postscriptName': 'DOUYINSANSBOLD-GB'}
        self.assertFalse(actual_font_matches([{'postScriptName': 'DOUYINSANSBOLD-GB', 'isCustomFont': False}], spec, '400'))
        self.assertFalse(actual_font_matches([{'postScriptName': 'NotoSansSC-Thin', 'isCustomFont': True}], spec, '400'))
        self.assertFalse(actual_font_matches([], spec, '400'))

    def test_current_baseline_is_self_contained(self):
        report = validate(ROOT)
        self.assertTrue(report['verified'], report['issues'])
        self.assertGreaterEqual(report['checkedFiles'], 12)

    def test_missing_baseline_is_not_ready(self):
        with tempfile.TemporaryDirectory() as folder:
            report = validate(Path(folder))
            self.assertFalse(report['verified'])
            self.assertEqual(report['issues'][0]['kind'], 'missing-contract')

    def test_changed_file_is_detected(self):
        contract = json.loads((ROOT / 'design/contract.json').read_text())
        contract = copy.deepcopy(contract)
        contract['files'][0]['sha256'] = '0' * 64
        report = validate(ROOT, contract=contract)
        self.assertIn('hash-mismatch', {issue['kind'] for issue in report['issues']})

    def test_escape_path_is_rejected(self):
        contract = json.loads((ROOT / 'design/contract.json').read_text())
        contract['files'].append({'path': '../outside.ttf', 'sha256': '0' * 64})
        report = validate(ROOT, contract=contract)
        self.assertIn('unsafe-path', {issue['kind'] for issue in report['issues']})

    def test_wrong_home_font_is_detected(self):
        contract = json.loads((ROOT / 'design/contract.json').read_text())
        contract['typography']['homeChinese']['fontId'] = 'game'
        report = validate(ROOT, contract=contract)
        self.assertIn('font-role-mismatch', {issue['kind'] for issue in report['issues']})

    def test_legacy_game_frame_is_rejected(self):
        contract = json.loads((ROOT / 'design/contract.json').read_text())
        contract['pages']['lieflat']['desktop'] = '121:230'
        report = validate(ROOT, contract=contract)
        self.assertIn('frame-mismatch', {issue['kind'] for issue in report['issues']})


if __name__ == '__main__':
    unittest.main()
