import sqlite3
import os
from werkzeug.security import generate_password_hash
from app.models import SCHEMA_SQL

DB_PATH = 'bookclub.db'

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript(SCHEMA_SQL)

    print("Seeding database...")

    # 1. Create users
    cursor.execute('''
        INSERT OR IGNORE INTO Users (id, username, email, password_hash)
        VALUES (?, ?, ?, ?)
    ''', (1, 'admin_user', 'admin@test.com', generate_password_hash('password123')))

    cursor.execute('''
        INSERT OR IGNORE INTO Users (id, username, email, password_hash)
        VALUES (?, ?, ?, ?)
    ''', (2, 'regular_user', 'user@test.com', generate_password_hash('password123')))

    cursor.execute('''
        INSERT OR IGNORE INTO Users (id, username, email, password_hash)
        VALUES (?, ?, ?, ?)
    ''', (3, 'regular_user1', 'user1@test.com', generate_password_hash('password123')))

    cursor.execute('''
        INSERT OR IGNORE INTO Users (id, username, email, password_hash)
        VALUES (?, ?, ?, ?)
    ''', (4, 'regular_user2', 'user2@test.com', generate_password_hash('password123')))

    cursor.execute('''
        INSERT OR IGNORE INTO Users (id, username, email, password_hash)
        VALUES (?, ?, ?, ?)
    ''', (5, 'regular_user3', 'user3@test.com', generate_password_hash('password123')))

    cursor.execute('''
        INSERT OR IGNORE INTO Users (id, username, email, password_hash)
        VALUES (?, ?, ?, ?)
    ''', (6, 'regular_user4', 'user4@test.com', generate_password_hash('password123')))

    cursor.execute('''
        INSERT OR IGNORE INTO Users (id, username, email, password_hash)
        VALUES (?, ?, ?, ?)
    ''', (7, 'regular_user5', 'user5@test.com', generate_password_hash('password123')))

    # 2. Create sample book clubs
    cursor.execute('''
        INSERT OR IGNORE INTO BookClubs (id, name, description, genre, is_private, passcode, admin_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (1, 'Sci-Fi & Fantasy Enthusiasts', 'A community reading group for sci-fi lovers.', 'Sci-Fi', 0, '', 1))

    cursor.execute('''
        INSERT OR IGNORE INTO BookClubs (id, name, description, genre, is_private, passcode, admin_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (2, 'Mystery & Mayhem Society', 'A group dedicated to whodunits and detective fiction.', 'Mystery', 0, '', 3))

    cursor.execute('''
        INSERT OR IGNORE INTO BookClubs (id, name, description, genre, is_private, passcode, admin_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (3, 'Starlight Romance & Drama', 'Exploring contemporary drama and romantic comedy.', 'Romance', 1, 'secret123', 4))

    cursor.execute('''
        INSERT OR IGNORE INTO BookClubs (id, name, description, genre, is_private, passcode, admin_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (4, 'Chronicles & History Guild', 'Immersing ourselves in rich historical settings.', 'Historical Fiction', 0, '', 5))

    # 3. Add memberships
    memberships = [(1, 1), (2, 1), (3, 2), (4, 2), (5, 2), (4, 3), (6, 3), (5, 4), (7, 4)]
    cursor.executemany('INSERT OR IGNORE INTO ClubMemberships (user_id, club_id) VALUES (?, ?)', memberships)

    # 4. Create active polls (id, club_id, title, is_active)
    polls = [
        (1, 2, "Vote for Next Month's Mystery", 0),
        (2, 4, 'Select Winter Historical Selection', 1)
    ]
    cursor.executemany('INSERT OR IGNORE INTO BookPolls (id, club_id, title, is_active) VALUES (?, ?, ?, ?)', polls)

    # 5. Create poll nominations (id, poll_id, nominated_by, title, author, cover_url)
    nominations = [
        (1, 1, 3, 'The Silent Patient', 'Alex Michaelides', 'https://covers.openlibrary.org/b/isbn/9781250301697-M.jpg'),
        (2, 1, 4, 'The Thursday Murder Club', 'Richard Osman', 'https://covers.openlibrary.org/b/isbn/9781984880963-M.jpg'),
        (3, 1, 5, 'And Then There Were None', 'Agatha Christie', 'https://covers.openlibrary.org/b/isbn/9780062073488-M.jpg'),
        (4, 2, 5, 'All the Light We Cannot See', 'Anthony Doerr', 'https://covers.openlibrary.org/b/isbn/9781476746586-M.jpg'),
        (5, 2, 7, 'Wolf Hall','Hilary Mantel', 'https://covers.openlibrary.org/b/isbn/9780312429980-M.jpg')
    ]
    cursor.executemany('INSERT OR IGNORE INTO PollNominations (id, poll_id, nominated_by, title, author, cover_url) VALUES (?, ?, ?, ?, ?, ?)', nominations)

    # 6. Add test poll votes (poll_id, nomination_id, user_id)
    votes = [(1, 1, 3), (1, 1, 4)]
    cursor.executemany('INSERT OR IGNORE INTO PollVotes (poll_id, nomination_id, user_id) VALUES (?, ?, ?)', votes)

    # 7. Create book setups in clubs ( id, club_id, title, author, cover_url, total_chapters, has_prologue, has_epilogue, target_deadline, is_active)
    books = [
        (1, 1, 'Dune', 'Frank Herbert', 'https://covers.openlibrary.org/b/isbn/9780441172719-M.jpg', 12, 1, 0, '2026-11-30', 1),
        (2, 3, 'Pride and Prejudice', 'Jane Austen', 'https://covers.openlibrary.org/b/isbn/9780141439518-M.jpg', 61, 0, 0, '2026-12-15', 1),
        (3, 4, 'The Book Thief', 'Markus Zusak', 'https://covers.openlibrary.org/b/isbn/9780375842207-M.jpg', 10, 1, 1, '2026-10-01', 0)
    ]
    cursor.executemany('INSERT OR IGNORE INTO Books (id, club_id, title, author, cover_url, total_chapters, has_prologue, has_epilogue, target_deadline, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', books)

    # 8. Seed chapter progress (user_id, book_id, highest_chapter_completed)
    progress = [(1, 1, 2), (2, 1, 5), (4, 2, 2), (6, 2, 5)]
    cursor.executemany('INSERT OR IGNORE INTO UserBookProgress (user_id, book_id, highest_chapter_completed) VALUES (?, ?, ?)', progress)

    conn.commit()
    conn.close()
    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()