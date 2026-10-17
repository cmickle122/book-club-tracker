from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/dashboard')
def dashboard():
    """DEVELOPER 1: User Dashboard (Lists joined clubs and active reading targets)"""
    # Write your code here:
    # 1. Check if user is logged in (session.get('user_id'))
    # 2. Fetch all clubs user belongs to from ClubMemberships & BookClubs
    # 3. For each club, fetch active book title, cover_url, and target_deadline
    # 4. Render 'dashboard.html' with club cards
    # To here.
    return "<h1>User Dashboard (Developer 1 Placeholder)</h1><p>Welcome back! Your joined book clubs will be listed here.</p>"

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """DEVELOPER 1: User Login"""
    if request.method == 'POST':
        # Write your code here:
        # 1. Extract email and password from request.form
        # 2. Fetch user record from Users table where email = email
        # 3. Verify password hash using werkzeug.security.check_password_hash
        # 4. Save session['user_id'] = user['id'] and session['username'] = user['username']
        # 5. Redirect to url_for('auth.dashboard')
        # 6. If invalid, flash error message and re-render login form
        # To here.
        session['user_id'] = 1
        session['username'] = 'TestUser'
        return redirect(url_for('auth.dashboard'))

    return "<h1>Login Page (Developer 1 Placeholder)</h1>"

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """DEVELOPER 1: User Registration"""
    if request.method == 'POST':
        # Write your code here:
        # 1. Extract username, email, password from request.form
        # 2. Hash password using werkzeug.security.generate_password_hash
        # 3. Insert new user into Users table
        # 4. Redirect to url_for('auth.login')
        # To here.
        return redirect(url_for('auth.login'))

    return "<h1>Register Page (Developer 1 Placeholder)</h1>"

@auth_bp.route('/logout')
def logout():
    """DEVELOPER 1: User Logout"""
    # Write your code here:
    # 1. Clear session dictionary
    # 2. Redirect to url_for('auth.login')
    # To here.
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/clubs/search')
def search_clubs():
    """DEVELOPER 1: Club Search & Discovery"""
    # Write your code here:
    # 1. Extract query parameter (e.g., search = request.args.get('q'))
    # 2. Query BookClubs table matching name or genre
    # 3. Render search results displaying Public vs. Private badges
    # To here.
    return "<h1>Search Clubs Page (Developer 1 Placeholder)</h1>"

@auth_bp.route('/clubs/create', methods=['GET', 'POST'])
def create_club():
    """DEVELOPER 1: Create New Book Club"""
    if request.method == 'POST':
        # Write your code here:
        # 1. Extract name, description, genre, is_private, passcode from request.form
        # 2. Insert new club into BookClubs with admin_id = session['user_id']
        # 3. Insert creator into ClubMemberships
        # 4. Redirect to url_for('auth.dashboard')
        # To here.
        return redirect(url_for('auth.dashboard'))

    return "<h1>Create Club Page (Developer 1 Placeholder)</h1>"

@auth_bp.route('/clubs/<int:club_id>/join', methods=['POST'])
def join_club(club_id):
    """DEVELOPER 1: Join Club (Validates Passcode if Private)"""
    # Write your code here:
    # 1. Fetch club details from BookClubs
    # 2. If private, check passcode entered in request.form against database passcode
    # 3. Insert row into ClubMemberships (user_id, club_id)
    # 4. Redirect to url_for('club.view_club', club_id=club_id)
    # To here.
    return redirect(url_for('club.view_club', club_id=club_id))
