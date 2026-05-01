# Team USHIET - DATATHON 2026

This is the main repository, hosting the assets and works from group USHIET in
the DATATHON 2026 competition by VinUniversity.

<!-- ### Table of Contents -->
<!-- 1. [Quick Start](#Quick-Start) -->
<!-- 2. How To Navigate?  -->

## Quick Start
Python 3.12+ is recommended.

1. **Pull LFS**
```bash
git lfs pull
```
2. **Unzip data archive**
```bash
mkdir assets/data
unzip assets/datathon-2026-round-1.zip -d assets/data
```
3. **Install Python Envrionment**
```bash
python -m venv .venv & . .venv/Scripts/activate
pip install -r requirements.txt
```

## How To Navigate?
This repository contains four main directories:
1. The [`assets`](./assets/) directory: This is where the primary data is.
  There are other miscellaneous referential materials as well.
2. The [`docs`](./docs/) repository: This is where we host materials for the
  reports, including the source TeX files as well as other demonstrative materials.
3. The [`src`](./src/) and [`notebooks`](./notebooks/) directories: This contains
  all of our experimental notebooks, utility scripts and other code used to
  generate the dasboards and analysis.

    a. The notebooks for figuring out the multiple-choice questions are located
      at [`notebooks/02_mcq_mcq_answers.ipynb`](./notebooks/02_mcq_answers.ipynb)
      and [`notebooks/mcq-analysis.ipynb`](./notebooks/mcq-analysis.ipynb).

    b. The notebook for investigating and fitting the forecasting models is at
      [`notebooks/vindatathon_task3_forecasting.ipynb`](./notebooks/vindatathon_task3_forecasting.ipynb)

## About the dashboards
A preview of the dashboards can be seen in [`DASHBOARD.pdf`](./DASHBOARD.pdf).
These dashboards are generated using Streamlit.

The main script can be run by following these steps:
1. Preprocess the data:
```bash
# remember to activate your corresponding virtual environment
python src/prepare_tableau_data.py
```
2. Run the main script:
```bash
streamlit run src/streamlit_app/app.py
```
