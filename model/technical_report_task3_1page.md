# Technical Report - Task 3 Revenue and COGS Forecasting

**Team:** USHIET  
**Public Kaggle score:** **678560.02794**  
**Forecast horizon:** 2023-01-01 to 2024-07-01, 548 daily records  
**Training period:** 2012-07-04 to 2022-12-31, 3,833 daily records  
**Targets:** `Revenue` and `COGS`

## 1. Problem Setting and Objective

The goal of Task 3 is to forecast daily `Revenue` and `COGS` for the hidden test period from 2023-01-01 to 2024-07-01. The available training signal comes from the historical daily sales table, while the final output must follow the exact row order and schema of `sample_submission.csv`. Because the future period does not contain observed operational outcomes, the main modelling constraint is to avoid leakage from variables that would not be known at prediction time, such as future orders, future traffic, future inventory states, future returns, or future reviews.

Our final solution therefore uses a leakage-safe, calendar-driven forecasting pipeline. The model focuses on deterministic time features, recurring seasonal effects, Tet and holiday windows, and promotion-family timing patterns that can be encoded before the forecast period. This design is intentionally conservative: it sacrifices some potentially useful but unavailable future signals in exchange for reproducibility and valid generalization to the Kaggle hidden period.

## 2. End-to-End Pipeline

**[CÓ HÌNH - Figure 1: Pipeline build model]**  
![Figure 1: Pipeline build model](../../figures/model_pipeline.svg)

The pipeline starts from raw `sales.csv` and `sample_submission.csv`, then performs date parsing, schema validation, chronological sorting, and submission-format checks. The feature builder converts each date into 82 deterministic predictors. These include basic calendar variables (`year`, `month`, `day`, `dow`, `doy`, `quarter`), distance-to-boundary variables such as `days_to_eom`, cyclic Fourier encodings for yearly/monthly/weekly seasonality, fixed Vietnamese holiday indicators, Tet distance and window features, and recurring promotion-family windows such as spring sale, mid-year, fall launch, year-end, urban blowout, and rural special.

After feature construction, the notebook evaluates candidate models using walk-forward validation. For each validation fold, models are trained only on historical dates and evaluated on the next contiguous half-year period. After choosing the best blending parameters, the final models are retrained on the full training window and used to predict the 548 submission dates. The last stage enforces submission invariants: row count must match the sample file, date order must be unchanged, columns must be exactly `Date`, `Revenue`, and `COGS`, predictions must be non-null, and predictions must be non-negative.

## 3. Validation Design

The validation strategy uses expanding walk-forward splits rather than random train-test splits. This is important because random splitting would allow the model to learn future seasonal regimes while being evaluated on past dates, which would overestimate real forecasting performance. The implemented folds evaluate six half-year windows:

| Fold | Train End | Validation Window |
| --- | --- | --- |
| WF1 | 2019-12-31 | 2020-01-01 to 2020-06-30 |
| WF2 | 2020-06-30 | 2020-07-01 to 2020-12-31 |
| WF3 | 2020-12-31 | 2021-01-01 to 2021-06-30 |
| WF4 | 2021-06-30 | 2021-07-01 to 2021-12-31 |
| WF5 | 2021-12-31 | 2022-01-01 to 2022-06-30 |
| WF6 | 2022-06-30 | 2022-07-01 to 2022-12-31 |

The latest fold, WF6, is treated as the most relevant offline proxy because it is closest to the hidden test period. On this fold, the final blend obtains average **MAE = 436,996** and average **RMSE = 586,117** across `Revenue` and `COGS`, with average **R2 = 0.738**. The public Kaggle leaderboard score of the final submitted file is **678560.02794**.

## 4. Model Families

The final system is an ensemble of three complementary model families.

**Ridge Regression.** Ridge is used as a stable linear baseline. It is less expressive than boosting, but it helps regularize the ensemble because it captures smooth trend and seasonality without chasing sharp local noise. It also provides a sanity check that engineered calendar features contain meaningful signal even for a simple model.

**Prophet.** Prophet is included as an interpretable time-series baseline with selected regressors. Its role is to capture broad trend and seasonal structure in a robust way. In the final blend, Prophet receives a smaller weight because validation indicates that the nonlinear LightGBM component fits the competition target better.

**LightGBM.** LightGBM is the strongest component and the main model used for interpretation. The notebook trains both a base LightGBM model and quarter-specialist LightGBM models. The quarter specialists receive additional weighting for observations from their target quarter, allowing the ensemble to adapt to seasonal regimes such as Tet-adjacent months, mid-year demand, and year-end campaign periods.

