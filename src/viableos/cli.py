"""CLI for ViableOS — init, check, generate, and app commands."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from viableos.budget import calculate_budget
from viableos.checker import ViabilityReport, check_viability
from viableos.generator import generate_openclaw_package
from viableos.schema import load_yaml, validate

console = Console()

STARTER_TEMPLATE = Path(__file__).parent / "templates" / "starter.yaml"


@click.group()
@click.version_option(package_name="viableos")
def main() -> None:
    """ViableOS — The operating system for viable AI agent organizations."""


@main.command()
@click.argument("path", type=click.Path(exists=True))
def check(path: str) -> None:
    """Check a YAML config against VSM principles."""
    config = load_yaml(path)

    errors = validate(config)
    if errors:
        console.print(f"\n[bold red]Schema errors in {path}:[/bold red]")
        for err in errors:
            console.print(f"  • {err}")
        raise SystemExit(1)

    report = check_viability(config)
    system_name = config.get("viable_system", {}).get("name", "Unknown")
    _print_report(path, system_name, report)

    if report.score < report.total:
        raise SystemExit(1)


@main.command()
@click.option(
    "--output",
    "-o",
    default="viableos.yaml",
    help="Output file path",
    type=click.Path(),
)
@click.option("--name", prompt="System name", help="Name for your system")
@click.option("--purpose", prompt="System purpose", help="What is your system for?")
def init(output: str, name: str, purpose: str) -> None:
    """Generate a starter ViableOS config."""
    template = STARTER_TEMPLATE.read_text()
    content = template.replace('"My System"', f'"{name}"')
    content = content.replace('purpose: ""', f'purpose: "{purpose}"')

    out_path = Path(output)
    out_path.write_text(content)
    console.print(
        f"\n[bold green]✓[/bold green] Created [cyan]{out_path}[/cyan]"
    )
    console.print(f"  Edit the file, then run: [bold]viableos check {out_path}[/bold]")


@main.command()
@click.argument("config_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    default="./viableos-openclaw",
    help="Output directory for the OpenClaw package",
    type=click.Path(),
)
def generate(config_path: str, output: str) -> None:
    """Generate an OpenClaw deployment package from a ViableOS config."""
    config = load_yaml(config_path)

    errors = validate(config)
    if errors:
        console.print(f"\n[bold red]Schema errors in {config_path}:[/bold red]")
        for err in errors:
            console.print(f"  • {err}")
        raise SystemExit(1)

    plan = calculate_budget(config)
    out_path = generate_openclaw_package(config, output)

    vs = config.get("viable_system", {})
    system_name = vs.get("name", "Unknown")

    console.print(
        Panel(
            f'System: [bold]"{system_name}"[/bold]\n'
            f"Output: [cyan]{out_path}[/cyan]\n"
            f"Budget: [green]${plan.total_monthly_usd:.0f}/mo[/green] ({plan.strategy})",
            title="[bold]ViableOS Package Generated[/bold]",
        )
    )

    table = Table(title="Agent Allocation")
    table.add_column("Agent", style="bold")
    table.add_column("Model")
    table.add_column("Budget", justify="right")
    table.add_column("Share", justify="right")

    for alloc in plan.allocations:
        table.add_row(
            alloc.friendly_name,
            alloc.model,
            f"${alloc.monthly_usd:.0f}",
            f"{alloc.percentage:.0f}%",
        )
    console.print(table)

    console.print(
        f"\n  [bold green]✓[/bold green] {len(list(out_path.glob('workspaces/*/SOUL.md')))} agents generated"
    )
    console.print(f"  Copy [cyan]{out_path}[/cyan] to your OpenClaw server and run [bold]bash install.sh[/bold]")


@main.command()
@click.option("--port", default=8501, help="Port for the web app")
def app(port: int) -> None:
    """Launch the ViableOS web wizard and dashboard."""
    app_path = Path(__file__).parent / "app" / "main.py"
    if not app_path.exists():
        console.print("[bold red]App files not found.[/bold red]")
        raise SystemExit(1)
    console.print(f"\n[bold]Starting ViableOS...[/bold] → http://localhost:{port}")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.port",
            str(port),
            "--server.headless",
            "true",
            "--browser.gatherUsageStats",
            "false",
        ],
        check=False,
    )


def _print_report(path: str, system_name: str, report: ViabilityReport) -> None:
    """Render the viability report to the terminal."""
    lines: list[str] = []
    lines.append(f"Config: [cyan]{path}[/cyan]")
    lines.append(f'System: [bold]"{system_name}"[/bold]\n')

    for c in report.checks:
        icon = "[green]✅[/green]" if c.present else "[red]❌[/red]"
        label = f"{c.system:<3} {c.name:<14}"
        lines.append(f"  {icon} {label} {c.details}")
        if not c.present:
            for s in c.suggestions:
                lines.append(f"     [dim]→ {s}[/dim]")

    lines.append("")
    if report.score == report.total:
        verdict = "[bold green]Your system is fully viable.[/bold green]"
    else:
        verdict = "[bold yellow]Some systems are missing — see suggestions above.[/bold yellow]"
    lines.append(
        f"Viability Score: [bold]{report.score}/{report.total}[/bold] — {verdict}"
    )

    console.print(
        Panel("\n".join(lines), title="[bold]ViableOS Viability Check[/bold]")
    )
