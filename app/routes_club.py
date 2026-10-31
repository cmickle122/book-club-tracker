from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests, os
from app.db import (
    get_club_by_id,
    get_active_book,
    get_active_poll,
    get_club_members,
    get_user_chapter_progress,
    get_poll_results, 
    get_user_completed_chapters,
    get_user_max_chapter,
    add_discussion_post,
    get_discussion_posts,
    is_club_member,
    remove_club_member
)

club_bp = Blueprint('club', __name__)

@club_bp.route('/clubs/<int:club_id>', methods=['GET', 'POST'])
def view_club(club_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    club = get_club_by_id(club_id)
    if not club:
        flash('Club not found.')
        return redirect(url_for('auth.dashboard'))

    is_member = is_club_member(session['user_id'], club_id)
    is_admin = (club['admin_id'] == session['user_id'])

    if club['is_private'] and not is_member:
        flash('Access Denied: You cannot view a private club. You must join with a passcode to view its content.')
        return redirect(url_for('auth.search_clubs'))

    active_book = get_active_book(club_id)

    my_progress = {'completed': 0, 'total': 0, 'pct': 0}
    chapters = []

    if active_book:
        total_chapters = active_book['total_chapters'] or 0
        has_prologue = 1 if active_book['has_prologue'] else 0
        has_epilogue = 1 if active_book['has_epilogue'] else 0

        total_units = total_chapters + has_prologue + has_epilogue
        
        # Calculate reading progress metrics ONLY for active members
        if is_member:
            completed = get_user_completed_chapters(session['user_id'], active_book['id'], has_prologue)
            pct = round((completed / total_units) * 100) if total_units > 0 else 0
            highest_ch = get_user_max_chapter(session['user_id'], active_book['id'])

            my_progress = {
                'completed': completed, 
                'total': total_units, 
                'pct': pct, 
                'highest_chapter': highest_ch if highest_ch is not None else -1
            }

        if has_prologue:
            chapters.append(0) 
        for ch in range(1, total_chapters + 1):
            chapters.append(ch)
        if has_epilogue:
            chapters.append(total_chapters + 1) 

    active_poll = get_active_poll(club_id)
    nominations = get_poll_results(active_poll['id']) if active_poll else []

    # Handle Google Books API Search when submitting from club.html (Members Only)
    search_results = []
    search_query = ''

    if request.method == 'POST' and request.form.get('action') == 'search_books' and is_member:
        search_query = request.form.get('search_query', '').strip()
        if search_query:
            try:
                api_url = "https://www.googleapis.com/books/v1/volumes"
                headers = {'User-Agent': 'Mozilla/5.0'}
                params = {'q': search_query, 'maxResults': 6}

                api_key = os.environ.get('GOOGLE_BOOKS_API_KEY')
                print("KEY LOADED:", bool(api_key))
                if api_key:
                    params['key'] = api_key

                res = requests.get(api_url, params=params, headers=headers, timeout=10)
                print("STATUS:", res.status_code)
                print("BODY:", res.text[:500])

                if res.status_code == 200:
                    data = res.json()
                    items = data.get('items', [])
                    for item in items:
                        volume_info = item.get('volumeInfo', {})
                        title = volume_info.get('title', 'Unknown Title')
                        authors_list = volume_info.get('authors', [])
                        author = ", ".join(authors_list) if authors_list else 'Unknown Author'
                        image_links = volume_info.get('imageLinks', {})
                        cover_url = image_links.get('thumbnail') or image_links.get('smallThumbnail') or ''
                        if cover_url.startswith('http://'):
                            cover_url = 'https://' + cover_url[7:]

                        search_results.append({
                            'title': title,
                            'author': author,
                            'cover_url': cover_url
                        })
                    if not search_results:
                        flash(f'No books found matching "{search_query}".')
                else:
                    flash(f'Google Books API error (status {res.status_code}).')
            except Exception as e:
                print("EXCEPTION:", repr(e))
                flash(f'Error fetching results from Google Books API: {str(e)}')

    members = get_club_members(club_id)

    return render_template(
        'club.html',
        club=club,
        active_book=active_book,
        my_progress=my_progress,
        chapters=chapters,
        active_poll=active_poll,
        nominations=nominations,
        members=members,
        is_admin=is_admin,
        is_member=is_member,
        search_results=search_results,
        search_query=search_query
    )

@club_bp.route('/clubs/<int:club_id>/discussion/<int:chapter_num>', methods=['GET', 'POST'])
def view_discussion(club_id, chapter_num):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    club = get_club_by_id(club_id)
    active_book = get_active_book(club_id)
    if not club or not active_book:
        flash('Club or active book not found')
        return redirect(url_for('auth.dashboard'))

    if club['is_private'] and not is_club_member(session['user_id'], club_id):
        flash('Access Denied: You cannot view a private club. You must join with a passcode to view its content.')
        return redirect(url_for('auth.search_clubs'))

    if active_book['is_active'] == 0:
        flash('This book is archived. Read-only mode.')
        if request.method == 'POST':
            return redirect(url_for('club.view_discussion', club_id=club_id, chapter_num=chapter_num))

    max_completed = get_user_max_chapter(session['user_id'], active_book['id'])

    if request.method == 'POST':
        if active_book['is_active'] == 0:
            flash('This book is archived. Read-only mode.')
            return redirect(url_for('club.view_discussion', club_id=club_id, chapter_num=chapter_num))
        content = request.form.get('content','').strip()
        if content:
            add_discussion_post(club_id, active_book['id'], chapter_num, session['user_id'], content)
        return redirect(url_for('club.view_discussion', club_id=club_id, chapter_num=chapter_num))

    posts = get_discussion_posts(club_id, active_book['id'], chapter_num)

    return render_template(
        'discussion.html',
        club=club,
        active_book=active_book,
        book=active_book,
        club_id=club_id,
        chapter_num=chapter_num,
        posts=posts,
        is_archived=(active_book['is_active'] == 0),
        max_completed=max_completed,
    )

@club_bp.route('/clubs/<int:club_id>/leave', methods=['POST'])
def leave_club(club_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    club = get_club_by_id(club_id)
    if not club:
        flash('Club not found.')
        return redirect(url_for('auth.dashboard'))

    if club['admin_id'] == session['user_id']:
        flash('Admins cannot leave their own club.')
        return redirect(url_for('club.view_club', club_id=club_id))

    if not is_club_member(session['user_id'], club_id):
        flash('You are not a member of this club.')
        return redirect(url_for('club.view_club', club_id=club_id))

    remove_club_member(session['user_id'], club_id)
    flash('You left the club.')
    return redirect(url_for('auth.dashboard'))

@club_bp.route('/clubs/<int:club_id>/kick/<int:user_id>', methods=['POST'])
def kick_member(club_id, user_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    club = get_club_by_id(club_id)
    if not club or club['admin_id'] != session['user_id']:
        flash('Only admin can kick members')
        return redirect(url_for('club.view_club', club_id=club_id))
    if user_id == club['admin_id']:
        flash('Cannot kick yourself (admin)')
        return redirect(url_for('club.view_club', club_id=club_id))
    
    remove_club_member(user_id, club_id)
    flash('Member kicked')
    return redirect(url_for('club.view_club', club_id=club_id))
