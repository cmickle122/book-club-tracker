from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import (
    get_user_by_email,
    get_user_by_username_or_email,
    create_user,
    get_user_clubs,
    find_clubs,
    insert_club,
    get_club_by_id,
    is_club_member,
    add_club_member,
    get_active_book
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/dashboard')
def dashboard():
    """DEVELOPER 1: User Dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    clubs_raw = get_user_clubs(session['user_id'])

    clubs = []
    for club in clubs_raw:
        active_book = get_active_book(club['id'])
        clubs.append({
            'club': club,
            'active_book': active_book
        })

    return render_template('dashboard.html', clubs_data=clubs)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """DEVELOPER 1: User Login"""
    if request.method == 'POST':
        email = request.form.get('email','').strip()
        password = request.form.get('password','')

        user = get_user_by_email(email)
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid email or password')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """DEVELOPER 1: User Registration"""
    if request.method == 'POST':
        
        username = request.form.get('username','').strip()
        email = request.form.get('email','').strip()
        password = request.form.get('password','')
        confirm_password = request.form.get('confirm_password','')

        if not username or not email or not password:
            flash('All fields required')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.')
            return render_template('register.html')

        hashed = generate_password_hash(password)

        create_user(username, email, hashed)

        flash('Account created! Please log in.')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    """DEVELOPER 1: User Logout"""
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/clubs/search')
def search_clubs():
    """DEVELOPER 1: Club Search & Discovery"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    q = request.args.get('q','').strip()
    clubs = find_clubs(q)
    joined_ids = {c['id'] for c in get_user_clubs(session['user_id'])}

    return render_template('search_clubs.html', clubs=clubs, q=q, joined_ids=joined_ids)

@auth_bp.route('/clubs/create', methods=['GET', 'POST'])
def create_club():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name','').strip()
        description = request.form.get('description','').strip()
        genre = request.form.get('genre','').strip()
        is_private = 1 if request.form.get('is_private') else 0
        passcode = request.form.get('passcode','').strip() if is_private else None

        if not name or not description or not genre:
            flash('Club name, description, and genre are all required.')
            return render_template('create_club.html')

        if is_private and not passcode:
            flash('Private clubs require a passcode.')
            return render_template('create_club.html')

        insert_club(name, description, genre, is_private, passcode, session['user_id'])
        return redirect(url_for('auth.dashboard'))

    return render_template('create_club.html')

@auth_bp.route('/clubs/<int:club_id>/join', methods=['POST'])
def join_club(club_id):
    """DEVELOPER 1: Join Club (Validates Passcode if Private)"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    club = get_club_by_id(club_id)
    if not club:
        flash('Club not found')
        return redirect(url_for('auth.search_clubs'))

    if club['is_private']:
        entered = request.form.get('passcode', '')
        if entered != club['passcode']:
            flash('Incorrect passcode for private club')
            return redirect(url_for('auth.search_clubs'))

    if not is_club_member(session['user_id'], club_id):
        add_club_member(session['user_id'], club_id)
        flash(f"Joined {club['name']}!")

    return redirect(url_for('club.view_club', club_id=club_id))