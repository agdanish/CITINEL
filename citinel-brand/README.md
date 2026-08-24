# CITINEL Brand Assets

Authoritative reference for everything in `citinel-brand/`. If a claim about the brand conflicts with this file, this file wins. Do not invent assets, colors, spellings, or taglines that are not listed here.

**For AI tools and agents working in this repo:** read the "Hard rules" section before touching, referencing, or generating anything brand-related.

---

## Identity

| Field | Value |
|---|---|
| Product | CITINEL |
| Official styling | "CITINEL — Autonomous Cyber SOC" (locked; rename frozen until after 5 Sep 2026) |
| Name meaning | CITE + SENTINEL: the sentinel that cites its evidence. Phonetic bonus: sounds like "citadel" |
| Team | Team AeroFyta ("The Sentinel Six") |
| Context | Decode SIH 2026, Track 3 Bharat Pragati, PS4: Autonomous Cyber SOC for AI-powered threat detection and automated incident response |
| Symbol | One faceted crystal falcon. There is exactly one falcon design. Any other bird or wing style is deprecated |

Spelling is always `CITINEL` (C-I-T-I-N-E-L) and `AEROFYTA` (A-E-R-O-F-Y-T-A). Autocorrect drift to CITADEL, SENTINEL, CITIZEN, CITINAL, or AEROFYTA variants is a bug.

---

## Asset inventory (15 files)

| File | What it is | Background | Use on |
|---|---|---|---|
| `citinel-badge-full.png` | Circular badge: crystal falcon + CITINEL + AUTONOMOUS CYBER SOC + TEAM AEROFYTA. No "SIH 2026" text | Opaque white inside the circle (sticker style, by design) | Title slide, splash, print, DP |
| `citinel-badge-tagline-light.png` | Badge with "CAUGHT. CITED. CLOSED." below in navy | Transparent canvas | Light surfaces |
| `citinel-badge-tagline-dark.png` | Same badge, tagline in white | Transparent canvas | Dark surfaces |
| `citinel-wordmark-navy.png` | Falcon + CITINEL lettering, solid navy | Light / transparent | Light slides, docs, README light mode |
| `citinel-wordmark-white.png` | Falcon + CITINEL lettering, solid white | Dark / transparent | Dark UI header, dark slides, README dark mode |
| `citinel-falcon-navy.png` | Falcon symbol only, solid navy | Transparent | Small light-surface marks, watermarks |
| `citinel-falcon-white.png` | Falcon symbol only, solid white | Transparent | Small dark-surface marks |
| `citinel-appicon-dark.png` | Solid white falcon, optically centered (v2 centering fix, 3 Aug 2026) in a deep-charcoal rounded square | Baked dark square | Primary app icon, favicon source, chat DPs |
| `citinel-appicon-light.png` | Solid navy falcon in a white rounded square; layout pixel-identical to the dark icon (v2) | Baked white square | Light-context listings and icon slots that require a light tile |
| `aerofyta-badge-full.png` | Team badge: winged swirl emblem + AEROFYTA + INNOVATE \| SOLVE \| ELEVATE + TEAM AEROFYTA | Opaque white inside the circle | Team slide, team surfaces |
| `aerofyta-emblem-color.png` | AeroFyta swirl bird emblem only, original blue metallic finish | Transparent | Team accents where the full badge is too heavy |
| `aerofyta-emblem-navy.png` | Swirl emblem only, flat solid navy | Transparent | Small team marks on light surfaces |
| `aerofyta-emblem-white.png` | Swirl emblem only, solid white | Transparent | Small team marks on dark surfaces (legacy swirl style) |
| `aerofyta-faceted-wordmark.png` | Stacked lockup: faceted AeroFyta bird above AEROFYTA in plain geometric caps. Navy on white, 1254x1205, opaque | Baked white | Team slide, vertical/square team placements |
| `aerofyta-lockup-brandfont.png` | Horizontal lockup: faceted bird + AEROFYTA in the angular brand font (wedge-A). Navy on white, 2320x740, opaque | Baked white | Team headers, wide footers, document letterheads |

Naming convention: `-light` / `-dark` means "use on this background", not the color of the artwork.

The AeroFyta swirl emblem and the CITINEL crystal falcon are intentionally different marks (team vs product). Do not unify them.

**AeroFyta has two emblem generations.** The original *swirl* bird (in `aerofyta-badge-full.png` and the three `aerofyta-emblem-*` carve-outs) and the newer *faceted* bird (in `aerofyta-faceted-wordmark.png` and `aerofyta-lockup-brandfont.png`). The faceted style is the current standard for new AeroFyta placements because it rhymes with CITINEL's crystal falcon. The swirl survives only inside the established `aerofyta-badge-full.png`; the three swirl carve-outs are LEGACY and should not be used in new work. Never mix the two styles on one surface.

---

## Color tokens

| Token | Hex | Use |
|---|---|---|
| Brand navy (ink) | `#0B1F3A` | Flat logos, headings, tagline on light |
| Surface charcoal | `#0E1116` | Dark UI background, app icon square |
| Pure white | `#FFFFFF` | Flat logos and text on dark |
| Evidence gold (accent) | `#E7B10A` | UI only: citation highlights and the regulatory clock. Never inside any logo. Never as a status chip |
| Alert red | reserved | Product severity states only. Never brand, never decoration |
| Template cyan (external) | ~`#42BFEE` | OSCode deck template accent. Harmonize with it; do not adopt it as a brand color |

