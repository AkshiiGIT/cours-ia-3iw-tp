# Mesures du CC2 : prompt et choix du modèle

Mesuré le 13/11/2026 15:49 sur macOS 27.0.1, Apple M5, 24 Go de RAM, Ollama 0.34.1.
Jeu de test : les 20 tickets de `tp/05_prompt/cas.json`. Température 0, 80 tokens maximum.
Produit par `python3 tp/mesures_cc2.py` avec les instruments du cours (`evaluer.py`, `banc.py`).

## 1. Versions du prompt (séance 5), modèle qwen2.5:3b

| Version | JSON valide | Catégorie | Urgence | Exact (les deux) |
| --- | ---: | ---: | ---: | ---: |
| V1 · consigne fournie | 0 % | 0 % | 0 % | 0 % |
| V2 · format JSON imposé | 100 % | 85 % | 50 % | 35 % |
| V3 · + exemples de calibration | 100 % | 100 % | 75 % | 75 % |
| V4 · + règles d'urgence (finale) | 100 % | 95 % | 85 % | 80 % |
| V5 · V4 avec exemples hors jeu de test | 100 % | 90 % | 90 % | 80 % |

V1 est la consigne fournie par le cours. V2 à V4 ajoutent un à un les blocs de ma consigne finale (celle de `tp/05_prompt/evaluer.py`), pour mesurer ce que chaque bloc apporte.

**Limite repérée** : 5 exemples de la consigne finale sont des cas du jeu de test, recopiés. V3 et V4 sont donc optimistes. V5 garde les mêmes règles avec des exemples rédigés hors du jeu de test : c'est son score qui compte, et c'est elle que le banc utilise.

## 2. Banc d'essai (séance 11) : seul le modèle change

Consigne constante pour tous les modèles : V5 · V4 avec exemples hors jeu de test.

| Modèle | JSON valide | Exact | 1er fragment (médiane) | Débit (médiane) |
| --- | ---: | ---: | ---: | ---: |
| qwen2.5:3b | 100 % | 80 % | 71 ms | 45.7 tokens/s |
| qwen2.5:7b | 100 % | 65 % | 150 ms | 21.8 tokens/s |

Seuils : JSON valide ≥ 100 %, exacts ≥ 70 %. Le premier appel de chaque modèle (chargement en mémoire) n'est pas compté.

## 3. Justification du choix

Sur les 20 cas du cours, même consigne, température 0 : **qwen2.5:3b** classe juste 80 % des tickets (catégorie et urgence), avec 100 % de JSON valide.
qwen2.5:7b, plus gros, fait 65 % (79 ms plus lent au premier fragment, 21.8 tokens/s).
Je retiens donc qwen2.5:3b : le plus petit modèle qui passe mes seuils (JSON 100 %, exacts 70 %), avec un premier fragment en 71 ms et 45.7 tokens/s sur ma machine.

Dans AlterRADAR, le modèle conseillé dépend de la mémoire de l'ordinateur (3B dès 8 Go, 7B dès 16 Go) : ce banc est à relancer à chaque changement de modèle ou de consigne.
