import pandas as pd

from collections import defaultdict
from pathlib import Path

_EXCLUDE = ["sample_submission"]


def _is_excluded(filename: str, include_files: list[str] | None = None) -> bool:
    # some utility check
    not_included = include_files is not None and filename not in include_files
    excluded = filename in _EXCLUDE
    return not_included or excluded

def load_csv(
    data_dir: str,
    load_only: list[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """
    Bulk load competition data from `data_dir` directory.

    :param str data_dir: The data directory containing the competition tables.
    :param list[str] or None load_only: A list of table names to load. When
        given, this will only load the specified tables, to save memory. If `None`,
        all tables will be loaded.

    :return: A dictionary with `(table_name, df)` as key-value pairs.
    :rtype: dict[str, pd.DataFrame]
    """
    return {
        csv.stem: pd.read_csv(csv)
        for csv in Path(data_dir).glob("*.csv")
        if not _is_excluded(csv.stem, load_only)
    }
