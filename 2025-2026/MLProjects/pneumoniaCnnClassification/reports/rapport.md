# Rapport - Classification d'images medicales : Detection de pneumonie

**Projet B3 - Deep Learning / ECE Paris**

Collaborateurs : Yildiz Julien, Minh Khang Thai, Naira Awadin, Mahdi Bennamane

---

## 1. Objectif du projet

Construire un pipeline complet de classification binaire (**NORMAL** vs **PNEUMONIA**) sur radiographies thoraciques, en comparant :
- un **Baseline CNN** entraine from scratch,
- un **ResNet18** en transfer learning,
- avec analyse des performances et interpretabilite via **Grad-CAM**.

---

## 2. Synthese du Notebook 01 - EDA et preparation des donnees

## Workflow
1. Initialisation et configuration
2. Indexation des donnees
3. Analyse de la distribution
4. Analyse des caracteristiques image
5. Verification anti-data leakage (niveau fichier)
6. Export des artefacts EDA
7. Conclusion

### 2.1 Structure du dataset
- Total : **5 856 images**
- Train : **5 216** (**89,07 %**)
- Validation : **16** (**0,27 %**)
- Test : **624** (**10,66 %**)

### 2.2 Qualite et variabilite des donnees
- **Aucun fichier corrompu** detecte.
- Images heterogenes (resolutions variables), majoritairement en niveaux de gris.
- Pretraitement standardise justifie : resize/crop/normalisation.

### 2.3 Desequilibre de classes
- Train : **PNEUMONIA 74,29 % (3875)** vs **NORMAL 25,71 % (1341)**
- Validation : **8/8** (50/50, mais tres petit echantillon)
- Test : **PNEUMONIA 62,5 % (390)** vs **NORMAL 37,5 % (234)**

### 2.4 Verification anti-leakage (ajoutee)
- Verification d'absence de doublons de noms de fichiers entre `train/val/test`.
- Resultat : `len(filenames) == len(set(filenames))` -> **True**.
- Limite : ce controle est fait au niveau *fichier*, pas au niveau *patient*.

### 2.5 Conclusion EDA
Le dataset est exploitable pour la modelisation, avec trois points de vigilance majeurs :
- fort desequilibre de classes,
- validation extremement petite,
- controle leakage a renforcer idealement par identifiant patient.

---

## 3. Synthese du Notebook 02 - Entrainement du Baseline CNN

## Workflow
1. Indexer les donnees
2. Transformer les images (pretraitement + augmentation)
3. Charger via Dataset/DataLoader
4. Definir le modele
5. Entrainer
6. Valider
7. Sauvegarder le meilleur checkpoint

### 3.1 Pipeline de pretraitement
- Evaluation/Test : `Resize(256)` + `CenterCrop(224)` + `ToTensor()` + `Normalize(ImageNet)`
- Train : transformations ci-dessus + augmentations legeres (rotation, contraste/luminosite, translation/zoom)
- Batch size : **32**, seed : **42**, `pin_memory=True`

### 3.2 Architecture Baseline CNN
- 3 blocs convolution (`Conv + ReLU + MaxPool`) : 32 -> 64 -> 128 filtres
- Classifieur : `Flatten -> Linear(128) -> ReLU -> Dropout(0.5) -> Linear(1)`
- **Important** : la sortie est un **logit** (pas de Sigmoid dans le reseau), compatible avec `BCEWithLogitsLoss`.

### 3.3 Resultats finaux Baseline CNN (jeu de test, n=624)
- Accuracy : **0.7644**
- Precision : **0.7314**
- Recall : **0.9846**
- F1-score : **0.8393**
- AUC-ROC : **0.8576**

### 3.4 Matrice de confusion Baseline (test)
- **TP = 384**
- **TN = 93**
- **FP = 141**
- **FN = 6**

Lecture clinique :
- FN tres faibles (bon point pour le depistage),
- FP eleves (sur-triage, examens complementaires inutiles).

### 3.5 Courbes d'entrainement (Baseline)
- `train_loss` : **0.2303 -> 0.0446**
- `train_acc` : **0.9095 -> 0.9824**
- `val_loss` : minimum ~**0.4038** puis remontee
- `val_acc` : fluctue ~**0.56 a 0.81**

