# Datathon 2026 Round 1 Execution Plan

## 1. Objective

Deliver a strong Round 1 submission that:

- Maximizes points across all 3 sections
- Meets every hard requirement and avoids disqualification
- Produces a clear, business-oriented story from the data
- Builds a reproducible forecasting pipeline with explainable outputs

The round has 3 scored parts:

- Part 1: MCQ from the provided data only, `20` points
- Part 2: Visualization and analysis, `60` points
- Part 3: Revenue forecasting, `20` points

The scoring structure makes one thing clear: the highest leverage is Part 2, but Part 3 can decide competitiveness if executed cleanly.

## 2. What The Competition Is Actually Asking For

The dataset simulates a Vietnamese fashion e-commerce business from `2012-07-04` to `2022-12-31`, with a hidden forecast test period from `2023-01-01` to `2024-07-01`.

The work expected from the team is not just "analyze data" or "train a model". It is a combined business case:

- Understand the business through linked tables
- Answer concrete data questions correctly
- Tell a compelling story with evidence
- Recommend actions supported by data
- Forecast revenue in a reproducible, explainable way

## 3. Core Deliverables

The team should produce the following final outputs.

### Required competition outputs

1. MCQ answers for 10 questions
2. `submission.csv` for Kaggle with the exact same row order as `sample_submission.csv`
3. A report in NeurIPS LaTeX format
4. A public or accessible GitHub repository containing code, notebooks, and submission assets
5. Final submission through the official Round 1 form

### Internal team outputs you should create before submission

1. A cleaned data dictionary and table relationship note
2. A single source of truth notebook or pipeline for MCQ calculations
3. A curated EDA storyline with selected charts only
4. A reproducible forecasting pipeline
5. A validation memo documenting assumptions, leakage checks, and final model choices
6. A submission checklist owned by one team member

## 4. Data Scope And Table Roles

The provided files fall into 4 roles:

### Master tables

- `products.csv`: product attributes, category, segment, size, color, price, COGS
- `customers.csv`: demographics, signup timing, acquisition channel
- `promotions.csv`: promotion rules, type, discount value, channels, stackability
- `geography.csv`: zip, city, district, region

### Transaction tables

- `orders.csv`: order-level behavior, status, device, source, payment method
- `order_items.csv`: product-line facts, quantities, discount amount, promotion usage
- `payments.csv`: payment value and installment choice
- `shipments.csv`: shipping timing and shipping fee
- `returns.csv`: reasons, quantities, refund amount
- `reviews.csv`: ratings and text metadata

### Analytical table

- `sales.csv`: daily `Revenue` and `COGS` for training

### Operational tables

- `inventory.csv`: monthly inventory health, stockouts, overstock, fill rate
- `web_traffic.csv`: sessions, visitors, bounce rate, duration, source

## 5. Constraints You Must Not Violate

These are hard rules.

### Forecasting constraints

- Do not use external data
- Do not use hidden test `Revenue` or `COGS` as features
- Include full source code
- Make the pipeline reproducible
- Explain the main revenue drivers in business language

### Submission constraints

- `submission.csv` must preserve the exact order of `sample_submission.csv`
- The GitHub repository must be public or accessible before the deadline
- The report must be at most `4` pages, excluding references and appendix

### Disqualification risks for Part 3

The forecasting section can be fully disqualified if the team:

- Uses test `Revenue` or `COGS` as features
- Uses outside data
- Fails to include code or reproducibility

## 6. How To Win The Scoring Rubric

### Part 1: MCQ, 20 points

This is straightforward execution. Build one notebook or script that computes each answer directly from the raw CSVs so every answer is auditable.

### Part 2: EDA, 60 points

This is the main battlefield. The judges want more than charts. They want progression across 4 levels:

- Descriptive: what happened
- Diagnostic: why it happened
- Predictive: what is likely to happen
- Prescriptive: what should the business do

