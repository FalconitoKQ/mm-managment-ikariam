# MM Management for Ikariam

> **Disclaimer:** Unofficial fan project. Not affiliated with Gameforge or the Ikariam team.

A full-stack Flask web application that helps **Ikariam** alliances manage resources and coordination. It automates repetitive tasks and improves communication between players. The app ships with a browser UI (Jinja templates + static assets) and a Python backend. **SQLite** is used by default for a zero-setup database. **Docker** is supported.

---

## Table of Contents
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quickstart (Linux)](#quickstart-linux)
- [Database & Migrations](#database--migrations)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Features
- Alliance **resource & logistics** tracking
- Planning views (e.g., **logistics**, **battles**, **admin**, **users/roles**)
- Clean browser UI with **Jinja2** templates and static assets
- Lightweight setup with **SQLite** by default

---

## Tech Stack
- **Backend:** Python 3, Flask (Jinja2 templates)
- **Persistence:** SQLAlchemy (ORM), SQLite (default)
- **Migrations:** Alembic (when configured)
- **Observability:** Python `logging`
- **Containerization:** Docker (optional)

## Project Structure

```text
.
├── helpers/             # Shared utilities and small helper functions
├── models/              # SQLAlchemy ORM models and metadata
├── object/              # Domain objects / dataclasses (pure Python)
├── routes/              # Flask Blueprints (HTTP endpoints)
├── services/            # Application services / business logic
├── static/              # Public assets: CSS
├── templates/           # Jinja2 templates (HTML)
├── config.py            # Base configuration (env, DB URI, etc.)
├── security_config.py   # Security-related settings (CSRF, CORS, headers)
├── run.py               # App entrypoint (Flask app factory / CLI)
└── requirements.txt     # Python dependencies (pinned)
```
---

## Quickstart (Linux)

### Prerequisites
- Python **3.x**
- Git
- (Optional) Docker

### 1) Run locally (virtual environment)
```bash
# clone
git clone https://github.com/FalconitoKQ/mm-managment-ikariam.git
cd mm-managment-ikariam; mkdir db

# create and activate venv
python3 -m venv venv
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run the app
python3 run.py
# open http://localhost:5500 or http://127.0.0.1:5500
```
### 2) Build and run from the project root
├─ Dockerfile
├─ .dockerignore
└─ .gitignore
```bash
# build image
docker build -t mm-managment-ikariam:latest .

# run container (map host 5500 -> container 5500)
docker run -d --name mm-app -p 5000:5000 mm-managment-ikariam:latest

# open http://localhost:5500
```

If you want to log in for the first time then type (default):
```txt
login: admin
password: admin
```

#### Handy comments:

```bash
docker ps
docker logs -f mm-app
docker stop mm-app && docker rm mm-app
```

#### Persist SQLite (optional). If your SQLite file is inside a folder like ./data, mount it:
```bash
mkdir -p data
docker run -d --name mm-app \
  -p 5500:5500 \
  -v "$(pwd)/data:/app/data" \
  mm-managment-ikariam:latest
```

## Database & Migrations

- **SQLite** is the default (file-based, no external server required).

- **Alembic** (if configured in the project):
```bash
# initialize (once, if not already present)
alembic init migrations

# generate a new migration after model changes
alembic revision --autogenerate -m "Describe your change"

# apply migrations
alembic upgrade head
```

## Troubleshooting

ModuleNotFoundError: **No module named 'flask'**
Make sure your virtualenv is active and **pip install -r requirements.txt** completed without errors.

Merge markers in requirements.txt (<<<<<<< HEAD)
Resolve the merge conflict in that file, then reinstall:

```bash
# edit requirements.txt to remove conflict markers and keep valid lines
pip install -r requirements.txt
```

Port already in use
Change the port:
```bash
flask run --port=5001
```
or
```bash
docker run -d -p 5001:5000 mm-managment-ikariam:latest
```

## Roadmap

- Detailed feature pages (logistics, battles, admin screenshots); dashboards & summaries; notifications.
- Switchable DB backends (PostgreSQL/MySQL).
- Flexible battle time grids: 00/15/30/45; 05/20/35/50; 10/25/40/55.
- Discord integration: OAuth login, role mapping, slash commands (view/add).
- ML-based loss estimation from battle history (MVP + confidence in UI).



## Contributing

Pull Requests are welcome. For larger changes, please open an issue first to discuss what you’d like to change.

Basic workflow:

```bash
# create a feature branch
git checkout -b feature/your-idea

# commit changes
git commit -m "Add your feature"

# push and open a PR
git push origin feature/your-idea
```
## License
This project is released under the **MM-NC-1.0 Non-Commercial License**.  
You may use, copy, modify, and distribute it **for non-commercial purposes only**.  
**Commercial use is not permitted** without a separate license.  
© 2025 Łukasz Kłak. See the [LICENSE](./LICENSE) file for full terms.

**Commercial license?** Contact: LukaszKlak-github@pm.me

