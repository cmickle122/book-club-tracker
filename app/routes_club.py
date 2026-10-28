from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import get_db

club_bp = Blueprint('club', __name__)

@club_bp.route('/clubs/<int:club_id>')
def view_club(club_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db()
    club = db.execute('SELECT * FROM BookClubs WHERE id = ?', (club_id,)).fetchone()
    if not club:
        flash('Club not found')
        return redirect(url_for('auth.dashboard'))

    active_book = db.execute('SELECT * FROM Books WHERE club_id = ? AND is_active = 1 LIMIT 1', (club_id,)).fetchone()

    progress_pct = 0
    total_units = 0
    completed = 0
    user_progress = None
    if active_book:
        total_units = (active_book['total_chapters'] or 0) + (1 if active_book['has_prologue'] else 0) + (1 if active_book['has_epilogue'] else 0)
        user_progress = db.execute('SELECT * FROM ChapterProgress WHERE user_id = ? AND book_id = ?', (session['user_id'], active_book['id'])).fetchone()
        if user_progress:
            completed = user_progress['completed_chapters'] or 0
        if total_units > 0:
            progress_pct = round((completed / total_units) * 100)

    active_poll = db.execute('SELECT * FROM BookPolls WHERE club_id = ? AND is_active = 1 LIMIT 1', (club_id,)).fetchone()
    nominations = []
    if active_poll:
        nominations = db.execute('SELECT * FROM PollNominations WHERE poll_id = ?', (active_poll['id'],)).fetchall()

    members = db.execute('''
        SELECT u.id, u.username, u.email FROM Users u
        JOIN ClubMemberships cm ON u.id = cm.user_id
        WHERE cm.club_id = ?
    ''', (club_id,)).fetchall()

    # FIX FOR YOUR ERROR - build members_progress dict that club.html expects
    members_progress = {}
    if active_book and total_units > 0:
        for m in members:
            prog = db.execute('SELECT completed_chapters FROM ChapterProgress WHERE user_id = ? AND book_id = ?', (m['id'], active_book['id'])).fetchone()
            comp = prog['completed_chapters'] if prog else 0
            pct = round((comp / total_units) * 100) if total_units else 0
            members_progress[m['id']] = {'pct': pct, 'completed': comp}

    is_admin = (club['admin_id'] == session['user_id'])

    return render_template('club.html', club=club, active_book=active_book, progress_pct=progress_pct, total_units=total_units, completed=completed, user_progress=user_progress, active_poll=active_poll, nominations=nominations, members=members, members_progress=members_progress, is_admin=is_admin)

@club_bp.route('/clubs/<int:club_id>/discussion/<int:chapter_num>', methods=['GET', 'POST'])
def view_discussion(club_id, chapter_num):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db()
    club = db.execute('SELECT * FROM BookClubs WHERE id = ?', (club_id,)).fetchone()
    active_book = db.execute('SELECT * FROM Books WHERE club_id = ? AND is_active = 1 LIMIT 1', (club_id,)).fetchone()
    if not club or not active_book:
        flash('Club or active book not found')
        return redirect(url_for('auth.dashboard'))

    if active_book['is_active'] == 0:
        flash('This book is archived. Read-only mode.')
        if request.method == 'POST':
            return redirect(url_for('club.view_discussion', club_id=club_id, chapter_num=chapter_num))

    max_row = db.execute('SELECT MAX(chapter_num) as max_c FROM ChapterProgress WHERE user_id = ? AND book_id = ?', (session['user_id'], active_book['id'])).fetchone()
    max_completed = max_row['max_c'] if max_row and max_row['max_c'] is not None else 0
    is_admin = (club['admin_id'] == session['user_id'])
    if not is_admin and chapter_num > 1 and max_completed < (chapter_num - 1):
        flash(f'Finish chapter {chapter_num - 1} first to unlock this discussion.')
        return redirect(url_for('club.view_club', club_id=club_id))

    if request.method == 'POST':
        if active_book['is_active'] == 0:
            flash('This book is archived. Read-only mode.')
            return redirect(url_for('club.view_discussion', club_id=club_id, chapter_num=chapter_num))
        content = request.form.get('content','').strip()
        if content:
            db.execute('INSERT INTO DiscussionPosts (club_id, book_id, chapter_num, user_id, content) VALUES (?, ?, ?, ?, ?)',
                       (club_id, active_book['id'], chapter_num, session['user_id'], content))
            db.commit()
        return redirect(url_for('club.view_discussion', club_id=club_id, chapter_num=chapter_num))

    posts = db.execute('''
        SELECT dp.*, u.username FROM DiscussionPosts dp
        JOIN Users u ON dp.user_id = u.id
        WHERE dp.club_id = ? AND dp.book_id = ? AND dp.chapter_num = ?
        ORDER BY dp.id ASC
    ''', (club_id, active_book['id'], chapter_num)).fetchall()

    return render_template('discussion.html', club=club, active_book=active_book, chapter_num=chapter_num, posts=posts, is_archived=(active_book['is_active']==0), max_completed=max_completed)

@club_bp.route('/clubs/<int:club_id>/leave', methods=['POST'])
def leave_club(club_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db()
    db.execute('DELETE FROM ClubMemberships WHERE user_id = ? AND club_id = ?', (session['user_id'], club_id))
    db.commit()
    flash('You left the club')
    return redirect(url_for('auth.dashboard'))

@club_bp.route('/clubs/<int:club_id>/kick/<int:user_id>', methods=['POST'])
def kick_member(club_id, user_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    db = get_db()
    club = db.execute('SELECT * FROM BookClubs WHERE id = ?', (club_id,)).fetchone()
    if not club or club['admin_id'] != session['user_id']:
        flash('Only admin can kick members')
        return redirect(url_for('club.view_club', club_id=club_id))
    if user_id == club['admin_id']:
        flash('Cannot kick yourself (admin)')
        return redirect(url_for('club.view_club', club_id=club_id))
    db.execute('DELETE FROM ClubMemberships WHERE user_id = ? AND club_id = ?', (user_id, club_id))
    db.commit()
    flash('Member kicked')
    return redirect(url_for('club.view_club', club_id=club_id))
