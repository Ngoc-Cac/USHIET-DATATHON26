"""Shared sidebar filter widgets used across pages."""
from __future__ import annotations
import streamlit as st

ALL_OPTION = "All"


def build_select_options(options: list[str]) -> list[str]:
    return [ALL_OPTION, *options]


def resolve_select_filter(selection: str, options: list[str]) -> list[str]:
    if selection == ALL_OPTION:
        return options
    return [selection]


def single_select(label: str, options: list[str], key: str) -> list[str]:
    selection = st.sidebar.selectbox(
        label,
        options=build_select_options(options),
        index=0,
        key=key,
    )
    return resolve_select_filter(selection, options)


def year_range(min_y: int = 2012, max_y: int = 2022, key_prefix: str = "f_year") -> tuple[int, int]:
    years = list(range(min_y, max_y + 1))
    start_year = st.sidebar.selectbox(
        "From year",
        options=years,
        index=0,
        key=f"{key_prefix}_from",
    )
    end_candidates = [year for year in years if year >= start_year]
    end_year = st.sidebar.selectbox(
        "To year",
        options=end_candidates,
        index=len(end_candidates) - 1,
        key=f"{key_prefix}_to",
    )
    return start_year, end_year


def region_select(options: list[str], key: str = "f_region") -> list[str]:
    return single_select("Region", options, key=key)


def category_select(options: list[str], key: str = "f_category") -> list[str]:
    return single_select("Category", options, key=key)
