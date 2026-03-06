# K-Means Real Estate Price Predictor

Pipeline to clean real-estate listing data, vectorize features, cluster with custom K-means, and estimate prices.

## Main Files

- `sl_vectorization.py`: data cleaning and feature engineering helpers.
- `k_means.py`: custom K-means implementation.
- `model.py`: model creation and prediction utilities.
- `app.py`: CLI app loading a saved model and returning predictions.
- Notebooks:
  - `K-algorithms.ipynb`
  - `vectorize_dataset_seloger.ipynb`
  - `k-means-applied.ipynb`

## Data and Artifacts

- `dataset/`: raw and transformed datasets.
- `models/`: saved model artifacts.
- `graphs/`: generated charts/plots.
- `backups/`: historical experiment copies.

## Requirements

- Python 3.x
- `numpy`, `pandas`, `matplotlib`, `scikit-learn`, `nltk`, `fastparquet`

## Run CLI Predictor

1. Activate your environment.
2. Run:
   - `python app.py`
3. Enter model path without extension when prompted, for example:
   - `models/model_sl_10`

## Notes

- `README.txt` is a legacy document; this file is the maintained reference.
- The folder currently contains local experiment artifacts (including `.venv/`).
