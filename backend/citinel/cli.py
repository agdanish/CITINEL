"""CITINEL command line.

Deliberately small at Step 1: one command that runs, reports honestly what
exists and what does not, and never prints a credential value.
"""

from __future__ import annotations

import sys
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


if __name__ == "__main__":
    app()
