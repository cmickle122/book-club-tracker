from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.db import (
    is_club_member,
    get_active_poll,
    add_nomination,
    record_vote,
    get_club_by_id,
    close_poll,
    set_active_book,
    setup_book_details,
    get_latest_poll,
    get_poll_results,
    get_pending_closed_poll,
    get_active_book,
    get_club_members,
    save_user_progress,
    archive_active_book,
    create_poll,
    update_club_settings
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
    Allows a user to nominate a candidate book for an active poll. 
    Receives title, author, and cover_url from the Google Books search card.
    """
    if not _require_login():
        return redirect(url_for('auth.login'))

    if not is_club_member(session['user_id'], club_id):
        flash('You must be a member of this club to nominate books.')
        return redirect(url_for('club.view_club', club_id=club_id))

    title = request.form.get('title', '').strip()
    author = request.form.get('author', '').strip()
    cover_url = request.form.get('cover_url', '').strip()

    poll = get_active_poll(club_id)
    if not poll or not title or not author:
        flash('Invalid nomination details.')
        return redirect(url_for('club.view_club', club_id=club_id))

    add_nomination(poll['id'], session['user_id'], title, author, cover_url)
    flash('Book nominated successfully!')
    return redirect(url_for('club.view_club', club_id=club_id))


@admin_bp.route('/clubs/<int:club_id>/poll/vote', methods=['POST'])
def vote_poll(club_id):
    """
    Records user votes in book poll.
    """
    # Check if the user is logged in
    if not _require_login():
        return redirect(url_for('auth.login'))

    if not is_club_member(session['user_id'], club_id):
        flash('You must be a member of this club to vote.')
        return redirect(url_for('club.view_club', club_id=club_id))

    poll = get_active_poll(club_id)
    if not poll:
        flash('Voting is closed for this poll.')
        return redirect(url_for('club.view_club', club_id=club_id))

    nomination_id = request.form.get('nomination_id', type=int)
    valid_ids = [n['id'] for n in get_poll_results(poll['id'])]
    if nomination_id not in valid_ids:
        flash('Invalid nomination.')
        return redirect(url_for('club.view_club', club_id=club_id))

    if record_vote(poll['id'], nomination_id, session['user_id']):
        flash('Vote registered successfully!')
    else:
        flash('You have already voted in this poll.')

    return redirect(url_for('club.view_club', club_id=club_id))


@admin_bp.route('/clubs/<int:club_id>/manage', methods=['GET', 'POST'])
def manage_club(club_id):
    """
    Admin control panel: Manage Polls -> 1-Click Winner Selection -> Chapter Setup -> Archive Read
    """
    if not _require_login():
        return redirect(url_for('auth.login'))

    club = get_club_by_id(club_id)

    if not club or club['admin_id'] != session['user_id']:
        flash('Access denied. Admin permissions required.')
        return redirect(url_for('club.view_club', club_id=club_id))

    if request.method == 'POST':
        action = request.form.get('action')

        # Close Active Poll
        if action == 'close_poll':
            poll_id = request.form.get('poll_id')
            if poll_id:
                close_poll(poll_id, club_id)
                flash('The poll has closed! Voting is locked and final results are displayed.')
            return redirect(url_for('admin.manage_club', club_id=club_id))

        # Create New Poll
        elif action == 'create_poll':
            poll_title = request.form.get('poll_title', '').strip()
            if not poll_title:
                flash('Please enter a title for the new poll.')
            else:
                create_poll(club_id, poll_title)
                flash('New book poll created successfully!')
            return redirect(url_for('admin.manage_club', club_id=club_id))

        # Select Candidate Book (from closed poll results)
        elif action == 'select_book':
            book_title = request.form.get('book_title', '').strip()
            author = request.form.get('author', '').strip()
            cover_url = request.form.get('cover_url', '').strip()

            if not book_title or not author:
                flash('Invalid book selection. Title and author are required.')
                return redirect(url_for('admin.manage_club', club_id=club_id))

            set_active_book(club_id, book_title, author, cover_url)
            flash('Active book set successfully! Configure its chapters and target deadline below.')
            return redirect(url_for('admin.manage_club', club_id=club_id))

        # Set up and edit chapters & target deadline
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
            flash('Book details saved successfully!')
            return redirect(url_for('admin.manage_club', club_id=club_id))

        # End Active Book & Archive
        elif action == 'end_book':
            archive_active_book(club_id)
            flash('The active book has been finished and moved to archives!')
            return redirect(url_for('admin.manage_club', club_id=club_id))


        # Update Club Details & Privacy Settings
        elif action == 'update_club_details':
            name = request.form.get('name', '').strip()
            description = request.form.get('description', '').strip()
            genre = request.form.get('genre', '').strip()
            is_private = 1 if request.form.get('is_private') == '1' else 0
            passcode = request.form.get('passcode', '').strip() if is_private else ''

            if not name or not description or not genre:
                flash('Club name, description, and genre cannot be empty.')
            elif is_private and not passcode:
                flash('Private clubs require a passcode.')
            else:
                update_club_settings(club_id, name, description, genre, is_private, passcode)
                flash('Club settings updated successfully!')
            return redirect(url_for('admin.manage_club', club_id=club_id))


    active_book = get_active_book(club_id)
    active_poll = get_active_poll(club_id)
    latest_poll = get_latest_poll(club_id)
    
    pending_closed_poll = None
    poll_results = []
    
    if active_poll:
        poll_results = get_poll_results(active_poll['id'])
    elif not active_book:
        pending_closed_poll = get_pending_closed_poll(club_id)
        if pending_closed_poll:
            poll_results = get_poll_results(pending_closed_poll['id'])

    members = get_club_members(club_id)

    return render_template(
        'manage_club.html', 
        club=club, 
        active_poll=active_poll,
        latest_poll=latest_poll,
        pending_closed_poll=pending_closed_poll,
        poll_results=poll_results,
        active_book=active_book, 
        members=members
    )

@admin_bp.route('/clubs/<int:club_id>/progress/update', methods=['POST'])
def update_progress(club_id):
    """
    Saves the checkbox status for chapter progress.
    """
    # Check if the user is logged in
    if not _require_login():
        return redirect(url_for('auth.login'))

    if not is_club_member(session['user_id'], club_id):
        flash('You must be a member of this club.')
        return redirect(url_for('club.view_club', club_id=club_id))

    active_book = get_active_book(club_id)
    try:
        book_id = int(request.form.get('book_id'))
        highest_chapter = int(request.form.get('highest_chapter'))
    except (TypeError, ValueError):
        flash('Invalid progress update.')
        return redirect(url_for('club.view_club', club_id=club_id))

    max_ch = 0
    if active_book:
        max_ch = active_book['total_chapters'] + (1 if active_book['has_epilogue'] else 0)

    if not active_book or active_book['id'] != book_id or not -1 <= highest_chapter <= max_ch:
        flash('Invalid progress update.')
        return redirect(url_for('club.view_club', club_id=club_id))

    save_user_progress(session['user_id'], book_id, highest_chapter)
    return redirect(url_for('club.view_club', club_id=club_id))