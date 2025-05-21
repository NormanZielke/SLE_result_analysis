import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
plt.style.use('bmh')


def barplot_c(df, unit="MW", title="Kapazitäten", filename=None):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(df["name"], df["var_value"])
    ax.set_ylabel(unit)
    ax.set_xlabel("Technologie / Komponente")
    ax.set_title(title)

    bars = ax.bar(df["name"], df["var_value"])

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # Abstand zum Balken
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if filename:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)
        plt.savefig(filename, dpi=300)

    plt.show()


def barplot_e(df, unit="MWh", title="Kapazitäten", filename=None):
    total = df["var_value"].sum()

    fig, ax = plt.subplots(figsize=(12, 9))
    bars = ax.bar(df["name"], df["var_value"])

    ax.set_ylabel(unit)
    ax.set_xlabel("Technologie / Komponente")
    ax.set_title(title)

    for bar, value in zip(bars, df["var_value"]):
        height = bar.get_height()
        percent = (value / total) * 100 if total > 0 else 0
        ax.annotate(f"{height:.2f} {unit}\n({percent:.1f}%)",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # Abstand zum Balken
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if filename:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)
        plt.savefig(filename, dpi=300)

    plt.show()

