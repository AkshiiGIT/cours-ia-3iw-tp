# 🤖 Assistant Support Client - Projet IA (ESGI 3IW)

Ce projet est une application web intégrant des fonctionnalités d'Intelligence Artificielle s'appuyant sur un modèle local via Ollama. Développé par Akasche MAHINTAN dans le cadre du module "Les Fondamentaux de l'IA" (ESGI), le backend est conçu en Python (FastAPI) et interagit avec un frontend moderne.

## 🚀 Fonctionnalités implémentées

Tout au long de ce projet, plusieurs routes API ont été développées pour répondre à différents cas d'usage concrets de l'IA générative :

*   **S09 - Résumé de tickets (Streaming SSE) :**
    *   **Route :** `POST /api/resumer`
    *   Reçoit un texte brut et un paramètre de ton (neutre ou direct).
    *   Génère un résumé en faisant appel au LLM local.
    *   Renvoie la réponse au fil de l'eau à l'utilisateur grâce au protocole Server-Sent Events (SSE).

*   **S10 - Assistant avec Appel d'Outil (Function Calling) :**
    *   **Route :** `POST /api/assistant`
    *   Permet au modèle d'interagir avec le code métier du serveur (boucle ReAct).
    *   Le modèle analyse la question de l'utilisateur, détermine s'il doit utiliser l'outil `chercher_commande`, et renvoie les arguments. 
    *   Le serveur valide les arguments, exécute la fonction, puis le modèle synthétise la réponse finale.

*   **S13 - Moteur de Recherche Sémantique (RAG) :**
    *   **Route :** `POST /api/documents`
    *   **Pipeline complet :** Découpage du corpus documentaire, vectorisation (Embeddings), et recherche par similarité cosinus.
    *   Le modèle répond à la question de l'utilisateur en se basant *strictement* sur les extraits pertinents trouvés, tout en citant ses sources.

## 🎨 Interface Utilisateur

Le frontend fourni initialement a bénéficié d'une refonte CSS complète pour adopter un design beaucoup plus professionnel et contemporain :
*   **Dark Mode & Glassmorphism :** Interface nocturne inspirée des outils SaaS modernes avec effets de transparence et de flou.
*   **UX Dynamique :** Animations de chargement au moment des requêtes, curseur IA clignotant, et boutons avec effets de survol.
*   **Composants enrichis :** Badges stylisés pour afficher les sources (RAG) et les métriques de consommation des tokens.

## 🛠️ Stack Technique

*   **Backend :** Python, FastAPI
*   **Modèle IA :** Ollama (LLM local type `qwen2.5:3b`, et modèle d'embeddings `paraphrase-multilingual`)
*   **Frontend :** HTML5, CSS3 (Custom Dark Theme), JavaScript Vanilla
*   **Protocoles :** API REST, Streaming SSE

## ⚙️ Installation & Lancement

### Prérequis
* Python 3 installé.
* Ollama installé et lancé en arrière-plan avec les modèles requis téléchargés (`ollama pull qwen2.5:3b` et `ollama pull paraphrase-multilingual`).

### Lancement
```bash
# Installer les dépendances (une seule fois)
make install

# Lancer le serveur de développement
make app

L'interface utilisateur est ensuite accessible sur http://localhost:3000.

✅ Tests & Conformité
Le projet inclut une suite de tests stricts (tests unitaires avec pytest) pour vérifier le respect des contrats d'API HTTP.

# Lancer l'intégralité de la suite de tests
make conformite
