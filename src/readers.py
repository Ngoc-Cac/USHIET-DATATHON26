import json
import pandas as pd

from collections import defaultdict
from pathlib import Path

_CUR_DIR = Path(__file__).parent
_EXCLUDE = ["sample_submission"]
with open(f"{_CUR_DIR}/schemas.json", encoding="utf-8") as file:
    _SCHEMAS = defaultdict(lambda: (None, None), json.load(file))


def _is_excluded(filename: str, include_files: list[str] | None = None) -> bool:
    # some utility check
    not_included = include_files is not None and filename not in include_files
    excluded = filename in _EXCLUDE
    return not_included or excluded

def _read_csv_with_schema(file) -> pd.DataFrame:
    other_dtypes, datetime_cols = _SCHEMAS[file.stem]
    return pd.read_csv(file, dtype=other_dtypes, parse_dates=datetime_cols)

def load_csv(
    data_dir: str,
    load_only: list[str] | None = None,
    enforce_schema: bool = True
) -> dict[str, pd.DataFrame]:
    """
    Bulk load competition data from `data_dir` directory.

    :param str data_dir: The data directory containing the competition tables.
    :param list[str] or None load_only: A list of table names to load. When
        given, this will only load the specified tables, to save memory. If `None`,
        all tables will be loaded.
    :param bool enforce_schema: Whether to enforce the schema specified by the
        competition. This is `True`, by default.

    :return: A dictionary with `(table_name, df)` as key-value pairs.
    :rtype: dict[str, pd.DataFrame]
    """
    return {
        csv.stem: _read_csv_with_schema(csv)
            if enforce_schema else pd.read_csv(csv)
        for csv in Path(data_dir).glob("*.csv")
        if not _is_excluded(csv.stem, load_only)
    }
