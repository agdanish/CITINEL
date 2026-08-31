# Labeled ground truth — the missing precondition for an FP rate

This directory is **empty on purpose**, and the eval harness reports the
false-positive rate as `UNMEASURED` because of it. That is not a gap someone
forgot to close; it is the honest state, and it is what stands between
CITINEL's `<10%` **target** and a `<10%` **measurement**.

## Why an FP rate cannot be computed without this

A false positive is a detection that fired on activity which was not
malicious. Nothing in the pipeline's own output can establish that — the
detection says what matched, not whether matching was correct. Deciding that
requires a human reading the raw evidence and ruling. Absent these labels,
any published rate would be invented, which the project's own rule forbids
("no fabricated metrics"; the FP figure is a target, never an achieved
result).

## Schema

One JSONL file, one row per labeled detection:

```json
{"detection_id": "<rule_id>|<timestamp>|<host>", "verdict": "tp", "labeled_by": "a.deshmukh", "note": "genuine Cerber shadow-copy deletion"}
{"detection_id": "<rule_id>|<timestamp>|<host>", "verdict": "fp", "labeled_by": "a.deshmukh", "note": "routine domain named-pipe traffic, not lateral movement"}
```

- `detection_id` — matches the harness's own fingerprint key, so labels join
  to detections without a separate index.
- `verdict` — `tp` or `fp` only. An unsure detection should be left unlabeled
  rather than guessed; a coerced label is worse than a smaller sample.
- `labeled_by` — who ruled. Provenance applies to labels too.

## Where to start, if this gets done

The harness already surfaces the highest-leverage target: **"First Time Seen
Remote Named Pipe" produced 2,366 of 2,701 detections (87.6%), every one
flagged `high`.** One rule generating seven-eighths of all alerts, at high
severity, across two hosts, is the textbook alert-fatigue pattern — and it is
almost certainly where most of the false positives live.

Labeling a sample of that one rule would move the FP rate from UNMEASURED to
a real figure faster than labeling anything else, and it is also the most
honest demonstration of the product's own thesis: deterministic rules close
what they can, and the noise they generate is exactly what the escalation
layer exists to triage.

Note that a sample needs its denominator published too — "42 of 2,366
reviewed" is a measurement; "the FP rate is 8%" from the same 42 is not.
