# Installer son environnement

À faire **avant la séance 1**, chez vous, sur votre connexion personnelle.
Le réseau de l'école ne supportera pas trente téléchargements simultanés.

Tout le module tourne sur votre machine. Vous n'avez besoin d'aucun compte,
d'aucune clé d'API et d'aucun moyen de paiement.

## 1. Ce qu'il faut installer

| Outil | Pourquoi | Où |
| --- | --- | --- |
| Ollama | télécharge et sert les modèles en local, via HTTP | [ollama.com](https://ollama.com) |
| Git | récupérer les squelettes de TP et rendre le projet | [git-scm.com](https://git-scm.com) |
| Node 20+ **ou** Python 3.11+ | pour écrire vos routes, au choix | [nodejs.org](https://nodejs.org) ou [python.org](https://python.org) |

### Choisir sa voie

Le cours est bilingue. Les démonstrations et les corrigés sont en Python, mais
**vous rendez dans la langue que vous voulez** : ce qui est évalué est le
contrat HTTP, pas votre code. Voir [app/CONTRAT.md](../app/CONTRAT.md).

- **Voie JavaScript** : Node 20 ou plus. C'est la voie naturelle pour vous, et
  le squelette Express est fourni.
- **Voie Python** : Python 3.11 ou plus. C'est la voie de l'enseignant, donc
  celle où vous obtiendrez de l'aide le plus vite.

Installez au moins l'une des deux, et vérifiez :

```bash
node --version     # v20.x ou plus
python3 --version  # 3.11 ou plus
```

Node 18 ne suffit pas : les squelettes utilisent `fetch`, les flux et
`AbortSignal.timeout`. Attention sous macOS : le `python3` fourni par le système
est souvent en 3.9, trop ancien.

## 2. Installer Ollama

**macOS et Linux**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows** : téléchargez l'installeur `.exe` sur [ollama.com/download](https://ollama.com/download).
Ollama démarre ensuite tout seul au lancement de la session.

Vérification :

```bash
ollama --version
ollama list       # une liste vide au premier lancement, c'est normal
```

## 3. Télécharger le socle de la classe

Deux modèles, environ **2,2 Go** au total. Ce socle est le même pour tout le
monde : les corrigés, les TP et le barème sont calibrés dessus.

```bash
ollama pull qwen2.5:3b               # generation, ~1,9 Go
ollama pull paraphrase-multilingual  # embeddings, ~562 Mo
```

Pourquoi ces deux-là :

- **qwen2.5:3b** tient sur une machine modeste, répond correctement en français,
  sait produire du JSON valide et gère l'appel d'outils (séance 10).
- **paraphrase-multilingual** est petit, tourne partout, et surtout il est
  **multilingue**. Il sert au bloc RAG des séances 12 et 13.

> **Pourquoi pas `nomic-embed-text`**, que vous verrez recommandé partout ?
> Parce qu'il est entraîné sur de l'anglais. Mesuré sur huit paires de phrases
> françaises courtes tirées du corpus du cours, il donne un écart **négatif**
> entre les paires proches et les paires éloignées, et inverse trois paires sur
> quatre : il rapproche en moyenne ce qui n'a rien à voir. Sur un corpus
> français, il est inutilisable. C'est une bonne illustration de la séance 3 :
> un modèle bien classé sur les palmarès publics peut échouer complètement sur
> votre cas précis.

Premier essai, hors ligne :

```bash
ollama run qwen2.5:3b "Bonjour, tu tournes bien en local ?"
```

## 4. Quel modèle pour quelle machine

Regardez la RAM de votre machine, pas sa marque.

| RAM | Modèle de travail | Taille | Ce que ça donne |
| --- | --- | --- | --- |
| 8 Go | `llama3.2:1b` | 1,3 Go | ça tourne, qualité juste, suffisant pour suivre |
| 8 à 16 Go | `qwen2.5:3b` | 1,9 Go | **le socle du cours**, le bon compromis |
| 16 Go et plus | `qwen2.5:7b` | 4,7 Go | meilleures réponses, nettement plus lent |
| Machine trop juste | serveur de classe | 0 | identique, servi par le poste enseignant |

Une carte graphique dédiée accélère beaucoup les choses, mais n'est pas
nécessaire. Les Mac à puce Apple sont à l'aise, y compris en 8 Go.

Si vous prenez un modèle qui ne tient pas en mémoire, il ne plante pas : il
bascule sur le disque et devient dix fois plus lent. C'est le symptôme à
reconnaître.

## 5. Vérifier que tout est en place

Depuis la racine du dépôt, dans la langue de votre choix. Les deux scripts sont
strictement équivalents : même sortie, mêmes verdicts. C'est la première
illustration du principe du module, un contrat unique et deux implémentations.

```bash
node tp/00_setup/check.mjs     # voie JavaScript
python3 tp/00_setup/check.py   # voie Python
```

Le script contrôle votre version de Node, la présence du serveur Ollama, les
deux modèles du socle, puis mesure le débit de votre machine en tokens par
seconde et teste l'API compatible OpenAI et les embeddings.

**Notez le débit affiché.** Il vous servira en séance 6, quand nous comparerons
le coût d'un modèle local et celui d'un modèle cloud.

Pour viser le serveur de classe plutôt que votre machine :

```bash
OLLAMA_BASE_URL=http://<ip-enseignant>:11434 node tp/00_setup/check.mjs
OLLAMA_BASE_URL=http://<ip-enseignant>:11434 python3 tp/00_setup/check.py
```

## 6. LM Studio, si vous préférez une interface graphique

[LM Studio](https://lmstudio.ai) fait la même chose qu'Ollama avec une fenêtre :
catalogue de modèles, chat intégré, et un serveur local compatible OpenAI sur le
port 1234.

C'est une alternative acceptable pour explorer, mais les consignes de TP sont
écrites pour Ollama. Si vous utilisez LM Studio, pensez à démarrer son serveur
local et à adapter `OLLAMA_BASE_URL` en conséquence.

## 7. Le serveur de classe

Si votre machine ne suit pas, le poste enseignant sert un modèle plus gros sur
le réseau de la salle. Vous ne changez **qu'une variable d'environnement** :

```bash
# .env.local
OLLAMA_BASE_URL=http://<ip-enseignant>:11434
```

Votre code reste rigoureusement identique. C'est d'ailleurs la démonstration en
acte de ce que nous verrons en séance 7 : le modèle est un service HTTP, et
l'endroit où il tourne ne regarde pas votre application.

## 8. Quand ça ne marche pas

| Symptôme | Cause probable | Ce qu'il faut faire |
| --- | --- | --- |
| `connection refused` sur le port 11434 | le serveur n'est pas lancé | `ollama serve` dans un terminal à part |
| `model not found` | le modèle n'a pas été téléchargé | `ollama pull qwen2.5:3b` |
| Réponse en plus de 30 secondes | le modèle ne tient pas en RAM | prenez `llama3.2:1b`, ou le serveur de classe |
| Débit sous 8 tokens/s | machine trop juste | même réponse que ci-dessus |
| Le ventilateur s'emballe | c'est normal | branchez le secteur, l'inférence consomme |
| `This server does not support embeddings` | vous demandez un vecteur à un modèle de génération | `ollama pull paraphrase-multilingual`, et vérifiez `MODEL_EMBED` |
| La recherche sémantique remonte n'importe quoi | modèle d'embedding anglophone | utilisez bien `paraphrase-multilingual`, pas `nomic-embed-text` |
| `fetch is not defined` | Node trop ancien | installez Node 20 ou plus |
| `Python 3.9` signalé en échec | le Python du système est ancien | installez Python 3.11+, ou passez par la voie Node |
| Le serveur de classe ne répond pas | pare-feu ou mauvaise IP | vérifiez l'IP au tableau, testez `curl http://<ip>:11434/api/tags` |

## 9. Faire de la place

Les modèles s'accumulent vite. Pour voir ce qui occupe votre disque et faire
le ménage :

```bash
ollama list              # taille de chaque modele
ollama rm <nom-du-modele>
```

Si la qualité de la recherche sémantique ne vous suffit pas et que votre machine
le permet, `bge-m3` est l'autre modèle d'embedding multilingue courant, plus
lourd (environ 1,2 Go).

Les poids sont stockés dans `~/.ollama/models` sous macOS et Linux, et dans
`%USERPROFILE%\.ollama\models` sous Windows.
