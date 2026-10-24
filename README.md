# book-club-tracker
## CST5322 Group Project

## Project Structure

```
book-club-tracker/
├── app/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   │   └── partials/
│   ├── __init__.py
│   ├── routes_admin.py
│   ├── routes_auth.py
│   ├── routes_club.py
│   ├── models.py
│   └── db.py
├── tests/
├── docs/
├── Dockerfile
├── requirements.txt
├── README.md
└── .gitignore
```

## What Goes Where

| Folder / File | Purpose |
|---|---|
| `app/` | The Flask application code |
| `app/static/css/` | Stylesheets |
| `app/static/js/` | JavaScript files |
| `app/static/images/` | Images used by the site |
| `app/templates/` | HTML pages |
| `app/templates/partials/` | Reusable pieces like the header and footer |
| `app/routes_admin.py` | Developer 2: Carlianne (Polls, Admin Setup, Chapter Progress) |
| `app/routes_auth.py` | Developer 1: G'La (Authorization, Dashboard, Search and Join Clubs) |
| `app/routes_club.py` | Developer 3: Zaden (Discussions, Spoiler Tagging, Member Removal) |
| `app/models.py` | Database table definitions |
| `app/db.py` | Database connection |
| `tests/` | Automated tests |
| `docs/` | Project documentation (vision, user stories, scenarios, architecture diagram) |
| `Dockerfile` | Instructions for building the Docker image |
| `requirements.txt` | List of Python packages the project needs |