# Customer Lifetime Value and Churn Prediction — Online Retail

A customer analytics project using transaction history to study customer value, predict three-month purchasing inactivity, and design a testable retention strategy. The analysis combines decision-time RFM segmentation, revenue forecasting, churn modeling, intervention economics, and a proposed randomized experiment.

## Project Overview

The project asks three connected questions:

1. Which repeat customers appear most valuable based on purchasing history available at a fixed decision date?
2. How well can future revenue and the probability of no future purchase be predicted from that history?
3. Given an assumed cost of outreach, which customers would a proposed retention policy flag, and what would need to be tested before deploying it?

The decision date is **September 1, 2011**. Purchases before that date provide the customer features; purchases from September through November 2011 provide the three-month outcomes. A single population of **1,926 customers** with at least two earlier invoices is used throughout the current six-notebook workflow. Customers are assigned once to a **60/20/20 train/validation/test split**.

The project also retains an [initial iteration and post-mortem](initial_iteration/README.md). The current notebooks incorporate the lessons from that first pass, especially the need for a consistent customer population, a common decision clock, and a separate test set for evaluating a validation-selected policy.

## Results Summary

### Customer value and revenue forecasting

Observed historic value is highly concentrated. Among eligible repeat customers, median calibration-period revenue was approximately **£539**, compared with a mean of **£1,508**. The RFM analysis describes differences in recency, frequency, and monetary value without using purchases from the outcome window to define segments.

Three approaches to predicting future revenue were considered. On the validation population, a simple historic-rate extrapolation had lower individual-customer error than the fitted regression model:

| Three-month revenue estimate | Validation mean absolute error |
| --- | ---: |
| Historic-rate extrapolation | **£900.71** |
| Gradient boosting regression | £996.92 |

Both approaches underpredicted aggregate holdout revenue. A BG-NBD/Gamma-Gamma approach failed the notebook's suitability checks: its fitted Gamma-Gamma parameters did not support a usable population-mean prediction. The project therefore reports that modeling limitation instead of using those forecasts in the proposed intervention policy.

### Predicting no future purchase

“Churn” in this analysis means **no purchase during the three-month outcome window** by a customer who had previously made at least two purchases. It does not mean account cancellation.

Two models were trained on information available before the decision date:

| Model | Validation ROC AUC | Validation PR AUC | Validation Brier score |
| --- | ---: | ---: | ---: |
| Logistic regression | 0.7294 | 0.5236 | 0.1811 |
| Gradient boosting classifier | **0.7495** | **0.5566** | **0.1755** |

Gradient boosting performed modestly better on these validation measures. The churn notebook exports probabilities without choosing an outreach cutoff; that choice belongs to the subsequent economic analysis.

### Intervention policy and held-out evaluation

The policy analysis attaches **illustrative** segment-specific outreach prices, a **25% assumed margin**, and a model-based proxy for the value of missing an active customer. On validation customers, the lowest modeled loss under the chosen assumptions came from the gradient boosting classifier at a churn-probability threshold of **0.09**.

The threshold and model were then locked before the test evaluation. On the held-out test population, a prespecified alternative threshold of **0.06** produced lower modeled loss. This result is retained rather than using the test set to change the selected rule. The choice was also sensitive to the assumed prices and margin: only three of nine examined scenarios selected the 0.09 rule.

These loss figures are **scenario estimates, not measured savings or incremental revenue**. The transaction data contain no actual outreach treatment, response, or intervention cost.

## Recommended Next Step

The final notebook translates the locked rule into a proposed customer-level action plan and outlines a prospective experiment. Newly eligible customers flagged by the rule would be randomized **within segment** to the proposed outreach or a no-contact control. The primary evaluation would compare incremental contribution net of the actual intervention cost over a specified follow-up window.

That experiment is necessary before deciding whether contact changes customer behavior enough to justify its cost. Retrospective prediction alone cannot answer that causal question.

## Data

