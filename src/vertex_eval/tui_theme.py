"""Vertex-Eval brand — Vertex orange + grid graphite, grid-vertex logo."""
from __future__ import annotations

from harness_tui.theme import Theme
from harness_tui.themes import catppuccin_mocha

VERTEX_LOGO = r"""
   [bold #1F2937]·──·──·[/]
   [bold #1F2937]│[/] [bold #EA580C]X[/] [bold #1F2937]│[/] [bold #EA580C]X[/] [bold #1F2937]│[/]
   [bold #1F2937]·──·──·[/]   [dim]Vertex-Eval[/]
   [bold #1F2937]│[/] [bold #EA580C]X[/] [bold #1F2937]│[/] [bold #EA580C]X[/] [bold #1F2937]│[/]
   [bold #1F2937]·──·──·[/]
""".strip("\n")


def vertex_theme() -> Theme:
    return catppuccin_mocha().with_brand(
        name="vertex-eval",
        primary="#EA580C",
        primary_alt="#9A3412",
        accent="#FB923C",
        ascii_logo=VERTEX_LOGO,
        spinner_frames=("·", "•", "●", "•"),
    )
