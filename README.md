# Machine Learning Framework for Surface Water Fraction Retrieval

> Machine learning framework for global Surface Water Fraction (SWF) estimation from passive microwave brightness temperatures, developed as part of a Master's thesis in Data Science in the context of the [CIMR L2PAD](https://github.com/CIMR-L2PAD) project.

---

## Overview

Surface Water Fraction (SWF) — the proportion of open water within a satellite pixel — is a key geophysical variable for flood monitoring, hydrology, and climate studies. Current retrieval methods are physics-based and operate on a single observation point in space and time. This repository implements a complete machine learning framework to estimate SWF from passive microwave brightness temperatures recorded by the **WindSat** radiometer, serving as a proxy for the future **Copernicus Imaging Microwave Radiometer (CIMR)** mission.

The framework covers the full pipeline: from raw data download and harmonisation, through exploratory analysis, to a structured model development study including physics baseline, scaling, model selection, feature engineering, hyperparameter optimisation, and explainability analysis. Two experimental notebooks additionally explore whether incorporating **spatial and temporal context** via neural networks can yield further improvements.

---

## Repository Structure

```
.
├── 1-Data_preprocessing.ipynb          # Data download, reprojection, harmonisation, feature engineering
├── 2-Data_analysis.ipynb               # Exploratory data analysis (EDA)
├── 3-Model_training.ipynb              # Full regression pipeline: baseline → HPO → explainability
├── 4-Geographical_context_neural_network.ipynb  # Experimental: spatial/temporal context models
├── .gitignore
└── README.md
```

---

## Notebooks

### `1-Data_preprocessing.ipynb`
Downloads and validates the raw data products, reprojects the LPDR dataset from EASE-Grid v1 (EPSG:3410) to a standard 0.25° geographic grid (EPSG:4326) to match WindSat, and merges all sources into a single unified Parquet dataset. Also computes physically-motivated engineered features: land surface emissivity, atmospheric corrections, and the physics-based SWF estimate used as a baseline.

**Key steps:** LPDR download · WindSat download · GDAL reprojection · product harmonisation · feature engineering · dataset serialisation

### `2-Data_analysis.ipynb`
Performs a thorough exploratory analysis of the harmonised dataset before any modelling. Examines temporal and spatial data distributions, univariate statistics, inter-variable correlations, PCA structure, and class imbalance in the SWF target. Findings directly inform design decisions in the training pipeline.

**Key steps:** coverage analysis · distribution plots · correlation heatmaps · PCA · spatial visualisation with Cartopy

### `3-Model_training.ipynb`
The core of the thesis. Implements a structured, sequential model development pipeline in which each step conditions the next:

| Step | Description |
|---|---|
| Physics Baseline | Evaluates the Difference Ratio (DR) formula on the 2018 test set as a reference |
| Scaling Study | Compares 6 preprocessing variants (zero removal, Box-Cox, feature scaling) |
| Model Selection | Benchmarks XGBoost, LightGBM, CatBoost, Ridge, ElasticNet with light HPO |
| Feature Study | Forward feature-set comparison across 18 candidate sets |
| Feature Pruning | RFECV + SHAP-based redundancy removal |
| Full HPO | Optuna Bayesian optimisation (200 trials, 5-fold CV) on fixed architecture and feature set |
| Explainability | SHAP global importance, beeswarm, dependence plots, interaction values, local explanations |
| Error Analysis | Residual diagnostics, spatial/temporal error maps, stratification by land cover and SWF quantile |
| Final Model | Retrained on full data; consolidated comparison table across all tiers |

### `4-Geographical_context_neural_network.ipynb`
Experimental extension investigating whether providing spatial neighbours or temporal history as additional inputs improves SWF prediction. Implements neural network architectures that consume context windows around each target pixel.

---

## Data Sources

| Dataset | Description | Access |
|---|---|---|
| [WindSat Daily TB Maps](https://data.remss.com/TB/intercalibration/windsat_TB_maps_daily_025deg_unfiltered/) | Top-of-atmosphere brightness temperatures at 18.7 and 37 GHz, 0.25° grid | Remote Sensing Systems |
| [LPDR v3.1](http://files.ntsg.umt.edu/data/LPDR_v3/) | Daily global SWF, soil moisture, VOD, PWV, VPD, air temperature | NSIDC / NTSG |

> **Note:** Raw data files are not included in this repository due to storage constraints (~1 TB for two years). The download scripts are provided in `1-Data_preprocessing.ipynb`.

---

## Installation

### Requirements

- Python 3.10+
- Two separate conda/virtual environments are needed due to a conflict between `rasterio` and `gdal` (used only in the reprojection step of notebook 1).

### Main environment

```bash
pip install numpy pandas xarray scipy scikit-learn matplotlib seaborn cartopy
pip install xgboost lightgbm catboost optuna shap tqdm
```

### GDAL environment (reprojection only)

```bash
conda install -c conda-forge gdal rasterio
```

---

## Reproducing the Results

Run the notebooks in order:

```
1-Data_preprocessing.ipynb   →   2-Data_analysis.ipynb   →   3-Model_training.ipynb   →   4-Geographical_context_neural_network.ipynb
```

> The temporal split used throughout is **2017 → train / 2018 → test**, reflecting the operational deployment scenario where the model is trained on historical data and applied to future observations.

---

## Hardware

All experiments were developed and run on a personal computer:

| Component | Specification |
|---|---|
| CPU | Intel Core i5-14600KF (14 cores, 5.3 GHz) |
| RAM | 32 GB DDR5 |
| GPU | NVIDIA GeForce RTX 5060 Ti |
| Storage | 1 TB NVMe SSD |
| OS | Windows 11 Home |

GPU acceleration (CUDA) is used by XGBoost for training and SHAP computation.

---

## References

- Du, J., Kimball, J.S., Jones, L.A., Kim, Y., Glassy, J., and Watts, J.D. (2017). A global satellite environmental data record derived from AMSR-E and AMSR2 microwave earth observations. *Earth System Science Data*, 9, 791–808. https://doi.org/10.5194/essd-9-791-2017
- Du, J., Kimball, J.S., Galantowicz, J., Kim, S.B., Chan, S.K., Reichle, R., Jones, L.A., and Watts, J.D. (2018). Assessing global surface water inundation dynamics using combined satellite information from SMAP, AMSR2 and Landsat. *Remote Sensing of Environment*, 213, 1–17.
- Meissner, T. (2023). RSS SMAP–WindSat TB Match-Ups on daily 0.25° grid, Version 1.0. Remote Sensing Systems, Santa Rosa, CA.
- Fernandez-Moran, R., Terrer-Gómez, A., Link, M., Lavergne, T., and Piles, M. CIMR L2PAD Algorithm Theoretical Basis Document — Surface Water Fraction. ESA-funded project 4000143081/23/I-NS (2023–2027).

---

## License

This repository is associated with a Master's thesis and is shared for reproducibility and academic reference. Please cite the associated thesis if you use this code in your work.
