> **Start with `HANDOFF.md`** — it is the wiring manifest: endpoint contract, per-page
> live-vs-scripted status, and the single file to edit (`api.js`). This file covers
> serving and caching only.

# Deployment scope — CITINEL UI prototype

What ships is the product surface only. Everything below is excluded from the
deployed build; it stays in project history as the design and QA record.

## Already removed from the project

These were deleted in the export-readiness pass, not merely excluded. Nothing
referenced them.

    _audit/                 measurement harnesses (reflow, matrix, read,
                            harness, sweep). QA tooling, never product surface.
    uploads/                source material the brand crops in assets/ came from.
    screenshots/            capture byproducts from verification passes.

## Exclude — project instructions, not routes

    CLAUDE.md               standing build instructions
    HANDOFF.md              backend wiring manifest
    DEPLOY.md               this file

## Exclude — shared child components, not pages

These are mounted by their parent screens via `<dc-import>` and are never
navigated to. They open standalone only because every Design Component is a
valid document; they are not routes and must not be linked or indexed.

    StandardRef.dc.html
    RuleRef.dc.html
    ExternalProvenance.dc.html
    ExternalCitationChip.dc.html
    StateNotice.dc.html

## Ship — routes

    Entry.dc.html           Shell.dc.html          Overview.dc.html
    Queue.dc.html           Replay.dc.html         Confidence.dc.html
    Evidence.dc.html        Approvals.dc.html      Corpus.dc.html
    Eval.dc.html            Policy.dc.html         Compliance.dc.html
    Audit.dc.html           Handover.dc.html       Executive.dc.html
    Settings.dc.html        Demo.dc.html

## Ship — runtime assets

    support.js  role.js  ledger.js  reveal.js  motion.js
    a11y.css  motion.css
    assets/lockup-white.png  assets/lockup-navy.png
    _ds/citinel-design-system-fdfd662c-b7a8-446c-963a-2f11a1f91d2a/

## Cache

`a11y.css` carries the layout guardrails, the reflow rules and the focus
ring; `motion.css` carries the instrument animation. Both change more often than
any screen. Serve them with a content hash in the filename or
`Cache-Control: no-cache` — a stale copy silently reverts the reflow behaviour and
the focus states, which is a defect class this build has already hit once.
