#!/usr/bin/env python3
"""Mesures demandées au CC2, en une seule commande (environ 5 minutes, Ollama lancé) :

  1. la trace des versions du prompt (séance 5), mesurée sur les 20 cas du cours ;
  2. le banc d'essai (séance 11) : même consigne, seul le modèle change ;
  3. la justification du choix de modèle, rédigée à partir de ces chiffres.

    python3 tp/mesures_cc2.py
    python3 tp/mesures_cc2.py qwen2.5:14b      # ajoute un modèle installé au banc

Écrit tp/RESULTATS_CC2.md. Chaque chiffre vient d'un appel réel au modèle : rien n'est estimé.
Les instruments de mesure sont ceux du cours (tp/05_prompt/evaluer.py et tp/11_banc/banc.py),
importés tels quels.
"""
import datetime
import importlib.util
import json
import os
import pathlib
import platform
import subprocess
import sys
import time
import unicodedata
import urllib.request

ICI = pathlib.Path(__file__).resolve().parent
BASE = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
MODELE_PROMPT = os.environ.get("MODEL_BASE", "qwen2.5:3b")
# Testés s'ils sont installés, du plus petit au plus gros.
CANDIDATS = ["llama3.2:1b", "qwen2.5:1.5b", "qwen2.5:3b", "qwen2.5:7b", "qwen2.5:14b"]
# Mes seuils : on retient le plus petit modèle qui passe les deux.
SEUIL_JSON = 100   # % de réponses au format JSON lisible
SEUIL_EXACT = 70   # % de cas où catégorie ET urgence sont justes
SORTIE = ICI / "RESULTATS_CC2.md"
# Exemples de calibration rédigés hors du jeu de test : mêmes catégories et urgences que ceux de la
# consigne finale, mais aucune phrase reprise de cas.json. Utilisés quand la consigne finale en recopie.
EXEMPLES_DISTINCTS = """Exemples de calibration :
"Où puis-je modifier le numéro de téléphone de mon profil ?" => {"categorie": "compte", "urgence": 1}
"Mon compte est bloqué après trois tentatives de connexion." => {"categorie": "compte", "urgence": 2}
"Le bouton Payer ne réagit pas, je ne peux pas finaliser ma commande." => {"categorie": "paiement", "urgence": 2}
"Ma carte est refusée à chaque tentative alors qu'elle fonctionne ailleurs." => {"categorie": "paiement", "urgence": 2}
"Mon colis devait arriver il y a une semaine et le suivi ne bouge plus." => {"categorie": "livraison", "urgence": 2}"""


def charger(nom, chemin):
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


evaluer = charger("evaluer", ICI / "05_prompt" / "evaluer.py")
banc = charger("banc", ICI / "11_banc" / "banc.py")
CAS = evaluer.CAS["cas"]


def get_json(chemin):
    with urllib.request.urlopen(f"{BASE}{chemin}", timeout=10) as reponse:
        return json.loads(reponse.read())


def machine():
    infos = {"systeme": f"{platform.system()} {platform.release()}", "processeur": platform.machine(), "ram": "?"}
    if platform.system() == "Darwin":
        def sysctl(cle):
            return subprocess.run(["sysctl", "-n", cle], capture_output=True, text=True).stdout.strip()
        version = subprocess.run(["sw_vers", "-productVersion"], capture_output=True, text=True).stdout.strip()
        infos["systeme"] = f"macOS {version}"
        infos["processeur"] = sysctl("machdep.cpu.brand_string") or platform.machine()
        octets = sysctl("hw.memsize")
        if octets.isdigit():
            infos["ram"] = f"{int(octets) / 1024 ** 3:.0f} Go"
    return infos


# ----- 1. Versions du prompt -------------------------------------------------------------