The analysis uses [Online Retail](https://archive.ics.uci.edu/dataset/352/online+retail), a transaction dataset from a UK-based non-store retailer, made available by the UCI Machine Learning Repository. The source workbook, converted CSV, and generated tables are **not included in this repository**.

Download **Online Retail.xlsx** from the UCI page, place it in `data/raw/`, and run the included conversion script to create `data/raw/Online Retail.csv`. See [data/README.md](data/README.md) for the exact steps. Generated outputs from the current analysis stay under `data/processed/`; the initial iteration uses its own `initial_iteration/data/processed/` folder.

**Dataset citation:** Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. [doi:10.24432/C5BW33](https://doi.org/10.24432/C5BW33). The source dataset is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Analytical Workflow

| Notebook | Focus |
| --- | --- |
| [01 — ETL and cleaning](notebooks/01_ETL_and_Cleaning.ipynb) | Clean transaction data, reconcile cancellations using the decision clock, and audit exclusions. |
| [02 — Population, historic value, RFM, and cohorts](notebooks/02_Population_Historic_Value_RFM_and_Cohorts.ipynb) | Define eligible customers and fixed splits; calculate observed value and train-fitted RFM cutpoints. |
| [03 — Predictive CLV](notebooks/03_Predictive_CLV.ipynb) | Compare three-month revenue estimates and construct a conditional-active spend proxy for policy analysis. |
| [04 — Churn model](notebooks/04_Churn_Model.ipynb) | Model the probability of no purchase in the outcome window. |
| [05 — Threshold economics](notebooks/05_Threshold_Economics.ipynb) | Choose a model and threshold on validation, check sensitivity, and evaluate the locked rule on test. |
| [06 — Intervention design](notebooks/06_Intervention_Design.ipynb) | Audit the action plan and specify a prospective randomized test. |

Run the current notebooks in numerical order. Each notebook saves inputs needed by the next one. The [notebook guide](notebooks/README.md) lists the main generated outputs.

## Methodology

### Decision-time preparation and segmentation

The ETL notebook removes records without a customer identifier, exact duplicates, non-product entries, and invalid transaction values. It handles cancellations according to when a reversal would have been known at the decision date. The partial December 2011 period is excluded. Eligibility, train/validation/test assignment, and RFM cutpoints are fixed before the outcome period is used for evaluation.

### Predictive modeling

Future revenue estimates are compared against the same three-month holdout. A separate conditional-active spend model estimates the value proxy used by the policy calculation; it is distinct from an unconditional revenue forecast. Churn models use only pre-decision customer features, and their discrimination and probability quality are examined on validation data.

### Decision analysis

The threshold notebook converts predicted inactivity risk into a hypothetical outreach decision. It compares costs under stated assumptions, chooses a policy on validation only, checks sensitivity to those assumptions, and audits the locked choice once on test. The final notebook examines who would be flagged and describes how to measure real intervention effects prospectively.

## Repository Structure

```text
LTV-Churn-Online-Retail/
├── data/
│   ├── raw/                 # downloaded workbook and converted CSV; ignored by Git
│   ├── processed/           # generated current-iteration tables; ignored by Git
│   ├── prepare_raw.py       # converts the UCI workbook to the expected CSV
│   └── README.md
├── notebooks/               # six current analysis notebooks and notebook guide
├── initial_iteration/       # six first-pass notebooks, error log, post-mortem, guide
│   └── data/processed/      # generated first-pass tables; ignored by Git
├── .gitignore
├── README.md
└── requirements.txt
```

## Reproducing the Analysis

1. Clone this repository and activate a Python environment. Install the listed packages with `python -m pip install -r requirements.txt`.
2. Download **Online Retail.xlsx** from the [UCI dataset page](https://archive.ics.uci.edu/dataset/352/online+retail) and place it at `data/raw/Online Retail.xlsx`.
3. From the repository root, run `python data/prepare_raw.py`. This creates `data/raw/Online Retail.csv`.
4. Launch Jupyter from the repository root or `notebooks/`, select the environment used in step 1, and run notebooks **01 through 06** in order.

The raw file and all generated tables remain local and are ignored by Git. The initial-iteration notebooks can be run separately using the [archive instructions](initial_iteration/README.md); they do not write into the current output folder.

## Limitations

- The nine-month calibration history and three-month outcome window do not measure a customer's full lifetime value. Historic revenue and short-horizon forecasts are labeled accordingly.
- No purchase during the holdout is an operational inactivity label, not proof that a customer permanently left.
- A large customer and concentrated revenue make forecast accuracy sensitive to outliers. The probabilistic revenue model did not meet its own suitability gate.
- The policy's margin, outreach prices, and conditional-value proxy are assumptions or estimates. Different plausible assumptions can change the preferred threshold.
- No actual outreach occurred in the source data. Predicted risk and modeled loss do not establish that an intervention would improve retention or profit.

## Tools

Python · pandas · NumPy · scikit-learn · imbalanced-learn · lifetimes · Matplotlib · seaborn · Jupyter
