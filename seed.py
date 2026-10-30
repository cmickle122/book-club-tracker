import sqlite3
import os
from werkzeug.security import generate_password_hash

# Path to database
DB_PATH = 'bookclub.db'

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Seeding database...")

    # 1. Create users (admin and regular members)
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
    # Club 1 members
    cursor.execute('''
        INSERT OR IGNORE INTO ClubMemberships (user_id, club_id) VALUES (?, ?)
    ''', (1, 1))

    cursor.execute('''
        INSERT OR IGNORE INTO ClubMemberships (user_id, club_id) VALUES (?, ?)
    ''', (2, 1))

    # Club 2 members
    cursor.execute('''
        INSERT OR IGNORE INTO ClubMemberships (user_id, club_id) VALUES (?, ?)
    ''', (3, 2))

    cursor.execute('''
        INSERT OR IGNORE INTO ClubMemberships (user_id, club_id) VALUES (?, ?)
    ''', (4, 2))

    cursor.execute('''
        INSERT OR IGNORE INTO ClubMemberships (user_id, club_id) VALUES (?, ?)
    ''', (5, 2))

    # Club 3 members
    cursor.execute('''
        INSERT OR IGNORE INTO ClubMemberships (user_id, club_id) VALUES (?, ?)
    ''', (4, 3))

    cursor.execute('''
        INSERT OR IGNORE INTO ClubMemberships (user_id, club_id) VALUES (?, ?)
    ''', (6, 3))

    # Club 4 members
    cursor.execute('''
        INSERT OR IGNORE INTO ClubMemberships (user_id, club_id) VALUES (?, ?)
    ''', (5, 4))

    cursor.execute('''
        INSERT OR IGNORE INTO ClubMemberships (user_id, club_id) VALUES (?, ?)
    ''', (7, 4))

    # 4. Create active polls
    cursor.execute('''
        INSERT OR IGNORE INTO BookPolls (id, club_id, title, is_active)
        VALUES (?, ?, ?, ?)
    ''', (1, 1, 'November 2026 Book Selection', 1))

    cursor.execute('''
        INSERT OR IGNORE INTO BookPolls (id, club_id, title, is_active)
        VALUES (?, ?, ?, ?)
    ''', (2, 2, 'Vote for Next Month\'s Mystery', 1))

    cursor.execute('''
        INSERT OR IGNORE INTO BookPolls (id, club_id, title, is_active)
        VALUES (?, ?, ?, ?)
    ''', (3, 4, 'Select Winter Historical Selection', 1))

    # 5. Create poll nominations
    nominations = [
        (1, 1, 1, 'Dune', 'Frank Herbert', ''),
        (2, 1, 2, 'Neuromancer', 'William Gibson', ''),
        (3, 1, 1, 'Foundation', 'Isaac Asimov', ''),
        (4, 2, 3, 'The Silent Patient', 'Alex Michaelides', ''),
        (5, 2, 4, 'The Thursday Murder Club', 'Richard Osman', ''),
        (6, 2, 5, 'And Then There Were None', 'Agatha Christie', ''),
        (7, 3, 5, 'All the Light We Cannot See', 'Anthony Doerr', ''),
        (8, 3, 6, 'Wolf Hall', 'Hilary Mantel', '')
    ]
    for nom in nominations:
        cursor.execute('''
            INSERT OR IGNORE INTO PollNominations (id, poll_id, nominated_by, title, author, cover_url)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', nom)

    # 6. Add test poll votes
    cursor.execute('''
        INSERT OR IGNORE INTO PollVotes (poll_id, nomination_id, user_id)
        VALUES (?, ?, ?)
    ''', (1, 1, 1))  # Admin votes for Dune in Club 1

    cursor.execute('''
        INSERT OR IGNORE INTO PollVotes (poll_id, nomination_id, user_id)
        VALUES (?, ?, ?)
    ''', (1, 1, 2))  # Regular user votes for Dune in Club 1

    cursor.execute('''
        INSERT OR IGNORE INTO PollVotes (poll_id, nomination_id, user_id)
        VALUES (?, ?, ?)
    ''', (2, 4, 3))  # regular_user1 votes for The Silent Patient in Club 2

    cursor.execute('''
        INSERT OR IGNORE INTO PollVotes (poll_id, nomination_id, user_id)
        VALUES (?, ?, ?)
    ''', (2, 5, 4))  # regular_user2 votes for The Thursday Murder Club in Club 2

    # 7. Create book setups in clubs (active and archived)
    cursor.execute('''
        INSERT OR IGNORE INTO Books (id, club_id, title, author, cover_url, total_chapters, has_prologue, has_epilogue, target_deadline, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (1, 1, 'Dune', 'Frank Herbert', '', 12, 1, 0, '2026-11-30', 1))

    cursor.execute('''
        INSERT OR IGNORE INTO Books (id, club_id, title, author, cover_url, total_chapters, has_prologue, has_epilogue, target_deadline, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (2, 3, 'Pride and Prejudice', 'Jane Austen', '', 61, 0, 0, '2026-12-15', 1))

    cursor.execute('''
        INSERT OR IGNORE INTO Books (id, club_id, title, author, cover_url, total_chapters, has_prologue, has_epilogue, target_deadline, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (3, 4, 'The Book Thief', 'Markus Zusak', '', 10, 1, 1, '2026-10-01', 0))

    # 8. Seed chapter progress for active books using UserBookProgress
    # Club 1 (Book 1: Dune) - Admin read to Chapter 2, Regular user read to Chapter 5
    cursor.execute('''
        INSERT OR IGNORE INTO UserBookProgress (user_id, book_id, highest_chapter_completed)
        VALUES (?, ?, ?)
    ''', (1, 1, 2))

    cursor.execute('''
        INSERT OR IGNORE INTO UserBookProgress (user_id, book_id, highest_chapter_completed)
        VALUES (?, ?, ?)
    ''', (2, 1, 5))

    # Club 3 (Book 2: Pride and Prejudice) - User 4 read to Chapter 2, User 6 read to Chapter 5
    cursor.execute('''
        INSERT OR IGNORE INTO UserBookProgress (user_id, book_id, highest_chapter_completed)
        VALUES (?, ?, ?)
    ''', (4, 2, 2))

    cursor.execute('''
        INSERT OR IGNORE INTO UserBookProgress (user_id, book_id, highest_chapter_completed)
        VALUES (?, ?, ?)
    ''', (6, 2, 5))
    
    conn.commit()
    conn.close()
    print("Database seeded successfully!")

if __name__ == '__main__':
    seed_database()