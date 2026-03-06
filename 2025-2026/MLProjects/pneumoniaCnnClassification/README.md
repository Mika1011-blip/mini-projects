# Pneumonia CNN Classification

Notebook-first binary classification project for chest X-ray pneumonia detection (`NORMAL` vs `PNEUMONIA`) with PyTorch.

## Project Workflow

1. `notebooks/01_eda.ipynb`
   - Dataset inspection, class distribution checks, and sample visualization.
   - Generates exploratory outputs under `eda_outputs/`.
2. `notebooks/02_training_cnn.ipynb`
   - Data preprocessing, dataloaders, training loop, validation, and test evaluation.
   - Produces model/output artifacts (for example under `models/` and `training_outputs/`).
3. `notebooks/03_evaluation_gradcam.ipynb`
   - Post-training evaluation and interpretability checks (Grad-CAM style analysis).

## Repository Layout

- `data/`: dataset root expected by notebooks (`data/chest_xray/...`).
- `notebooks/`: EDA, training, evaluation notebooks.
- `eda_outputs/`: generated CSV/figure outputs from EDA.
- `models/`: saved model weights (example: `baseline_cnn_last.pt`).
- `training_outputs/`: generated outputs such as preprocessed image exports.
- `src/`: reserved for script refactoring (currently placeholders).
- `requirements.txt`: Python dependencies.
- `.gitignore`: ignores datasets, model artifacts, outputs, and virtualenv files.

## Environment Setup

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Register kernel (optional for Jupyter):
   - `python -m ipykernel install --user --name pneumonia-cnn`

## Optional GPU Setup (CUDA)

If you want notebook training on GPU, install a CUDA-enabled PyTorch build in the same environment:

- `python -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu129`

Verify from notebook or shell:

- `python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"`

## Notebook Run Order

1. Open Jupyter in this folder:
   - `jupyter notebook`
2. Run notebooks in order:
   - `01_eda.ipynb`
   - `02_training_cnn.ipynb`
   - `03_evaluation_gradcam.ipynb`

## Reproducibility Notes

- Keep data under `data/chest_xray` with `train/`, `val/`, and `test/` class subfolders.
- Use fixed seeds in training cells for stable experiment comparisons.
- Save metrics/plots after each run for report-ready tracking.
