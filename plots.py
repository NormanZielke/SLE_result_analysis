import pandas as pd
import matplotlib.pyplot as plt
import os

# Use a simple built-in style for consistent appearance
plt.style.use("bmh")


def barplot_c(df,
              unit="Optimierte Kapazität in MW",
              title="Kapazitäten",
              filename=None,
              potential_data=None
              ):
    """
    Create a capacity bar plot with optional potential markers.

    Each bar represents a technology/component capacity. If ``potential_data``
    is provided, potential values are drawn as point markers at the
    corresponding x-positions.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with at least columns ``name`` and ``var_value``. Values
        are plotted on the y-axis and names on the x-axis.
    unit : str, optional
        Y-axis unit label, by default ``"MW"``.
    title : str, optional
        Plot title, by default ``"Kapazitäten"``.
    filename : str or None, optional
        If provided, the plot is saved to this path. Parent folders are created
        if necessary. If ``None``, the plot is not saved.
    potential_data : pandas.DataFrame or None, optional
        Optional DataFrame with two columns (in this order) ``name`` and
        ``capacity_potential``. If given, a point marker is placed at the
        potential value for matching ``name``.

    Notes
    -----
    - Names that exist in ``df`` but not in ``potential_data`` simply
      do not receive a marker.
    - Only numeric potential values are plotted (NaNs are ignored).
    """

    fig, ax = plt.subplots(figsize=(12, 10))
    bars = ax.bar(df["name"], df["var_value"])

    ax.set_ylabel(unit)
    ax.set_xlabel("Komponente")
    ax.set_title(title)

    # Annotate bar heights
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.2f}",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    # Draw potential markers, if provided
    potentials_set = False
    if potential_data is not None:
        # Iterate over rows (name, capacity_potential)
        for i, (name, pot) in enumerate(potential_data.itertuples(index=False)):
            if pd.notna(pot):
                # Find the bar index for this name
                idx = df.index[df["name"] == name]
                if not idx.empty:
                    bar = bars[idx[0]]
                    ax.plot(
                        bar.get_x() + bar.get_width() / 2,
                        pot,
                        marker="o",
                        color="red",
                        label="Potenzial" if i == 0 else "",
                        zorder=5,
                    )
                    potentials_set = True

    if potentials_set:
        ax.legend(["Potenzial"], loc="upper right", fontsize="small")

    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.tight_layout()

    if filename:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)
        plt.savefig(filename, dpi=300)

    plt.close()


def barplot_e(df, unit="MWh", title="Kapazitäten", filename=None):
    """
    Create a bar plot for energy values with absolute and relative labels.

    Each bar shows an energy contribution per technology/component.
    The annotation includes both the absolute value and the percentage share
    relative to the total.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame with columns ``name`` and ``var_value``.
    unit : str, optional
        Y-axis unit label, by default ``"MWh"``.
    title : str, optional
        Plot title, by default ``"Kapazitäten"``.
    filename : str or None, optional
        If provided, the plot is saved to this path. Parent folders are created
        if necessary. If ``None``, the plot is not saved.
    """

    total = df["var_value"].sum()

    fig, ax = plt.subplots(figsize=(12, 10))
    bars = ax.bar(df["name"], df["var_value"])

    ax.set_ylabel(unit)
    ax.set_xlabel("Technologie / Komponente")
    ax.set_title(title)

    # Annotate absolute values and percentage shares
    for bar, value in zip(bars, df["var_value"]):
        height = bar.get_height()
        percent = (value / total) * 100 if total > 0 else 0
        ax.annotate(
            f"{height:.2f} {unit}\n({percent:.1f}%)",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if filename:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)
        plt.savefig(filename, dpi=300)

    plt.close()


def plot_pie(labels, values, title=None, unit="GWh", filename=None):
    """
    Create a pie chart with percentage labels including absolute values.

    Parameters
    ----------
    labels : list of str
        Labels for each pie slice.
    values : list of float
        Numeric values for each label; must be non-negative.
    title : str or None, optional
        Plot title, by default ``None``.
    unit : str, optional
        Unit appended to absolute values in labels, by default ``"GWh"``.
    filename : str or None, optional
        If provided, the plot is saved to this path. Parent folders are created
        if necessary. If ``None``, the plot is not saved.
    """

    total = sum(values)

    # Formatter with both percentage and absolute value
    autopct = lambda pct: f"{pct:.1f}%\n({pct / 100 * total:.1f} {unit})"

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct=autopct, startangle=90)

    ax.set_title(title)
    ax.axis("equal")  # Draw a circle instead of an ellipse

    if filename:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)
        plt.savefig(filename, dpi=300)

    plt.close()


def plot_pie_2(labels, values, title=None, unit="GWh", filename=None):
    """
    Create a pie chart with a legend sorted by descending value.

    Instead of labeling slices directly, this variant uses a legend
    showing percentage and absolute values next to the figure.

    Parameters
    ----------
    labels : list of str
        Labels for each category.
    values : list of float
        Values corresponding to ``labels``.
    title : str or None, optional
        Plot title, by default ``None``.
    unit : str, optional
        Unit appended to absolute values in the legend, by default ``"GWh"``.
    filename : str or None, optional
        If provided, the plot is saved to this path. Parent folders are created
        if necessary. If ``None``, the plot is not saved.
    """

    total = sum(values)

    # Sort pairs by value (descending) for a clearer legend
    sorted_data = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
    sorted_labels, sorted_values = zip(*sorted_data)

    # Build legend entries with percentage and absolute
    percentages = [v / total * 100 if total > 0 else 0 for v in sorted_values]
    legend_labels = [
        f"{label}: {pct:.1f}% ({v:.1f} {unit})"
        for label, pct, v in zip(sorted_labels, percentages, sorted_values)
    ]

    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, _ = ax.pie(sorted_values, startangle=90)

    ax.set_title(title)
    ax.axis("equal")

    # Legend to the right of the pie
    ax.legend(wedges, legend_labels, loc="center left", bbox_to_anchor=(1, 0.5), fontsize="small")

    if filename:
        folder = os.path.dirname(filename)
        if folder:
            os.makedirs(folder, exist_ok=True)
        # Use tight bounding box to include the legend
        plt.savefig(filename, dpi=300, bbox_inches="tight")

    plt.close()