Interpretation : **surapprentissage** apres les meilleures epoques de validation.

### 3.6 Analyse d'erreurs (Baseline)
Causes probables des erreurs :
- seuil de decision fixe (0.5) pas toujours optimal,
- variabilite de radios normales pouvant imiter des patterns pathologiques,
- capacite limitee du modele baseline,
- sensibilite a des artefacts (contraste, cadrage, annotations).

---

## 4. Synthese du Notebook 03 - Evaluation comparative et Grad-CAM

## Workflow
1. Charger Baseline CNN et ResNet18
2. Evaluer (Accuracy, Precision, Recall, F1, AUC)
3. Visualiser la matrice de confusion
4. Interpreter avec Grad-CAM
5. Comparer les deux modeles

### 4.1 Comparaison principale (metriques test depuis checkpoints)

| Metrique | Baseline CNN | ResNet18 |
|---|---:|---:|
| Accuracy | 76.44 % | **87.02 %** |
| Precision | 73.14 % | **83.08 %** |
| Recall | 98.46 % | **99.49 %** |
| F1-score | 83.93 % | **90.55 %** |
| AUC-ROC | 0.8576 | **0.9485** |

Conclusion : **ResNet18 surpasse le baseline sur toutes les metriques**.

### 4.2 Evaluation sur le set de validation (n=16)

Avec seuil 0.5 :
- Baseline : Accuracy **0.6875**, Precision **0.6364**, Recall **0.8750**, F1 **0.7368**, AUC **0.8281**
- ResNet18 : metriques **1.0000** sur ce set

Attention : ces resultats validation sont **tres instables** car n=16 seulement.

### 4.3 Seuil de decision optimal (validation)
- **Baseline CNN** : seuil optimal (F1 max et Youden J max) a **t = 0.8233**
- Intervalle de seuils F1 max : **[0.8233 ; 0.9068]**
- Effet observe a `t=0.8233` vs `t=0.5` :
  - F1 : **0.8235** vs 0.7368
  - Precision : **0.7778** vs 0.6364
  - Specificite : **0.75** vs 0.50
  - Recall : **inchange a 0.8750**

Pourquoi ce seuil est pertinent : reduction des faux positifs sans perte de sensibilite (sur cette validation).

- **ResNet18** : separation parfaite sur validation, F1 max sur une large plage `0.6589-0.9867`.
- Choix pratique actuel : conserver `0.5` pour ResNet18, en attendant une validation plus large.

### 4.4 Interpretabilite (Grad-CAM)
- Le ResNet18 focalise globalement mieux les activations sur les zones pulmonaires.
- Le baseline montre des activations plus diffuses.
- Message methodologique : Grad-CAM aide a analyser le comportement du modele, mais **ne constitue pas une preuve clinique**.

---

## 5. Limites globales

1. Validation trop petite (16 images) -> variabilite forte des metriques et du seuil optimal.
2. Desequilibre de classes important.
3. Controle leakage uniquement au niveau nom de fichier (pas niveau patient).
4. Probabilites non calibrees.
5. Dataset possiblement biaise (source et protocole d'acquisition).

---

## 6. Pistes d'amelioration

1. Renforcer la validation (split stratifie plus robuste ou validation croisee).
2. Ajuster le seuil selon l'objectif clinique (sensibilite vs specificite).
3. Etendre les augmentations de donnees (tout en restant medicalement plausibles).
4. Ajouter calibration des probabilites (temperature scaling / Platt).
5. Tester d'autres backbones (DenseNet, EfficientNet) et/ou un ensemble de modeles.
6. Ajouter une evaluation patient-level et, si possible, multi-centres.

---

## 7. Conclusion generale

Le pipeline est fonctionnel de bout en bout :
- preparation des donnees,
- entrainement baseline et transfer learning,
- evaluation quantitative,
- interpretabilite par Grad-CAM.

Le **ResNet18** est actuellement le meilleur compromis et ameliore nettement la performance globale tout en conservant une sensibilite tres elevee, ce qui est pertinent pour un contexte de depistage.

Le principal verrou restant est la **fiabilite statistique** de la validation (n=16). Avant un usage plus avance, il faut renforcer la strategie de validation et la calibration du systeme.
