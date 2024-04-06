CREATE TABLE IF NOT EXISTS users (
    name TEXT,
    username TEXT UNIQUE NOT NULL PRIMARY KEY,
    password TEXT NOT NULL,
    isAdmin TEXT,
    email TEXT,
    bio TEXT
);