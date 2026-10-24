from flask import Blueprint, render_template, request, redirect, url_for, session, flash

import requests
from app.db import get_db

admin_bp = Blueprint('admin', __name__)

def _require_login():
        if 'user_id' not in session:
            flash('Please log in first.')
            return False
        return True


@admin_bp.route('/clubs/<int:club_id>/poll/nominate', methods=['POST'])
def nominate_book(club_id):
    """
    Allows the user to nominate a candidate book for an active poll.
    """
    # Check if the user is logged in.  
    if not _require_login():
        return redirect(url_for('auth.login'))

    # Extract the information from the selected book from the request form.
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    cover_url = request.form.get('cover_url', '').strip()

    # Get active poll_id for club_id from BookPolls.
    db = get_db()
    poll = db.execute(
        'SELECT id FROM BookPolls WHERE club_id = ? AND is_active = 1 LIMIT 1',
        (club_id,)
    ).fetchone()

    # Insert the user's book selection into the PollNominations table.
    if poll and title:
        db.execute(
            'INSERT INTO PollNominations (poll_id, nominated_by, title, author, cover_url) VALUES (?, ?, ?, ?, ?)',
            (poll['id'], session['user_id'], title, author, cover_url)
        )
        
        db.commit()
        flash('Your book has been nominated!')
    else:
        flash('No active poll found or invalid book title.')

    return redirect(url_for('club.view_club', club_id=club_id))


@admin_bp.route('/clubs/<int:club_id>/poll/vote', methods=['POST'])
def vote_poll(club_id):
    """
    Records user votes in book poll.
    """
    # Check if the user is logged in.  
    if not _require_login():
        return redirect(url_for('auth.login'))

    # Extract nomination and poll ids from the request form.
    nomination_id = request.form.get('nomination_id')
    poll_id = request.form.get('poll_id')

    #  Add the user's vote into the PollVotes unless they have already voted.
    db = get_db()
    try:
        db.execute(
            'INSERT INTO PollVotes (poll_id, nomination_id, user_id) VALUES (?, ?, ?)',
            (poll_id, nomination_id, session['user_id'])
        )
        db.commit()
        flash('Vote registered successfully!')
    except db.IntegrityError:
        flash('You have already voted in this poll.')

    return redirect(url_for('club.view_club', club_id=club_id))


@admin_bp.route('/clubs/<int:club_id>/manage', methods=['GET', 'POST'])
def manage_club(club_id):
    """
    Admin Setup Panel & Google Books API Integration
    """
    if request.method == 'POST':
        # Write your code here:
        # Action A: Close Poll & Declare Winner
        #   - Update BookPolls SET is_active = 0 WHERE id = poll_id
        #   - Optional Google Books API lookup using requests library to fetch cover URL
        #   - Insert winning book into Books (club_id, title, author, cover_url, is_active=1)
        #
        # Action B: Book Chapter Setup & Target Reading Deadline
        #   - Extract total_chapters, has_prologue, has_epilogue, target_deadline from request.form
        #   - Update active book record in Books table
        #   - Redirect to url_for('admin.manage_club', club_id=club_id)
        
        
        return redirect(url_for('admin.manage_club', club_id=club_id))

    return f"<h1>Admin Management Panel for Club #{club_id} (Developer 2 Placeholder)</h1>"


@admin_bp.route('/clubs/<int:club_id>/progress/update', methods=['POST'])
def update_progress(club_id):
    """
    Saves the checkbox status for chapter progress.
    """
    # Check if the user is logged in.  
    if not _require_login():
        return redirect(url_for('auth.login'))

    # Extract book information from the request form.
    book_id = request.form.get('book_id')
    chapter_num = request.form.get('chapter_num')
    is_completed = 1 if request.form.get('is_comppleted') else 0

    # Add the row in ChapterProgress or update existing row.
    db = get_db()
    if is_completed:
        db.execute('INSERT INTO ChapterProgress (user_id, book_id, chapter_num, is_completed) VALUES (?, ?, ?, ?) ON CONFLICT(user_id, book_id, chapter_num) DO UPDATE SET is_completed=1,
        (session['user_id'], book_id, chapter_num))
    else:
        db.execute(
            'DELETE FROM ChapterProgress WHERE user_id = ? AND book_id = ? AND chapter_num = ?',
            (session['user_id'], book_id, chapter_num)
        )
    db.commit()

    return redirect(url_for('club.view_club', club_id=club_id))
