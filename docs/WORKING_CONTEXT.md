# Continue on a new Mac

The next planned task is to implement the existing NewPlay Figma pages. Do not restart typography selection or redesign the pages by default.

Read `docs/FIGMA_IMPLEMENTATION.md` and `design/contract.json`. Exact approved fonts, licenses, selected images and four reference screenshots are bundled in `design/`. Home Chinese uses G DouyinSans Bold, Latin uses Space Grotesk Bold, and the lieflat hero game name uses F ZCOOL KuaiLe Regular. The home Chinese display in Figma uses font-derived vectors; hidden legacy text must not determine the frontend font.

No marketing-site frontend is implemented by this migration snapshot. The existing `newplay-library` application is a different service. Confirm whether a frontend application has subsequently been added before scaffolding another one.

Current visual authority is the exact remote Figma target and subsequent user approvals. The dated local baseline must be updated explicitly if new approvals change it. Fetch design context and screenshots before implementing each page.

Private archives, conversations, service authorization and historical operation receipts are deliberately absent. Do not reconstruct business requirements from guesses or interpret missing history as permission to repeat external operations. Setup only validates dependencies and bundled design data.
