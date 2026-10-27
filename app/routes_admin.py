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
    # Check if the user is logged in  
    if not _require_login():
        return redirect(url_for('auth.login'))

    # Extract the information from the selected book from the request form.
    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    cover_url = request.form.get('cover_url', '').strip()

    # Get active poll_id for club_id from BookPolls
    db = get_db()
    poll = db.execute(
        'SELECT id FROM BookPolls WHERE club_id = ? AND is_active = 1 LIMIT 1',
        (club_id,)
    ).fetchone()

    # Insert the user's book selection into the PollNominations table
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
    # Check if the user is logged in
    if not _require_login():
        return redirect(url_for('auth.login'))

    # Extract nomination and poll ids from the request form
    nomination_id = request.form.get('nomination_id')
    poll_id = request.form.get('poll_id')

    #  Add the user's vote into the PollVotes unless they have already voted
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
    Admin setup panel: Close Poll -> View Tallies -> Google Books Search -> Select Book -> Chapter Setup
    """
    # Check if the user is logged in
    if not _require_login():
        return redirect(url_for('auth.login'))

    db = get_db()
    club = db.execute('SELECT * FROM BookClubs WHERE id = ?', (club_id,)).fetchone()

    # Check if the user is the club admin
    if not club or club['admin_id'] != session['user_id']:
        flash('Access denied. Admin permissions required.')
        return redirect(url_for('club.view_club', club_id=club_id))

    search_results = []
    search_query = ''

    # Admin actions submitted in the form
    if request.method == 'POST':
        action = request.form.get('action')

        # 1. Close the Active Poll
        if action == 'close_poll':
            poll_id = request.form.get('poll_id')
            if poll_id:
                db.execute('UPDATE BookPolls SET is_active = 0 WHERE id = ? AND club_id = ?', (poll_id, club_id))
                db.commit()
                flash('The poll has closed! Voting is locked and final results are displayed.')
            return redirect(url_for('admin.manage_club', club_id=club_id))

        # 2. Search Google Books API for up to 4 Candidates
        elif action == 'search_books':
            search_query = request.form.get('search_query', '').strip()
            if not search_query:
                flash('Please enter a book title or keyword to search.')
            else:
                try:
                    api_url = "https://www.googleapis.com/books/v1/volumes"
                    res = requests.get(
                        api_url, 
                        params={'q': search_query, 'maxResults': 4}, 
                        timeout=5
                    ).json()

                    if 'items' in res:
                        for item in res['items']:
                            volume_info = item.get('volumeInfo', {})
                            authors_list = volume_info.get('authors', [])
                            author = ", ".join(authors_list) if authors_list else 'Unknown Author'
                            image_links = volume_info.get('imageLinks', {})
                            cover_url = image_links.get('thumbnail') or image_links.get('smallThumbnail') or ''
                            title = volume_info.get('title', 'Unknown Title')

                            search_results.append({
                                'title': title,
                                'author': author,
                                'cover_url': cover_url
                            })
                        if not search_results:
                            flash('No books found matching your search query.')
                except Exception:
                    flash('Error fetching book results from Google Books API.')

        # 3. Select candidate book
        elif action == 'select_book':
            book_title = request.form.get('book_title', '').strip()
            author = request.form.get('author', '').strip()
            cover_url = request.form.get('cover_url', '').strip()

            if not book_title:
                flash('Invalid book selection.')
                return redirect(url_for('admin.manage_club', club_id=club_id))

            # Deactivate previous active book for this club
            db.execute('UPDATE Books SET is_active = 0 WHERE club_id = ?', (club_id,))

            # Insert selected book as active
            db.execute(
                'INSERT INTO Books (club_id, title, author, cover_url, is_active) VALUES (?, ?, ?, ?, 1)',
                (club_id, book_title, author, cover_url)
            )
            db.commit()
            flash('Active book set successfully! You can now configure its chapters and target deadline.')
            return redirect(url_for('admin.manage_club', club_id=club_id))

        # 4. Set up book chapters and target reading deadline
        elif action == 'setup_book':
            book_id = request.form.get('book_id')
            try:
                total_chapters = int(request.form.get('total_chapters', 0))
                if total_chapters < 1:
                    raise ValueError
            except ValueError:
                flash('Total chapters must be a number greater than 0.')
                return redirect(url_for('admin.manage_club', club_id=club_id))

            has_prologue = 1 if request.form.get('has_prologue') else 0
            has_epilogue = 1 if request.form.get('has_epilogue') else 0
            target_deadline = request.form.get('target_deadline') or None

            # Update active book details in Books table
            db.execute(
                '''UPDATE Books 
                   SET total_chapters = ?, has_prologue = ?, has_epilogue = ?, target_deadline = ? 
                   WHERE id = ? AND club_id = ?''', 
                (total_chapters, has_prologue, has_epilogue, target_deadline, book_id, club_id)
            )
            db.commit()
            flash('Book details set up successfully!')
            return redirect(url_for('admin.manage_club', club_id=club_id))

    # Fetch the club's latest poll (active OR closed)
    latest_poll = db.execute(
        'SELECT * FROM BookPolls WHERE club_id = ? ORDER BY created_at DESC LIMIT 1', 
        (club_id,)
    ).fetchone()

    # Calculate poll tallies using a LEFT JOIN so books with 0 votes are included
    poll_results = []
    if latest_poll:
        poll_results = db.execute(
            '''SELECT pn.id, pn.title, pn.author, pn.cover_url, COUNT(pv.id) AS vote_count
               FROM PollNominations pn
               LEFT JOIN PollVotes pv ON pn.id = pv.nomination_id
               WHERE pn.poll_id = ?
               GROUP BY pn.id
               ORDER BY vote_count DESC''',
            (latest_poll['id'],)
        ).fetchall()

    # Get the club's active book
    active_book = db.execute(
        'SELECT * FROM Books WHERE club_id = ? AND is_active = 1 ORDER BY created_at DESC LIMIT 1', 
        (club_id,)
    ).fetchone()

    # Get all members of the club
    members = db.execute(
        '''SELECT Users.id, Users.username, Users.email 
           FROM Users JOIN ClubMemberships ON Users.id = ClubMemberships.user_id 
           WHERE ClubMemberships.club_id = ?''', 
        (club_id,)
    ).fetchall()

    return render_template(
        'manage_club.html', 
        club=club, 
        latest_poll=latest_poll,
        poll_results=poll_results,
        active_book=active_book, 
        members=members,
        search_results=search_results,
        search_query=search_query
    )

@admin_bp.route('/clubs/<int:club_id>/progress/update', methods=['POST'])
def update_progress(club_id):
    """
    Saves the checkbox status for chapter progress.
    """
    # Check if the user is logged in
    if not _require_login():
        return redirect(url_for('auth.login'))

    # Extract book information from the request form
    book_id = request.form.get('book_id')
    chapter_num = request.form.get('chapter_num')
    is_completed = 1 if request.form.get('is_completed') else 0

    # Add the row in ChapterProgress or update existing row
    db = get_db()
    if is_completed:
        db.execute('INSERT INTO ChapterProgress (user_id, book_id, chapter_num, is_completed) VALUES (?, ?, ?, ?) ON CONFLICT(user_id, book_id, chapter_num) DO UPDATE SET is_completed = 1',
        (session['user_id'], book_id, chapter_num, is_completed))
    else:
        db.execute(
            'DELETE FROM ChapterProgress WHERE user_id = ? AND book_id = ? AND chapter_num = ?',
            (session['user_id'], book_id, chapter_num)
        )
    db.commit()

    return redirect(url_for('club.view_club', club_id=club_id))