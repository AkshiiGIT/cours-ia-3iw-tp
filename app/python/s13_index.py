"""Seance 13, premiere partie : l'index de recherche semantique.

Objectif : retrouver les extraits du corpus les plus proches d'une question,
SANS modele de generation. C'est la brique que la seance 12 enseigne.

Vous remplissez les TODO 9 a 11 de ce fichier, et rien d'autre.

Verifier la recherche seule, avant de brancher le modele :
    uv run python app/python/s13_index.py "comment demander un remboursement ?"
"""
from fourni.donnees import charger_documents
from fourni.modele import plonger


"""Seance 13, premiere partie : l'index de recherche semantique."""
from fourni.donnees import charger_documents
from fourni.modele import plonger

# =====================================================================
# TODO 9 : decouper un document en morceaux
# =====================================================================
def decouper(titre, texte):
    """Renvoie une liste de (titre_du_morceau, texte_du_morceau)."""
    morceaux = []
    # Découpage basique sur la structure (les titres Markdown ##)
    parties = texte.split("\n## ")
    for partie in parties:
        partie = partie.strip()
        if len(partie) > 50: # Écarter les petits morceaux sans sens
            morceaux.append((titre, partie))
    return morceaux

_MORCEAUX = None

def morceaux():
    """FOURNI : decoupe tout le corpus, une seule fois."""
    global _MORCEAUX
    if _MORCEAUX is None:
        _MORCEAUX = [m for titre, texte in charger_documents()
                     for m in decouper(titre, texte)]
    return _MORCEAUX

# =====================================================================
# TODO 10 : vectoriser les morceaux, une seule fois
# =====================================================================
_VECTEURS = None

async def indexer():
    """Renvoie la liste des vecteurs, dans le meme ordre que morceaux()."""
    global _VECTEURS
    if _VECTEURS is None:
        textes = [m[1] for m in morceaux()]
        _VECTEURS = await plonger(textes)
    return _VECTEURS

# =====================================================================
# TODO 11 : recherche par similarite cosinus
# =====================================================================
def similarite(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    norm_a = sum(x*x for x in a) ** 0.5
    norm_b = sum(x*x for x in b) ** 0.5
    return dot / (norm_a * norm_b)

def chercher(vecteur_question, vecteurs, k=3):
    """Renvoie les k morceaux les plus proches : [(titre, texte, score), ...]."""
    resultats = []
    for i, v in enumerate(vecteurs):
        score = similarite(vecteur_question, v)
        titre, texte = morceaux()[i]
        resultats.append((titre, texte, score))
        
    resultats.sort(key=lambda x: x[2], reverse=True)
    return resultats[:k]

if __name__ == "__main__":
    import asyncio
    import sys

    async def _essai(question):
        print(f"{len(morceaux())} morceaux")
        vecteurs = await indexer()
        vecteur_question = (await plonger([question]))[0]
        print("vectorises, voici les plus proches :\n")
        for titre, texte, score in chercher(vecteur_question, vecteurs):
            print(f"  {score:.3f}  {titre}")
            print(f"         {texte[:90].replace(chr(10), ' ')}...")

    asyncio.run(_essai(" ".join(sys.argv[1:]) or "comment demander un remboursement ?"))