The selected blend uses **LightGBM 85%**, **Ridge 10%**, and **Prophet 5%**. Within the LightGBM component, the quarter-specialist prediction receives `alpha = 0.70`, while the remaining 0.30 comes from the base LightGBM model. This means the final prediction relies mostly on nonlinear seasonal modelling but keeps smaller stabilizing contributions from linear and time-series baselines.

## 5. Feature Importance and Business Interpretation

**[CÓ HÌNH - Figure 2: LightGBM/XGBoost feature importance của model tốt nhất]**  
Use the final LightGBM feature-importance plot here. Since this project uses LightGBM rather than XGBoost as the best tree model, the report should show LightGBM gain importance. If the final slide/report title must mention both, use: "Tree Model Feature Importance (LightGBM)".

The highest-gain features for `Revenue` are dominated by seasonal and trend variables: `cos_y1`, `doy`, `days_to_eom`, `day`, `cos_m1`, `t_days`, `sin_y2`, `sin_m1`, `sin_y3`, and `sin_y1`. The top features for `COGS` are very similar: `cos_y1`, `doy`, `days_to_eom`, `cos_m1`, `day`, `t_days`, `sin_y1`, `sin_m1`, and additional yearly Fourier terms. This alignment is expected because `Revenue` and `COGS` move together at daily aggregation level.

From a business perspective, the model is learning four major demand patterns. First, annual seasonality is strong, shown by yearly Fourier terms and day-of-year features. Second, within-month timing matters: `day` and `days_to_eom` suggest recurring changes around salary, month-end, and campaign-close periods. Third, long-term trend features such as `t_days` help capture the scale change across years. Fourth, holiday and Tet timing features help account for Vietnam-specific demand shifts that standard month and weekday features cannot fully capture.

## 6. xAI Explanation

**[CÓ HÌNH - Figure 3: xAI plot SHAP hoặc LIME]**  
Use the SHAP plot from the final LightGBM model here. SHAP is preferable to LIME for this report because the best model is tree-based and SHAP TreeExplainer gives consistent global and local explanations for LightGBM. Recommended figures are `shap_feature_importance.png` and one SHAP beeswarm plot for `Revenue`; if space is limited, prioritize the `Revenue` SHAP plot and mention that `COGS` has similar drivers.

The SHAP analysis should be described as follows: features with high mean absolute SHAP values are the strongest contributors to daily prediction changes. Positive SHAP values increase the predicted `Revenue` or `COGS`, while negative values reduce it. If the beeswarm plot shows high impact from `doy`, yearly Fourier terms, `days_to_eom`, trend, Tet distance, and recurring promotion windows, it confirms that the model is using interpretable seasonal demand signals rather than memorizing future outcomes.

This explanation is useful for the business story. The model predicts higher or lower sales primarily based on where a day falls in the annual retail cycle, whether it is close to month-end, whether it is near Tet or fixed holidays, and whether it overlaps recurring campaign windows. These are actionable drivers: marketing and inventory teams can plan campaigns, stock allocation, and operational capacity around the same seasonal windows that the model identifies as predictive.

## 7. Final Result and Submission Quality

The final submission file contains 548 predictions for the hidden period and passes the main reproducibility checks: exact sample row order, exact required columns, no missing predictions, and non-negative `Revenue`/`COGS` values. The public Kaggle score is **678560.02794**.

Overall, the system is not just a leaderboard solution but a defensible forecasting workflow. It uses time-aware validation, avoids future operational leakage, combines multiple model families, and provides tree-model explainability through feature importance and SHAP. For the final NeurIPS-format report page, include three visuals: **Figure 1 pipeline diagram**, **Figure 2 LightGBM gain feature importance**, and **Figure 3 SHAP explanation plot**. These figures directly address the requested xAI and model-building evidence while keeping the technical report compact.

## 8. Notes for NeurIPS LaTeX Conversion

Suggested one-page structure in the final LaTeX report:

- **Paragraph 1:** problem setting, date range, targets, Kaggle score.
- **Figure 1:** compact pipeline diagram.
- **Paragraph 2:** leakage-safe feature engineering and validation.
- **Paragraph 3:** model families and selected ensemble weights.
- **Figure 2:** LightGBM gain feature importance.
- **Figure 3:** SHAP or LIME xAI plot.
- **Paragraph 4:** final result, business interpretation, and conclusion.

Keep the text around figures concise. If page space is tight, merge Sections 1-2 into one paragraph and use a small table for validation/final score.
