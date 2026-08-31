# CITINEL Design System

CITINEL — Autonomous Cyber SOC by Team AeroFyta (Decode SIH 2026). A dense, dark-first 24/7 security-operations console for Indian cooperative banks and small NBFCs, plus a lighter executive view. Every verdict cites the exact log line behind it. Tagline: **Caught. Cited. Closed.**

The aesthetic lane is **Statutory Instrumentation**: glass-cockpit / trading-terminal discipline, not SaaS-dashboard decoration. The screens must be credible enough to hand to an RBI auditor unaltered. Optimize for "could this be produced in a tribunal without alteration," never "does this look premium." Apply the instrument-vs-costume test to every flourish: if removing it destroys no real information, delete it.

Sources given: eight locked brand PNGs (falcon navy/white, wordmark navy/white, app icon dark/light, badge+tagline dark/light), now in `assets/`, plus the full CITINEL screen-generation brief (§1–§15) pasted as the opening message. No Figma, no codebase — components here are authored from the brief's explicit specifications.

## Content fundamentals

- Terse operational prose, the register a real analyst writes at 3am: "Three failed su attempts preceded the dump." No marketing voice inside the product.
- Name exact mechanisms, never intensifiers: "OCSF 1.4.0", "3,000-rule Sigma corpus", "MITRE ATT&CK v16", "Open Policy Agent" — never "AI-powered", "next-gen", "seamless", "single pane of glass", "enterprise-grade", or any "100% coverage" claim.
- Bounded numbers over adjectives: "214/823 techniques mapped", not "broad coverage". "We draft, we never file." "Sits beside your SIEM — the bank keeps its SIEM."
- Caught / Cited / Closed are literal, functioning UI state labels, not just tagline copy.
- No Title Case headers in generated copy, no bold-term-colon bullet lists, no all-caps sentences, no emoji ever.
- Sentence case everywhere humans read; the display face's all-caps is reserved for placards (eyebrows, status tags) ≤ ~24 characters.
- Family naming: `CITINEL [Domain Noun]` (AIOps, Fraud, Exchange); connector packs named after the concrete system (`Finacle Connector Pack`); regulator packs literally the regulator (`SEBI Pack`). AeroFyta is the legal brand — footer/legal only.

## Visual foundations

- **Color:** five locked sRGB hexes — navy `#0B1F3A`, charcoal `#0E1116`, white, evidence-gold `#E7B10A`, severity-red `#D01F17` (fill) / `#E8594A` (text on dark). Everything else is OKLCH-derived (`tokens/colors.primitive.css`). Gold appears on exactly two element types system-wide: citation chips and the statutory clock. Red is severity only, and the deny dead-end. Max one accent per surface — no component takes both gold and red.
- **Elevation:** stepped surface lightness (well → shell → panel → raised), never shadow bloom. One edge treatment per surface class: inline/scrolling = hairline border, zero shadow; floating/overlay = one coordinated navy-hue shadow (`--ctn-shadow-overlay`), zero border. Never both.
- **No gradients, no glow, no backdrop-blur, no glassmorphism, anywhere.** No bento grids, no icon-tile card grids, no colored-left-border severity.
- **Radius:** exactly three tokens — pill (chips/tags), 6px (dense rows/tiles), 14px (large single-instance surfaces only).
- **Type:** three strictly separated tiers. Display = Michroma (Orbitron fallback), placards only, never a heading tag, never prose. Body = IBM Plex Sans 14px/1.55 — deliberate pairing: an instrumentation-heritage grotesque with a distinct numeral set (not Inter/Geist/Space Grotesk/Instrument Serif). Mono = zero-payload OS stack, 13px logs / 12px audit-dense, letter-spacing always 0. Weight floor 400.
- **Numerals:** `tabular-nums slashed-zero` on all clocks and counts.
- **Motion:** purpose-bound only — a value updating, a queue re-sorting, a clock ticking. Nothing decorative; nothing competes with an Approve/Deny decision. `prefers-reduced-motion` swaps motion for opacity + a non-motion cue, never nothing.
- **Hover/selected:** background step + left indicator dot, never font-weight (no reflow jitter). Focus: two-color ring via box-shadow (light ring + dark spacer). Dropdowns open on mousedown.
- **Severity:** documented 4-step ramp; every step = color + shape glyph + printed label + rank position. Critical octagon (solid fill, 3px), high triangle, medium diamond, low circle — grayscale-discriminable.
- **State machine:** Caught (navy circle) → Cited (~270° gold arc) → Gated (dashed hollow circle, deny branch dead-ends in a red square) → Actioned (navy diamond, heaviest stroke) → Closed (arc completes to a full gold ring). Stroke weight rises monotonically. Gold never before Cited; red only on deny.
- **Evidence:** citation chips are gold hairline mono pills with a visible locator; provenance is always the triplet (timestamp · source · hash); the audit log is visually append-only (no edit/delete/reorder affordances); attacker-controlled text always rides in the four-signal quarantine well (mono + inset + dashed gray + persistent corner label).
- **Imagery:** none. No photography, no illustration. The falcon renders in exactly two lockups: white-on-navy, navy-on-white.

