# K-Means Real Estate Price Predictor

Pipeline to clean real-estate listings data, vectorize features, cluster with custom K-means, and estimate property prices.

## Main Files

- `sl_vectorization.py` : data cleaning and feature engineering utilities.
- `k_means.py` : custom K-means implementation and helpers.
- `model.py` : model building + prediction functions.
- `app.py` : CLI app that loads a parquet model and predicts price.
- Notebooks:
  - `K-algorithms.ipynb`
  - `vectorize_dataset_seloger.ipynb`
  - `k-means-applied.ipynb`

## Data / Artifacts

- `dataset/` : raw + vectorized datasets.
- `models/` : parquet model files.
- `graphs/` : generated charts.
- `backups/` : historical experiments.

## Requirements

- Python 3.x
- `numpy`, `pandas`, `matplotlib`, `scikit-learn`, `nltk`, `fastparquet`

## Run CLI Predictor

1. Activate environment.
2. Run:
   - `python app.py`
3. Provide model path without extension, for example:
   - `models/model_sl_10`

## Notes

- There is a legacy `README.txt`; this `README.md` is the maintained version.
- Folder includes virtualenv/build artifacts committed during experimentation.
