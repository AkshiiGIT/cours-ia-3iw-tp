# Les Fondamentaux de l'IA (ESGI 3IW) · rendu d'Akasche MAHINTAN

Ce dépôt contient deux travaux :

| Dossier | Quoi |
| --- | --- |
| `alterradar/` | **AlterRADAR**, mon projet présenté au CC2. Le prof a autorisé l'usage d'un projet existant. |
| `app/python/` | Mon TP du module en Python (FastAPI), routes S09 à S13 sur le jeu de données du cours. |

## AlterRADAR : le projet du CC2

Application de bureau (Electron, Node.js) qui cherche des alternances et des stages adaptés au CV,
prépare des candidatures avec une IA locale (Ollama, Qwen 2.5) et laisse l'étudiant valider chaque envoi.

- Dépôt d'origine : <https://github.com/AkshiiGIT/AlterRADAR>. Le dossier `alterradar/` en est une copie de la version **0.16.0**.
- Les trois fonctions du cours (résumer, assistant avec appel d'outil, RAG) sont dans `alterradar/lib/ia/`, utilisées par l'onglet **Assistant IA** et par un chatbot présent sur toutes les pages.
- La correspondance fichier par fichier avec les TODO du cours, l'architecture et les règles du contrat sont détaillées dans [alterradar/serveur-ia/README.md](alterradar/serveur-ia/README.md).

### Vérifier le contrat HTTP

Aucune installation npm n'est nécessaire pour la partie IA (Node 20 ou plus suffit).

```bash
ollama pull qwen2.5:3b
ollama pull paraphrase-multilingual

node alterradar/serveur-ia/serveur.cjs      # terminal 1 : le serveur du contrat, port 3000
make conformite                              # terminal 2 : la suite du cours
```

Résultat : **34 tests sur 35**, mode dégradé compris (Ollama éteint, puis `MODELE_INJOIGNABLE=1 make conformite`).
Le test restant (`test_l_outil_est_reellement_appele`) demande où en est la commande `CMD-2024-118` du
jeu de données du cours. Les outils d'AlterRADAR cherchent dans des **candidatures** (`chercher_candidature`,
`bilan_candidatures`), pas dans des commandes : ce test est propre au domaine du TP, que couvre `app/python/`.

### Lancer l'application

Le plus simple : télécharger l'installateur Windows ou macOS sur la page
[Releases](https://github.com/AkshiiGIT/AlterRADAR/releases/latest). Depuis les sources (Node 24) :

```bash
cd alterradar
npm install
npm start          # l'application
npm test           # ses 219 tests
```

Au premier lancement, un guide pas à pas installe Ollama, choisit le modèle adapté à la mémoire de
l'ordinateur et importe le CV.

## TP Python (séances 9 à 13)

Backend FastAPI qui s'appuie sur un modèle local via Ollama, sur le jeu de données du cours (support client).

- **S09, résumé de tickets en streaming SSE** (`POST /api/resumer`) : reçoit un texte et un ton (neutre ou direct), renvoie le résumé au fil de l'eau.
- **S10, assistant avec appel d'outil** (`POST /api/assistant`) : le modèle décide d'appeler l'outil `chercher_commande`, le serveur valide les arguments, exécute la fonction, puis le modèle rédige la réponse finale.
- **S13, recherche sémantique (RAG)** (`POST /api/documents`) : découpage du corpus, embeddings, similarité cosinus. Le modèle répond à partir des extraits trouvés et cite ses sources.

Stack : Python, FastAPI, Ollama (`qwen2.5:3b` et `paraphrase-multilingual`), le front fourni par le cours.

```bash
make install       # dépendances, une seule fois
make app           # serveur sur http://localhost:3000
make conformite    # suite de tests du contrat, dans un second terminal
```
