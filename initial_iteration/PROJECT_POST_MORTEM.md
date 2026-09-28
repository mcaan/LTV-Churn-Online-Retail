# Iteration 1 Post-Mortem: Customer Churn Prediction and Lifetime Value

This document records the results, decisions, and unresolved issues at the end of iteration 1. It does not incorporate work completed in iteration 2; later changes are documented separately.

## Project context

A portfolio project applying techniques from a series of CLV/churn articles (Towards
Data Science) to the **UCI Online Retail dataset** (541,909 transactions, Dec 2010–Dec
2011, UK-based online gift retailer, a customer base mixing retail and wholesale
buying patterns). 

**Source articles** (Towards Data Science):
1. *Your Churn Threshold Is a Pricing Decision* (Fabio Oliveira) — argues most churn
   analyses default to a 0.5 classification threshold, which implicitly assumes false
   positives and false negatives cost the same. Uses Kaplan-Meier 
   survival analysis and a dollar-cost profit curve across thresholds on the IBM Telco 
   dataset.
2. *From Analytics to Actual Application: CLV* (Katherine Munro) — historic CLV
   calculation, segmentation, acquisition-cost breakeven.
3. *Congrats on Your CLV Prediction Model, Now What* (Munro) — use cases for CLV
   predictions: loyalty nudges, retention targeting, B2B detection, forecasting.
4. *Methods for Modelling CLV* (Munro) — Stupid Simple Formula (+ margin variants),
   Cohort Analysis, RFM segmentation.
5. *From Probabilistic to Predictive: CLV* (Munro) — BG-NBD + Gamma-Gamma vs. ML
   approaches to predictive CLV.

Built as six notebooks, each an `nbformat` build
script (source of truth in `src/`), tested in the sandbox against synthetic data
(`ast.parse` → `nbformat.validate` → `nbconvert --execute`) and run by the project
owner against the real dataset, with real results fed back and verified rather than
assumed.

Conducted with help from Claude Sonnet 5.

---

## Notebook findings

### Notebook 1 — ETL & Cleaning
Standard cleaning (missing IDs, cancellations, non-product line items, non-positive
quantities, duplicates, partial final month). **Major fix added mid-project:**
discovered downstream in notebook 3 via an implausible CLV prediction traced to a
single 74,215-unit order cancelled 16 minutes later — the original cleaning dropped
only the cancellation row, leaving the matching (fictitious) original purchase intact.
Fixed with a rank-based matching join removing both sides of exact reversals.
**Scope: 3,072 matched pairs, 844 customers, £434,534.94 removed (~5.1% of revenue).**
Revenue concentration analysis (top 10% of customers) established the case for
segmentation-based rather than average-based CLV work, directly motivating notebook 2.

### Notebook 2 — Historic CLV, RFM & Cohorts
Revenue-based CLV as the primary metric; a margin-adjusted variant included only as an
explicitly-flagged illustrative assumption (25% margin — no real cost data exists).
**RFM segmentation went through real iteration, not a first-try result:** an initial
loose Champions definition (top 40% on R/F/M) came out oversized (934 customers,
21.8%); a correlation check (F↔M = 0.57, far stronger than R↔F = 0.25) corrected an
initial wrong hypothesis about what was driving the inflation; tightened to the
conventional strict definition (top 20% on all three). Breaking down the "Needs
Attention" catch-all surfaced a genuinely distinct customer type — low recency, low
frequency, meaningful spend — carved out as a new 9th segment, **"High-Value
One-Time/Infrequent Buyers," deliberately not labeled "churn risk"** on the reasoning
that churn presupposes an established repeat relationship these customers never had.
This distinction became central to notebook 4's population-scoping decision.
Cohort analysis found the **Dec 2010 cohort anomalously large and high-retaining** —
two wrong explanations (holiday seasonality, then a circular shape-based
extrapolation) before landing on the real cause: **left-censoring**, since Dec 2010 is
the first month in the dataset and some of its "new" customers are just pre-existing
customers appearing for the first time because tracking started then (confirmed: 65.6%
of Dec 2010's "new" customers appear in the first 9 days — the opposite of a
seasonality signal). Documented as an acknowledged limitation, not solved further.
A later addendum re-ran the segmentation on the phantom-revenue-corrected data:
segment counts were nearly unchanged, with Churn Risk (high value) dropping 186→179 —
traced precisely to phantom invoices inflating both revenue and order counts,
confirmed down to the exact quintile-boundary mechanics involved.