To score near the top, the analysis must consistently move into prescriptive territory with quantified tradeoffs.

### Part 3: Forecasting, 20 points

This is split into:

- `12` points for leaderboard performance
- `8` points for technical report quality

A decent model with a disciplined pipeline can outperform a stronger raw model if the stronger one leaks information or is poorly explained.

## 7. Recommended Team Strategy

Split work into 4 tracks running in parallel.

### Track A: Data foundation

Owner goals:

- Validate schemas, nulls, keys, date ranges
- Confirm table relationships
- Create reusable join logic
- Document business definitions for revenue, promotions, returns, and fulfillment

Outputs:

- `data_dictionary.md`
- `data_quality_checks.ipynb` or equivalent script

### Track B: MCQ engine

Owner goals:

- Build exact reproducible calculations for all 10 questions
- Store answer logic in code, not manual spreadsheet work
- Record assumptions for ties, null handling, and denominators

Outputs:

- `mcq_answers.ipynb`
- `mcq_results.csv` or a short markdown summary

### Track C: EDA and story

Owner goals:

- Explore across customers, products, promotions, geography, operations, and demand
- Select only the insights that materially affect business decisions
- Convert findings into a report narrative, not a chart dump

Outputs:

- Final shortlist of `6` to `10` high-value charts
- Insight summary with business recommendations

### Track D: Forecasting

Owner goals:

- Build leakage-safe time-based validation
- Engineer features from allowed historical tables
- Benchmark multiple model families
- Produce explainability artifacts

Outputs:

- Training pipeline
- Validation results
- Final `submission.csv`
- Driver explanation section for the report

## 8. Recommended Storyline For The Final Report

Use a business storyline instead of organizing by file.

### Suggested narrative

1. Business overview
2. Demand and revenue trends over time
3. Customer and channel behavior
4. Product, promotion, and return dynamics
5. Inventory and traffic signals that explain performance
6. Business actions the company should take
7. Forecasting approach and expected generalization

This structure aligns better with the judging rubric than presenting one chart per table.

## 9. High-Value EDA Questions To Pursue

Not all questions are equally useful. Prioritize analyses that connect performance to action.

### Revenue and demand

- What are the major seasonality patterns by month, quarter, and year?
- Are there structural breaks or growth slowdowns?
- How much volatility is explained by promotions, traffic, or stockouts?

### Customer behavior

- Which acquisition channels bring higher-value or more repeat customers?
- Which age groups or gender segments show stronger repeat behavior?
- How long is the repeat-purchase cycle for core customer segments?

### Product and pricing

- Which categories and segments drive revenue versus margin?
- Which products show high sales but poor return economics?
- Where do discount-heavy products destroy margin?

### Promotions

- Which promotion types lift demand efficiently?
- Do stackable promotions improve revenue enough to justify margin loss?
- Which channels respond best to promotions?

### Operations

- Where are stockouts suppressing sales?
- Which product groups are overstocked and tie up capital?
- How do fill rate and days of supply connect to future revenue?

### Experience and retention

- Which return reasons are most common by product segment or size?
- Do poor ratings predict higher returns or weaker repeat behavior?
- Which delivery patterns correlate with lower reviews?

## 10. What A Strong Prescriptive Section Looks Like

The best submissions will not stop at "this segment has high returns". They will answer what to do next.

Examples:

- Reduce promotion intensity on low-margin products where discount elasticity is weak
- Reallocate inventory to categories with repeated stockouts and strong sell-through
- Target acquisition spend toward channels with better repeat-order economics
- Fix sizing issues for segments with high `wrong_size` returns
- Improve shipping experience where late delivery is associated with rating decline

Each recommendation should include:

- Evidence from data
- Expected business impact
- Tradeoff or risk
- Suggested owner or action

## 11. Forecasting Plan

The forecasting target is `Revenue`, but the sample format includes `COGS`, so keep the output schema aligned with the required submission format.

### Step 1: Establish a leakage-safe baseline

