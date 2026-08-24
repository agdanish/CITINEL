"""CITINEL command line.

Deliberately small at Step 1: one command that runs, reports honestly what
exists and what does not, and never prints a credential value.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from citinel.config import REPO_ROOT, settings

app = typer.Typer(
    name="citinel",
    help="CITINEL - Autonomous Cyber SOC. Caught. Cited. Gated. Actioned. Closed.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()

# The build ladder. Each entry is (step, label, marker path relative to repo
# root). A step counts as built only when its marker actually exists on disk,
# so this table can never drift ahead of the code the way a checklist would.
LADDER: list[tuple[str, str, str]] = [
    ("0",  "Git / version control",        ".git"),
    ("1",  "Skeleton + config",            "backend/citinel/config.py"),
    ("2",  "Telemetry replay",             "backend/citinel/ingest/replay.py"),
    ("3",  "OCSF normalizer",              "backend/citinel/ocsf/normalize.py"),
    ("4",  "Sigma engine",                 "backend/citinel/detect/sigma_engine.py"),
    ("5",  "Anomaly scorer",               "backend/citinel/detect/anomaly.py"),
    ("6",  "Incident record + audit log",  "backend/citinel/audit/ledger.py"),
    ("7",  "Agent swarm",                  "backend/citinel/agents/sentinel.py"),
    ("8",  "OPA gate + autonomy dial",     "backend/citinel/policy/gate.py"),
    ("9",  "Injection hardening",          "backend/citinel/agents/quarantine.py"),
    ("10", "Compliance drafter",           "backend/citinel/compliance/certin.py"),
    ("11", "Glass-box dashboard",          "dashboard/app.py"),
    ("12", "Sponsor integrations",         "backend/citinel/connectors/render.py"),
    ("13", "Eval harness",                 "evals/harness/run.py"),
    ("14", "Demo fallback capture",        "scripts/record_demo.py"),
]

CREDENTIALS: list[tuple[str, str | None, str]] = []


def _credential_rows() -> list[tuple[str, bool, str]]:
    return [
        ("Anthropic (swarm)",   bool(settings.anthropic_api_key),   "Step 7"),
        ("Tavily (OSINT)",      bool(settings.tavily_api_key),      "Step 7"),
        ("VirusTotal",          bool(settings.virustotal_api_key),  "Step 7"),
        ("AbuseIPDB",           bool(settings.abuseipdb_api_key),   "Step 7"),
    ]


@app.command()
def status() -> None:
    """Report what is built, what is configured, and what the safety rails are."""

    console.print(
        Panel.fit(
            "[bold]CITINEL[/bold] - Autonomous Cyber SOC\n"
            "[dim]Caught. Cited. Gated. Actioned. Closed.[/dim]",
            border_style="cyan",
        )
    )

    # --- safety rails, shown first because they are the product's premise ---
    rails = Table(title="Safety rails", title_justify="left", show_header=False, box=None)
    rails.add_column(style="dim")
    rails.add_column()
    endpoint_state = (
        "[green]simulated only[/green]"
        if settings.simulated_endpoints_only
        else "[bold red]LIVE ENDPOINTS - this must never be on for a demo[/bold red]"
    )
    rails.add_row("Response endpoints", endpoint_state)
    rails.add_row("Default autonomy", f"[yellow]{settings.default_autonomy.value}[/yellow]")
    rails.add_row("Filing behaviour", "[green]drafts only, never files[/green]")
    console.print(rails)
    console.print()

    # --- build ladder -------------------------------------------------------
    built = 0
    ladder = Table(title="Build ladder", title_justify="left")
    ladder.add_column("Step", justify="right", style="dim", width=4)
    ladder.add_column("Component")
    ladder.add_column("State", width=12)
    for step, label, marker in LADDER:
        exists = (REPO_ROOT / marker).exists()
        built += exists
        ladder.add_row(
            step,
            label,
            "[green]built[/green]" if exists else "[dim]pending[/dim]",
        )
    console.print(ladder)
    console.print(f"[dim]{built} of {len(LADDER)} steps built.[/dim]\n")

    # --- credentials: presence only, never a value --------------------------
    creds = Table(title="Credentials (presence only)", title_justify="left")
    creds.add_column("Service")
    creds.add_column("State", width=16)
    creds.add_column("Needed from", style="dim")
    for name, present, needed in _credential_rows():
        creds.add_row(
            name,
            "[green]configured[/green]" if present else "[dim]not set[/dim]",
            needed,
        )
    console.print(creds)
    console.print(
        "[dim]Stage 1 (steps 1-5) is fully offline and needs none of these.[/dim]"
    )


@app.command()
def rails() -> None:
    """Print the non-negotiable claim rules this build must obey."""
    rules = [
        "We draft, we never file. A human always signs and submits.",
        "Mitigates, never solves. No claim eliminates risk.",
        "No fabricated metrics. Every number traces to a finding ID or a "
        "verified source. The <10% false-positive figure is a TARGET.",
        "Response actions run against simulated endpoints only.",
        "CERT-In empanelment is a services authorization for audit firms. "
        "CITINEL never claims it as a product credential.",
        "No timelines. Danish owns all timelines.",
    ]
    console.print(Panel("\n".join(f"- {r}" for r in rules), title="Claim discipline", border_style="yellow"))


telemetry = typer.Typer(help="Demo telemetry: extract and verify BOTS v1 replay data.")
app.add_typer(telemetry, name="telemetry")


@telemetry.command("verify")
def telemetry_verify(
    dataset: Path = typer.Option(
        REPO_ROOT / "data/raw/botsv1_data_set",
        help="Root of the extracted BOTS v1 dataset.",
    ),
) -> None:
    """Score event extraction against Splunk's own recorded event counts.

    Ground truth comes from each bucket's SourceTypes.data, written by Splunk
    at index time. Any recovery figure CITINEL quotes has to come from here.
    """
    from citinel.ingest.verify import verify as run_verify

    if not dataset.exists():
        console.print(f"[red]Dataset not found:[/red] {dataset}")
        raise typer.Exit(1)

    results = run_verify(dataset)
    total_got = total_want = 0

    for r in results:
        total_got += r.extracted
        total_want += r.declared
        table = Table(title=f"{r.name}", title_justify="left")
        table.add_column("Sourcetype", max_width=46)
        table.add_column("Extracted", justify="right")
        table.add_column("Declared", justify="right")
        table.add_column("Recovery", justify="right", width=9)
        for st, got, want in r.per_sourcetype:
            pct = (got / want * 100) if want else 0.0
            colour = "green" if pct >= 99 else ("yellow" if pct >= 80 else "red")
            table.add_row(st, f"{got:,}", f"{want:,}", f"[{colour}]{pct:.1f}%[/{colour}]")
        console.print(table)
        # The stream:* subtypes are CITINEL-derived labels, not Splunk's own.
        # Reporting them individually understates recovery, because an event
        # filed under a sibling subtype reads as "missing" when it was in fact
        # extracted. The family aggregate is the honest figure.
        fam_got = sum(g for st, g, _ in r.per_sourcetype if st.startswith("stream:"))
        fam_want = sum(w for st, _, w in r.per_sourcetype if st.startswith("stream:"))
        if fam_want:
            fam_pct = fam_got / fam_want * 100
            console.print(
                f"[dim]  stream:* family aggregate: {fam_got:,} / {fam_want:,} = "
                f"{fam_pct:.1f}%  (per-subtype rows above are CITINEL-derived "
                f"labels, not Splunk's; a subtype reading low means mislabelled, "
                f"not missing)[/dim]"
            )
        console.print(
            f"[dim]bucket total: {r.extracted:,} / {r.declared:,} = "
            f"{r.recovery:.1f}%[/dim]\n"
        )

    overall = (total_got / total_want * 100) if total_want else 0.0
    console.print(
        Panel.fit(
            f"[bold]{total_got:,}[/bold] of [bold]{total_want:,}[/bold] declared events "
            f"recovered = [bold]{overall:.1f}%[/bold]\n"
            "[dim]Ground truth: Splunk SourceTypes.data, written at index time.[/dim]",
            title="Telemetry extraction",
            border_style="cyan",
        )
    )


@telemetry.command("build")
def telemetry_build(
    dataset: Path = typer.Option(
        REPO_ROOT / "data/raw/botsv1_data_set", help="Root of the BOTS v1 dataset."
    ),
    cache: Path = typer.Option(
        REPO_ROOT / "data/cache/botsv1.jsonl", help="Where to write the replay cache."
    ),
) -> None:
    """Extract, timestamp and chronologically order the replay cache."""
    from citinel.ingest.replay import build_cache

    if not dataset.exists():
        console.print(f"[red]Dataset not found:[/red] {dataset}")
        raise typer.Exit(1)
    with console.status("extracting and ordering telemetry..."):
        stats = build_cache(dataset, cache)
    console.print(f"[green]cache written[/green] {cache}")
    console.print(f"  {stats.summary()}")


@telemetry.command("peek")
def telemetry_peek(
    count: int = typer.Option(5, help="How many events to show."),
    event_class: str = typer.Option("", help="Filter to one derived class."),
    cache: Path = typer.Option(REPO_ROOT / "data/cache/botsv1.jsonl"),
) -> None:
    """Show the head of the replay stream, in chronological order."""
    from citinel.ingest.replay import stream_cache

    if not cache.exists():
        console.print("[red]No cache.[/red] Run `citinel telemetry build` first.")
        raise typer.Exit(1)
    shown = 0
    for ev in stream_cache(cache):
        if event_class and ev["event_class"] != event_class:
            continue
        body = ev["body"].replace("\n", " | ")[:110]
        console.print(
            f"[dim]{ev['timestamp']}[/dim] [cyan]{ev['event_class']:<20}[/cyan] {body}"
        )
        shown += 1
        if shown >= count:
            break


ocsf_app = typer.Typer(help="OCSF normalization: map telemetry onto one schema.")
app.add_typer(ocsf_app, name="ocsf")


@ocsf_app.command("verify")
def ocsf_verify(
    cache: Path = typer.Option(REPO_ROOT / "data/cache/botsv1.jsonl"),
    out: Path = typer.Option(
        REPO_ROOT / "data/cache/ocsf.jsonl", help="Where to write normalized records."
    ),
    write: bool = typer.Option(True, help="Write the normalized cache as well."),
) -> None:
    """Normalize the replay cache to OCSF and validate every record.

    Validation is against a pinned snapshot of OCSF's own published schema,
    so 'valid' means checkable rather than asserted.
    """
    import json as _json
    from collections import Counter

    from citinel.ingest.replay import stream_cache
    from citinel.ocsf import schema as S
    from citinel.ocsf.normalize import normalize
    from citinel.ocsf.validate import validate_record

    if not cache.exists():
        console.print("[red]No replay cache.[/red] Run `citinel telemetry build` first.")
        raise typer.Exit(1)

    total = mapped = valid = 0
    unmapped: Counter = Counter()
    failures: Counter = Counter()
    by_class: Counter = Counter()
    examples: dict[str, str] = {}
    fh = out.open("w", encoding="utf-8") if write else None

    with console.status("normalizing to OCSF..."):
        for ev in stream_cache(cache):
            total += 1
            rec = normalize(ev)
            if rec is None:
                unmapped[ev["event_class"]] += 1
                continue
            mapped += 1
            by_class[S.class_name(rec["class_uid"]) or str(rec["class_uid"])] += 1
            problems = validate_record(rec)
            if problems:
                for pr in problems:
                    key = pr.split(":")[0]
                    failures[key] += 1
                    examples.setdefault(key, pr)
            else:
                valid += 1
            if fh is not None:
                fh.write(_json.dumps(rec, ensure_ascii=False) + "\n")
    if fh is not None:
        fh.close()

    table = Table(title="OCSF classes produced", title_justify="left")
    table.add_column("Class")
    table.add_column("uid", justify="right")
    table.add_column("Records", justify="right")
    for name, n in by_class.most_common():
        uid = next(
            (c["uid"] for cn, c in S.classes().items() if cn == name), ""
        )
        table.add_row(name, str(uid), f"{n:,}")
    console.print(table)

    if unmapped:
        console.print("[yellow]unmapped source classes:[/yellow] " +
                      ", ".join(f"{k} ({v:,})" for k, v in unmapped.most_common(6)))
    if failures:
        console.print("[red]contract violations:[/red]")
        for k, n in failures.most_common(8):
            console.print(f"  {n:,}  {examples[k]}")

    pct_map = mapped / total * 100 if total else 0
    pct_val = valid / mapped * 100 if mapped else 0
    console.print(
        Panel.fit(
            f"normalized [bold]{mapped:,}[/bold] of [bold]{total:,}[/bold] events "
            f"([bold]{pct_map:.2f}%[/bold])\n"
            f"OCSF-valid  [bold]{valid:,}[/bold] of [bold]{mapped:,}[/bold] records "
            f"([bold]{pct_val:.2f}%[/bold])\n"
            f"[dim]schema: OCSF {S.OCSF_VERSION}, pinned snapshot of schema.ocsf.io[/dim]",
            title="OCSF normalization",
            border_style="cyan",
        )
    )


detect_app = typer.Typer(help="Deterministic detection: Sigma rules before any model.")
app.add_typer(detect_app, name="detect")


@detect_app.command("run")
def detect_run(
    rules: Path = typer.Option(REPO_ROOT / "data/raw/sigma/rules"),
    cache: Path = typer.Option(REPO_ROOT / "data/cache/botsv1.jsonl"),
    out: Path = typer.Option(REPO_ROOT / "data/cache/detections.jsonl"),
    limit: int = typer.Option(0, help="0 = full corpus."),
) -> None:
    """Run the pinned Sigma corpus over the replay stream and persist hits."""
    from citinel.detect.run import run_detection

    for path, hint in ((rules, "download the pinned SigmaHQ release"),
                       (cache, "run `citinel telemetry build`")):
        if not path.exists():
            console.print(f"[red]missing:[/red] {path}  ({hint})")
            raise typer.Exit(1)

    with console.status("matching (full corpus takes ~8 minutes)..."):
        report = run_detection(rules, cache, out, limit=limit or None)

    table = Table(title="Rules fired", title_justify="left")
    table.add_column("Rule", max_width=58)
    table.add_column("Level", width=9)
    table.add_column("Hits", justify="right")
    level_of = {}
    # by_rule holds counts; recover levels from the output for display order.
    for title, n in sorted(report.by_rule.items(), key=lambda kv: -kv[1])[:30]:
        table.add_row(title, "", f"{n:,}")
    console.print(table)
    console.print(
        Panel.fit(
            f"{report.summary()}\n"
            f"by level: {dict(sorted(report.by_level.items()))}\n"
            f"[dim]corpus: SigmaHQ pinned release; every hit stores the exact "
            f"raw log line as evidence[/dim]",
            title="Deterministic detection",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    app()
