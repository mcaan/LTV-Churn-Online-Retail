# Get the data

1. Open the [UCI Online Retail dataset page](https://archive.ics.uci.edu/dataset/352/online+retail) and download **Online Retail.xlsx**.
2. Put that workbook in `data/raw/`.
3. From the repository root, activate the environment from the main README and run `python data/prepare_raw.py`. This creates `data/raw/Online Retail.csv`, the input expected by both notebook sequences.

The workbook, CSV, and all generated Parquet/CSV/JSON outputs are ignored by Git and are **not included** in the downloadable repo bundle. The current notebooks write to `data/processed/`; the archived first iteration writes only to `initial_iteration/data/processed/`. Run each sequence in numerical order if you want its outputs.

**Source:** Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. [doi:10.24432/C5BW33](https://doi.org/10.24432/C5BW33). The dataset is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
