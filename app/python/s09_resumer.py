"""Seance 9 : la route POST /api/resumer.

Objectif : resumer le message d'un client, en streaming, dans le ton demande.
Le contrat exact est dans app/CONTRAT.md, section "Route 1".

Vous remplissez les TODO 1 a 5 de ce fichier, et rien d'autre.
Tant qu'un TODO n'est pas ecrit, la route repond 501 "a ecrire".

Verifier :
    make app                     # terminal 1
    make conformite SEANCE=9     # terminal 2
"""
import time

from fastapi import APIRouter, Request
from fourni.modele import streamer
from fourni.transport import RequeteInvalide, fin, flux_ou_503, fragment, lire_corps

routeur = APIRouter()

TONS = {"neutre", "direct"}
LONGUEUR_MAX = 20_000


# =====================================================================
# TODO 1 : valider l'entree du client
# =====================================================================
def valider_resumer(corps):
    """Renvoie (texte, ton) ou leve RequeteInvalide."""
    texte = corps.get("texte")
    
    # Vérification de la présence, du type et de la longueur du texte
    if not isinstance(texte, str) or not texte.strip():
        raise RequeteInvalide("Le texte est absent, vide ou n'est pas une chaîne de caractères.")
    if len(texte) > LONGUEUR_MAX:
        raise RequeteInvalide(f"Le texte dépasse la limite autorisée de {LONGUEUR_MAX} caractères.")
    
    # Vérification du ton avec valeur par défaut
    ton = corps.get("ton", "neutre")
    if ton not in TONS:
        raise RequeteInvalide("Le ton est invalide. Attendu : 'neutre' ou 'direct'.")
        
    return texte, ton


# =====================================================================
# TODO 2 : assembler le prompt, cote serveur et nulle part ailleurs
# =====================================================================
def prompt_resumer(texte, ton):
    """Renvoie la liste de messages envoyee au modele."""
    # On sépare bien le contexte de la consigne (les données utilisateur à part)
    consigne_systeme = (
        "Tu es un assistant spécialisé dans le support client. "
        "Ton objectif est de résumer le message du client de manière claire et concise. "
        f"Le ton de ta réponse doit impérativement être : {ton}."
    )
    
    return [
        {"role": "system", "content": consigne_systeme},
        {"role": "user", "content": texte}
    ]


@routeur.post("/api/resumer")
async def resumer(requete: Request):
    debut = time.perf_counter()
    texte, ton = valider_resumer(await lire_corps(requete))
    messages = prompt_resumer(texte, ton)

    async def flux():
        usage = {}
        # =============================================================
        # TODO 3 et 4 : appeler le modele et relayer chaque fragment
        # =============================================================
        async for genre, valeur in streamer(messages):
            if genre == "delta":
                # On relaie le morceau de texte généré au format SSE
                yield fragment(valeur)
            elif genre == "usage":
                # On stocke l'utilisation des tokens pour la fin de la requête
                usage = valeur
                
        # =============================================================
        # TODO 5 : cloturer le flux avec l'evenement done et l'usage
        # =============================================================
        yield fin(usage, debut)

    return await flux_ou_503(flux())