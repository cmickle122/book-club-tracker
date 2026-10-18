from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import get_db

club_bp = Blueprint('club', __name__)

def _require_login():
    if 'user_id' not in session:
        flash('Please log in first.')
        return False
    return True

@club_bp.route('/clubs/<int:club_id>')
def view_club(club_id):
    if not _require_login():
        return redirect(url_for('auth.login'))

    db = get_db()
    user_id = session['user_id']

    # 1. Fetch club details
    club = db.execute('SELECT * FROM BookClubs WHERE id = ?', (club_id,)).fetchone()
    if not club:
        flash('Club not found.')
        return redirect(url_for('auth.dashboard'))

    # Check membership (admin can always view)
    membership = db.execute(
        'SELECT * FROM ClubMemberships WHERE user_id = ? AND club_id = ?', 
        (user_id, club_id)
    ).fetchone()
    is_admin = club['admin_id'] == user_id
    if not membership and not is_admin:
        flash('You are not a member of this club.')
        return redirect(url_for('auth.dashboard'))

    # 2. Active book
    active_book = db.execute(
        'SELECT * FROM Books WHERE club_id = ? AND is_active = 1 ORDER BY created_at DESC LIMIT 1',
        (club_id,)
    ).fetchone()

    # 3. User progress
    user_progress_rows = []
    if active_book:
        user_progress_rows = db.execute(
            'SELECT chapter_num FROM ChapterProgress WHERE user_id = ? AND book_id = ?',
            (user_id, active_book['id'])
        ).fetchall()
    completed_chapters = set([r['chapter_num'] for r in user_progress_rows])

    # Members + progress % calculation
    members = db.execute('''
        SELECT Users.id, Users.username, Users.email, ClubMemberships.joined_at
        FROM Users JOIN ClubMemberships ON Users.id = ClubMemberships.user_id
        WHERE ClubMemberships.club_id = ?
    ''', (club_id,)).fetchall()

    member_progress = {}
    if active_book:
        total = (active_book['total_chapters'] or 0) + (active_book['has_prologue'] or 0) + (active_book['has_epilogue'] or 0)
        if total == 0:
            total = 1
        for m in members:
            count = db.execute(
                'SELECT COUNT(*) as c FROM ChapterProgress WHERE user_id = ? AND book_id = ?',
                (m['id'], active_book['id'])
            ).fetchone()['c']
            member_progress[m['id']] = int((count / total) * 100)

    # 4. Active poll + nominations
    active_poll = db.execute(
        'SELECT * FROM BookPolls WHERE club_id = ? AND is_active = 1 ORDER BY created_at DESC LIMIT 1',
        (club_id,)
    ).fetchone()
    nominations = []
    if active_poll:
        nominations = db.execute(
            'SELECT * FROM PollNominations WHERE poll_id = ?', (active_poll['id'],)
        ).fetchall()

    return render_template('club.html', 
                           club=club, 
                           active_book=active_book,
                           members=members,
                           member_progress=member_progress,
                           completed_chapters=completed_chapters,
                           is_admin=is_admin,
                           active_poll=active_poll,
                           nominations=nominations)

@club_bp.route('/clubs/<int:club_id>/discussion/<int:chapter_num>', methods=['GET', 'POST'])
def view_discussion(club_id, chapter_num):
    if not _require_login():
        return redirect(url_for('auth.login'))

    db = get_db()
    user_id = session['user_id']

    club = db.execute('SELECT * FROM BookClubs WHERE id = ?', (club_id,)).fetchone()
    active_book = db.execute(
        'SELECT * FROM Books WHERE club_id = ? AND is_active = 1 ORDER BY created_at DESC LIMIT 1',
        (club_id,)
    ).fetchone()

    if not active_book:
        flash('No active book for this club yet.')
        return redirect(url_for('club.view_club', club_id=club_id))

    # Spoiler Protection Check
    completed = db.execute(
        'SELECT chapter_num FROM ChapterProgress WHERE user_id = ? AND book_id = ?',
        (user_id, active_book['id'])
    ).fetchall()
    completed_set = set([r['chapter_num'] for r in completed])
    max_completed = max(completed_set) if completed_set else 0

    # Allow if chapter 0/1 or user has completed previous chapter or is admin
    is_admin = club['admin_id'] == user_id
    blocked = False
    if not is_admin and chapter_num > 1 and max_completed < (chapter_num - 1):
        blocked = True

    if request.method == 'POST':
        # 1. Archived check
        if active_book['is_active'] == 0:
            flash('This book is archived. Read-only mode.')
            return redirect(url_for('club.view_discussion', club_id=club_id, chapter_num=chapter_num))
        
        if blocked:
            flash(f'Finish chapter {chapter_num - 1} first to unlock this discussion!')
            return redirect(url_for('club.view_discussion', club_id=club_id, chapter_num=chapter_num))

        content = request.form.get('content', '').strip()
        if not content:
            flash('Post cannot be empty.')
        else:
            db.execute(
                'INSERT INTO DiscussionPosts (club_id, book_id, chapter_num, user_id, content) VALUES (?, ?, ?, ?, ?)',
                (club_id, active_book['id'], chapter_num, user_id, content)
            )
            db.commit()
        return redirect(url_for('club.view_discussion', club_id=club_id, chapter_num=chapter_num))

    # GET: fetch posts only if not blocked
    posts = []
    if not blocked:
        posts = db.execute('''
            SELECT DiscussionPosts.*, Users.username 
            FROM DiscussionPosts JOIN Users ON DiscussionPosts.user_id = Users.id
            WHERE club_id = ? AND book_id = ? AND chapter_num = ?
            ORDER BY created_at ASC
        ''', (club_id, active_book['id'], chapter_num)).fetchall()

    return render_template('discussion.html',
                           club=club,
                           book=active_book,
                           chapter_num=chapter_num,
                           posts=posts,
                           blocked=blocked,
                           max_completed=max_completed,
                           is_archived=(active_book['is_active'] == 0))

@club_bp.route('/clubs/<int:club_id>/leave', methods=['POST'])
def leave_club(club_id):
    if not _require_login():
        return redirect(url_for('auth.login'))
    db = get_db()
    db.execute('DELETE FROM ClubMemberships WHERE user_id = ? AND club_id = ?',
               (session['user_id'], club_id))
    db.commit()
    flash('You left the club.')
    return redirect(url_for('auth.dashboard'))

@club_bp.route('/clubs/<int:club_id>/members/<int:user_id>/kick', methods=['POST'])
def kick_member(club_id, user_id):
    if not _require_login():
        return redirect(url_for('auth.login'))
    db = get_db()
    club = db.execute('SELECT admin_id FROM BookClubs WHERE id = ?', (club_id,)).fetchone()
    if not club or club['admin_id'] != session['user_id']:
        flash('Only the admin can kick members.')
        return redirect(url_for('club.view_club', club_id=club_id))

    if user_id == club['admin_id']:
        flash('Admin cannot kick themselves.')
        return redirect(url_for('club.view_club', club_id=club_id))

    db.execute('DELETE FROM ClubMemberships WHERE user_id = ? AND club_id = ?', (user_id, club_id))
    db.commit()
    flash('Member removed.')
    return redirect(url_for('admin.manage_club', club_id=club_id))
