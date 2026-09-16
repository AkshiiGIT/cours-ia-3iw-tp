#!/usr/bin/env python3
"""Atelier de la seance 5 : mesurer un prompt de classification.

Vous ne modifiez QUE la constante CONSIGNE. Tout le reste est l'instrument de
mesure : y toucher fausserait la comparaison.

    python3 tp/05_prompt/evaluer.py

Jumeau exact de evaluer.mjs : meme jeu de cas, meme score.
"""
import json
import os
import pathlib
import sys
import urllib.request

BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
MODELE = os.environ.get("MODEL_BASE", "qwen2.5:3b")
CAS = json.loads((pathlib.Path(__file__).parent / "cas.json").read_text(encoding="utf-8"))


# =====================================================================
# LA SEULE CHOSE QUE VOUS MODIFIEZ
# =====================================================================
CONSIGNE = """Analyse le texte et réponds UNIQUEMENT par un objet JSON {"categorie": "paiement|livraison|compte", "urgence": 1|2|3}. Ne dis rien d'autre.

Règles d'urgence strictes :
1 : Simple question, demande de document, changer une adresse email ou passer en adresse pro.
2 : Bug technique bloquant, page qui tourne dans le vide, paiement refusé, mot de passe/connexion HS, retard de colis de quelques jours (ex: 12 jours).
3 : Fuite de données (emails d'un autre), vol (colis ouvert/boîte vide), double débit, prélèvement malgré annulation, retard extrême (3 semaines), adresse de livraison totalement fausse.

Exemples de calibration :
"Comment changer l'adresse email de mon compte ?" => {"categorie": "compte", "urgence": 1}
"Je n'arrive plus a me connecter, le lien de reinitialisation ne marche pas." => {"categorie": "compte", "urgence": 2}
"Impossible de valider le paiement, la page tourne dans le vide." => {"categorie": "paiement", "urgence": 2}
"Mon paiement en trois fois a ete refuse alors que je remplis les conditions." => {"categorie": "paiement", "urgence": 2}
"Bonjour, je n'ai toujours pas recu mon colis commande il y a 12 jours." => {"categorie": "livraison", "urgence": 2}
"""
# =====================================================================
def classer(texte):
    charge = json.dumps({
        "model": MODELE,
        "temperature": 0,
        "max_tokens": 80,
        "messages": [{"role": "system", "content": CONSIGNE},
                     {"role": "user", "content": texte}],
    }).encode()
    requete = urllib.request.Request(
        f"{BASE}/v1/chat/completions", data=charge,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        brut = json.loads(reponse.read())["choices"][0]["message"]["content"]
    debut, fin = brut.find("{"), brut.rfind("}")
    if debut == -1 or fin == -1:
        return None
    try:
        return json.loads(brut[debut:fin + 1])
    except json.JSONDecodeError:
        return None


def main():
    total = len(CAS["cas"])
    formes, categories, urgences = 0, 0, 0
    print(f"modele : {MODELE}   cas : {total}\n")
    for i, cas in enumerate(CAS["cas"], 1):
        obtenu = classer(cas["texte"])
        if obtenu is None:
            print(f"  {i:2d}. JSON illisible          <- {cas['texte'][:44]}")
            continue
        formes += 1
        bonne_categorie = obtenu.get("categorie") == cas["categorie"]
        bonne_urgence = obtenu.get("urgence") == cas["urgence"]
        categories += bonne_categorie
        urgences += bonne_urgence
        marque = "ok " if bonne_categorie and bonne_urgence else "   "
        print(f"  {i:2d}. {marque} attendu {cas['categorie']}/{cas['urgence']}"
              f"  obtenu {obtenu.get('categorie')}/{obtenu.get('urgence')}")

    print(f"\n  JSON valide  : {formes}/{total}  ({100 * formes // total} %)")
    print(f"  Categorie    : {categories}/{total}  ({100 * categories // total} %)")
    print(f"  Urgence      : {urgences}/{total}  ({100 * urgences // total} %)")
    print("\nNotez ce score, modifiez CONSIGNE, relancez. Gardez la trace de "
          "chaque version : elle est demandee au CC2.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
