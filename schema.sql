CREATE TABLE IF NOT EXISTS users (
    username TEXT UNIQUE NOT NULL,
    name TEXT,
    password TEXT NOT NULL,
    email TEXT,
    bio TEXT,
    isAdmin TEXT,
    CONSTRAINT username_unique UNIQUE (username)
);

CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    section_id INTEGER NOT NULL,
    description TEXT,
    copies INTEGER NOT NULL,
    rating REAL DEFAULT 0,
    ratingCount INTEGER DEFAULT 0,
    CONSTRAINT section_fk FOREIGN KEY (section_id) REFERENCES sections(id)
);

CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    CONSTRAINT name_unique UNIQUE (name)
);
