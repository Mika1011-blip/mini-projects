# Rapport — Classification d'images médicales : Détection de Pneumonie

**Projet B3 — Deep Learning / ECE Paris**

Collaborateurs : Yildiz Julien, Minh Khang Thai, Naira Awadin, Mahdi Bennamane

---

## 1. Introduction

### Contexte
La pneumonie est l'une des premières causes de mortalité infantile dans le monde. Un diagnostic rapide à partir de radiographies thoraciques (chest X-rays) peut sauver des vies, mais l'interprétation manuelle par des radiologues est coûteuse et sujette à la fatigue. L'objectif de ce projet est de développer un système de classification automatique capable de distinguer les radiographies **normales** des radiographies présentant une **pneumonie**.

### Objectifs
1. Indexer et préparer un pipeline de traitement d'images médicales.
2. Développer un modèle **Baseline CNN** "from scratch".
3. Implémenter le **Transfer Learning** avec ResNet18.
4. Comparer les performances et interpréter les décisions via **Grad-CAM**.

---

## 2. Analyse exploratoire (EDA) et Pipeline
*Basé sur les travaux d'indexation et de préparation (Notebook 01)*

### 2.1 Structure et Indexation des données
Le dataset total comprend **5 856 images**. Une vérification d'intégrité a été effectuée : **aucun fichier corrompu** n'a été détecté. Les données ont été structurées via des DataFrames indexant les chemins ('path'), labels et splits.

![corurpted_file](../outputs/images/img1.jpg)

**Répartition des données :**
- **Train** : 5 216 images (89,07%)
- **Validation** : 16 images (0,27%) — *Note : Ce split est très réduit, ce qui peut impacter la stabilité des métriques en cours d'entraînement.*
- **Test** : 624 images (10,66%)

![data_organization](../outputs/images/img2.jpg)

### 2.2 Analyse Visuelle (EDA)
L'analyse montre un déséquilibre de classe significatif : la classe **PNEUMONIA** est majoritaire.
- Les radiographies "Normal" présentent des poumons clairs sans zones d'opacité anormales.
- Les radiographies "Pneumonia" présentent des zones blanches diffuses (infiltrats) caractéristiques de l'infection.

![desequilibre](../outputs/images/img4.jpg)

### 2.3 Pipeline de traitement (Notebook 02)

Les images sont majoritairement en niveaux de gris (parfois 3 canaux), ce qui nécessite un **prétraitement standardisé**.

