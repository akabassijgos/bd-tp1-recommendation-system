# Plan du rapport (README.md)

## 1. Introduction

* Contexte du projet
* Objectif du TP
* Problématique : recommandation personnalisée
* Présentation générale de la solution

---

## 2. Présentation du système de recommandation

### 2.1 Type de recommandation

* Filtrage collaboratif
* Approche **item-item**
* Principe général

### 2.2 Fonctionnement global

* Données d’entrée (ratings)
* Calcul des similarités
* Génération des recommandations

---

## 3. Jeu de données

### 3.1 Source des données

* MovieLens (latest-small)

### 3.2 Description

* Nombre d’utilisateurs
* Nombre de films
* Nombre de ratings

### 3.3 Prétraitement

* Nettoyage des titres (suppression des années)
* Gestion des genres
* Jointure avec TMDB (affiches + métadonnées)

---

## 4. Architecture du projet

### 4.1 Organisation des fichiers

```bash
app/
│
├── app.py
├── pages/
├── recommender.py
├── auth.py
├── ratings.py
├── tmdb.py
├── scripts/
└── app.db
```

### 4.2 Description des modules

* Authentification
* Recommandation
* Interface utilisateur
* Base de données

---

## 5. Base de données

### 5.1 Choix de SQLite

* Simplicité
* Portabilité

### 5.2 Schéma des tables

* users
* movies
* ratings

### 5.3 Particularités techniques

* Offset des user_id (>1000)
* Index pour optimisation
* Gestion des ratings unifiée

---

## 6. Implémentation du moteur de recommandation

### 6.1 Construction de la matrice utilisateur-item

* Sparse matrix

### 6.2 Calcul de similarité

* Cosine similarity

### 6.3 Génération des recommandations

* Top-N items
* Exclusion des films déjà vus

### 6.4 Gestion des cas particuliers

* Cold start (fallback popularité)

---

## 7. Fonctionnalités de l’application

### 7.1 Authentification

* Inscription
* Connexion
* Sécurité (hash mot de passe)

### 7.2 Navigation

* Navbar personnalisée
* Redirection automatique

### 7.3 Recherche et filtres

* Recherche par titre
* Filtre par genre
* Pagination ("Charger plus")

### 7.4 Système de notation

* Slider 0.5 → 5
* Mise à jour dynamique
* Impact sur recommandations

### 7.5 Profil utilisateur

* Informations personnelles
* Photo de profil
* Suppression des notes
* Taste profile

### 7.6 Détails des films

* Modal (via streamlit-modal)
* Synopsis
* Bande-annonce (TMDB)

---

## 8. Interface utilisateur (UI/UX)

### 8.1 Design choisi

* Inspiration Netflix

### 8.2 Composants clés

* Cards films
* Grille responsive
* Navbar

### 8.3 Expérience utilisateur

* Feedback visuel
* Navigation fluide
* Chargement progressif

---

## 9. Optimisations techniques

* Caching (Streamlit)
* Index SQL
* Pagination
* Gestion des rerun Streamlit

---

## 10. Limites du projet

* Dataset limité (MovieLens small)
* Pas de deep learning
* Sécurité simplifiée
* UI limitée par Streamlit

---

## 11. Améliorations possibles

* Hybrid recommender (content + collaborative)
* Déploiement (Streamlit Cloud)
* Meilleur design (React / frontend dédié)
* Recommandations temps réel

---

## 12. Conclusion

* Bilan du projet
* Apports pédagogiques
* Difficultés rencontrées
* Résultats obtenus

---

## 13. Installation et utilisation

### 13.1 Prérequis

```bash
python 3.x
pip install -r requirements.txt
```

### 13.2 Lancer l’application

```bash
streamlit run app/app.py
```

---

## 14. Auteur

* Nom
* Formation
* Encadrant (prof)
