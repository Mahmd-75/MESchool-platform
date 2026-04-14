# MESchool — Plateforme de Gestion Académique Sécurisée

> Projet DevSecOps — GCS2 UE7-2 | Guardia Cybersecurity School 2025-2026

## Présentation

MESchool est une application web de gestion académique développée dans le cadre du module DevSecOps. Elle permet la gestion des notes, des classes et des emplois du temps avec un système de contrôle d'accès basé sur les rôles (RBAC).

## Stack Technique

| Composant | Technologie |
|-----------|-------------|
| Back-end | Python 3.13 / Flask |
| Base de données | MySQL 8.0 |
| Conteneurisation | Docker / Docker Compose |
| CI/CD | GitHub Actions |
| Sécurité | bcrypt, flask-wtf, OWASP ZAP |

## Architecture
```
academic-platform/
├── app/
│   ├── __init__.py          # Factory create_app()
│   ├── auth.py              # Authentification
│   ├── config.py            # Configuration
│   ├── decorators.py        # RBAC décorateurs
│   ├── models.py            # Accès base de données
│   ├── utils.py             # Validation des entrées
│   ├── routes/
│   │   ├── admin.py         # Routes administrateur
│   │   ├── prof.py          # Routes professeur
│   │   └── etudiant.py      # Routes étudiant
│   └── templates/           # Templates Jinja2
├── db/
│   ├── schema.sql           # Schéma de la base de données
│   └── seed.sql             # Données de test
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # Pipeline CI/CD
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Rôles et Permissions

| Rôle | Permissions |
|------|-------------|
| **Administrateur** | Gérer les comptes, classes, emplois du temps, affecter étudiants et professeurs |
| **Professeur** | Créer des évaluations, attribuer des notes, consulter son emploi du temps |
| **Étudiant** | Consulter ses notes et son emploi du temps |

## Installation et Lancement

### Prérequis

- Docker Desktop installé et démarré
- Git

### Étapes

1. Cloner le dépôt :
```bash
git clone https://github.com/Mahmd-75/academic-platform.git
cd academic-platform
```

2. Créer le fichier `.env` à la racine :
```
SECRET_KEY=votre-cle-secrete
FLASK_DEBUG=false
PORT=5000
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=votre-mot-de-passe
MYSQL_DB=academic_db
```

3. Lancer l'application :
```bash
docker compose up --build
```

4. Accéder à l'application : `http://localhost:5000/auth/login`

### Comptes de test

| Utilisateur | Mot de passe | Rôle |
|-------------|--------------|------|
| admin1 | password123 | Administrateur |
| prof1 | password123 | Professeur |
| etudiant1 | password123 | Étudiant |

## Mesures de Sécurité Implémentées

- **Hachage bcrypt** — mots de passe hashés avec rounds=12, aucun mot de passe en clair
- **Protection CSRF** — tokens sur tous les formulaires via flask-wtf
- **Requêtes paramétrées** — aucune concaténation SQL, 100% requêtes préparées
- **Headers HTTP** — X-Frame-Options, X-Content-Type-Options, CSP, HSTS
- **Validation des entrées** — sanitization et validation côté serveur sur tous les inputs
- **Gestion des sessions** — HttpOnly, SameSite=Lax, expiration 30 minutes, invalidation au logout
- **RBAC côté serveur** — décorateurs login_required et role_required, accès non autorisé → 403

## Pipeline CI/CD

La pipeline se déclenche automatiquement à chaque push sur `main` :

| Étape | Outil | Rôle |
|-------|-------|------|
| Lint | Flake8 | Qualité du code Python |
| Scan dépendances | pip-audit | Détection de vulnérabilités CVE |
| Scan dynamique | OWASP ZAP | Test d'intrusion automatisé |
| Build | Docker | Construction de l'image |

## Équipe
- Mahmoud EL SHETEWI
- Rayan LABED
- Yoann GIRAULT

Projet réalisé en groupe dans le cadre de l'UE7-2 DevSecOps — Guardia Cybersecurity School GCS2 2025-2026.