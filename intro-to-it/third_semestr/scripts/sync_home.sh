#!/usr/bin/env bash
# Запуск из third_semestr: bash scripts/sync_home.sh
set -euo pipefail
cd "$(dirname "$0")/.."
remote_dir=/home/knyze/pfur-coursework/intro-to-it/third_semestr
rsync -az --exclude '.env' --exclude '.venv' --exclude '.mamba' \
  --exclude '__pycache__' --exclude 'data' ./ "home:$remote_dir/"
if [ -f .env ]; then
  chmod 600 .env
  scp -q .env "home:$remote_dir/.env"
  ssh home "chmod 600 $remote_dir/.env"
fi
echo "Код и .env синхронизированы с home. Данные не копировались."
