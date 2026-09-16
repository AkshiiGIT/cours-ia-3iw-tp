#!/usr/bin/env bash
#
# setup-mac.sh — Installe tout l'environnement du module en une fois (macOS)
#
# Usage :
#   chmod +x setup-mac.sh
#   ./setup-mac.sh
#
set -euo pipefail

BOLD="\033[1m"
GREEN="\033[32m"
YELLOW="\033[33m"
RED="\033[31m"
RESET="\033[0m"

step() { echo -e "\n${BOLD}▶ $1${RESET}"; }
ok()   { echo -e "${GREEN}✓ $1${RESET}"; }
warn() { echo -e "${YELLOW}! $1${RESET}"; }
fail() { echo -e "${RED}✗ $1${RESET}"; }

if [[ "$(uname)" != "Darwin" ]]; then
  fail "Ce script est écrit pour macOS uniquement."
  exit 1
fi

# ---------------------------------------------------------------------------
step "1. Homebrew"
# ---------------------------------------------------------------------------
if ! command -v brew &>/dev/null; then
  warn "Homebrew absent, installation..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  # Ajoute brew au PATH pour la suite du script (Apple Silicon)
  if [[ -d /opt/homebrew/bin ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
else
  ok "Homebrew déjà présent"
fi

# ---------------------------------------------------------------------------
step "2. Git"
# ---------------------------------------------------------------------------
if ! command -v git &>/dev/null; then
  brew install git
else
  ok "Git déjà présent ($(git --version))"
fi

# ---------------------------------------------------------------------------
step "3. Node.js 20+ et Python 3.11+ (les deux, au choix ensuite)"
# ---------------------------------------------------------------------------
NODE_OK=false
if command -v node &>/dev/null; then
  NODE_MAJOR=$(node --version | sed 's/v//' | cut -d. -f1)
  if [[ "$NODE_MAJOR" -ge 20 ]]; then
    NODE_OK=true
    ok "Node $(node --version) déjà OK"
  fi
fi
if [[ "$NODE_OK" == false ]]; then
  warn "Installation de Node 20 via Homebrew..."
  brew install node@20
  brew link --overwrite --force node@20
fi

PYTHON_OK=false
if command -v python3 &>/dev/null; then
  PY_VER=$(python3 --version | awk '{print $2}')
  PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
  PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
  if [[ "$PY_MAJOR" -eq 3 && "$PY_MINOR" -ge 11 ]]; then
    PYTHON_OK=true
    ok "Python $PY_VER déjà OK"
  fi
fi
if [[ "$PYTHON_OK" == false ]]; then
  warn "Le python3 système est absent ou trop ancien (souvent 3.9 sous macOS), installation de 3.11 via Homebrew..."
  brew install python@3.11
  brew link --overwrite --force python@3.11
fi

# ---------------------------------------------------------------------------
step "4. Ollama"
# ---------------------------------------------------------------------------
if ! command -v ollama &>/dev/null; then
  curl -fsSL https://ollama.com/install.sh | sh
else
  ok "Ollama déjà installé ($(ollama --version))"
fi

# S'assure que le serveur tourne avant de télécharger les modèles
if ! curl -s http://localhost:11434 &>/dev/null; then
  warn "Démarrage du serveur Ollama en arrière-plan..."
  nohup ollama serve >/tmp/ollama.log 2>&1 &
  sleep 3
fi

# ---------------------------------------------------------------------------
step "5. Téléchargement du socle de la classe (~2,2 Go)"
# ---------------------------------------------------------------------------
ollama pull qwen2.5:3b
ollama pull paraphrase-multilingual

# ---------------------------------------------------------------------------
step "6. Vérification finale"
# ---------------------------------------------------------------------------
echo "Modèles installés :"
ollama list

if [[ -f "tp/00_setup/check.mjs" ]]; then
  node tp/00_setup/check.mjs
elif [[ -f "tp/00_setup/check.py" ]]; then
  python3 tp/00_setup/check.py
else
  warn "Script check.mjs / check.py introuvable ici — lance-le depuis la racine du dépôt du cours."
fi

echo -e "\n${GREEN}${BOLD}Installation terminée.${RESET}"
