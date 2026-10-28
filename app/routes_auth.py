from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/dashboard')
def dashboard():
    """DEVELOPER 1: User Dashboard (Lists joined clubs and active reading targets)"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    db = get_db()
    # 2. Fetch all clubs user belongs to
    clubs_raw = db.execute('''
        SELECT bc.* FROM BookClubs bc
        JOIN ClubMemberships cm ON bc.id = cm.club_id
        WHERE cm.user_id = ?
        UNION
        SELECT * FROM BookClubs WHERE admin_id = ?
    ''', (session['user_id'], session['user_id'])).fetchall()

    # 3. For each club, fetch active book title, cover_url, and target_deadline
    clubs = []
    for club in clubs_raw:
        active_book = db.execute(
            'SELECT * FROM Books WHERE club_id = ? AND is_active = 1 LIMIT 1',
            (club['id'],)
        ).fetchone()
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

        db = get_db()
        user = db.execute('SELECT * FROM Users WHERE email = ?', (email,)).fetchone()
        
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

        if not username or not email or not password:
            flash('All fields required')
            return render_template('register.html')

        db = get_db()
        exists = db.execute('SELECT id FROM Users WHERE email = ? OR username = ?', (email, username)).fetchone()
        if exists:
            flash('Email or username already taken')
            return render_template('register.html')

        hashed = generate_password_hash(password)
        db.execute('INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)',
                   (username, email, hashed))
        db.commit()
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
    db = get_db()
    
    if q:
        # Search filter SQL query (filtering by genre/name)
        clubs = db.execute('''
            SELECT * FROM BookClubs 
            WHERE name LIKE ? OR genre LIKE ? OR description LIKE ?
        ''', (f'%{q}%', f'%{q}%', f'%{q}%')).fetchall()
    else:
        clubs = db.execute('SELECT * FROM BookClubs').fetchall()

    return render_template('search.html', clubs=clubs, q=q)

@auth_bp.route('/clubs/create', methods=['GET', 'POST'])
def create_club():
    """DEVELOPER 1: Create New Book Club"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name','').strip()
        description = request.form.get('description','').strip()
        genre = request.form.get('genre','').strip()
        is_private = 1 if request.form.get('is_private') else 0
        passcode = request.form.get('passcode','').strip() if is_private else None

        if not name:
            flash('Club name required')
            return render_template('create_club.html')

        db = get_db()
        cur = db.execute('''
            INSERT INTO BookClubs (name, description, genre, is_private, passcode, admin_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, genre, is_private, passcode, session['user_id']))
        club_id = cur.lastrowid
        db.execute('INSERT INTO ClubMemberships (user_id, club_id) VALUES (?, ?)',
                   (session['user_id'], club_id))
        db.commit()
        return redirect(url_for('auth.dashboard'))

    return render_template('create_club.html')

@auth_bp.route('/clubs/<int:club_id>/join', methods=['POST'])
def join_club(club_id):
    """DEVELOPER 1: Join Club (Validates Passcode if Private)"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    db = get_db()
    club = db.execute('SELECT * FROM BookClubs WHERE id = ?', (club_id,)).fetchone()
    if not club:
        flash('Club not found')
        return redirect(url_for('auth.search_clubs'))

    # passcode verification logic for private clubs
    if club['is_private']:
        entered = request.form.get('passcode','')
        if entered != club['passcode']:
            flash('Incorrect passcode for private club')
            return redirect(url_for('auth.search_clubs'))

    already = db.execute('SELECT 1 FROM ClubMemberships WHERE user_id = ? AND club_id = ?',
                         (session['user_id'], club_id)).fetchone()
    if not already:
        db.execute('INSERT INTO ClubMemberships (user_id, club_id) VALUES (?, ?)',
                   (session['user_id'], club_id))
        db.commit()
        flash(f"Joined {club['name']}!")

    return redirect(url_for('club.view_club', club_id=club_id))
