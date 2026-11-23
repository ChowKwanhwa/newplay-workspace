# NewPlay development context

The next task on the new MacBook Pro is implementing existing Figma pages, not redesigning them.

- Read `CLAUDE.md`, `README.md`, `docs/WORKING_CONTEXT.md`, `docs/FIGMA_IMPLEMENTATION.md` and `design/contract.json` before website work.
- Run `uv run --frozen python tools/design_baseline.py`. Connect the user's own Figma MCP session; fetch exact target desktop/mobile design context and screenshots before coding.
- Approved hero fonts: home Chinese = original DouyinSans Bold (G); home Latin = Space Grotesk Bold; lieflat game name = ZCOOL KuaiLe Regular (F). Use bundled fonts and licenses, not system-dependent substitutes.
- Figma home Chinese is a vector display generated from the approved font. Hidden old text is not authoritative. Preserve the approved line breaks and markers; do not silently substitute a near-match font.
- Use lieflat frames602:126/602:252, not the legacy tower-defense frames. Do not turn prototype review navigation into website navigation.
- `newplay-library` is the resource library, not the marketing-site application. Reuse an existing frontend directory if one is later added; otherwise establish one only for an explicitly requested implementation task.
- Keep private data excluded. Missing receipts or private history are not permission to resend, republish or redeploy. Never perform external writes as installation tests.
- Mock payments, NC, agent status, rewards and ranking data are not real backend functionality. Do not fabricate production states.
- Use project-local locked Python dependencies. Do not depend on a previous Mac's absolute paths, global fonts or copied virtual environments.
- Before completion, verify actual browser fonts and responsive geometry, then compare implemented desktop/mobile pages with current Figma screenshots. The provided font proof is a technical check, not a production page.
