# Project Error and Revision Log

This log records errors, analytical revisions, and documentation gaps identified across six notebooks. Each entry summarizes the issue, the evidence used to diagnose it, and the resolution or remaining action. Repeated descriptions of the same logistic regression findings have been consolidated.

## Notebook 1 — Data Cleaning

**Regex warning.** A non-product `StockCode` filter used capturing parentheses, triggering a pandas warning. The expression was changed to a non-capturing group `(?:...)`.

**Incorrect audit counts.** A forward-looking difference assigned dropped-row counts to the wrong step after the December 2011 trim was inserted. A standard backward-looking `diff()` corrected the audit table.

**Phantom revenue from cancelled purchases.** Cleaning removed cancellation rows but retained their original purchases. An implausible prediction exposed the problem. A rank-based consuming join removed 3,072 matched pairs across 844 customers, representing about 5.1% of revenue; duplicate-order cases were checked.

## Notebook 2 — RFM and Cohorts

**Champions threshold too broad.** Requiring top-40% scores on all three RFM measures produced an inflated segment. Frequency and monetary value were correlated (0.57). The threshold was tightened to the top 20% on each measure.

**Incorrect explanation for the inflated Champions segment.** Recency was initially proposed as the main driver. The measured frequency–monetary correlation (0.57) exceeded the recency–frequency correlation (0.25), supporting a different explanation.

**Undifferentiated Needs Attention segment.** A diagnostic revealed a high-value, low-frequency group within the catch-all segment. A separate segment was added.

**Misdiagnosed December 2010 cohort anomaly.** Holiday seasonality was proposed first, but extrapolation from partial December 2011 data did not support it. A subsequent shape-based extrapolation reused a pattern affected by the same bias. Left censoring was the supported diagnosis.

## Notebook 3 — Predictive CLV

**Probability-alive plotting call failed.** plot_probability_alive_matrix(bgf, ax=ax) did not accept ax in practice because the function created its own subplot. Removing the argument resolved the error.

**In-sample ML evaluation.** `GradientBoostingRegressor` was trained and evaluated on the same customers, producing a misleading near-zero aggregate error. `cross_val_predict` supplied out-of-fold evaluation.

**Incorrect import path.** `ConvergenceError` was imported from the nonexistent `lifetimes.exceptions`; the correct location was `lifetimes.utils`.

**Insufficient penalizer search range.** A ceiling of 1.0 failed on harder synthetic stress-test data. The ceiling was raised to 5.0 and failure guidance clarified.

**Missing zero-duration QA guard.** A notebook rewrite omitted the `T_cal == 0` check, allowing a division-by-zero diagnostic to yield NaN for purchases on the calibration cutoff. Execution testing caught the omission; the guard was restored.

**Inadequate convergence criterion.** The loop accepted a fit with no `ConvergenceError` even though penalizer 0.1 produced NaN standard errors from a non-invertible Hessian. This numerical validity check remained unresolved in the recorded notebook state.

**Incorrect Gamma-Gamma population mean formula.** The formula was corrected to p·v/(q−1). With q < 1, the implied term is undefined.

**BG-NBD fitting instability.** Wholesale-scale outliers caused one convergence failure and were excluded using a documented frequency rule. A second failure required penalizer tuning. The fitted dropout parameters remained degenerate, an analytical finding that was retained.

### Cross-notebook observation

Customers 15749 and 17511 appeared in multiple investigations. The phantom-revenue correction in Notebook 1 could therefore affect conclusions in Notebook 3.

**Misattributed change in customer 15749’s prediction.** Predicted revenue rose from 12,040 to 12,777 although that customer’s calibration record was unchanged. The automated loop selected penalizer 0.1 instead of 0.5, shifting predictions across customers; unchanged summary inputs and nearly unchanged predicted average value isolated the effect to predicted purchases.

**Undocumented penalizer sensitivity.** The stopping rule can accept different penalizers, leading to different individual predictions. The caveat was added to the notebook.

