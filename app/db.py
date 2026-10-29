import sqlite3
from flask import g, current_app
from app.models import SCHEMA_SQL

def get_db():
    if 'db' not in g:
        db_path = current_app.config.get('DATABASE', 'bookclub.db')
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def init_db():
    db = get_db()
    db.executescript(SCHEMA_SQL)
    db.commit()
    print("Database tables initialized successfully in bookclub.db!")

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# Developer 1's Helper Functions:
def create_user(username, email, password_hash):
    """
    Inserts new user into Users
    """
    db = get_db()
    db.execute('''
        INSERT INTO Users (username, email, password_hash) VALUES (?, ?, ?)
        ''', (username, email, password_hash))
    db.commit()

def get_user_by_email(email):
    """
    Gets a user record by email address.
    """
    db = get_db()
    return db.execute('SELECT * FROM Users WHERE email = ?', (email,)).fetchone()
    
def get_user_by_username_or_email(username, email):
    """
    Checks for existing accounts when registering.
    """
    db = get_db()
    return db.execute('''
        SELECT id FROM Users WHERE email = ? OR username = ?
        ''', (email, username)).fetchone()

def is_club_member(user_id, club_id):
    """
    Checks if the user is already a member of a given club.
    """
    db = get_db()
    return db.execute(
        'SELECT 1 FROM ClubMemberships WHERE user_id = ? AND club_id = ?',
        (user_id, club_id)
    ).fetchone() is not None

def add_club_member(user_id, club_id):
    """
    Adds user to a club's membership.
    """
    db = get_db()
    db.execute('INSERT INTO ClubMemberships (user_id, club_id) VALUES (?, ?)', (user_id, club_id))
    db.commit()

def get_user_clubs(user_id):
    """
    Fetch all clubs user belongs to
    """
    db = get_db()
    clubs_raw = db.execute('''
        SELECT bc.* FROM BookClubs bc
        JOIN ClubMemberships cm ON bc.id = cm.club_id
        WHERE cm.user_id = ?
        UNION
        SELECT * FROM BookClubs WHERE admin_id = ?
    ''', (user_id, user_id)).fetchall()
    