def versions_du_prompt(finale):
    """V1 est la consigne fournie par le cours ; V2 à V4 ajoutent, dans l'ordre, les blocs
    de la consigne finale (celle de evaluer.py). V4 est la consigne finale, mot pour mot."""
    fournie = "Classe le ticket de support."
    i_regles, i_exemples = finale.find("Règles d'urgence"), finale.find("Exemples de calibration")
    if i_regles == -1 or i_exemples == -1 or not i_regles < i_exemples:
        return [("V1 · consigne fournie", fournie), ("V2 · consigne finale", finale)]
    format_ = finale[:i_regles].strip()
    regles = finale[i_regles:i_exemples].strip()
    exemples = finale[i_exemples:].strip()
    versions = [
        ("V1 · consigne fournie", fournie),
        ("V2 · format JSON imposé", format_),
        ("V3 · + exemples de calibration", f"{format_}\n\n{exemples}"),
        ("V4 · + règles d'urgence (finale)", finale),
    ]
    if fuite(finale):
        versions.append(("V5 · V4 avec exemples hors jeu de test", f"{format_}\n\n{regles}\n\n{EXEMPLES_DISTINCTS}"))
    return versions


def mesurer_consigne(consigne):
    evaluer.CONSIGNE, evaluer.MODELE = consigne, MODELE_PROMPT
    formes = categories = urgences = exacts = 0
    depart = time.perf_counter()
    for i, cas in enumerate(CAS, 1):
        print(f"    cas {i}/{len(CAS)}", end="\r", flush=True)
        try:
            obtenu = evaluer.classer(cas["texte"])
        except Exception as erreur:
            print(f"    cas {i} : échec ({erreur})")
            continue
        if obtenu is None:
            continue
        formes += 1
        c = obtenu.get("categorie") == cas["categorie"]
        u = obtenu.get("urgence") == cas["urgence"]
        categories += c
        urgences += u
        exacts += c and u
    n = len(CAS)
    return {"json": 100 * formes // n, "categorie": 100 * categories // n, "urgence": 100 * urgences // n,
            "exact": 100 * exacts // n, "duree": time.perf_counter() - depart}


def normaliser(texte):
    texte = unicodedata.normalize("NFD", texte.lower())
    return "".join(ch for ch in texte if ch.isalnum())


def fuite(consigne):
    """Cas du jeu de test recopiés tels quels dans les exemples de la consigne."""
    corps = normaliser(consigne)
    return [cas["texte"] for cas in CAS if normaliser(cas["texte"]) in corps]


# ----- 2. Banc d'essai -----------------------------------------------------------------

def installes():
    return {m["name"] for m in get_json("/api/tags").get("models", [])}


def choisir(resultats):
    passent = [r for r in resultats if r["json"] >= SEUIL_JSON and r["exact"] >= SEUIL_EXACT]
    return (passent[0], True) if passent else (max(resultats, key=lambda r: (r["exact"], r["json"])), False)


def justification(resultats, choisi, passe):
    lignes = []
    lignes.append(f"Sur les {len(CAS)} cas du cours, même consigne, température 0 : **{choisi['modele']}** "
                  f"classe juste {choisi['exact']} % des tickets (catégorie et urgence), avec {choisi['json']} % de JSON valide.")
    plus_petits = [r for r in resultats if resultats.index(r) < resultats.index(choisi)]
    plus_gros = [r for r in resultats if resultats.index(r) > resultats.index(choisi)]
    comparaisons = []
    if plus_petits:
        p = plus_petits[-1]
        comparaisons.append(f"{p['modele']}, plus petit, descend à {p['exact']} % d'exacts et {p['json']} % de JSON")
    if plus_gros:
        g = plus_gros[0]
        ecart = g["ttft"] - choisi["ttft"]
        lenteur = f"{ecart:.0f} ms plus lent au premier fragment" if ecart > 0 else f"premier fragment en {g['ttft']:.0f} ms"
        comparaisons.append(f"{g['modele']}, plus gros, fait {g['exact']} % ({lenteur}, {g['debit']:.1f} tokens/s)")
    lignes.append((" ; ".join(comparaisons) + ".") if comparaisons else "C'est le seul modèle installé : à comparer dès qu'un second est disponible.")
    if passe:
        lignes.append(f"Je retiens donc {choisi['modele']} : le plus petit modèle qui passe mes seuils "
                      f"(JSON {SEUIL_JSON} %, exacts {SEUIL_EXACT} %), avec un premier fragment en {choisi['ttft']:.0f} ms "
                      f"et {choisi['debit']:.1f} tokens/s sur ma machine.")
    else:
        lignes.append(f"Aucun modèle ne passe mes deux seuils (JSON {SEUIL_JSON} %, exacts {SEUIL_EXACT} %) : je retiens le meilleur, "
                      f"{choisi['modele']}, et la prochaine étape est de retravailler la consigne avant de changer de modèle.")
    return lignes


def main():
    try:
        version = get_json("/api/version").get("version", "?")
        presents = installes()
    except Exception as erreur:
        print(f"Ollama ne répond pas sur {BASE} ({erreur}). Lance Ollama, puis relance ce script.")
        return 1
    if MODELE_PROMPT not in presents:
        print(f"Le modèle {MODELE_PROMPT} n'est pas installé : ollama pull {MODELE_PROMPT}")
        return 1
    finale = evaluer.CONSIGNE
    modeles = [m for m in CANDIDATS if m in presents] + [m for m in sys.argv[1:] if m in presents and m not in CANDIDATS]
    absents = [m for m in sys.argv[1:] if m not in presents]
    if absents:
        print(f"Ignorés, non installés : {', '.join(absents)}")

    print(f"1/2 · Versions du prompt sur {MODELE_PROMPT} ({len(CAS)} cas)")
    versions = []
    for nom, consigne in versions_du_prompt(finale):
        print(f"  {nom}")
        versions.append((nom, mesurer_consigne(consigne)))
    print(" " * 40)

    # Le banc compare les modèles avec la consigne la plus honnête : sans cas du jeu de test recopiés.
    nom_banc, consigne_banc = versions_du_prompt(finale)[-1]
    print(f"2/2 · Banc d'essai ({nom_banc.split(' · ')[0]}) : {', '.join(modeles)}")
    banc.CONSIGNE = consigne_banc
    resultats = [banc.evaluer(m) for m in modeles]
    choisi, passe = choisir(resultats)
    infos = machine()
    copies = fuite(finale)
    date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    md = [
        "# Mesures du CC2 : prompt et choix du modèle",
        "",
        f"Mesuré le {date} sur {infos['systeme']}, {infos['processeur']}, {infos['ram']} de RAM, Ollama {version}.",
        f"Jeu de test : les {len(CAS)} tickets de `tp/05_prompt/cas.json`. Température 0, 80 tokens maximum.",
        "Produit par `python3 tp/mesures_cc2.py` avec les instruments du cours (`evaluer.py`, `banc.py`).",
        "",
        f"## 1. Versions du prompt (séance 5), modèle {MODELE_PROMPT}",
        "",
        "| Version | JSON valide | Catégorie | Urgence | Exact (les deux) |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for nom, r in versions:
        md.append(f"| {nom} | {r['json']} % | {r['categorie']} % | {r['urgence']} % | {r['exact']} % |")
    md += ["", "V1 est la consigne fournie par le cours. V2 à V4 ajoutent un à un les blocs de ma consigne finale "
           "(celle de `tp/05_prompt/evaluer.py`), pour mesurer ce que chaque bloc apporte."]
    if copies:
        md += ["", f"**Limite repérée** : {len(copies)} exemples de la consigne finale sont des cas du jeu de test, recopiés. "
               "V3 et V4 sont donc optimistes. V5 garde les mêmes règles avec des exemples rédigés hors du jeu de test : "
               "c'est son score qui compte, et c'est elle que le banc utilise."]
    md += [
        "",
        "## 2. Banc d'essai (séance 11) : seul le modèle change",
        "",
        f"Consigne constante pour tous les modèles : {nom_banc}.",
        "",
        "| Modèle | JSON valide | Exact | 1er fragment (médiane) | Débit (médiane) |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for r in resultats:
        md.append(f"| {r['modele']} | {r['json']} % | {r['exact']} % | {r['ttft']:.0f} ms | {r['debit']:.1f} tokens/s |")
    md += ["", f"Seuils : JSON valide ≥ {SEUIL_JSON} %, exacts ≥ {SEUIL_EXACT} %. Le premier appel de chaque modèle "
           "(chargement en mémoire) n'est pas compté.", "", "## 3. Justification du choix", ""]
    md += justification(resultats, choisi, passe)
    md += ["", "Dans AlterRADAR, le modèle conseillé dépend de la mémoire de l'ordinateur (3B dès 8 Go, 7B dès 16 Go) : "
           "ce banc est à relancer à chaque changement de modèle ou de consigne.", ""]
    SORTIE.write_text("\n".join(md), encoding="utf-8")
    print("\n" + "\n".join(md))
    print(f"\nÉcrit dans {SORTIE.relative_to(ICI.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
