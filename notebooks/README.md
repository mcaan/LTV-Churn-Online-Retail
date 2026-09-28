# Current analysis notebooks

Run `01` through `06` in order with a Python kernel containing the packages in the root `requirements.txt`. Launch Jupyter from the repository root or `notebooks/`; all data reads and writes target the repository-level `data/` folder.

| Notebook | Main output in `data/processed/` |
| --- | --- |
| 01 ETL and cleaning | `online_retail_clean.parquet`, cancellation and ETL audit tables |
| 02 Population and RFM | `retail_population_manifest.parquet`, `retail_rfm.parquet`, `retail_config.json` |
| 03 Predictive CLV | `retail_features.parquet`, `retail_clv_policy_inputs.parquet` |
| 04 Churn | `retail_churn_probabilities.parquet` |
| 05 Threshold economics | `retail_locked_policy.json`, validation/test comparisons and decisions |
| 06 Intervention design | `retail_intervention_plan.parquet`, `retail_segment_audit.parquet` |

Saved notebook outputs document an earlier full run. Rerun all six notebooks after changing upstream data or assumptions; downstream saved tables otherwise reflect the older run. The archived `initial_iteration/` notebooks are a separate first pass and are not part of this execution sequence.
