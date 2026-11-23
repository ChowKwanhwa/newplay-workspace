from pathlib import Path
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import threading

from playwright.sync_api import sync_playwright

from design_baseline import ROOT, validate


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def actual_font_matches(rendered, spec, weight):
    names = {spec['postscriptName']}
    if spec.get('axisRange') and str(weight) == '700':
        names.add(spec['postscriptName'] + '_Bold')
    return bool(rendered) and all(font['isCustomFont'] and font['postScriptName'] in names for font in rendered)


def check(root, destination):
    baseline = validate(root)
    if not baseline['verified']:
        raise RuntimeError('Design baseline integrity check failed; run tools/design_baseline.py first.')
    destination.mkdir(parents=True, exist_ok=True)
    contract = json.loads((root / 'design/contract.json').read_text())
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(root / 'design')))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    origin = f'http://127.0.0.1:{server.server_port}'
    checks = []
    blocked = []
    try:
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch(channel='chrome', headless=True)
            context = browser.new_context()

            def local_only(route):
                if route.request.url.startswith(origin + '/'):
                    route.continue_()
                else:
                    blocked.append('non-local-request')
                    route.abort()

            context.route('**/*', local_only)
            for mode, width in [('desktop', 1440), ('mobile', 390)]:
                page = context.new_page()
                page.set_viewport_size({'width': width, 'height': 1000})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(origin + '/font-proof.html', wait_until='networkidle')
                page.evaluate('document.fonts.ready')
                session = context.new_cdp_session(page)
                session.send('DOM.enable')
                session.send('CSS.enable')
                document = session.send('DOM.getDocument')
                expected = {'#home-first': 'home', '#game': 'game', '#latin': 'latin', '#body-proof': 'body'}
                fonts = {}
                weights = {}
                failures = []
                for selector, font_id in expected.items():
                    node = session.send('DOM.querySelector', {'nodeId': document['root']['nodeId'], 'selector': selector})
                    rendered = session.send('CSS.getPlatformFontsForNode', {'nodeId': node['nodeId']})['fonts']
                    fonts[selector] = rendered
                    weight = page.locator(selector).evaluate('node => getComputedStyle(node).fontWeight')
                    weights[selector] = weight
                    if not actual_font_matches(rendered, contract['fonts'][font_id], weight):
                        failures.append({'selector': selector, 'kind': 'actual-font-mismatch'})
                    if weight != str(contract['fonts'][font_id].get('cssWeight', 700)):
                        failures.append({'selector': selector, 'kind': 'font-weight-mismatch'})
                layout = page.evaluate('''() => ({
                    bodyOverflow: document.documentElement.scrollWidth > innerWidth,
                    lines: [...document.querySelectorAll('.home > span, #game')].filter(node => node.getBoundingClientRect().height > 0).map(node => {
                        const range = document.createRange(); range.selectNodeContents(node);
                        const text = range.getBoundingClientRect(); const box = node.getBoundingClientRect();
                        return { text: node.textContent, width: box.width, textWidth: text.width, overflow: text.right > box.right + 2.1 };
                    })
                })''')
                if layout['bodyOverflow'] or any(line['overflow'] for line in layout['lines']):
                    failures.append({'kind': 'title-overflow'})
                if errors:
                    failures.append({'kind': 'browser-error', 'count': len(errors)})
                page.screenshot(path=str(destination / f'fonts-{mode}.png'), full_page=True)
                checks.append({'mode': mode, 'width': width, 'fonts': fonts, 'weights': weights, 'layout': layout, 'failures': failures})
                page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
    report = {'verified': not blocked and all(not item['failures'] for item in checks), 'checks': checks, 'blockedExternalRequests': len(blocked), 'scope': 'Local font render/identity and title geometry only; not full-page visual or interaction acceptance.'}
    (destination / 'font-browser-verification.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description='Check actual Chrome font rendering using bundled files only')
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--out-dir', type=Path, default=ROOT / '.local/migration/design-font-check')
    args = parser.parse_args()
    report = check(args.root.resolve(), args.out_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if report['verified'] else 2)


if __name__ == '__main__':
    main()
