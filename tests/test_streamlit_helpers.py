import sys
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from streamlit_app.data import available_parse_dates
from streamlit_app.filters import build_select_options, resolve_select_filter, single_select, year_range


class FilterHelpersTest(unittest.TestCase):
    def test_build_select_options_prepends_all(self) -> None:
        self.assertEqual(
            build_select_options(["West", "East"]),
            ["All", "West", "East"],
        )

    def test_resolve_select_filter_all_returns_every_option(self) -> None:
        self.assertEqual(
            resolve_select_filter("All", ["East", "West"]),
            ["East", "West"],
        )

    def test_resolve_select_filter_single_value_returns_singleton_list(self) -> None:
        self.assertEqual(
            resolve_select_filter("East", ["East", "West"]),
            ["East"],
        )

    @patch("streamlit_app.filters.st.selectbox")
    @patch("streamlit_app.filters.st.sidebar.selectbox")
    def test_single_select_uses_main_canvas_selectbox(self, sidebar_selectbox, selectbox) -> None:
        selectbox.return_value = "All"
        self.assertEqual(single_select("Region", ["East", "West"], key="k"), ["East", "West"])
        selectbox.assert_called_once()
        sidebar_selectbox.assert_not_called()

    @patch("streamlit_app.filters.st.selectbox")
    @patch("streamlit_app.filters.st.sidebar.selectbox")
    def test_year_range_uses_main_canvas_selectbox(self, sidebar_selectbox, selectbox) -> None:
        selectbox.side_effect = [2012, 2022]
        self.assertEqual(year_range(2012, 2022, key_prefix="yr"), (2012, 2022))
        self.assertEqual(selectbox.call_count, 2)
        sidebar_selectbox.assert_not_called()


class DataHelpersTest(unittest.TestCase):
    def test_available_parse_dates_skips_missing_date_columns(self) -> None:
        self.assertEqual(
            available_parse_dates(
                "fact_returns_enriched",
                ("category", "return_reason", "return_year"),
            ),
            None,
        )

    def test_available_parse_dates_keeps_selected_date_columns(self) -> None:
        self.assertEqual(
            available_parse_dates(
                "fact_returns_enriched",
                ("category", "return_date", "return_year"),
            ),
            ["return_date"],
        )


if __name__ == "__main__":
    unittest.main()
