# Pneumonia CNN Classification

Projet de classification binaire de radiographies thoraciques (`NORMAL` vs `PNEUMONIA`) avec PyTorch, centre sur les notebooks.

## Workflow du projet

1. `notebooks/01_eda.ipynb`
   - Inspection du dataset, verification de la distribution des classes et visualisations.
   - Genere les sorties EDA dans `eda_outputs/`.
2. `notebooks/02_training_cnn.ipynb`
   - Pretraitement, dataloaders, entrainement, validation et evaluation test.
   - Genere les artefacts (par ex. dans `models/` et `training_outputs/`).
3. `notebooks/03_evaluation_gradcam.ipynb`
   - Evaluation post-entrainement et verification d'interpretabilite (Grad-CAM).

## Rapport

- Rapport principal : `reports/rapport.md`
- Ce rapport consolide les conclusions des notebooks `01`, `02` et `03` (EDA, entrainement, evaluation et Grad-CAM).

## Structure du depot

- `data/` : racine dataset attendue par les notebooks (`data/chest_xray/...`).
- `notebooks/` : notebooks EDA, entrainement et evaluation.
- `eda_outputs/` : sorties CSV/figures generees par l'EDA.
- `models/` : poids de modeles sauvegardes (exemple : `baseline_cnn_last.pt`).
- `training_outputs/` : sorties generees (ex. images pretraitees exportees).
- `src/` : fonctions/scripts reutilisables.
- `requirements.txt` : dependances Python.
- `.gitignore` : ignore datasets, artefacts, sorties et environnements virtuels.

## Setup environnement

1. Creer et activer un environnement virtuel.
2. Installer les dependances :
   - `pip install -r requirements.txt`
3. Enregistrer un kernel (optionnel pour Jupyter) :
   - `python -m ipykernel install --user --name pneumonia-cnn`

## Setup GPU optionnel (CUDA)

Si tu veux entrainer sur GPU depuis le notebook, installe une version CUDA de PyTorch dans le meme environnement :

- `python -m pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu129`

Verification notebook ou terminal :

- `python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"`

## Ordre d'execution des notebooks

1. Ouvrir Jupyter dans ce dossier :
   - `jupyter notebook`
2. Executer dans l'ordre :
   - `01_eda.ipynb`
   - `02_training_cnn.ipynb`
   - `03_evaluation_gradcam.ipynb`

## Notes de reproductibilite

- Garder les donnees sous `data/chest_xray` avec sous-dossiers `train/`, `val/`, `test/`.
- Utiliser des seeds fixes dans les cellules d'entrainement.
- Sauvegarder metriques/figures apres chaque run pour le suivi.
