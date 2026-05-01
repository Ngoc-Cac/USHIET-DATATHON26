import datetime as dt

import numpy as np
import pandas as pd
import holidays


_TWO_PI = 2 * np.pi


def _lookup_by_year(date: dt.date, *, lookup_dict: dict):
    # look up the next holiday in a year
    next_date = lookup_dict[date.year]
    return next_date if date < next_date else lookup_dict[date.year + 1]


def _days_to_christmas(dates: pd.Series) -> pd.Series:
    lookup = {
        year: pd.Timestamp(f"{year}-12-25")
        for year in range(dates.dt.year.min(), dates.dt.year.max() + 2)
    }
    return (dates.map(_lookup_by_year, lookup_dict=lookup) - dates).dt.days


def _days_to_vn_holiday(dates: pd.Series, holiday_name: str) -> pd.Series:
    lookup = {
        date.year: pd.Timestamp(date)
        for date, name in holidays.country_holidays(
            "VN",
            years=list(range(dates.dt.year.min(), dates.dt.year.max() + 2))
        ).items()
        if name == holiday_name
    }

    return (dates.apply(_lookup_by_year, lookup_dict=lookup) - dates).dt.days


def _days_to_summer(dates: pd.Series):
    lookup = {
        year: pd.Timestamp(f"{year}-05-01")
        for year in range(dates.dt.year.min(), dates.dt.year.max() + 2)
    }
    return (dates.map(_lookup_by_year, lookup_dict=lookup) - dates).dt.days


def get_date_features(
    dates: pd.Series,
    include_circular: bool = False,
    normalise: bool = False,
) -> pd.DataFrame:
    """
    Create features based on given `dates`.

    :param pandas.Series dates: A `pandas.Series` of datetime objects.
    :param bool include_circular: Whether to include circularised features. This
        essentially converts some of the periodic features into their corresponding
        polar coordinates. For example, `day_of_year` will have the corresponding
        sine/cosine components.

    :return: A `pandas.DataFrame` of the constructed features.
    :rtype: `pandas.DataFrame`
    """
    if normalise:
        days_in_year = dates.dt.is_leap_year.map({True: 366, False: 365})
        days_in_month = dates.dt.days_in_month
        days_in_week, total_quarters  = 7, 4
    else:
        days_in_year, days_in_month, days_in_week, total_quarters = 1, 1, 1, 1

    features = {
        "quarter": dates.dt.quarter / total_quarters,
        "doy": dates.dt.day_of_year / days_in_year,
        "dom": dates.dt.day / days_in_month,
        "dow": (dates.dt.weekday + 1) / days_in_week,
        "days_to_christmas": _days_to_christmas(dates),
        "days_to_new": _days_to_vn_holiday(dates, "New Year's Day"),
        "days_to_tet": _days_to_vn_holiday(dates, "Lunar New Year"),
        "days_to_hun": _days_to_vn_holiday(dates, "Hung Kings' Commemoration Day"),
        "days_to_lib": _days_to_vn_holiday(dates, "Liberation Day/Reunification Day"),
        "days_to_lab": _days_to_vn_holiday(dates, "International Labor Day"),
        "days_to_nat": _days_to_vn_holiday(dates, "National Day"),
        "days_to_summer": _days_to_summer(dates)
    }
    if include_circular:
        if not normalise:
            days_in_year = dates.dt.is_leap_year.map({True: 366, False: 365})
            days_in_month = dates.dt.days_in_month
            days_in_week, total_quarters  = 7, 4
        features.update({
            "sin_quarter": np.sin(_TWO_PI * features["quarter"] / total_quarters),
            "cos_quarter": np.cos(_TWO_PI * features["quarter"] / total_quarters),
            "sin_doy": np.sin(_TWO_PI * features["doy"] / days_in_year),
            "cos_doy": np.cos(_TWO_PI * features["doy"] / days_in_year),
            "sin_dom": np.sin(_TWO_PI * features["dom"] / days_in_month),
            "cos_dom": np.cos(_TWO_PI * features["dom"] / days_in_month),
            "sin_dow": np.sin(_TWO_PI * features["dow"] / days_in_week),
            "cos_dow": np.cos(_TWO_PI * features["dow"] / days_in_week)
        })
    return pd.DataFrame(features)


def get_feat_target_indices(
    total_dates: int,
    in_len: int = 365,
    out_len: int = 30,
    stride: int = 5,
):
    starts = np.arange(0, total_dates - in_len - out_len + 1, stride)[:, None]
    return starts + np.arange(in_len), starts + in_len + np.arange(out_len) 
