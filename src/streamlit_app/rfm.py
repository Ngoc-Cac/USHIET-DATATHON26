"""RFM segmentation rule.

Re-implements segment label based on R/F/M quintile scores.
Compared to the prep notebook this fixes 2 things:
  - "Cant Lose Them" is checked BEFORE At Risk so it actually fires.
  - "Potential Loyalists" / "About To Sleep" split by M score (≥3 vs <3).

Order of checks is significant.
"""
from __future__ import annotations
import pandas as pd


def label_from_scores(R: int, F: int, M: int) -> str:
    if R >= 4 and F >= 4:
        return "Champions"
    if R >= 3 and F >= 3:
        return "Loyal Customers"
    if R <= 2 and F >= 4 and M >= 4:
        return "Cant Lose Them"
    if R <= 2 and F >= 3:
        return "At Risk"
    if R >= 4 and F <= 2:
        return "New Customers"
    if R == 3 and F <= 2 and M >= 3:
        return "Potential Loyalists"
    if R == 3 and F <= 2 and M < 3:
        return "About To Sleep"
    if R <= 2 and F <= 2:
        return "Lost"
    return "NA"


def apply_segment(df: pd.DataFrame,
                  r_col: str = "R_score",
                  f_col: str = "F_score",
                  m_col: str = "M_score",
                  out_col: str = "rfm_segment",
                  inactive_label: str = "Never Purchased") -> pd.DataFrame:
    """Recompute the RFM segment column on a dataframe in place (returns same df).

    Customers without scores (no orders → score is NaN) get `inactive_label`.
    """
    df = df.copy()
    has_scores = df[[r_col, f_col, m_col]].notna().all(axis=1)

    def _row(row):
        return label_from_scores(int(row[r_col]), int(row[f_col]), int(row[m_col]))

    new_seg = pd.Series(inactive_label, index=df.index, dtype=object)
    new_seg.loc[has_scores] = df.loc[has_scores].apply(_row, axis=1)
    df[out_col] = new_seg
    return df