**Unexpected ML maximum for customer 14646.** The maximum prediction rose from 107,702.82 to 118,125.03. Transaction history confirmed sustained wholesale activity rather than a data defect. The example also clarified that the ML and BG-NBD/Gamma-Gamma models cover different customer populations.

**Incorrect segment-performance hypothesis.** BG-NBD/Gamma-Gamma was expected to perform worse for high-value, infrequent buyers, but the segment error table showed its best relative performance there. Uniform dropout collapse and the effect of q < 1 explained the result; the interpretation was revised.

**Missing re-verification notes.** Findings discussed during review were absent from Sections 4 and 5. Both sections were updated, including the customer 14646 population-coverage example.

## Notebook 4 — Churn Modeling

**Distorted logistic regression calibration.** With `class_weight="balanced"`, Brier score was 0.214 and 52.8% of customers were predicted to churn at threshold 0.5 versus a 29.1% actual rate. Removing the weight improved Brier to 0.180 and moved the calibration curve closer to the diagonal; the 0.5 classification rate became 11.0%.

**Duplicate logistic regression feature.** Mean predicted churn probability was 46.3% versus a 29.1% observed rate. A scaling hypothesis did not reproduce the shift in synthetic checks. Because all modeled customers had `frequency_cal > 0`, `avg_order_value_cal` duplicated `monetary_value_cal`. Removing it brought mean predicted probability to 29.2%.

### Validation lesson

Both logistic regression problems produced plausible surface metrics without runtime warnings. Independent checks of predicted means against observed rates revealed the discrepancies.

**Inaccurate dataset-loading handoff.** The handoff claimed a three-tier fallback; Notebook 1 used a single hardcoded local path. The handoff was corrected.

**Incorrect calibration count.** The handoff stated 3,315 customers, while Notebooks 3 and 4 both reported 3,310. The cause of the five-customer discrepancy was not confirmed.

**Unverified customer examples.** The handoff cited IDs 17511 and 12346 as notebook results, but neither appeared in the checked notebook markdown or outputs. The claims were marked unverified.

## Notebook 5 — Threshold Economics

**Missing false-negative costs for excluded wholesale customers.** Of 3,310 rows, 32 lacked BG-NBD/Gamma-Gamma values. Summing costs would silently skip their NaNs. ML values were used as a fallback; all 32 were non-churners in that run, so the sweep total did not change.

**Changed formula threshold after cost correction.** Mean false-negative cost rose from £153.22 to £208.46, moving the Bayes threshold from 0.0892 to 0.0671. Both thresholds were confirmed with `FP/(FP+FN)`.

**Rounded formula comparison.** The formula threshold was compared using the nearest 0.01 sweep point, creating a spurious zero gap for Gradient Boosting. Direct evaluation at the exact threshold gave LR a 5.0% (£1,090.37) gap and GBC a 0.3% (£60.00) gap.

**Cost comparison dominated by one customer.** The apparent £3,186.31 GBC advantage included £3,194.14 from one customer missed by LR. Excluding that case made LR £7.83 cheaper. The cost result was treated as fragile; the final LR recommendation relied on Notebook 4 calibration evidence.

**Stale artifact passed validation.** A nested docstring caused a notebook build syntax error, but a separate validation command checked an older .ipynb and reported success. Isolated build execution and output timestamp inspection exposed the problem. The nested docstring was replaced with comments.

## Notebook 6 — Segment Intervention Design

**Incomplete zero-churn segment explanation.** The explanation named Champions and Loyal Customers but omitted Needs Attention and Potential Loyalists. All four zero-churn segments were identified in the revised account.

**Fallback characterized as too rare.** The one-time-buyer fallback was framed as an unlikely edge case, but 34 customers (1.8%) met it because the population filters differed between notebooks. The description was updated with the count and cause.

**Imprecise segment-cost interpretation.** The initial explanation relied on a broad correlation between recency, value, and non-churn. The sharper mechanism is that the RFM snapshot date matches the churn holdout boundary, while recency ranks use the full population. The recorded Section 4a text had not yet been updated.
