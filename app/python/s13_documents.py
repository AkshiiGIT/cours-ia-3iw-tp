"""Seance 13, seconde partie : la route POST /api/documents.

Objectif : repondre a partir du corpus en citant les sources, et refuser
quand le corpus ne contient pas la reponse.
Le contrat exact est dans app/CONTRAT.md, section "Route 3".

Prerequis : les TODO 9 a 11 de s13_index.py.
Vous remplissez le TODO 12 de ce fichier, et rien d'autre.

Verifier :
    make app                      # terminal 1
    make conformite SEANCE=13     # terminal 2
"""
"""Seance 13, seconde partie : la route POST /api/documents."""
import time
import s13_index

from fastapi import APIRouter, Request
from fourni.modele import plonger, streamer
from fourni.transport import RequeteInvalide, fin, flux_ou_503, fragment, lire_corps, sse

routeur = APIRouter()

@routeur.post("/api/documents")
async def documents(requete: Request):
    debut = time.perf_counter()
    corps = await lire_corps(requete)
    question = corps.get("question")
    
    if not isinstance(question, str) or not question.strip():
        raise RequeteInvalide("question invalide")

    async def flux():
        # =============================================================
        # TODO 12 : le pipeline RAG
        # =============================================================
        # 1 et 2. Indexer et vectoriser la question
        vecteurs = await s13_index.indexer()
        vecteurs_question = await plonger([question])
        vecteur_question = vecteurs_question[0]
        
        # 3. Chercher les extraits les plus proches
        resultats = s13_index.chercher(vecteur_question, vecteurs, k=3)
        
        # 4. Émettre les sources en SSE avant la réponse du modèle
        sources_json = [{"titre": r[0], "score": r[2]} for r in resultats]
        yield sse({"sources": sources_json})
        
        # 5. Préparer le contexte et brider le modèle
        textes_extraits = "\n\n".join([f"Source: {r[0]}\n{r[1]}" for r in resultats])
        
        consigne = (
            "Tu dois répondre à la question de l'utilisateur en utilisant UNIQUEMENT les extraits suivants. "
            "Si la réponse ne se trouve pas dans les extraits, refuse de répondre en disant que tu n'as pas l'information.\n\n"
            f"Extraits:\n{textes_extraits}"
        )
        
        messages = [
            {"role": "system", "content": consigne},
            {"role": "user", "content": question}
        ]
        
        # 6. Streamer la réponse
        usage = {}
        async for genre, valeur in streamer(messages):
            if genre == "delta":
                yield fragment(valeur)
            elif genre == "usage":
                usage = valeur
                
        yield fin(usage, debut)

    return await flux_ou_503(flux())