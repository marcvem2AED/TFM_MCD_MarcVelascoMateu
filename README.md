# Machine Learning Framework for Surface Water Fraction Retrieval

> Machine learning framework for global Surface Water Fraction (SWF) estimation from passive microwave brightness temperatures, developed as part of a Master's thesis in Data Science in the context of the [CIMR L2PAD](https://github.com/CIMR-L2PAD) project.

---

## Overview

Surface Water Fraction (SWF) — the proportion of open water within a satellite pixel — is a key geophysical variable for flood monitoring, hydrology, and climate studies. The operational retrieval is physics-based (a closed-form Difference Ratio formula) and treats each observation as an independent point in space and time. This repository implements a complete machine learning framework that estimates SWF from passive microwave brightness temperatures recorded by the **WindSat** radiometer, serving as a proxy for the future **Copernicus Imaging Microwave Radiometer (CIMR)** mission.

The framework covers the full pipeline: from raw data download and harmonisation, through exploratory analysis, to a structured model-development study (physics baseline → preprocessing study → model selection → feature study → hyperparameter optimisation → explainability → error analysis → final model). A fourth notebook extends the work experimentally, testing whether incorporating **temporal** (prior-day) and **spatial** (neighbouring-pixel) context improves prediction.

The tuned model achieves a **test R² of 0.985** (RMSE 0.0073), substantially outperforming the physics baseline (R² 0.576) on the held-out 2018 data.

---

## Repository Structure

```
.
├── 1-Data_preprocessing.ipynb            # Download, reprojection, harmonisation, feature engineering
├── 2-Data_analysis.ipynb                 # Exploratory data analysis (EDA)
├── 3-Model_training.ipynb                # Full regression pipeline: baseline → HPO → explainability
├── 4-Temporal_and_spatial_context.ipynb  # Experimental: temporal & spatial context (XGBoost)
├── data/                                 # Raw + harmonised data and datasets (gitignored)
├── models/                               # Serialised XGBoost models and feature lists (gitignored)
├── results/                              # Metrics, Optuna studies, sweep tables (gitignored)
├── .gitignore
└── README.md
```

> The `data/`, `models/`, and `results/` directories are produced by running the notebooks and are excluded from version control (they hold ~1 TB of raw data and large binary artifacts). The four notebooks are fully self-contained: each numbered section reloads the persisted artifacts it needs, so chapters can be re-run in isolation without repeating earlier computations.

---

## Notebooks

### `1-Data_preprocessing.ipynb`
Transforms raw observations from two passive-microwave sensors into a machine-learning-ready tabular dataset for 2017–2018. Four stages:

1. **Download** — WindSat daily NetCDF maps (RSS) and LPDR v3 GeoTIFFs (NTSG).
2. **Reprojection** — warp LPDR from EASE-Grid v1 (EPSG:3410) onto the shared 0.25° geographic grid (EPSG:4326, 1440 × 720) used by WindSat, via GDAL nearest-neighbour resampling.
3. **Harmonisation** — merge the two datasets pixel-by-pixel, apply atmospheric corrections (first-order and the De Lannoy et al. two-stream formula), attach lookup-table reference emissivities, derive per-channel emissivity and the physics-based SWF estimate, integrate the GLWD land mask (with a derived coastal class), and apply quality filters.
4. **Data filing** — serialise each day to Parquet, adding cyclic temporal (`doy_sin`/`doy_cos`) and spatial (`lon_sin`/`lon_cos`) encodings.

**Key steps:** LPDR download · WindSat download · GDAL reprojection · product harmonisation · atmospheric correction · LUT emissivities · land-mask integration · feature engineering · Parquet serialisation

### `2-Data_analysis.ipynb`
Exploratory analysis of the harmonised dataset (≈26 million valid land-pixel observations, 49 columns) before any modelling: shape and dtypes, univariate distributions and target transformations, inter-variable correlation and brightness-temperature redundancy, a PCA dimensionality assessment (~20 components explain 95 % of variance), and the spatial/temporal structure of the target. Findings directly inform the training pipeline.

