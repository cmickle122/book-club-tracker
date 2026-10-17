SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS Users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS BookClubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    genre TEXT,
    is_private INTEGER DEFAULT 0,
    passcode TEXT,
    admin_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES Users (id)
);

CREATE TABLE IF NOT EXISTS ClubMemberships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    club_id INTEGER NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users (id),
    FOREIGN KEY (club_id) REFERENCES BookClubs (id),
    UNIQUE(user_id, club_id)
);

CREATE TABLE IF NOT EXISTS Books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    cover_url TEXT,
    total_chapters INTEGER DEFAULT 0,
    has_prologue INTEGER DEFAULT 0,
    has_epilogue INTEGER DEFAULT 0,
    target_deadline DATE,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES BookClubs (id)
);

CREATE TABLE IF NOT EXISTS BookPolls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES BookClubs (id)
);

CREATE TABLE IF NOT EXISTS PollNominations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poll_id INTEGER NOT NULL,
    nominated_by INTEGER NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    cover_url TEXT,
    FOREIGN KEY (poll_id) REFERENCES BookPolls (id),
    FOREIGN KEY (nominated_by) REFERENCES Users (id)
);

CREATE TABLE IF NOT EXISTS PollVotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    poll_id INTEGER NOT NULL,
    nomination_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (poll_id) REFERENCES BookPolls (id),
    FOREIGN KEY (nomination_id) REFERENCES PollNominations (id),
    FOREIGN KEY (user_id) REFERENCES Users (id),
    UNIQUE(poll_id, user_id)
);

CREATE TABLE IF NOT EXISTS ChapterProgress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    chapter_num INTEGER NOT NULL,
    is_completed INTEGER DEFAULT 1,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users (id),
    FOREIGN KEY (book_id) REFERENCES Books (id),
    UNIQUE(user_id, book_id, chapter_num)
);

CREATE TABLE IF NOT EXISTS DiscussionPosts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    club_id INTEGER NOT NULL,
    book_id INTEGER NOT NULL,
    chapter_num INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (club_id) REFERENCES BookClubs (id),
    FOREIGN KEY (book_id) REFERENCES Books (id),
    FOREIGN KEY (user_id) REFERENCES Users (id)
);

-- ==============================================================================
-- ADD EXTRA TABLES BELOW IF NEEDED
-- ==============================================================================


"""
