#!/usr/bin/env bash

#  Usage:  ssh root@your-vps < scripts/setup-vps.sh
set -euo pipefail

APP_DIR="/opt/subjex"

echo "Installing Docker"
if ! command -v docker &>/dev/null; then
  curl -fsSL https://get.docker.com | sh
  systemctl enable --now docker
fi

echo "Creating app directory"
mkdir -p "$APP_DIR"

echo "Copying .env template"
if [ ! -f "$APP_DIR/.env" ]; then
  cat > "$APP_DIR/.env" <<'ENVFILE'
# ----- PostgreSQL -----
POSTGRES_USER=subjex
POSTGRES_PASSWORD=CHANGE_ME
POSTGRES_DB=subjex

# ----- Flask App -----
SECRET_KEY=CHANGE_ME
FLASK_ENV=production
ELEVATE_ADMIN_SECRET=CHANGE_ME

# ----- GHCR image -----
GITHUB_REPOSITORY=your-org/subjex-0

# ----- Nginx port -----
HOST_PORT=80
ENVFILE
  echo "IMPORTANT: Edit $APP_DIR/.env and set secrets"
fi

echo "Done! The app is ready."
echo "> Edit $APP_DIR/.env with your secrets"
echo "> Push to 'main' to trigger the CI/CD pipeline"