**Key steps:** structure & missing-value checks · distribution plots · target-transform study · correlation heatmaps · brightness-temperature redundancy analysis · PCA · spatial visualisation with Cartopy

### `3-Model_training.ipynb`
The core of the thesis. A structured, sequential pipeline in which each step conditions the next:

| Step | Description |
|---|---|
| §1 Physics baseline | Evaluates the closed-form Difference Ratio (DR) formula on the 2018 test set (R² ≈ 0.58) as the reference any ML model must beat |
| §2 Scaling study | Compares 6 preprocessing variants (zero-removal, Box-Cox target, feature scaling); selects **raw** features — Box-Cox actually degraded performance |
| §3 Model selection | Equal-budget Optuna TPE search over 6 model families (LinearRegression, Ridge, ElasticNet, XGBoost, LightGBM, CatBoost); **XGBoost** wins |
| §4 Feature study | Medium Optuna pass + forward comparison of 24 candidate feature sets (families A–F) + RFECV + SHAP-guided pruning → final **15-feature** set |
| §5 Final HPO | Exhaustive Optuna TPE search (5-fold CV) on the full training set; yields a deep, heavily-tuned XGBoost (≈2 850 trees, depth 16) |
| §6 Explainability | SHAP global importance, beeswarm, dependence, interaction values, local and regime-specific explanations |
| §7 Error analysis | Residual diagnostics, baseline comparison, out-of-range (negative) prediction analysis, stratification by `fwns` quantile |
| §8 Final model | Consolidated comparison table across all model tiers; final model retrained and persisted |

### `4-Temporal_and_spatial_context.ipynb`
Experimental extension investigating whether richer context improves SWF prediction. Unlike earlier drafts, this notebook is built entirely on **XGBoost** (reusing the locked HPO hyperparameters) so that any accuracy difference is attributable solely to the added context features.

- **Temporal sweep** (lags 1–30 days): four feature sets compare current-day only (A), current + lagged features (B), current + lagged ground-truth `fwns` (C), and the full combination (D). A merge-based join (not positional `.shift`) correctly pairs each pixel with its observation exactly *L* days earlier, robust to irregular satellite passes.
- **Self-estimated FWN:** since ground-truth `fwns` is unavailable at inference, the trained model's own previous estimate is substituted (deployable inputs only).
- **Spatial sweep** (windows 3×3 → 9×9): aggregates the mean and/or standard deviation of neighbouring same-day pixels via a memory-bounded merge-accumulator, with correct longitude wrap-around and partial-window handling at coastlines and poles.

---

## Data Sources