def find_clubs(query):
    """
    Search filter SQL query (genre/name/description)
    """
    db = get_db()
    if query:
        return db.execute('''
            SELECT * FROM BookClubs 
            WHERE name LIKE ? OR genre LIKE ? OR description LIKE ?
        ''', (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
    return db.execute('SELECT * FROM BookClubs').fetchall()
    
def insert_club(name, description, genre, is_private, passcode, admin_id):
    """
    Inserts new clubs and adds the creator as the admin member.
    """
    db = get_db()
    cur = db.execute('''
        INSERT INTO BookClubs (name, description, genre, is_private, passcode, admin_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, description, genre, is_private, passcode, session['user_id']))
        
    club_id = cur.lastrowid
    db.execute('INSERT INTO ClubMemberships (user_id, club_id) VALUES (?, ?)',
        (admin_id, club_id))
    db.commit()
    return club_id
    

# Developer 2's Helper Functions:  
def add_nomination(poll_id, user_id, title, author, cover_url):
    """ 
    Insert the nomination into PollNominations table.
    """
    db = get_db()
    db.execute('''
        INSERT INTO PollNominations (poll_id, nominated_by, title, author, cover_url) 
        VALUES (?, ?, ?, ?, ?)''', (poll_id, user_id, title, author, cover_url)
    )
    db.commit()
    
def record_vote(poll_id, nomination_id, user_id):
    """
    Add the user's vote into the PollVotes unless they have already voted.
    """
    db = get_db()
    try:
        db.execute(
            'INSERT INTO PollVotes (poll_id, nomination_id, user_id) VALUES (?, ?, ?)',
            (poll_id, nomination_id, user_id)
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def get_latest_poll(club_id):
    """
    Finds the most recent poll (open or closed).
    """
    db = get_db()
    return db.execute(
        'SELECT * FROM BookPolls WHERE club_id = ? ORDER BY created_at DESC LIMIT 1', 
        (club_id,)
    ).fetchone()
    
def get_poll_results(poll_id):
    """
    Uses LEFT JOIN to calculate vote tallies.
    """
    db = get_db()
    return db.execute(
        '''SELECT pn.id, pn.title, pn.author, pn.cover_url, COUNT(pv.id) AS vote_count
           FROM PollNominations pn
           LEFT JOIN PollVotes pv ON pn.id = pv.nomination_id
           WHERE pn.poll_id = ?
           GROUP BY pn.id
           ORDER BY vote_count DESC''',
        (poll_id,)
    ).fetchall()
    
def close_poll(poll_id, club_id):
    """
    Locks voting on a poll.
    """
    db = get_db()
    db.execute('UPDATE BookPolls SET is_active = 0 WHERE id = ? AND club_id = ?', (poll_id, club_id))
    db.commit()
    
def set_active_book(club_id, title, author, cover_url):
    """
    Sets previous book to inactive, and new book to active.
    """
    db = get_db()
    db.execute('UPDATE Books SET is_active = 0 WHERE club_id = ?', (club_id,))
    db.execute(
        'INSERT INTO Books (club_id, title, author, cover_url, is_active) VALUES (?, ?, ?, ?, 1)',
        (club_id, title, author, cover_url)
    )
    db.commit()
    
def setup_book_details(book_id, club_id, total_chapters, has_prologue, has_epilogue, target_deadline):
    """
    Sets chapter count, prologue/epilogue chapters, and reading deadline.
    """
    db = get_db()
    db.execute(
        '''UPDATE Books 
           SET total_chapters = ?, has_prologue = ?, has_epilogue = ?, target_deadline = ? 
           WHERE id = ? AND club_id = ?''',
        (total_chapters, has_prologue, has_epilogue, target_deadline, book_id, club_id)
    )
    db.commit()
    
def save_user_progress(user_id, book_id, chapter_num, is_completed):
    """
    Updates ChapterProgress status.
    """
    db = get_db()
    if is_completed:
        db.execute('''
        INSERT INTO ChapterProgress (user_id, book_id, chapter_num, is_completed) VALUES (?, ?, ?, ?) 
        ON CONFLICT(user_id, book_id, chapter_num) DO UPDATE SET is_completed = 1
        ''', (user_id, book_id, chapter_num, is_completed))
    else:
        db.execute('''
            DELETE FROM ChapterProgress WHERE user_id = ? AND book_id = ? AND chapter_num = ?
            ''', (user_id, book_id, chapter_num)
        )
    db.commit()


# Developer 3's Helper Functions:
def get_user_chapter_progress(user_id, book_id):
    """
    Retrieves chapter progress for a user.
    """
    db = get_db()
    return db.execute('''SELECT * FROM ChapterProgress WHERE user_id = ? AND book_id = ?
    ''', (user_id, book_id)).fetchone()

def get_poll_nominations(poll_id):
    """
    Retrieves all candidates nominated in a poll.
    """
    db = get_db()
    return db.execute('SELECT * FROM PollNominations WHERE poll_id = ?', (poll_id,)).fetchall()

def get_user_completed_chapters(user_id, book_id):
    """
    Returns chapter completion count for progress bars.
    """
    db = get_db()
    prog = db.execute('''SELECT completed_chapters FROM ChapterProgress WHERE user_id = ? AND book_id = ?
    ''', (user_id, book_id)).fetchone()
    return prog['completed_chapters'] if prog else 0

def get_user_max_chapter(user_id, book_id):
    """
    Returns the highest completed chapter to enforce spoiler locks.
    """
    db = get_db()
    max_row = db.execute(
        'SELECT MAX(chapter_num) as max_c FROM ChapterProgress WHERE user_id = ? AND book_id = ?',
        (user_id, book_id)
    ).fetchone()
    return max_row['max_c'] if max_row and max_row['max_c'] is not None else 0

def add_discussion_post(club_id, book_id, chapter_num, user_id, content):
    """
    Inserts the user's post into DiscussionPosts.
    """
    db = get_db()
    db.execute('''INSERT INTO DiscussionPosts (club_id, book_id, chapter_num, user_id, content) 
    VALUES (?, ?, ?, ?, ?)''', (club_id, book_id, chapter_num, user_id, content))
    db.commit()

def get_discussion_posts(club_id, book_id, chapter_num):
    """
    Gets posts with user details for discussion threads.
    """
    db = get_db()
    return db.execute('''
        SELECT dp.*, u.username FROM DiscussionPosts dp
        JOIN Users u ON dp.user_id = u.id
        WHERE dp.club_id = ? AND dp.book_id = ? AND dp.chapter_num = ?
        ORDER BY dp.id ASC
    ''', (club_id, book_id, chapter_num)).fetchall()

def remove_club_member(user_id, club_id):
    """
    Allows members to leave or be removed from the club.
    """
    db = get_db()
    db.execute('DELETE FROM ClubMemberships WHERE user_id = ? AND club_id = ?', (user_id, club_id))
    db.commit()


# Helper Functions used by Developer 2 & 3:
def get_club_by_id(club_id):
    """
    Retrieves club data by id.
    """
    db = get_db()
    return db.execute('SELECT * FROM BookClubs WHERE id = ?', (club_id,)).fetchone()
    
def get_active_book(club_id):
    """
    Finds the current active book for a club.
    """
    db = get_db()
    return db.execute(
        'SELECT * FROM Books WHERE club_id = ? AND is_active = 1 ORDER BY created_at DESC LIMIT 1', 
        (club_id,)
    ).fetchone()
    
def get_active_poll(club_id):
    """
    Get active BookPoll for a club.
    """
    db = get_db()
    return db.execute(
        'SELECT id FROM BookPolls WHERE club_id = ? AND is_active = 1 LIMIT 1',
        (club_id,)
    ).fetchone()

def get_club_members(club_id):
    """
    Finds all members in a club.
    """
    db = get_db()
    return db.execute(
        '''SELECT Users.id, Users.username, Users.email 
           FROM Users JOIN ClubMemberships ON Users.id = ClubMemberships.user_id 
           WHERE ClubMemberships.club_id = ?''', 
        (club_id,)
    ).fetchall()