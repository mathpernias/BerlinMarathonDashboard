# Projet de Visualisation du Marathon de Berlin

## Vue d'ensemble

Ce projet propose des visualisations interactives des données du Marathon de Berlin à l'aide de Dash et Plotly. Il permet d'explorer les performances des coureurs, les répartitions par sexe et nationalité, ainsi que les tendances sur plusieurs années. Les utilisateurs peuvent interagir avec les graphiques pour filtrer les données et obtenir des informations détaillées.

## Fonctionnalités

Thème sombre « Berlin nocturne » (Instrument Serif · Inter · JetBrains Mono), palette de couleurs validée pour le daltonisme, entièrement responsive.

- **Palmarès** : temps des vainqueurs hommes/femmes par édition, records du monde battus à Berlin et fiches des légendes.
- **Ma course** ✦ : saisissez votre temps et découvrez votre classement, votre percentile, votre allure, vos passages et votre position dans la distribution — filtrable par sexe, édition et catégorie d'âge.
- **Une édition** : explorateur année par année (finishers, part des femmes, médiane, météo, vainqueurs, distribution des arrivées).
- **Temps & météo** : évolution des temps moyens indexés sur 1999, par niveau, sexe ou âge, face à la température et aux précipitations.
- **Sexe & nations** : sélectionnez une plage de temps pour voir la répartition par sexe et les nationalités.
- **Top 10** : nationalités du Top 10 par édition ; cliquez sur un coureur pour afficher son parcours à Berlin.

## Installation

1. Clonez le dépôt :
   ```bash
   git clone <repository-url>
   ```
2. Accédez au répertoire du projet :
   ```bash
   cd code/src
   ```
3. Installez les dépendances Python nécessaires :
   ```bash
   pip install -r requirements.txt
   ```

## Utilisation

1. Assurez-vous que les fichiers de données nécessaires (`marathon_df`, `years`) sont disponibles dans le module `data`.
2. Depuis la racine du dépôt, lancez l'application Dash :
   ```bash
   python src/app.py
   ```
3. Ouvrez votre navigateur et accédez à `http://localhost:8050` pour interagir avec le tableau de bord.

## Structure des fichiers

- `app.py` : Contient la logique principale de l'application Dash.
- `server.py` : Configure et exécute le serveur Flask pour l'application.
- `visualizations_1.py`, `visualizations_2.py`, `visualizations_3.py` : Scripts pour générer les différentes visualisations.
- `preprocess.py` : Fonctions de prétraitement des données.
- `layout_vis3.py` : Configure la mise en page pour la visualisation 3.
- `data/` : Répertoire contenant les fichiers de données du marathon.

## Dépendances

- Python 3.8 ou supérieur
- Dash
- Plotly
- Pandas
- NumPy


## Licence

Ce projet est sous licence MIT. Consultez le fichier `LICENSE` pour plus de détails.

## Remerciements

- Données du marathon fournies par [bmw-berlin-marathon.com].
- Visualisations réalisées avec [Plotly](https://plotly.com/).
