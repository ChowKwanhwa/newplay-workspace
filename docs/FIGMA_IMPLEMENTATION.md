# Figma implementation baseline

The next task on the new MacBook Pro is implementing existing Figma pages, not redesigning them. Read this document and `design/contract.json`; validate the bundled files before coding. Fetch current exact-node design context and screenshots through the user's own Figma MCP session, rather than relying only on this dated snapshot.

## Approved typography

| Role | Original font | Local CSS alias | Weight |
|---|---|---|---|
| Home Chinese hero | DouyinSans Bold, approved G | NewPlay Douyin | 400 mapped to original Bold outlines |
| Home Latin hero | Space Grotesk Bold | NewPlay Space | 700 variable axis |
| Lieflat game name | ZCOOL KuaiLe Regular, approved F | NewPlay KuaiLe | 400 |
| Chinese body | Noto Sans SC | NewPlay Noto SC | Read actual node; commonly400/500/700/900 |

Use `design/fonts.css` and the original bundled fonts with their OFL licenses. Do not depend on macOS font installation, a CDN or old temporary folders. Do not substitute Archivo for Space Grotesk, QingKe HuangYou for the game name or a visually similar font for G.

DouyinSansBold.ttf reports OS/2 weight400 despite containing the intended bold outlines. Keep the explicit400 CSS mapping and `font-synthesis:none`. Variable Space's internal name says Light and Noto's says Thin; use the intended axis, not that name, to determine UI weight.

### Figma vector-title trap

The home Chinese title is a visible editable vector display generated from the exact approved font. A retained hidden source TextNode may still report an old font: **that hidden font is not authoritative**. Read shared metadata namespace `newplay`, key `typography` from the visible display. Implement accessible real text with the bundled original TTF, not a screenshot or the legacy hidden font.

Latin remains native Space Grotesk. Its fullwidth comma uses explicit local Noto SC fallback; verify punctuation and spacing instead of replacing punctuation to fit. G/F apply only to the approved hero titles, not all headings throughout the site.

## Reference geometry

| Property | Desktop1440 | Mobile390 |
|---|---|---|
| Home title frame | 690×333 | 358×274 |
| Chinese size / line-height / tracking | 100 /112.32 /−2.08px | 64 /69.12 /−1.28px |
| Latin size / line-height | 104 /112.32px | 64 /69.12px |
| Complete title lines | NewPlay， / 年轻人的 / 数字娱乐空间。 | NewPlay， / 年轻人的 / 数字娱乐 / 空间。 |
| Game size / line-height / frame | 124px /110% /600×136 | 88px /110% /350×97 |

Home keyword text `#05289C`, yellow marker `#FFE44D`, mint marker `#A8F5D5`; marker widths415.76px desktop and268.16px mobile. Other title letters keep the actual continuous blue-green gradient; inspect current fills instead of inventing a near-match. Game title yellow is `#FFE04B`.

These are reference widths, not approved CSS breakpoints. Verify360/390/768/1024/1440 without shrinking the whole desktop page. The600px breakpoint in the font proof is for switching test specimens only.

## Exact pages

Figma key: `gtNhFwsEyHWKZU6dNWXsiZ`.

- Formal home desktop61:2 / mobile62:2; playback438:857 /438:2148.
- Formal lieflat desktop602:126 / mobile602:252; playback609:1120 /609:2101.
- NewCoin119:11 /119:159; fortune122:230 /122:309; fortune result372:49 /378:125.
- AI studio118:37 /112:13; cooperation119:335 /119:453; classic119:573 /121:92.
- Mini games122:11 /122:120; about123:11 /123:132; jump167:21 /167:23.
- Payment ready167:29 /167:31; pending236:49 /237:59.

Use links such as https://www.figma.com/design/gtNhFwsEyHWKZU6dNWXsiZ/NewPlay?node-id=61-2 with the exact target node. Old tower-defense frames121:230/121:362 are not the current lieflat page. The contract and readback preserve machine-readable node mappings; check for later approved remote updates before implementation.

## Assets and behavior

Selected original assets and hashes are bundled. The home hero is an RGB ice-blue image, not a transparent cutout. Intro/Agent PNGs and the official logo PNG have alpha; do not add a white logo background.

The four reference screenshots show current home/lieflat desktop/mobile prototypes. Home references include dark-blue review navigation above the website: do not implement that review chrome as production navigation. Use formal frames for layout and prototypes for behavior.

Layered PNG parallax is not a true interactive3D mesh. No GLB, skeleton, rig or generated3D character model is bundled. Do not claim real mouse-driven character actions from a static image.

Read each section's actual motion; avoid repeating the same floating dots everywhere. Keep text and controls stable, support pause/resume, reduced-motion preferences and touch without hover; do not autoplay audible video.

Quiz rewards, rankings, NC, payments and AI status include mock states. Do not turn them into real transactions, fabricated live data or guaranteed rewards without explicit backend/product requirements. Respect current role states and do not restore withdrawn historical content.

## Verification

Run `uv run --frozen python tools/design_baseline.py` and `uv run --frozen python tools/check_design_fonts.py`. The latter checks actual Chrome font identities, weights and reference line widths using local files; CSS declarations alone are not proof of correct rendering.

These checks prove bundled font/data portability, not full-page acceptance. Implemented pages still require desktop/mobile screenshot comparison, intermediate-width/overflow tests, navigation/modal states, motion pause/reduction, error/loading/empty states and normal frontend quality checks. Never deploy or send messages as an installation test.