Start with simple baselines:

- Lag-based naive forecast
- Rolling mean
- Seasonal baseline using day-of-week, month, holiday-like periodic effects visible from internal history

This provides a benchmark for all later models.

### Step 2: Build allowed features from historical data

Candidate feature groups:

- Calendar features: day, week, month, quarter, weekday, month-end markers
- Sales history: lagged revenue, rolling means, rolling volatility, trend slope
- Traffic history: sessions, visitors, bounce rate, duration, source mix
- Promotion history: number of active promotions, promotion type mix, category coverage
- Order behavior: order counts, item counts, AOV proxies, cancellation share
- Fulfillment: shipping fee, shipping delay proxies, return rates
- Inventory: stockout flags, fill rate, sell-through, days of supply

All features must be constructed using only information available up to the prediction timestamp.

### Step 3: Use time-aware validation

Use rolling or expanding-window validation only.

Do not use random split cross-validation.

Recommended evaluation setup:

- Train on early years
- Validate on later contiguous periods
- Repeat over multiple folds
- Track `MAE`, `RMSE`, and `R2`

### Step 4: Benchmark multiple model families

Try a sequence like:

- Linear or ridge regression baseline
- Tree-based gradient boosting
- Time-series regression with external regressors
- Ensemble of best complementary models

Model selection should be based on time-split validation, not intuition.

### Step 5: Add explainability

Prepare one of:

- Feature importance
- SHAP summary
- Partial dependence or equivalent driver analysis

Translate outputs into business language:

- Traffic growth explains revenue lifts
- Stockouts cap upside in certain periods
- Promotion intensity helps volume but compresses profitability

## 12. Recommended Report Structure

The report is capped at 4 pages, so it must be selective.

### Page allocation suggestion

1. Page 1: business context, dataset framing, top descriptive and diagnostic insights
2. Page 2: deeper insight and prescriptive recommendations
3. Page 3: forecasting approach, features, validation design
4. Page 4: forecasting results, explainability, conclusion

Appendix can hold supporting visuals, but the main story must stand on its own.

## 13. Suggested Repository Structure

Use a structure like this:

```text
repo/
  data/
  notebooks/
  src/
  outputs/
  figures/
  submission/
  README.md
```

Minimum expectations:

- One place for final figures
- One place for final submission files
- README with reproduce steps
- Clear distinction between exploration and final pipeline code

## 14. Execution Checklist

### Phase 1: Understand and verify

- Load all CSVs
- Validate keys, dates, duplicates, and nulls
- Build a join map
- Confirm target period boundaries

### Phase 2: Lock easy points

- Compute all 10 MCQ answers programmatically
- Review each answer twice

### Phase 3: Build the story

- Generate broad exploratory cuts
- Shortlist only the insights with business value
- Convert each selected chart into a claim with evidence and decision

### Phase 4: Build forecasting pipeline

- Create leakage-safe features
- Set up rolling validation
- Train baselines and candidate models
- Select final model
- Generate submission

### Phase 5: Package and submit

- Write final 4-page report
- Push complete GitHub repository
- Upload Kaggle submission
- Fill official form
- Confirm all administrative requirements are satisfied

## 15. Final Submission Checklist

- MCQ answers completed
- `submission.csv` validated against `sample_submission.csv`
- Report exported to PDF within page limit
- GitHub repository is public or shared correctly
- Kaggle submission link is ready
- Student ID images for all members are collected
- Team confirms at least one member can attend the final round in person on `2026-05-23` at VinUni, Hanoi

## 16. Practical Advice

- Do not try to show everything in the data
- Do not overload the report with weak charts
- Do not use random CV for a time-series problem
- Do not make recommendations without quantified evidence
- Do not leave reproducibility for the last day

The cleanest path to a strong result is:

1. Secure MCQ correctness
2. Win the EDA story with clear business actions
3. Ship a disciplined, explainable forecasting model