## Iconography

Inline SVG only, stroke-based on a 16/20/24px grid; no emoji, no dingbats, no icon fonts. Every icon must pass the removal test — functional or deleted, never wrapped in a tinted container. The system ships only functional glyphs: the four severity shapes (in `SeverityBadge`), the state-machine primitives (circle/arc/diamond in `StateChain`), and `§` as the citation marker. If a broader set is ever needed, use Lucide from CDN (matching 1.5px stroke) and flag the addition here. Third-party names (OCSF, Sigma, ATT&CK, OPA, the bank's SIEM) render as plain typographic citations, never fetched logos.

## Token architecture

Namespace `--ctn-`, tiered per the brief (§11):
- `tokens/colors.primitive.css` — Tier 0 raw values (locked hexes + OKLCH ramp). Never referenced by product code.
- `tokens/colors.semantic.css` — Tier 1 meaning-bearing roles (surfaces, text, severity, evidence, state, focus).
- `tokens/brand.flagship.css` — Tier 1.5: the single skin override point. A skin/partner file may declare ONLY `--ctn-brand-accent`, `--ctn-logo-lockup`, `--ctn-partner-name-text`.
- `tokens/component.css` — Tier 2 component-scoped, references semantic only.
- `tokens/typography.css`, `tokens/spacing.css`, `tokens/base.css`, `tokens/fonts.css` (Google Fonts: Michroma, Orbitron, IBM Plex Sans).

Locked, never re-themeable: the severity ramp, gold's binding to citations + clock, the falcon's two renderings, the state-machine shapes/sequence, the display family.

## Components

All in `components/`, each with `.d.ts` props contract and `.prompt.md` usage note:

- `actions/Button` — primary / approve / deny / secondary / ghost; display-face caps labels
- `indicators/SeverityBadge` — the shape-coded severity ramp
- `evidence/CitationChip` — gold locator pill; click opens the verbatim log line
- `evidence/Provenance` — mandatory timestamp · source · hash triplet
- `evidence/LogWell` — inset mono well with hanging punctuation for quoted machine text
- `evidence/QuarantineWell` — four-signal untrusted-content treatment
- `instruments/StatutoryClock` — gold statutory countdown / white elapsed
- `instruments/StateChain` — the five-node Caught→Cited→Gated→Actioned→Closed device
- `instruments/Sparkline` — axis-free trend line
- `forms/Input`, `forms/Select`, `forms/Switch` (in `FormControls.jsx`; `FormControls` itself is an empty namespace export)

UI-kit screens (also exported): `Shell`, `OverviewScreen`, `IncidentReplay`, `ApprovalCenter`, `AuditLogScreen`, `QueueScreen`.

Intentional additions: all components trace to devices the brief names; none are generic-library filler. Toast/Tooltip/Tabs etc. were deliberately not authored — the brief defines no such devices.

## Index

- `styles.css` — global entry; `@import`s everything under `tokens/`
- `assets/` — falcon (navy/white), wordmark (navy/white), app icons, badge+tagline lockups (the badge PNGs contain a gradient falcon rendering — badge/sticker use only; it predates the no-gradient lock)
- `guidelines/` — 17 specimen cards: colors (4), type (4), foundations (4), brand (3), state machine, evidence set (4)
- `components/` — primitives listed above, with showcase cards
- `ui_kits/console/` — the interactive flagship console (`index.html`): overview, alert queue, glass-box replay, action center, append-only audit log
- `SKILL.md` — agent skill entry point

## Caveats

- Fonts load from Google Fonts (Michroma, Orbitron, IBM Plex Sans) — no font binaries ship in-repo. Provide licensed files if offline use is required.
- The monospace tier is deliberately the OS stack (per brief §4) — rendering varies slightly per platform by design.
- The badge-tagline PNGs are the one gradient-bearing brand asset; quarantined to sticker/badge contexts.
