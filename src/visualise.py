# src/visualise.py
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import matplotlib.pyplot as plt


def plot_trend(
    years: list[int],
    values: list[float],
    title: str,
    ylabel: str = "Value",
    save_path: Optional[str | Path] = None,
) -> None:
    plt.figure()
    plt.plot(years, values, marker="o")
    plt.xlabel("Year")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150)

    plt.show()


def plot_bar_comparison(
    labels: list[str],
    values: list[float],
    title: str,
    ylabel: str = "Value",
    save_path: Optional[str | Path] = None,
    max_labels: int = 25,
) -> None:
    """
    Bar chart for comparisons. If there are too many labels, keep the first max_labels.
    """
    labels2 = labels[:max_labels]
    values2 = values[:max_labels]

    plt.figure()
    plt.bar(labels2, values2)
    plt.xticks(rotation=90)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()

    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150)

    plt.show()