| Dataset | Description | Access |
|---|---|---|
| [WindSat Daily TB Maps](https://data.remss.com/TB/intercalibration/windsat_TB_maps_daily_025deg_unfiltered/) | Top-of-atmosphere brightness temperatures and atmospheric RT terms at 18.7 GHz (Ku) and 37 GHz (Ka), V & H polarisations, 0.25° grid | Remote Sensing Systems |
| [LPDR v3](http://files.ntsg.umt.edu/data/LPDR_v3/) | Daily global surface water fraction, soil moisture, VOD, precipitable water vapour, vapour pressure deficit, surface temperature | NTSG / University of Montana |
| [GLWD](https://www.worldwildlife.org/pages/global-lakes-and-wetlands-database) | Global Lakes and Wetlands Database land-cover classification at 0.25° | WWF |

> **Note:** Raw data files are not included in this repository due to storage constraints (~1 TB for two years). The download instructions live in `1-Data_preprocessing.ipynb`. The pipeline pairs WindSat and the **descending** LPDR pass by (year, day-of-year); 726 of the 730 days in 2017–2018 are available (four dates are missing from the RSS archive).

---

## Installation

### Requirements

- Python 3.10+
- Two separate conda/virtual environments are needed because of a conflict between `rasterio` and `gdal`. GDAL (`osgeo`) is used **only** for the reprojection step in notebook 1; the rest of the project runs in the main environment.

### Main environment

```bash
pip install numpy pandas pyarrow xarray netCDF4 h5py scipy scikit-learn matplotlib seaborn cartopy
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
1-Data_preprocessing.ipynb  →  2-Data_analysis.ipynb  →  3-Model_training.ipynb  →  4-Temporal_and_spatial_context.ipynb
```

> The temporal split used throughout is **2017 → train / 2018 → test**, reflecting the operational deployment scenario where the model is trained on historical data and applied to future observations. Computationally expensive cells (model selection, the Optuna searches, RFECV, the lag/window sweeps) are flagged in the notebooks with expected runtimes and persist their outputs to `models/` and `results/`, so the figures and tables can be regenerated without re-running the heavy training.

---

## Key Results

**Model tiers** (all metrics on the held-out 2018 test split):

| Model tier | RMSE | MAE | R² |
|---|---|---|---|
| Physics baseline (DR formula) | 0.0380 | 0.0195 | 0.576 |
| XGBoost — forward-study best (17 feat) | 0.0126 | 0.0072 | 0.954 |
| XGBoost — mediumweight HPO | 0.0117 | 0.0068 | 0.960 |
| **XGBoost — final, full HPO (15 feat)** | **0.0073** | **0.0042** | **0.985** |

The final 15-feature model uses the four WindSat `tbtoa` channels, two atmospheric terms (`tran19V`, `tbup19V`), ERA5 surface temperature, the LPDR geophysical retrievals (`vsm`, `VOD`, `Tmn`, `PWV`, `VPD`), and the spatial encodings (`latitude_grid`, `lon_sin`, `lon_cos`). Stratified by target quantile it remains strong across regimes (R² ≈ 0.99 / 0.95 / 0.99 for low / medium / high `fwns`).

**Context experiments (notebook 4):**

- **Temporal context helps most through the autoregressive signal.** Supplying the previous day's *ground-truth* `fwns` (set C) lifts R² well above the current-day baseline, and combining it with lagged features (set D) is best (R² ≈ 0.97–0.98); lagged observational features alone (set B) add little. The gain persists across lags of 1–30 days.
- **Spatial context helps marginally.** A 3×3 window-mean aggregation gives a small lift (R² ≈ 0.956 → 0.958); the benefit fades for larger windows, and local standard deviation (texture) adds little.

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

GPU acceleration (CUDA) is used by XGBoost for training, the Optuna searches, and SHAP computation (`device='cuda'`, `tree_method='hist'`).

---

## References

- Du, J., Kimball, J.S., Jones, L.A., Kim, Y., Glassy, J., and Watts, J.D. (2017). A global satellite environmental data record derived from AMSR-E and AMSR2 microwave earth observations. *Earth System Science Data*, 9, 791–808. https://doi.org/10.5194/essd-9-791-2017
- Du, J., Kimball, J.S., Galantowicz, J., Kim, S.B., Chan, S.K., Reichle, R., Jones, L.A., and Watts, J.D. (2018). Assessing global surface water inundation dynamics using combined satellite information from SMAP, AMSR2 and Landsat. *Remote Sensing of Environment*, 213, 1–17.
- De Lannoy et al. (2016). Source of the reference land-emissivity lookup tables (binned by soil moisture and VOD) and the two-stream atmospheric-correction formula used in the harmonisation step.
- Meissner, T. (2023). RSS SMAP–WindSat TB Match-Ups on daily 0.25° grid, Version 1.0. Remote Sensing Systems, Santa Rosa, CA.
- Fernandez-Moran, R., Terrer-Gómez, A., Link, M., Lavergne, T., and Piles, M. CIMR L2PAD Algorithm Theoretical Basis Document — Surface Water Fraction. ESA-funded project 4000143081/23/I-NS (2023–2027).

---

## License

This repository is associated with a Master's thesis and is shared for reproducibility and academic reference. Please cite the associated thesis if you use this code in your work.
