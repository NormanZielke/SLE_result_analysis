import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
plt.style.use('bmh')


def barplot_c_old(df, unit="MW", title="Kapazitäten", filename=None):
    fig, ax = plt.subplots(figsize=(12, 8))
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

    #plt.show()
    plt.close()

def barplot_c(df, unit="MW", title="Kapazitäten", filename=None, potential_data=None):
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(df["name"], df["var_value"])

    ax.set_ylabel(unit)
    ax.set_xlabel("Technologie / Komponente")
    ax.set_title(title)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

    # 🔴 Potenziale als Punkte
    potentials_set = False
    if potential_data is not None:
        for i, (name, pot) in enumerate(potential_data.itertuples(index=False)):
            if pd.notna(pot):
                idx = df.index[df["name"] == name]
                if not idx.empty:
                    bar = bars[idx[0]]
                    ax.plot(bar.get_x() + bar.get_width() / 2, pot,
                            marker="o", color="red", label="Potenzial" if i == 0 else "", zorder=5)
                    potentials_set = True

    if potentials_set:
        ax.legend(["Potenzial"], loc="upper right", fontsize="small")

    plt.xticks(rotation=45, ha="right")
    #handles, labels = ax.get_legend_handles_labels()
    #by_label = dict(zip(labels, handles))
    #ax.legend(by_label.values(), by_label.keys())
    plt.tight_layout()

    if filename:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)
        plt.savefig(filename, dpi=300)
    plt.close()



def barplot_e(df, unit="MWh", title="Kapazitäten", filename=None):
    total = df["var_value"].sum()

    fig, ax = plt.subplots(figsize=(12, 10))
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

    #plt.show()
    plt.close()


def plot_pie( labels, values, title=None, unit="GWh", filename=None):
    labels = labels
    values = values
    total = sum(values)


    # Prozentwerte für Beschriftung berechnen
    autopct = lambda pct: f"{pct:.1f}%\n({pct / 100 * total:.1f} {unit})"

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        values, labels=labels, autopct=autopct, startangle=90
    )

    ax.set_title(title)
    ax.axis("equal")  # Kreis statt Oval

    if filename:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)
        plt.savefig(filename, dpi=300)

    #plt.show()
    plt.close()


def plot_pie_2(labels, values, title=None, unit="GWh", filename=None):
    total = sum(values)

    # 🔁 sortiere nach Werten absteigend
    sorted_data = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
    sorted_labels, sorted_values = zip(*sorted_data)

    # Prozentwerte berechnen für die Legende
    percentages = [v / total * 100 for v in sorted_values]
    legend_labels = [f"{label}: {pct:.1f}% ({v:.1f} {unit})" for label, pct, v in zip(sorted_labels, percentages, sorted_values)]

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, _ = ax.pie(sorted_values, startangle=90)

    ax.set_title(title)
    ax.axis("equal")  # Kreis statt Oval

    # Legende nach sortierten Werten
    ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5), fontsize="small")

    if filename:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)
        plt.savefig(filename, dpi=300, bbox_inches="tight")

    #plt.show()
    plt.close()

