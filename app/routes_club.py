from flask import Blueprint, render_template, request, redirect, url_for, session, flash

club_bp = Blueprint('club', __name__)

@club_bp.route('/clubs/<int:club_id>')
def view_club(club_id):
    """DEVELOPER 3: Individual Club Page (Book Banner, Progress Tracker, Polls)"""
    # Write your code here:
    # 1. Fetch club details from BookClubs
    # 2. Fetch active book from Books where club_id = club_id AND is_active = 1
    # 3. Fetch user chapter progress from ChapterProgress
    # 4. Fetch active voting poll and candidate nominations
    # 5. Render 'club.html' template
    # To here.
    return f"<h1>Individual Club Page #{club_id} (Developer 3 Placeholder)</h1>"

@club_bp.route('/clubs/<int:club_id>/discussion/<int:chapter_num>', methods=['GET', 'POST'])
def view_discussion(club_id, chapter_num):
    """DEVELOPER 3: Spoiler-Protected Chapter Discussion Thread"""
    if request.method == 'POST':
        # Write your code here:
        # 1. Check if active book is archived (is_active == 0)
        # 2. If archived, block post creation and flash 'This book is archived. Read-only mode.'
        # 3. If active, extract post content from request.form
        # 4. Insert into DiscussionPosts (club_id, book_id, chapter_num, user_id=session['user_id'], content)
        # 5. Redirect back to thread
        # To here.
        return redirect(url_for('club.view_discussion', club_id=club_id, chapter_num=chapter_num))

    return f"<h1>Discussion Thread for Chapter #{chapter_num} in Club #{club_id} (Developer 3 Placeholder)</h1>"

@club_bp.route('/clubs/<int:club_id>/leave', methods=['POST'])
def leave_club(club_id):
    """DEVELOPER 3: 1-Click Member Exit"""
    # Write your code here:
    # 1. Execute DELETE FROM ClubMemberships WHERE user_id = session['user_id'] AND club_id = club_id
    # 2. Redirect to url_for('auth.dashboard')
    # To here.
    return redirect(url_for('auth.dashboard'))

@club_bp.route('/clubs/<int:club_id>/members/<int:user_id>/kick', methods=['POST'])
def kick_member(club_id, user_id):
    """DEVELOPER 3: Admin Kick Member Action"""
    # Write your code here:
    # 1. Verify session['user_id'] is the admin_id of the club
    # 2. Execute DELETE FROM ClubMemberships WHERE user_id = user_id AND club_id = club_id
    # 3. Redirect back to admin management page or club page
    # To here.
    return redirect(url_for('admin.manage_club', club_id=club_id))
