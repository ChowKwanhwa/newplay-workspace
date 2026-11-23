# NewPlay workspace

Public source snapshot for continuing NewPlay development on another Mac. Includes the resource-library application and the verified Figma implementation baseline. It is not the complete private production archive or an implemented marketing website.

## New Mac setup

```sh
git clone https://github.com/ChowKwanhwa/newplay-workspace.git
cd newplay-workspace
brew bundle --file Brewfile
sh scripts/bootstrap.sh
uv run --frozen python tools/design_baseline.py
uv run --frozen python -m unittest discover -s tools -p 'test_*.py'
npm test --prefix newplay-library
uv run --frozen python tools/check_design_fonts.py
```

Python dependencies are locked in `uv.lock`. Do not copy an old virtual environment. Chrome is required for the local font-render check. System-tool versions are not fully locked.

## Start implementing Figma pages

Read `AGENTS.md`, `docs/WORKING_CONTEXT.md`, `docs/FIGMA_IMPLEMENTATION.md`, then `design/contract.json`. Before coding, connect your own Figma MCP session and fetch the exact current desktop/mobile nodes and screenshots. The bundled references are a dated baseline, not a replacement for checking later design updates.

- Home Chinese hero: original DouyinSans Bold, approved option G.
- Home Latin hero: Space Grotesk Bold.
- Lieflat game hero title: ZCOOL KuaiLe Regular, approved option F.
- Other text: inspect the target node; bundled Noto Sans SC provides the Chinese body family.

Original font files, OFL licenses, key project images and four Figma reference screenshots are bundled. They do not require Git LFS or installing fonts into macOS. Home Chinese is represented by font-derived vector outlines in Figma: hidden legacy text is not the current font authority.

## Included source

- `newplay-library/`: Cloudflare Worker, static UI, published catalog snapshot and offline tests.
- `design/`: precise typography/page mapping, licensed fonts, selected assets and reference screenshots.
- `tools/`: read-only migration/design validators and local typography checks.
- `docs/`: public-safe development and migration instructions.

The resource library is not the marketing-site frontend. Create or reuse a separate frontend application when implementation begins; do not overwrite the library Worker.

## Excluded data

Credentials, sessions, account logins, private Wiki, chat history, messaging automations, operational receipts, historical source materials and production archives are not in this public repository. Restore privately only when needed and authorized. Their absence does not mean they never existed or that prior external operations should be repeated.

No website deployment, message sending, real payment, NC deduction or reward issuance is part of setup. Public catalog metadata and thumbnails do not bundle the downloadable production documents or their R2 storage.

## Rights

Public visibility does not grant a general open-source license to NewPlay code or branded artwork. No project-wide license is granted by this snapshot. Bundled fonts retain their individual OFL licenses and copyright notices. Use project artwork only with the rights holder's permission.