### Notebook 3 — Predictive CLV (BG-NBD/Gamma-Gamma vs. ML)
Built a calibration/holdout split (first 9 months / last 3 months) and a **naive
baseline** (extrapolate each customer's own historic rate) specifically to test
notebook 2's "historic CLV assumes constant spending" critique empirically rather than
asserting it. **BG-NBD required substantial real debugging**: a convergence failure
traced to wholesale-scale accounts violating the model's "buy till you die"
assumption (excluded via a documented model-scoping decision, not data cleaning); a
second convergence failure requiring a wider penalizer sweep; and a stopping-criterion
bug where "no `ConvergenceError`" was found not to mean "numerically sound" — a smaller
penalizer converged cleanly but produced `NaN` standard errors, a more severe failure
than the wider-but-finite confidence interval at a larger penalizer. Even after a
sound fit, **the dropout-rate parameters were degenerate** — `p(alive)` collapses to
~1.0 for nearly the entire customer base, traced to the dataset's large one-time-buyer
population starving dropout estimation of signal. **Headline finding: BG-NBD's core
advantage over simpler methods ("makes churn explicit") does not meaningfully hold on
this dataset** — a real, evidence-based conclusion about fit-for-purpose, not a general
indictment of the technique. Gamma-Gamma converged cleanly but separately showed
`q < 1`, making its population-mean-transaction-value formula mathematically
undefined, confirmed via an overshoot diagnostic that shrinks monotonically with
frequency — a systemic, population-wide bias, not a one-customer artifact.
**Head-to-head result: the naive baseline wins on individual-level accuracy** (after
all that debugging effort, simple rate extrapolation predicts individual customers
about as well or better than either "sophisticated" method) **while ML wins clearly on
aggregate accuracy** (~0% error vs. naive/BG-NBD's -33% to -37% under-prediction, since
naive and BG-NBD are both structurally biased toward under-prediction while ML's
errors partially cancel out). **A stated hypothesis was directly falsified**: BG-NBD
was predicted to perform worst on the One-Time/Infrequent Buyers segment; real data
showed it performing *best* there, reconciled to Gamma-Gamma's `q<1` shrinkage
functioning as an accidental benefit for exactly this segment. Every core finding was
independently re-verified after the notebook 1 phantom-revenue fix and found
unchanged — the fix, though real, wasn't what was driving these model limitations.

### Notebook 4 — Churn Labeling & Model
Reused notebook 3's calibration/holdout split; defined churn as zero purchases in the
3-month holdout window; **excluded one-time buyers from the model**, consistent with
notebook 2's deliberate decision not to treat them as churn risks. Trained Logistic
Regression and Gradient Boosting with out-of-fold predictions; **dropped
`class_weight="balanced"`** after real-data results showed it distorting LR's
calibration the same way SMOTE would (Brier 0.214 vs. Gradient Boosting's 0.186),
for no benefit given the threshold gets tuned separately anyway. Feature importance
showed `recency_to_T_ratio` and `frequency_cal` dominating both models — consistent
with general churn-modeling literature — with a clear nonlinear signature in GBC
(`monetary_value_cal`, `T_cal` near-zero for LR but meaningfully important for GBC).
The segment-level breakdown here produced the **first version of this project's
biggest structural finding**: actual churn rate was already visibly bimodal across
segments (0% for several, 65–100% for others), with the notebook's own markdown
correctly attributing this to full-history segments overlapping with the holdout
window that defines churn — flagged explicitly as a reason `segment` was kept out of
the model as a feature, though its implications for *using segment as a read-only
analysis lens downstream* weren't fully worked through until notebook 6.

### Notebook 5 — Threshold Economics
Adapted Oliveira's framework to non-contractual retail: FN cost as per-customer
margin-adjusted predicted holdout revenue (notebook 3's BG-NBD/Gamma-Gamma output,
falling back to the ML prediction for the ~1% of customers BG-NBD couldn't fit — a
real bug caught here that would have silently zero-costed exactly the highest-value
missed churners); FP cost a flat £15, explicitly confirmed as a placeholder rather
than real campaign data; CAC omitted entirely rather than invented, since no
acquisition-cost data exists. **Real-data cost ratio: 13.90:1** (mean FN cost £208.46
vs. flat FP £15) — coincidentally close to Oliveira's own 13.2:1 from an unrelated
business. **Empirical-minimum thresholds: LR 0.03 (£21,608.39), GBC 0.07
(£18,422.08)**, both far below the default 0.5, mirroring the source article's pattern
despite a completely different business and cost structure. A robustness check on the
apparent £3,186 cost gap between the two models found it **driven almost entirely by a
single customer** (`fn_cost = £3,194.14`) that LR missed and GBC happened to catch —
excluding that customer, LR's cost actually came in £7.83 *below* GBC's, reversing the
ranking. **Conclusion: the observed cost ranking is fragile and depends heavily on one
customer**. This check does not establish statistical equivalence. The iteration 1
recommendation (LR at threshold 0.03) therefore relied on LR's better measured
calibration (Brier 0.180 vs. 0.186), rather than the cost comparison. The
notebook's own closing note explicitly carried forward two open items: the source article's own recommendation
that FP cost should vary by segment, and the fact that the threshold was chosen by
sweeping against the same data used to compute its cost, with no held-out validation.

### Notebook 6 — Segment-Aware Intervention Design
Built an illustrative segment → intervention → cost table (£5–£40, replacing the flat
£15) addressing the open item from notebook 5. Applied at the same LR@0.03 threshold:
**91.7% of the population flagged, 68.4% of flags false positive** — the expected
consequence of the 13.9:1 cost ratio, not a modeling defect. **Segment-aware pricing
came out 39.7% more expensive than flat pricing, not cheaper** — investigated down to
a precise, confirmed mechanism: notebook 2's RFM recency reference date and notebook
4's churn-holdout boundary are the *same date* (2011-12-01), making top-tier
full-history recency close to definitionally equivalent to not churning. Verified
directly against real data: `pct_last_purchase_in_holdout` and `churn_rate` summed to
exactly 1.00 in every one of the 9 segments. Four segments showed an exact 0.00 churn
rate (Champions, Loyal Customers, Potential Loyalists, Needs Attention) — a materially
sharper and more consequential finding than notebook 4's original "segments overlap
with the holdout window" observation, since it directly explains why the segment-aware
cost redesign moved the wrong direction: false positives concentrate in segments whose
"value"-based pricing (which correlates with recency, which correlates with
non-churn) is highest.

---

## Iteration 1 results

- **Final model/threshold recommendation:** Logistic Regression at threshold 0.03,
  resting on calibration evidence (Brier score) rather than the cost comparison, which
  was sensitive to one customer.
- **Flat-cost total (real data):** £21,608.39. **Segment-aware total (same population,
  same threshold):** £30,176.39 (+39.7%), for a specific, confirmed structural reason
  rather than a modeling improvement.
- **Two structural findings turned out to be bigger than the numbers they were
  attached to:** BG-NBD/Gamma-Gamma's core assumptions genuinely don't hold on this
  dataset (not a tuning failure — a fit-for-purpose finding), and full-history
  `segment` is a compromised lens for any churn-rate analysis in this project, not
  just for notebook 6's cost table specifically.
- **Deliverable:** a full per-customer, segment-aware intervention plan (action + cost)
  for every flagged customer.

---

## Data and project limitations

*Genuinely inherent to this dataset and project setup.*

- **No real cost, CAC, or campaign-response data exists.** The flat £15 FP cost, the
  25% margin assumption, and the £5–£40 segment-aware cost table are all illustrative,
  reasoned estimates — there's no real business behind this dataset to source them
  from, and no outcome data to validate whether any proposed intervention would
  actually work.
- **Structural weaknesses in BG-NBD/Gamma-Gamma for this specific dataset** (dropout-
  parameter degeneracy, `q<1` monetary bias) trace to the large one-time-buyer
  population — a property of the data, not a fixable modeling choice within the
  BG-NBD/Gamma-Gamma framework itself.
- **Left-censoring in the Dec 2010 cohort**, a direct consequence of tracking starting
  at the beginning of the dataset — undiagnosable further without pre-window data that
  doesn't exist.
- **Small sample size in several segments** (Needs Attention n=16, Lost/Lowest
  Priority n=21, High-Value One-Time/Infrequent Buyers n=34) and a modest overall
  population (~1,874 customers for the churn model) — adds real noise risk to
  segment-level conclusions and constrains further splitting (e.g., for held-out
  threshold validation).

---

## Fixable design issues

*Preventable methodological issues — a different design choice could have avoided or
can still fix these, independent of data availability.*

1. **No held-out validation of the classification threshold.** Selected and scored on
   the same population in notebook 5 — fixable with a train/validation split using
   data already available. (Notably, Oliveira's own source article shares this exact
   gap in its published methodology.)
2. **The threshold was never re-optimized under segment-aware costs.** Once FP cost
   varies by segment, 0.03 is no longer guaranteed to minimize total cost — notebook 6
   layers segment-aware pricing onto a threshold still chosen under the flat-cost
   assumption.
3. **Segment-aware cost design prices by segment value alone, ignoring false-positive
   volume per segment** — the direct cause of the counterintuitive "more expensive"
   result, and a modeling choice rather than a data constraint.
4. **Full-history `segment` used as a churn-rate lens is leakage-adjacent**, caused by
   notebook 2's RFM snapshot date coinciding exactly with notebook 4's churn-holdout
   boundary — confirmed directly against real data (`pct_last_purchase_in_holdout` +
   `churn_rate` = 1.00 in every segment). Notebook 4 protected the *model* from this
   (kept segment out as a feature) but the same overlap still compromises segment as a
   *post-hoc analysis lens*, used throughout notebooks 5 and 6.
5. **RFM quintiles computed on the full customer base, applied within pre-filtered
   modeling subpopulations** in notebooks 4–6 — quantile boundaries drawn on one
   population read as meaningful within a narrower one.
6. **Population-cut mismatch between notebook 2 (full-history) and notebook 4
   (calibration-period-based)**, never explicitly reconciled — the direct cause of
   both the 34-customer segment-mapping fallback case in notebook 6 and much of #4/#5
   above.
7. **A documentation-propagation gap in notebook 3's re-verification**: new findings
   were added to Sections 6/7's write-ups but not propagated to Sections 4/5, caught
   only by a follow-up question rather than by process — a recurring risk whenever a
   correction needs to reach every place a number or claim is quoted, not just where
   it was first found.

---

## Recommendations for iteration 2

These were proposed at the end of iteration 1. Their implementation status
belongs in the iteration 2 documentation.

1. **Decouple the RFM snapshot date from the churn-holdout boundary** — compute
   full-history recency as of `CALIBRATION_END` rather than the full dataset's end
   date, removing the mechanical overlap behind flaw #4 without touching the churn
   label.
2. **Re-quantile RFM scores within the actual modeling population**, not the full
   customer base, so segment membership means the same thing in every notebook that
   uses it.
3. **Define one canonical population cut early**, referenced explicitly by every
   notebook (extending `config.json`), so the notebook 2 vs. notebook 4 mismatch
   surfaces during initial design rather than after three notebooks are built.
4. **Add a real train/validation split for threshold selection**, reusing the
   existing calibration population with a stratified split.
5. **Build a per-segment threshold/cost sensitivity check into notebook 5 itself**,
   rather than leaving segment-aware pricing as an unexplored extension discovered
   downstream in notebook 6.
6. **Weight the segment-aware cost design by expected false-positive volume, not just
   cost-per-case**, avoiding the specific failure mode found here.
7. **Keep a single running assumptions/decisions ledger** (`DECISIONS.md`) logging
   every placeholder value — £15 FP cost, 25% margin, the £5–£40 segment table, the
   0.03 threshold, the wholesale-exclusion cutoff — with its rationale and status
   (illustrative vs. measured) in one place, rather than requiring a reader to
   reconstruct which numbers are assumptions from prose scattered across six
   notebooks.
8. **Make the robustness/sensitivity check a standard section in every notebook that
   produces a headline number**, not a reactive one triggered by a surprising result
   after the fact — this would likely have caught the segment/churn-rate overlap as
   early as notebook 4, rather than notebook 6.
9. **Add an explicit cross-notebook propagation check whenever a finding changes** —
   a short checklist (which sections/notebooks reference this number or claim) run
   before considering a fix complete, directly addressing flaw #7.
