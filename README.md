# Subjex

QA Y2 Software Agile Project
Authored: Bradley W
Date: 27 . 06 . 2025

## Perquisites

- You will need node (v20.17.0 (min)) installed on your system.
- You will need python (v3.10.12 (min)) installed on your system.
- You will need venv (a python package for handling virtual environments) installed on your system.

Run in the root directory `python -m venv venv` (you may need to use python3 instead of just python)

### On Mac & Linux

Run in the root directory `source venv/bin/activate`

### On Windows

Run in the root directory `venv\Scripts\activate`

## Install Dependencies

Run in the root directory `pip install -r requirements.txt`
Run in the /frontend directory `npm install`

## Environment Secrets

Utilise the .env.example as a template to create a .env file in the root directory.
You should also create one in the /frontend directory using the .env.template file there. Avoid changing default values given to you, these aren't secret/unique.

## Build

Run in the /frontend directory `npm run build`

This will create a /out file in the /frontend directory that the flask container references to deliver it's static HTML/JS content. It is not required if you only wish to test/develop the API. It's not a very pleasant developer experience to have to rebuild every time you wish to see any frontend changes in the web application, so see point on hot reload below if you wish to develop the frontend/UI.

## Hot Reload / Developer frontend environment

The current branch is configured to serve a built version of the application from the address served via flask. To get hot reload functionality simply run from the /frontend directory  `npm run dev`. This will create a frontend server separate from the flask API for you to develop in. You will need to run the flask server at the same time.

## Running the Flask in dev

Run in the root directory `export FLASK_APP=app.py && flask run` for subsequent re-running within that terminal you only have to do `flask run`.
Site accessible on `http://localhost:5000/`


## Running the Flask in prod

Run in the root directory `gunicorn app:app`. It's worth noting you should modify the .env variable "FLASK_ENV" to be "production" instead of "development".
Site accessible on `http://localhost:8000/`

---

## Docker & CI/CD Deployment

The project includes a full Docker Compose setup with GitHub Actions to deploy to a VPS.

### Local Docker Setup

```bash
# Copy the env template and fill in real values
cp .env.example .env

# Build and start all services
docker compose up --build -d

# View logs
docker compose logs -f
```

The app will be available at `http://localhost` (port 80).

### Key Files

`backend/Dockerfile` | Multi-stage build — compiles the Next.js frontend, then bundles it into a Python image with gunicorn |
`docker-compose.yml` | Base compose: PostgreSQL + Flask app + Nginx |
`docker-compose.prod.yml` | Prod |
`nginx/default.conf` | Nginx config proxying all traffic to Flask |
`.github/workflows/ci-cd.yml` | GitHub Actions pipeline |
`scripts/setup-vps.sh` | One-time VPS bootstrap script |

### CI/CD Pipeline (GitHub Actions)

The pipeline triggers on every push to `main`:

1. **Test** — runs `pytest` against a Postgres service container + lints and builds the frontend
2. **Build & Push** — builds the Docker image and pushes it to GitHub Container Registry (`ghcr.io`)
3. **Deploy** — SSHs into the VPS, pulls the new image, and restarts with `docker compose up -d`

#### Required GitHub Secrets

`VPS_HOST` | Your VPS IP address or hostname |
`VPS_USER` | SSH user on the VPS (e.g. `deploy`) |
`VPS_SSH_KEY` | Private SSH key for that user |

### First-Time VPS Setup

```bash
# Run the bootstrap script
ssh root@your-vps < scripts/setup-vps.sh

# Then edit the .env file
ssh root@your-vps "nano /opt/subjex/.env"
```

The script installs Docker, creates `/opt/subjex`, and seeds a `.env` template. After that, every push to `main` will automatically test, build, and deploy.