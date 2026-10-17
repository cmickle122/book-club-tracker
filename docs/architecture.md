# Architecture Documentation
See project requirements and source guidelines.

# File Architecture:
book-club-tracker/  
├── .gitignore                     # Excludes temporary files (venv, __pycache__) from Git  
├── Dockerfile                     # Deployment container instructions  
├── README.md                      # Team setup & task assignment documentation  
├── requirements.txt               # Dependencies (Flask, Jinja2, requests, etc.)  
├── run.py                         # Root file to launch the local development server  
├── bookclub.db                    # Pre-initialized SQLite database (contains all 9 tables)  
├── app/  
│   ├── __init__.py                # Flask app factory (registers all 3 route blueprints)  
│   ├── db.py                      # Database connection & init helpers (get_db, init_db)  
│   ├── models.py                  # All 9 table schemas (Users, BookClubs, Books, etc.)  
│   ├── routes_auth.py             # Developer 1: Auth, Dashboard, Search & Join  
│   ├── routes_admin.py            # Developer 2: Polls, Admin Setup & Chapter Progress  
│   ├── routes_club.py             # Developer 3: Discussions, Spoilers & Member Removal  
│   ├── static/  
│   │   ├── css/  
│   │   │   └── style.css          # Global styling & spoiler blur CSS rules  
│   │   ├── js/  
│   │   │   └── main.js            # Spoiler warning modal logic  
│   │   └── images/  
│   │       └── .gitkeep           # Placeholder for book cover image assets  
│   └── templates/  
│       ├── base.html              # Master Bootstrap 5 layout frame  
│       └── partials/  
│           ├── navbar.html        # Top navigation bar  
│           └── footer.html        # Page footer  
├── docs/  
│   └── architecture.md            # Architecture notes  
└── tests/  
    └── test_basic.py              # Automated test stubs  