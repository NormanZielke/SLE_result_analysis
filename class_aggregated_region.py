import os
import pandas as pd
import yaml
from class_region import read_csv_auto_sep

from calc_results import (
    capacities_opt,
    cap_opt_bar,
    dispatch_bar,
    techs_none,
    import_pie,
    generation_heat_high,
    generation_heat_low_central,
    generation_heat_low_decentral,
)


def load_label_mapping(yaml_path="de.yml"):
    """
    Load label mapping from a YAML file.

    The YAML file should map internal component/technology identifiers
    to human-readable (German) labels.

    Parameters
    ----------
    yaml_path : str, optional
        Path to the YAML mapping file, by default ``"de.yml"``.

    Returns
    -------
    dict
        Mapping dictionary used to relabel technology/component names.
    """
    with open(yaml_path, "r", encoding="utf-8") as f:
        mapping = yaml.safe_load(f)
    return mapping


def apply_label_mapping(df, mapping, column="name"):
    """
    Apply a label mapping to a DataFrame column.

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame that contains the column to be relabeled.
    mapping : dict
        Dictionary mapping original labels to human-readable labels.
    column : str, optional
        Column name to apply the mapping on, by default ``"name"``.

    Returns
    -------
    pandas.DataFrame
        DataFrame with the relabeled column. Unmapped entries remain unchanged.
    """
    df[column] = df[column].map(mapping).fillna(df[column])
    return df


class aggregated_region:
    """
    Container class to aggregate scalar results across multiple regions/files.

    This class reads one or multiple ``scalars.csv`` files, removes region
    prefixes from component names, groups by ``name`` and ``var_name`` to
    sum values, applies a label mapping, and exposes plotting/analysis
    helpers (bound from ``calc_results``).

    Parameters
    ----------
    args : dict
        Configuration dictionary. Must contain the key ``"all_capacities"`` (bool),
        which controls whether capacities with value zero are kept in plots.
    region_id : str
        Identifier displayed in output (e.g., ``"Gemeindeverbund"`` or ``"Einzelregionen"``).
    csv_paths : str or list of str
        Either a single path to a combined ``scalars.csv`` file or a list of
        paths to separate region ``scalars.csv`` files to be concatenated.
    output_folder : str
        Base output directory where figures and CSVs will be written.

    Attributes
    ----------
    all_caps : bool
        Whether to include technologies with zero capacity in capacity plots.
    region_id : str
        Logical label used in output filenames and plot titles.
    output_folder : str
        Directory where results are saved.
    scalars : pandas.DataFrame
        Aggregated table (after concatenation and grouping) with at least
        ``name``, ``var_name``, ``var_value``. Names are already de-prefixed
        and mapped to human-readable labels.

    Notes
    -----
    - Region prefix removal assumes a pattern ``r\\d{12}-`` at the beginning
      of the ``name`` field.
    - Grouping is done by both ``name`` and ``var_name`` to combine multiple
      regional files consistently.
    """

    def __init__(self, args, region_id, csv_paths, output_folder):
        self.all_caps = args["all_capacities"]
        self.region_id = region_id
        self.output_folder = output_folder

        # Read and concatenate one or many CSV sources
        if isinstance(csv_paths, str):
            df = read_csv_auto_sep(csv_paths)
        elif isinstance(csv_paths, list):
            df_list = [read_csv_auto_sep(p) for p in csv_paths]
            df = pd.concat(df_list, ignore_index=True)
        else:
            raise ValueError("csv_paths must be a str or a list of str.")

        # Remove region prefix (e.g., r123456789012-) from 'name'
        df["name"] = df["name"].str.replace(r"^r\d{12}-", "", regex=True)

        # Group by both name and var_name to sum values across files/regions
        df_grouped = df.groupby(["name", "var_name"], as_index=False)["var_value"].sum()

        # Apply human-readable label mapping for component/technology names
        mapping = load_label_mapping("de.yml")
        df_grouped = apply_label_mapping(df_grouped, mapping)

        # Expose aggregated scalars
        self.scalars = df_grouped

    def get_results_path(self, filename):
        """
        Build an output path within this aggregated region's output folder.

        Parameters
        ----------
        filename : str
            Output filename including file extension.

        Returns
        -------
        str
            Full path pointing to ``{output_folder}/{filename}``.
        """
        return os.path.join(self.output_folder, filename)

    # Add functions
    capacities_opt = capacities_opt
    cap_opt_bar = cap_opt_bar
    dispatch_bar = dispatch_bar
    techs_none = techs_none
    import_pie = import_pie
    generation_heat_high = generation_heat_high
    generation_heat_low_central = generation_heat_low_central
    generation_heat_low_decentral = generation_heat_low_decentral