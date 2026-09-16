"""Seance 10 : la route POST /api/assistant, avec appel d'outil."""
import json
import time

from fastapi import APIRouter, Request
from fourni.donnees import chercher_commande
from fourni.modele import appeler, streamer
from fourni.transport import RequeteInvalide, fin, flux_ou_503, fragment, lire_corps

routeur = APIRouter()

# =====================================================================
# TODO 6 : declarer l'outil au format attendu par le modele
# =====================================================================
OUTILS = [{
    "type": "function",
    "function": {
        "name": "chercher_commande",
        "description": "Retrouve le statut d'une commande à partir de son numéro.",
        "parameters": {
            "type": "object",
            "properties": {
                "numero": {
                    "type": "string",
                    "description": "Le numéro de la commande, ex: CMD-2024-118"
                }
            },
            "required": ["numero"],
        }
    }
}]

# =====================================================================
# TODO 7 : la table des outils executables
# =====================================================================
def executer_chercher_commande(args_json: str):
    try:
        args = json.loads(args_json)
        return chercher_commande(args.get("numero"))
    except Exception as e:
        return {"erreur": str(e)}

TABLE_DES_OUTILS = {
    "chercher_commande": executer_chercher_commande
}

@routeur.post("/api/assistant")
async def assistant(requete: Request):
    debut = time.perf_counter()
    corps = await lire_corps(requete)
    question = corps.get("question")
    
    if not isinstance(question, str) or not question.strip():
        raise RequeteInvalide("question invalide")

    async def flux():
        # =============================================================
        # TODO 8 : la boucle d'appel d'outil
        # =============================================================
        messages = [{"role": "user", "content": question}]
        
        # 1. Appel asynchrone restauré (le await est obligatoire ici)
        message_reponse, usage_total = await appeler(messages, outils=OUTILS)
        
        # Sécurité au cas où l'usage initial est vide
        if usage_total is None:
            usage_total = {"prompt_tokens": 0, "completion_tokens": 0}
        
        # 2. Vérifier s'il y a des appels d'outils
        appels = message_reponse.get("tool_calls")
        if appels:
            messages.append(message_reponse) # On ajoute la demande d'outil à l'historique
            
            for appel in appels:
                nom_outil = appel["function"]["name"]
                args_json = appel["function"]["arguments"]
                
                if nom_outil in TABLE_DES_OUTILS:
                    resultat = TABLE_DES_OUTILS[nom_outil](args_json)
                else:
                    resultat = {"erreur": "outil inconnu"}
                    
                messages.append({
                    "role": "tool",
                    "tool_call_id": appel["id"],
                    "content": json.dumps(resultat)
                })
        
        # 3. Streamer la réponse finale
        async for genre, valeur in streamer(messages):
            if genre == "delta":
                yield fragment(valeur)
            elif genre == "usage":
                # 4. Cumuler l'usage de façon sécurisée (évite les KeyError)
                usage_total["prompt_tokens"] = usage_total.get("prompt_tokens", 0) + valeur.get("prompt_tokens", 0)
                usage_total["completion_tokens"] = usage_total.get("completion_tokens", 0) + valeur.get("completion_tokens", 0)

        yield fin(usage_total, debut)

    return await flux_ou_503(flux())