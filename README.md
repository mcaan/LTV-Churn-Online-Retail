# Customer Lifetime Value and Churn | Online Retail

An end-to-end portfolio analysis of customer value, no-purchase risk, and the economics of a proposed retention intervention. The six notebooks use the [UCI Online Retail dataset](https://archive.ics.uci.edu/dataset/352/online+retail) and take a fixed **September 1, 2011** decision date: historical purchases supply features, while purchases through November 30 provide the future outcome.

## What the analysis found

- **1,926 repeat customers** qualified for the decision population (at least two invoices before the decision date). The same population and a fixed 60/20/20 train/validation/test split run through the project.
- A simple historic-rate extrapolation beat a fitted regression benchmark for individual three-month revenue prediction on validation (£900.71 versus £996.92 MAE). BG-NBD/Gamma-Gamma failed the notebook's suitability gate, so the analysis reports that limitation rather than using its invalid predictions.
- A gradient boosting classifier modestly beat logistic regression for predicting **no purchase** during the three-month holdout (validation ROC AUC 0.7495 versus 0.7294).
- With *illustrative* segment-specific outreach costs and a 25% margin assumption, validation selected gradient boosting at a churn-probability threshold of **0.09**. A prespecified alternative scored better on test; the selected rule remains frozen in the audit.
- The final notebook proposes a randomized outreach experiment. Historical sales and assumed prices do **not** establish that contacting customers would cause incremental revenue.

## Read the project

| Step | Notebook | Purpose |
| --- | --- | --- |
| 1 | [ETL and cleaning](notebooks/01_ETL_and_Cleaning.ipynb) | Clean transactions and handle cancellations using the decision clock. |
| 2 | [Population, value, RFM, cohorts](notebooks/02_Population_Historic_Value_RFM_and_Cohorts.ipynb) | Fix eligibility and splits; calculate observed historic value and decision-time segments. |
| 3 | [Predictive CLV](notebooks/03_Predictive_CLV.ipynb) | Compare future revenue estimates and produce a conditional-spend proxy. |
| 4 | [Churn model](notebooks/04_Churn_Model.ipynb) | Predict three-month no-purchase probability without selecting a threshold. |
| 5 | [Threshold economics](notebooks/05_Threshold_Economics.ipynb) | Select the intervention rule on validation, then evaluate once on test. |
| 6 | [Intervention design](notebooks/06_Intervention_Design.ipynb) | Audit the locked policy and outline a prospective experiment. |

The [first iteration and post-mortem](initial_iteration/README.md) document the earlier approach and the revisions that led to this version. Start with `notebooks/` for the current analysis.

## Run locally

Use Python 3.10+ from a terminal **at the repository root**. Create an environment once; install packages into that environment, regardless of where the project folder is stored:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m jupyter lab
```

On macOS/Linux, activate with `source .venv/bin/activate` and replace `py` with `python3`. If you already have an environment with the listed packages, activate it and skip the environment creation/install steps.

Open the notebooks in numerical order and select that Python environment as the kernel. The notebooks accept Jupyter launched from the repository root or its `notebooks/` directory. Notebook 1 reads `data/raw/Online Retail.csv` and writes to `data/processed/`; each following notebook consumes earlier outputs. No processed tables are distributed; running the sequence creates them locally.

The download contains **no raw or processed data**. Follow the [data instructions](data/README.md) to get **Online Retail.xlsx** from UCI, put it in `data/raw/`, and run `python data/prepare_raw.py` to create the CSV used by notebook 1. Then run notebooks 1–6 in order. The [notebook guide](notebooks/README.md) maps their outputs.

## Scope and limitations

The dataset records transactions, not actual campaign assignment, action costs, or causal effects. “Churn” here means **no purchase during September–November 2011** among previously repeat customers; it is not account cancellation. Three-month holdout revenue is a short-horizon value target, not measured lifetime value. The policy loss calculation uses a conditional-active spend estimate, a hypothetical margin, and illustrative outreach prices. Its proposed actions are a test design, not a proven rollout recommendation.

## Data credit

Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. [https://doi.org/10.24432/C5BW33](https://doi.org/10.24432/C5BW33). Dataset licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The dataset and generated outputs are obtained and created locally; neither is included in this repository bundle. Project code and commentary are by the repository author.
