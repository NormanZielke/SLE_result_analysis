import os

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

from helpers import (
    read_csv_auto_sep,
    load_label_mapping,
    apply_label_mapping,
)



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
    """

    def __init__(self, args, csv_folder=None, region_id=None, from_combined_file=False):
        # Load scalars (auto-detect CSV delimiter)
        df_scalars = read_csv_auto_sep(csv_folder)

        # Store basic configuration
        self.all_caps = args["all_capacities"]
        self.region_id = region_id
        self.from_combined_file = from_combined_file
        self.args = args

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
        return os.path.join(self.args["results_dir"], base_folder, self.region_id, filename)


    # Add functions
    capacities_opt = capacities_opt
    cap_opt_bar = cap_opt_bar
    dispatch_bar = dispatch_bar
    techs_none = techs_none
    import_pie = import_pie
    generation_heat_high = generation_heat_high
    generation_heat_low_central = generation_heat_low_central
    generation_heat_low_decentral = generation_heat_low_decentral
