#!/usr/bin/env python3
"""Publication-figure helpers for paper-writer.

Enforces one consistent, colorblind-safe, vector-PDF style across the paper so
figures match. Import and adapt to your `toy-design` / `ablation-plan` results;
do not invent numbers — plot only data the user/experiments produced.

Install:  uv sync --extra figures           # adds matplotlib + numpy
Smoke test (writes /tmp/paperfigs/_smoketest.pdf):
          uv run --extra figures python skills/paper-writer/scripts/figs.py
Typical use:
          import sys; sys.path.insert(0, "skills/paper-writer/scripts")
          import figs, matplotlib.pyplot as plt
          figs.apply_style()
          fig, ax = plt.subplots()
          figs.band(ax, x, mean, std, label="ours")
          figs.save(fig, "coverage")          # -> paper/figures/coverage.pdf
"""
from __future__ import annotations

import os

# Wong (2011) colorblind-safe palette.
PALETTE = ["#0072B2", "#D55E00", "#009E73", "#CC79A7",
           "#E69F00", "#56B4E9", "#F0E442", "#000000"]


def apply_style() -> None:
    import matplotlib as mpl

    mpl.rcParams.update({
        "figure.figsize": (3.3, 2.4),   # one column; use (6.8, 2.6) for full width
        "figure.dpi": 150,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "font.family": "serif",
        "font.size": 8,
        "axes.titlesize": 8,
        "axes.labelsize": 8,
        "legend.fontsize": 7,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.prop_cycle": mpl.cycler(color=PALETTE),
        "lines.linewidth": 1.4,
        "text.usetex": False,           # set True only if a TeX install is on PATH
    })


def save(fig, name: str, outdir: str = "paper/figures") -> str:
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name if name.endswith(".pdf") else name + ".pdf")
    fig.savefig(path)
    print("wrote", path)
    return path


def band(ax, x, mean, std, label=None, color=None):
    """Mean line + ±1 std band — e.g. a multi-seed learning/coverage curve."""
    import numpy as np

    x, mean, std = map(np.asarray, (x, mean, std))
    line, = ax.plot(x, mean, label=label, color=color)
    ax.fill_between(x, mean - std, mean + std, alpha=0.2, color=line.get_color())
    return line


def ablation_bar(ax, labels, values, errs=None):
    """Horizontal bars for one ablation metric (rows = variants)."""
    import numpy as np

    y = np.arange(len(labels))
    ax.barh(y, values, xerr=errs, color=PALETTE[0], capsize=2)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np

    apply_style()
    x = np.linspace(0, 1, 50)
    fig, ax = plt.subplots()
    for i, name in enumerate(["ours", "baseline"]):
        mean = 1 - np.exp(-(i + 2) * x)
        band(ax, x, mean, 0.05 * np.ones_like(x), label=name)
    ax.set_xlabel("fraction of data")
    ax.set_ylabel("coverage")
    ax.legend()
    save(fig, "_smoketest", outdir="/tmp/paperfigs")
