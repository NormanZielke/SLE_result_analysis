import pandas as pd
import yaml


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


