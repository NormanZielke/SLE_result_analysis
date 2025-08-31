import pandas as pd
import os
import yaml

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


def read_csv_auto_sep(path):
    """
    Read a CSV file with automatic delimiter detection.

    The function inspects the first line of the file to decide whether
    to use a semicolon (``;``) or a comma (`,`) as the separator, and
    then loads the CSV into a pandas DataFrame.

    Parameters
    ----------
    path : str
        Path to the CSV file.

    Returns
    -------
    pandas.DataFrame
        Parsed CSV content.

    Raises
    ------
    ValueError
        If neither a semicolon nor a comma can be detected in the first line.
    """
    # Detect delimiter from the first line only (fast and robust for our inputs)
    with open(path, "r", encoding="utf-8") as f:
        first_line = f.readline()
        if ";" in first_line:
            sep = ";"
        elif "," in first_line:
            sep = ","
        else:
            raise ValueError("Unknown CSV delimiter: neither ';' nor ',' found in the first line.")

    return pd.read_csv(path, sep=sep)


def load_label_mapping(yaml_path="de.yml"):
    """
    Load label mapping from a YAML file.

    The YAML file is expected to map internal component or technology
    identifiers to human-readable (German) labels.

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


class region:
    """
    Container class for a single region's scalar results and plotting helpers.

    This class loads a `scalars.csv` (either for one region or a combined file
    containing multiple regions), strips the region prefix from the component
    names, applies a label mapping, and exposes convenience plotting/analysis
    methods imported from ``calc_results``.

    Parameters
    ----------
    args : dict
        Configuration dictionary. Must contain the key ``"all_capacities"`` (bool),
        which controls whether capacities with value zero are kept in plots.
    csv_folder : str, optional
        Path to the scalars CSV file. Despite the name, this argument is expected
        to be a file path, not a folder.
    region_id : str, optional
        Region identifier (e.g., ``"r120640428428"``). Used to filter and to build
        the output path structure.
    from_combined_file : bool, optional
        If ``True``, the input CSV contains rows for multiple regions. In that
        case, only rows starting with ``"{region_id}-"`` in the ``name`` field
        are kept, and the prefix is removed. If ``False``, the prefix
        ``"{region_id}-"`` is removed unconditionally.

    Attributes
    ----------
    all_caps : bool
        Whether to include technologies with zero capacity in capacity plots.
    region_id : str
        The region identifier passed in the constructor.
    from_combined_file : bool
        Whether the input CSV is a combined file with multiple regions.
    scalars : pandas.DataFrame
        Cleaned scalar results with columns (at least) ``name``, ``var_name``,
        and ``var_value`` after prefix removal and label mapping.
    region_name_map : dict, optional
        Optional mapping ``{region_id: human_readable_name}`` that can be set
        by the caller to control plot titles and labels.

    Notes
    -----
    - This class *does not* perform any unit conversions. Units are expected
      to be consistent with the upstream modeling outputs.
    - Plotting and aggregation logic is delegated to functions imported
      from ``calc_results`` (bound as instance methods below).
    """

    def __init__(self, args, csv_folder=None, region_id=None, from_combined_file=False):
        # Load scalars (auto-detect CSV delimiter)
        df_scalars = read_csv_auto_sep(csv_folder)

        # Store basic configuration
        self.all_caps = args["all_capacities"]
        self.region_id = region_id
        self.from_combined_file = from_combined_file

        # Normalize `name` by removing the region prefix.
        # - If `from_combined_file` is True, filter rows for this region first.
        if from_combined_file:
            df_scalars = df_scalars[df_scalars["name"].str.startswith(f"{region_id}-")].copy()
            df_scalars["name"] = df_scalars["name"].str.replace(f"{region_id}-", "", regex=False)
        else:
            df_scalars["name"] = df_scalars["name"].str.replace(f"{region_id}-", "", regex=False)

        # Apply human-readable label mapping for component/technology names.
        mapping = load_label_mapping("de.yml")
        df_scalars = apply_label_mapping(df_scalars, mapping)

        # Expose cleaned scalars
        self.scalars = df_scalars

    def get_results_path(self, filename):
        """
        Build an output path for storing results of this region.

        The base folder is chosen depending on whether the underlying results
        were loaded from a combined CSV (``01_ALL_REGIONS``) or a single-region
        CSV (``Single_Regions``). The final structure is:

        - ``results/01_ALL_REGIONS/{region_id}/{filename}`` if ``from_combined_file`` is True
        - ``results/Single_Regions/{region_id}/{filename}`` otherwise

        Parameters
        ----------
        filename : str
            Output filename (including file extension).

        Returns
        -------
        str
            Full file system path to the target output file.
        """
        base_folder = "01_ALL_REGIONS" if self.from_combined_file else "Single_Regions"
        return os.path.join("results", base_folder, self.region_id, filename)

    # Bind analysis/plotting utilities from `calc_results` as instance methods
    capacities_opt = capacities_opt
    cap_opt_bar = cap_opt_bar
    dispatch_bar = dispatch_bar
    techs_none = techs_none
    import_pie = import_pie
    generation_heat_high = generation_heat_high
    generation_heat_low_central = generation_heat_low_central
    generation_heat_low_decentral = generation_heat_low_decentral
