# book-club-tracker
## CST5322 Group Project
__ is a web application for managing online book clubs. The application features tracking chapter progress, spoiler-protected discussion boards, and voting in polls. Integration of Google Books API enables users to search for real books. 

  

####  Prerequisites: Python Version 3.12+

#### Dependencies: Flask, requests, Wekzeug, Jinja2 (found in `requirements.txt`)


## Setup & Installation:

### 1. Clone the repository and change directories to the local project
```
git clone 
cd documents/book-club-tracker
```
*Note your directory path may be different. 

### 2. Setup a virtual environment
```
python3 -m venv venv
source venv/bin/activate
```
### 3. Install dependencies
```
pip install -r requirements.txt
```
### 4. Initialize and Seed the database
```
python seed.py
```


## Usage Instructions and How to Run

### 1. Start the flask server
```
python run.py
```

### 2. Open your preferred browser and navigate to: 
```
127.0.0.1:5000
```

### 3. Testing account credentials:
Note: All accounts from `seed.py` use password123 to test.

#### Admin accounts: 
```
admin@test.com
```
#### Regular member accounts:
```
user@test.com
user1@test.com
user2@test.com
user3@test.com
user4@test.com
user5@test.com
```


## Project Structure

```
book-club-tracker/
├── app/                    # Flask application code
│   ├── static/
│   │   ├── css/            # Stylesheets
│   │   ├── js/             # JavaScript files
│   │   └── images/         # Images used by the app
│   ├── templates/          # HTML pages
│   │   └── partials/       # Reusable HTML pieces (header, footer, navbar)
│   ├── __init__.py
│   ├── routes_admin.py     # Polls, Admin Setup, Chapter Progress
│   ├── routes_auth.py      # Authorization, Dashboard, Search and Join Clubs
│   ├── routes_club.py      # Discussions, Spoiler Tagging, Member Removal
│   ├── models.py           # Database table definitions
│   └── db.py               # Database connection
├── Dockerfile
├── requirements.txt        # Python packages required
├── seed.py                 # Python file to seed with sample data
├── run.py                  # Python file to run the app
├── README.md               
└── .gitignore
```



## Technologies Used:  
- Google Books API: https://developers.google.com/books/docs/v1/getting_started
