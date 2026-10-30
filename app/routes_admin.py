from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests
from app.db import (
    get_active_poll,
    add_nomination,
    record_vote,
    get_club_by_id,
    close_poll,
    set_active_book,
    setup_book_details,
    get_latest_poll,
    get_poll_results,
    get_active_book,
    get_club_members,
    save_user_progress,
)

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

    poll = get_active_poll(club_id)

    if poll and title:
        add_nominations(poll['id'], session['user_id'], title, author, cover_url)
        flash('Your book as been nominated!')
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

    if record_vote(poll_id, nomination_id, session['user_id']):
        flash('Vote registered successfully!')
    else:
        flash('You have already voted in this poll.')

    return redirect(url_for('club.view_club', club_id=club_id))


@admin_bp.route('/clubs/<int:club_id>/manage', methods=['GET', 'POST'])
def manage_club(club_id):
    """
    Admin setup panel: Close Poll -> View Tallies -> Google Books Search -> Select Book -> Chapter Setup
    """
    if not _require_login():
        return redirect(url_for('auth.login'))

    # Helper 1: Fetch club
    club = get_club_by_id(club_id)

    if not club or club['admin_id'] != session['user_id']:
        flash('Access denied. Admin permissions required.')
        return redirect(url_for('club.view_club', club_id=club_id))

    search_results = []
    search_query = ''

    if request.method == 'POST':
        action = request.form.get('action')

        # 1. Close Active Poll
        if action == 'close_poll':
            poll_id = request.form.get('poll_id')
            if poll_id:
                close_poll(poll_id, club_id)
                flash('The poll has closed! Voting is locked and final results are displayed.')
            return redirect(url_for('admin.manage_club', club_id=club_id))

        # 2. Search Google Books API (No DB changes here)
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

        # 3. Select Candidate Book
        elif action == 'select_book':
            # Check if an active poll is still open
            active_poll = get_active_poll(club_id)
            if active_poll:
                flash('Voting is still open! You must close the active poll before selecting a winning book.')
                return redirect(url_for('admin.manage_club', club_id=club_id))

            # Extract the form data
            book_title = request.form.get('book_title', '').strip()
            author = request.form.get('author', '').strip()
            cover_url = request.form.get('cover_url', '').strip()

            # Validate defined book_title
            if not book_title:
                flash('Invalid book selection.')
                return redirect(url_for('admin.manage_club', club_id=club_id))

            set_active_book(club_id, book_title, author, cover_url)
            flash('Active book set successfully! You can now configure its chapters and target deadline.')
            return redirect(url_for('admin.manage_club', club_id=club_id))

        # 4. Set Up Chapters & Target Deadline
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

            setup_book_details(book_id, club_id, total_chapters, has_prologue, has_epilogue, target_deadline)
            flash('Book details set up successfully!')
            return redirect(url_for('admin.manage_club', club_id=club_id))

    # Helper calls for template data loading
    latest_poll = get_latest_poll(club_id)
    poll_results = get_poll_results(latest_poll['id']) if latest_poll else []
    active_book = get_active_book(club_id)
    members = get_club_members(club_id)

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
    highest_chapter = request.form.get('highest_chapter')

    if book_id is not None and highest_chapter is not None:
        save_user_progress(session['user_id'], int(book_id), int(highest_chapter))

    return redirect(url_for('club.view_club', club_id=club_id))