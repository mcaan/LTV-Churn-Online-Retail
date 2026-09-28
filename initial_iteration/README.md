# First iteration: archived analysis

The six numbered notebooks, [error log](PROJECT_ERROR_LOG.md), and [post-mortem](PROJECT_POST_MORTEM.md) document the first approach and why it was revised. The current analysis lives in [`../notebooks/`](../notebooks/README.md).

To rerun the archive, first follow the [data download and conversion instructions](../data/README.md). Launch Jupyter from the repository root or `initial_iteration/`, select the environment in the root README, and run these six older notebooks in numerical order. Notebook 1 creates `initial_iteration/data/processed/`; later archive notebooks read from the same directory. None of them writes to the current notebooks' `data/processed/` folder.

These notebooks preserve the original analytical methods and previously displayed results. They are an earlier exploration with limitations described in the post-mortem; their outputs should not be combined with the revised iteration. The archive's numerical results have not been revalidated under a fresh environment.