Rules: logos are single-color (navy or white) except the two badges, which keep their generated metallic-blue falcon. Maximum one accent per surface. No gradients, glows, or shadows on flat assets.

---

## Typography

The CITINEL letterforms in the wordmarks are baked raster art with no font file. Never retype the product name to imitate the logo; place the PNG.

For supporting text near the logos (taglines typed in Canva or UI labels), closest matches: **Michroma** or **Orbitron**, all caps, wide letterspacing (~300 in Canva), navy on light or white on dark.

---

## Tagline system (three tiers, all locked)

1. **Official tagline** (deck title slide, pitch, judge-facing): `The SOC that shows its evidence, obeys your policy, and beats the clock.`
2. **Brand hook** (splash, README hero, spoken opener): `CAUGHT. CITED. GATED. ACTIONED. CLOSED.` Exactly five words, five periods — updated 24 Aug 2026 from the original three-word form. It is also the product's incident state machine, now stated in full: Caught -> Cited -> Gated -> Actioned -> Closed in the glass-box UI. **Not yet true for the badge-tagline files** (`citinel-badge-tagline-light.png`, `citinel-badge-tagline-dark.png`, described below) — those PNGs still have the three-word form baked in, and regenerating them needs an explicit decision since this repo's own rule is to never regenerate locked assets casually.
3. **Category line** (baked into the badge): `AUTONOMOUS CYBER SOC`. This restates the PS and stays on the badge. It is never replaced by the hook.

Name-story line, usable in prose: "the sentinel that cites its evidence."

---

## Surface map

| Surface | Asset |
|---|---|
| Deck title slide (light template) | `citinel-badge-tagline-light.png`, or `citinel-badge-full.png` + tagline typed in Canva (Michroma, navy) |
| Slide footers | `citinel-wordmark-navy.png` or `citinel-falcon-navy.png`, small |
| Team-details slide | `aerofyta-badge-full.png` |
| Team headers / wide footers | `aerofyta-lockup-brandfont.png` (horizontal) |
| Team accents, square placements | `aerofyta-faceted-wordmark.png` (stacked). Swirl carve-outs `aerofyta-emblem-*` are legacy fallbacks only |
| Thank-you slide | AeroFyta badge + navy wordmark placed side by side in Canva (composite not committed) |
| App splash / login | `citinel-badge-tagline-dark.png` or `citinel-wordmark-white.png` |
| Dark dashboard header | `citinel-wordmark-white.png` |
| Favicon / app icon | derive from `citinel-appicon-dark.png` (primary); `citinel-appicon-light.png` only where a light tile is required |
| GitHub README hero | picture element below |

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="citinel-brand/citinel-wordmark-white.png">
  <img src="citinel-brand/citinel-wordmark-navy.png" alt="CITINEL — Autonomous Cyber SOC" width="420">
</picture>
```

---

## Hard rules (especially for AI tools)

1. Never regenerate, redraw, restyle, recolor, AI-upscale, or "improve" any asset in this folder. These files are frozen. Edits happen only by explicit human decision, using deterministic tools (background remover, color invert), never generative redraw.
2. One falcon. The faceted crystal falcon in these files is the only CITINEL symbol. The early blade-wing falcon lockup is deprecated and deleted; do not recreate it from memory or old screenshots.
3. Never reintroduce "SIH 2026" text into the CITINEL badge.
4. Never swap the badge's AUTONOMOUS CYBER SOC line for the tagline.
5. Never place navy assets on dark surfaces or white assets on light surfaces.
6. Never spell the names any way other than CITINEL and AEROFYTA. Quote the tagline strings exactly as written above, punctuation included.
7. Do not reference files that are not in the inventory table. Composites (side-by-side lockup, footer strip, demo QR) are assembled in Canva and are not committed yet; if asked about them, say they are planned, not present.
8. Gold accent lives in UI text highlights and the regulatory clock only. Red is reserved for severity. Neither ever appears in a logo.
9. App icons are the v2 optically centered pair (3 Aug 2026). The v1 top-heavy dark icon is deprecated; replace any deployed copies (chat DPs included). The dark and light icons share identical falcon scale and position and must never diverge.

---

## Provenance and known limitations

- All files were AI-generated (Gemini + ChatGPT image tools, Aug 2026) from human-approved masters, then curated. App icons were regenerated on 3 Aug 2026 to fix optical centering (v2). AeroFyta emblem carve-outs (color/navy/white) were extracted the same day, then superseded for new work by the faceted wordmark and horizontal lockup added later that morning. Both faceted files ship with opaque white backgrounds; run a background remover if a transparent version is needed. The horizontal lockup's letterforms are raster and show slight aliasing above roughly 60% of native width, so place it at or below native size. The PNGs are the current source of truth; no vector (SVG/AI) source exists yet.
- Planned before any trademark filing, print production, or merch: manual vector rebuild of the falcon and wordmark with documented construction ratios.
- Badge interiors are intentionally opaque white (sticker look). Canvas transparency outside the circle varies by file; when in doubt, test on a contrasting background.
- Quick health check for any asset: place it on both a white and a `#0E1116` surface. It should read cleanly on its intended side and be at least ~1000 px wide for slide-scale use.
