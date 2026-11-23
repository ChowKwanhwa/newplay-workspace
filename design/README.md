# Portable design baseline

Read `docs/FIGMA_IMPLEMENTATION.md` and `contract.json` before coding. This is a dated technical baseline, not an implemented website or redesign proposal.

- `fonts/`: four original OFL families and licenses, normal Git files.
- `fonts.css`: local loading and explicit approved font roles.
- `assets/`: selected NewPlay artwork; font licenses do not apply to branded images.
- `reference/`: current home/lieflat desktop/mobile screenshots; home review chrome is not part of the website.
- `figma-readback-20261124.json`: read-only page/font inventory.
- `font-proof.html`: technical font specimen, not a production page.

Validate hashes and coverage with `tools/design_baseline.py`, actual rendering with `tools/check_design_fonts.py`. Original TTFs remain intact for fidelity. Subsetting/optimization and reserved-name license implications require separate review; never replace an approved font silently.
