from flask import Blueprint, render_template, request, redirect, url_for, session, flash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/clubs/<int:club_id>/poll/nominate', methods=['POST'])
def nominate_book(club_id):
    """DEVELOPER 2: Nominate Candidate Book for Active Poll"""
    # Write your code here:
    # 1. Extract title, author, cover_url from request.form
    # 2. Fetch active poll_id for club_id from BookPolls
    # 3. Insert into PollNominations (poll_id, nominated_by=session['user_id'], title, author, cover_url)
    # 4. Redirect to url_for('club.view_club', club_id=club_id)
    # To here.
    return redirect(url_for('club.view_club', club_id=club_id))

@admin_bp.route('/clubs/<int:club_id>/poll/vote', methods=['POST'])
def vote_poll(club_id):
    """DEVELOPER 2: Record User Vote in Book Poll"""
    # Write your code here:
    # 1. Extract nomination_id and poll_id from request.form
    # 2. Insert into PollVotes (poll_id, nomination_id, user_id=session['user_id'])
    # 3. Catch UNIQUE constraint if user already voted in this poll
    # 4. Redirect back to club page
    # To here.
    return redirect(url_for('club.view_club', club_id=club_id))

@admin_bp.route('/clubs/<int:club_id>/manage', methods=['GET', 'POST'])
def manage_club(club_id):
    """DEVELOPER 2: Admin Setup Panel & Google Books API Integration"""
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
        # To here.
        return redirect(url_for('admin.manage_club', club_id=club_id))

    return f"<h1>Admin Management Panel for Club #{club_id} (Developer 2 Placeholder)</h1>"

@admin_bp.route('/clubs/<int:club_id>/progress/update', methods=['POST'])
def update_progress(club_id):
    """DEVELOPER 2: Save Chapter Progress Checkbox Status"""
    # Write your code here:
    # 1. Extract book_id, chapter_num, is_completed from request.form
    # 2. Insert or Update row in ChapterProgress (user_id=session['user_id'], book_id, chapter_num, is_completed)
    # 3. Return JSON response or redirect back to club page
    # To here.
    return redirect(url_for('club.view_club', club_id=club_id))
