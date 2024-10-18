# Image Ranker Project

Ce projet contient plusieurs scripts pour entraîner un modèle de classement d'images, faire des prédictions de classement, et classifier des images.

## Structure du Projet
- `src/image_Ranker_Training.py` : Script pour entraîner le modèle de classement d'images.
- `src/Predict_Rank.py` : Script pour prédire le classement des images.
- `src/ImageClassifier.py` : Script pour classifier des images en utilisant un modèle pré-entraîné.
- `data/` : Dossier où les données d'entraînement et de test doivent être placées.
- `results/` : Dossier où les résultats des modèles seront sauvegardés.

## Installation

Pour installer les dépendances, exécutez la commande suivante :

```sh
pip install -r requirements.txt
```

## Utilisation

- Pour entraîner le modèle de classement d'images :
  ```sh
  python src/image_Ranker_Training.py
  ```
- Pour prédire le classement des images :
  ```sh
  python src/Predict_Rank.py
  ```
- Pour classifier les images :
  ```sh
  python src/ImageClassifier.py
  ```

## Auteurs
- Alex
