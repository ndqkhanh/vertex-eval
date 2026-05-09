"""Vertex-Eval TUI — third-party agent evaluation platform."""
from __future__ import annotations

import os
from typing import Optional

import click
from harness_tui import HarnessApp, ProjectConfig
from harness_tui.commands.registry import register_command
from harness_tui.transport import HTTPTransport, MockTransport

from .tui_theme import vertex_theme
from .widgets import TrajectoryGrader


@register_command(name="ingest", description="Ingest a JSONL trajectory file",
                  category="Vertex")
async def cmd_ingest(app, args: str) -> None:  # type: ignore[no-untyped-def]
    path = args.strip() or "(no path)"
    app.shell.chat_log.write_system(f"ingest {path!r}: queued")


@register_command(name="rubric", description="Load a rubric for evaluation",
                  category="Vertex")
async def cmd_rubric(app, args: str) -> None:  # type: ignore[no-untyped-def]
    if args.startswith("load "):
        name = args[5:].strip()
        app.shell.chat_log.write_system(f"rubric {name!r}: loaded")
    else:
        app.shell.chat_log.write_system("usage: /rubric load <name>")


@register_command(name="judge", description="Run judges over current trajectories",
                  category="Vertex")
async def cmd_judge(app, args: str) -> None:  # type: ignore[no-untyped-def]
    app.shell.chat_log.write_system("judge run: dispatched (κ tracking on)")


@register_command(name="attribute", description="Attribute a claim to its source",
                  category="Vertex")
async def cmd_attribute(app, args: str) -> None:  # type: ignore[no-untyped-def]
    claim = args.strip() or "(no claim)"
    app.shell.chat_log.write_system(f"attribution requested for: {claim!r}")


@register_command(name="sla", description="Show SLA report",
                  category="Vertex")
async def cmd_sla(app, _: str) -> None:  # type: ignore[no-untyped-def]
    app.shell.chat_log.write_system("SLA: judge agreement κ=0.86, attribution recall 0.91")


@click.command()
@click.option("--url", default=None)
@click.option("--mock", is_flag=True)
@click.option("--serve", is_flag=True,
              help="Run the TUI in a browser via textual-serve.")
@click.option("--port", type=int, default=8010,
              help="Web mode port (with --serve).")
@click.option("--host", default="127.0.0.1",
              help="Web mode host (with --serve).")
def main(url: Optional[str], mock: bool, serve: bool, port: int, host: str) -> None:
    """Open the Vertex-Eval TUI."""
    if serve:
        from harness_tui.serve import serve_app, make_module_command

        flags = []
        if mock:
            flags.append("--mock")
        if url:
            flags.append(f"--url {url}")
        serve_app(
            command=make_module_command("vertex_eval.tui", " ".join(flags)),
            host=host, port=port,
            title="vertex-eval",
        )
        return
    if mock:
        transport = MockTransport()
    else:
        backend = url or os.environ.get("VERTEX_BACKEND") or "http://localhost:8010"
        transport = HTTPTransport(
            backend,
            endpoints={"run": "/v1/evaluate"},
            payload_builder=lambda t, m: {"trajectory_id": t, "rubric": "default"},
            text_field="report",
        )
    cfg = ProjectConfig(
        name="vertex-eval",
        description="Third-party agent evaluation platform",
        theme=vertex_theme(),
        transport=transport,
        model=os.environ.get("VERTEX_MODEL", "auto"),
        sidebar_tabs=[("Grader", TrajectoryGrader())],
    )
    app = HarnessApp(cfg)
    app.run()
    summary = getattr(app, "last_exit_summary", None)
    if summary:
        click.echo(summary.render())


if __name__ == "__main__":  # pragma: no cover
    main()
