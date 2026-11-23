from pathlib import Path
import hashlib
import json

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen


ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'tmp/figma-title-font-update-20261123'
FONT = ROOT / 'design/fonts/DouyinSansBold.ttf'


def outline_spec(mobile):
    font = TTFont(FONT)
    glyphs = font.getGlyphSet()
    cmap = font.getBestCmap()
    units = font['head'].unitsPerEm
    size = 64 if mobile else 100
    source_size = 64 if mobile else 104
    width, height = (358, 274) if mobile else (690, 333)
    line_height = source_size * 1.08
    tracking = source_size * -.02
    lines = ['年轻人的', '数字娱乐', '空间。'] if mobile else ['年轻人的', '数字娱乐空间。']
    paths = []
    row_widths = []
    keyword_widths = {}
    total_bounds = [width, height, 0, 0]
    for row, text in enumerate(lines, 1):
        baseline = row * line_height + line_height / 2 + (font['hhea'].ascent + font['hhea'].descent) / units * size / 2
        cursor = 0
        keyword = '年轻人的' if row == 1 else '数字娱乐' if row == 2 else ''
        for position, char in enumerate(text):
            glyph_name = cmap[ord(char)]
            pen = SVGPathPen(glyphs)
            scale = size / units
            glyphs[glyph_name].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, baseline)))
            bounds_pen = BoundsPen(glyphs)
            glyphs[glyph_name].draw(bounds_pen)
            bounds = bounds_pen.bounds
            if bounds:
                actual = [cursor + bounds[0] * scale, baseline - bounds[3] * scale, cursor + bounds[2] * scale, baseline - bounds[1] * scale]
                total_bounds = [min(total_bounds[0], actual[0]), min(total_bounds[1], actual[1]), max(total_bounds[2], actual[2]), max(total_bounds[3], actual[3])]
            paint = '#05289C' if position < len(keyword) else 'url(#brand)'
            paths.append(f'<path id="G-{row}-{position}" d="{pen.getCommands()}" fill="{paint}"/>')
            cursor += font['hmtx'][glyph_name][0] * scale
            if position < len(text) - 1:
                cursor += tracking
            if keyword and position == len(keyword) - 1:
                keyword_widths[keyword] = cursor - (tracking if position < len(text) - 1 else 0)
        row_widths.append(cursor)
    assert max(row_widths) <= width
    assert total_bounds[0] >= 0 and total_bounds[1] >= 0 and total_bounds[2] <= width and total_bounds[3] <= height, total_bounds
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><defs><linearGradient id="brand" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{width}" y2="0">__GRADIENT_STOPS__</linearGradient></defs>{"".join(paths)}</svg>'
    return {'svg': svg, 'width': width, 'height': height, 'fontSize': size, 'sourceFontSize': source_size, 'lineHeight': line_height, 'tracking': tracking, 'rowWidths': row_widths, 'keywordWidths': keyword_widths, 'bounds': total_bounds, 'sourceSha256': hashlib.sha256(FONT.read_bytes()).hexdigest(), 'family': 'DouyinSans', 'style': 'Bold', 'sourceUrl': 'https://github.com/bytedance/fonts'}


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    output = {'desktop': outline_spec(False), 'mobile': outline_spec(True)}
    (WORK / 'outlines.json').write_text(json.dumps(output, ensure_ascii=False, indent=2))
    for mode, spec in output.items():
        print(mode, {key: spec[key] for key in ['fontSize', 'rowWidths', 'keywordWidths', 'bounds']})


if __name__ == '__main__':
    main()