#### 1. Transformations de base (Évaluation/Test) :
* **Redimensionnement** : 'Resize(256)' + 'CenterCrop(224)'.
* **Conversion** : 'ToTensor()' pour passer en tenseurs PyTorch.
* **Normalisation** : 'Normalize' (Moyenne et Écart-type d'ImageNet).

#### 2. Augmentation de données (Train set) :
* **Rotation** : 'RandomRotation(5)' ajoutée aux étapes précédentes.
* **Photométrie** : Variation modérée de contraste et luminosité.
* **Géométrie** : Translation faible et zoom léger.

#### 3. Chargement PyTorch :
Chargement via un **dataset personnalisé** et un **DataLoader** :
* **Batch size** : 32.
* **Reproductibilité** : 'seed = 42'.
* **Optimisation** : 'pin_memory = True'.

![pipeline](../outputs/images/img3.jpg)

### 2.4 Exemple : prétraitement pour Train dataset

![train](../outputs/images/train_dataset.jpg)

---

## 3. Modèle 1 — Baseline CNN (Architecture)

### Conception
Le modèle "from scratch" est conçu pour extraire des caractéristiques hiérarchiques :
- **Extracteur de caractéristiques** : 3 blocs de convolution ($Conv + ReLU + MaxPool$) augmentant la profondeur (32, 64, 128 filtres).
- **Classificateur** : Une couche de mise à plat ('Flatten'), une couche dense de 128 neurones avec **Dropout (0.5)**, et une sortie **Sigmoid**.

![baseline_cnn](../outputs/images/baseline_cnn.jpg)

### Entraînement
- **Optimiseur** : Adam ($lr=10^{-3}$).
- **Fonction de cout** : BCEWithLogitsLoss (avec pos_weight si active).
- **Stratégie** : Utilisation de l'**Early Stopping** basé sur la perte de validation pour éviter le surapprentissage.

![img5](../outputs/images/img5.jpg)

---

## 4. Modèle 2 — ResNet18 (Transfer Learning)

### Approche
Utilisation d'une architecture **ResNet18 pré-entraînée** sur ImageNet.
- **Modification** : Remplacement de la couche entièrement connectée ('fc') par un bloc 'Linear(512, 1)'.
- **Fine-tuning** : Entraînement de l'ensemble du réseau avec un taux d'apprentissage réduit ($10^{-4}$) pour ajuster les poids aux spécificités des radiographies médicales.

---

## 5. Évaluation et comparaison

> Notebook : 'notebooks/03_evaluation_gradcam.ipynb'

### Métriques sur le set de validation (16 images)

| Métrique | Baseline CNN | ResNet18 |
|----------|:----------:|:------:|
| **Accuracy** | 76.4% | **87.0%** |
| **Precision** | 73.1% | **83.1%** |
| **Recall** | 98.5% | **99.5%** |
| **F1-score** | 83.9% | **90.6%** |
| **AUC-ROC** | 0.858 | **0.949** |

### Analyse

- **ResNet18 domine sur toutes les métriques**, grâce au transfer learning. Les features pré-apprises sur ImageNet (contours, textures, formes) sont transférables aux radiographies médicales.
- **Recall très élevé pour les deux modèles** (~98-99%) : quasi aucune pneumonie n'est manquée. C'est crucial en contexte médical — un faux négatif signifie une pneumonie non diagnostiquée.
- **Precision plus faible** : des images normales sont parfois classées pneumonie (faux positifs). Cela entraîne des examens complémentaires inutiles, mais c'est préférable à une pneumonie ratée.
- **AUC élevée du ResNet18** (0.949) : excellente capacité de discrimination indépendamment du seuil.

### Matrice de confusion

![Matrices de confusion](../outputs/figures/confusion_matrices.png)

### Courbe ROC

![Courbes ROC](../outputs/figures/roc_curves.png)

---

## 6. Interprétabilité — Grad-CAM

> Notebook : 'notebooks/03_evaluation_gradcam.ipynb'

### Principe
**Grad-CAM** (Gradient-weighted Class Activation Mapping) permet de visualiser quelles régions de l'image ont le plus influencé la décision du modèle :

1. Forward pass → logit de sortie
2. Backward pass → gradients sur les feature maps de la dernière couche conv
3. Moyenne pondérée des feature maps par les gradients
4. ReLU + normalisation → **heatmap** superposée à l'image

### Résultats

#### Baseline CNN
![Grad-CAM Baseline](../outputs/figures/gradcam_baseline_cnn.png)

#### ResNet18
![Grad-CAM ResNet18](../outputs/figures/gradcam_resnet18.png)

### Interprétation
- Le **ResNet18** focalise ses activations sur les **zones pulmonaires** de manière plus précise et cohérente.
- Le **Baseline CNN** a tendance à activer des zones plus larges et diffuses, parfois en dehors des poumons.
- Ces visualisations renforcent la confiance dans le modèle ResNet18 : il prend ses décisions pour les bonnes raisons.

---

## 7. Courbes d'entraînement

### BaselineCnn

![Courbes Baseline CNN](../outputs/figures/training_curves_baseline_cnn.png)

- train_loss : 0.2303 -> 0.0446 (forte baisse)
- train_acc : 0.9095 -> 0.9824 (forte hausse)
- val_loss : minimum ~0.4038 puis remontée (~0.7735 en fin de run).
- val\_acc : fluctue entre 0,5625 et 0,8125 (fin ~0,6875).
- Lecture technique : surapprentissage (overfitting) après les meilleures époques de validation.

### ResNet18

![Courbes ResNet18](../outputs/figures/training_curves_resnet18.png)

- train_loss : 0.1074 -> 0.0077 (forte baisse)
- train_acc : 0.9576 -> 0.9983 (forte hausse)
- val_loss : minimum ~0.0487 puis forte instabilité et remontée (jusqu’à ~1.0425 en fin de run).
- val_acc : fluctue entre 0.6250 et 1.0000 (fin ~0.6250).
- val_auc : 1.0000 sur toutes les époques (à interpréter avec prudence vu la taille très faible de la validation).
- Lecture technique : surapprentissage rapide après les meilleures époques de validation (best epoch = 3, early stopping à 9).

---

## 8. Limites et pistes d'amélioration

### Limites
1. **Set de validation minuscule** (16 images) : les métriques sont potentiellement instables et non représentatives.
2. **Pas de calibration des probabilités** : les scores de confiance du modèle ne sont pas calibrés.
3. **Source unique** : toutes les images proviennent d'un seul centre hospitalier → biais potentiel.
4. **Classe unique de pneumonie** : pas de distinction bactérienne vs virale.

### Pistes d'amélioration
1. **Augmenter le set de validation** avec un split stratifié plus équilibré
2. **Optimiser le seuil de décision** pour le compromis precision/recall souhaité
3. **Augmentation de données** plus agressive (elastic transform, cutout)
4. **Calibration** des probabilités (temperature scaling, Platt scaling)
5. **Ensemble** des deux modèles pour combiner leurs forces
6. **Validation croisée** (k-fold) pour des métriques plus robustes

---

## 9. Conclusion

Ce projet démontre l'efficacité du **deep learning** pour la classification de radiographies thoraciques :

- Un **CNN simple** atteint déjà un recall de 98%, prouvant que les patterns de pneumonie sont détectables automatiquement.
- Le **transfer learning** (ResNet18) améliore significativement toutes les métriques (+11 points d'accuracy, +7 points de precision).
- **Grad-CAM** confirme que le modèle se concentre sur les régions cliniquement pertinentes des poumons.
- Le système pourrait servir d'**outil d'aide au diagnostic**, en prioritisant les cas suspects pour un examen par un radiologue.

---

## Technologies utilisées

- **Python 3.10**
- **PyTorch** + torchvision — modèles et entraînement
- **scikit-learn** — métriques d'évaluation
- **matplotlib** — visualisations
- **pandas / numpy** — manipulation de données
- **Jupyter Notebook** — développement interactif
