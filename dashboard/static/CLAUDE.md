# Standing instructions — CITINEL screen builds

Apply to EVERY screen, not once:

1. Name a real physical-instrument tradition the screen's composition borrows from, and why. Vary the source across the app — never reuse the same reference (e.g. if Overview borrowed from an ATC strip board, the next hero screen draws from a genuinely different discipline's instrument). Seventeen "cockpit-styled" screens is a second cliché.
2. Identify the single most operationally critical element and make it dominate the composition by an order of magnitude — never a peer among equal boxes.
3. For screens presenting sets of items, produce genuinely different compositional geometries as options before committing — not re-skins of one grid.
4. Every hero screen (investigation replay, approval card, compliance clock) gets at least one real, state-tied physical-instrument behavior — moves like a needle sweep / strip advance / ring completion, driven by actual data changing, never decoration.
5. The Caught → Cited → Gated → Actioned → Closed arc-into-ring device is the product's one signature visual move. Let it recur meaningfully wherever honestly earned (compliance clock, audit log, shift handover card), not live once in one widget.
6. Self-test every result: negatively — "could this be mistaken for a Stripe/Linear/Vercel dashboard with labels swapped?" (if yes, redo); positively — "Bloomberg-terminal density AND decisive hierarchy?" (dense without hierarchy, or hierarchical without density, both fail).

All colors, type, spacing, tokens come from the imported CITINEL Design System — never specified per screen. Invent layout/motion/composition, differently across screens. Do not ask the user to re-state any of this.

## File hygiene (standing)

- **Revise in place.** Never archive a "v1" copy when a critique or later prompt causes a rebuild. No version history in the file list.
- **Never materialize rejected options as pages.** When the directive above calls for exploring different compositional geometries, describe the options in chat and build only the chosen one.
- **"Every screen built so far" means the canonical set only** — the 12 screens plus 2 shared components listed below. There are no archives.

### Canonical page set

Screens: `Entry`, `Shell`, `Overview`, `Queue`, `Replay`, `Confidence`, `Evidence`, `Approvals`, `Corpus`, `Eval`, `Policy`, `Compliance`, `Audit`, `Handover`, `Executive`, `Demo`, `Settings` (all `*.dc.html`).
Shared components: `ExternalCitationChip.dc.html`, `ExternalProvenance.dc.html`, `StandardRef.dc.html`, `RuleRef.dc.html`, `StateNotice.dc.html`.
Shared logic: `role.js` (analyst/CISO depth), `ledger.js`, `reveal.js`, `motion.js`, `api.js` (backend seam — see `HANDOFF.md`). Shared CSS: `a11y.css`, `motion.css`, `transitions.css` (page-to-page navigation only — a deliberate, Danish-approved exception to motion.css's own "no decorative animation" rule; see that file's header comment).
No `_audit/`, `uploads/` or `screenshots/` folders exist — deleted, not archived.

### Standing artefact rules
Version-pin every standard citation (`StandardRef`), give every fired detection a copyable rule id (`RuleRef`), use specific sub-technique ids, state coverage as a bounded count (214/823), pin the corpus commit + sync time, keep OPA decision traces expandable, and publish no measurement without its denominator.

### Layout rule — section header rows
A section header row that carries a prose subhead must be `flex-wrap:wrap`, with the last fixed item before the subhead taking `margin-right:auto` and the subhead on its own line via `flex:1 1 100%` plus a `max-width:110ch` measure. Never leave a two-sentence note as `flex:1` inside a `nowrap` row beside a wide display-face title — it collapses to a vertical ribbon and blows up the row height. This has been fixed on Corpus, Demo, Handover, Audit and Confidence; do not re-author the broken pattern.
Assets: `assets/lockup-white.png`, `assets/lockup-navy.png`.

### Narrow view: removed 2 Sep 2026
`Narrow.dc.html` and `route.js` (the sub-720px width redirect) were deleted on Danish's explicit instruction. There is no separate narrow composition and no width-based routing any more: every screen renders itself at whatever width it gets. Do not reintroduce either without asking — this reverses an earlier decision that had kept the tour card, and it was made deliberately.
