CREATE TABLE users(
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   username TEXT NO NULL UNIQUE,
   email TEXT NO NULL UNIQUE,
   hash TEXT NO NULL,
   institution TEXT,
   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE papers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    authors TEXT,
    year INTEGER,
    tldr TEXT,
    tags TEXT,
    pdf_path TEXT,
    status TEXT NOT NULL DEFAULT 'reading' CHECK (status IN('reading','completed')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE notes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    content TEXT NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(paper_id) REFERENCES papers(id)

);

CREATE TABLE tags(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
   name TEXT NOT NULL UNIQUE
);

CREATE TABLE paper_tags(
    paper_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY(paper_id,tag_id),
    FOREIGN KEY(paper_id) REFERENCES papers(id),
    FOREIGN KEY(tag_id) REFERENCES tags(id)
);

CREATE TABLE ratings(
     id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    stars INTEGER NOT NULL CHECK(stars BETWEEN 1 AND 5),
    FOREIGN KEY(paper_id) REFERENCES papers(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE related_papers(
    paper_id INTEGER NOT NULL,
    related_paper_id INTEGER NOT NULL,
    PRIMARY KEY(paper_id,related_paper_id),
    FOREIGN KEY(paper_id) REFERENCES papers(id),
    FOREIGN KEY(related_paper_id) REFERENCES papers(id)
);

CREATE INDEX idx_papers_user ON papers(user_id);
CREATE INDEX idx_notes_user ON notes(paper_id);
CREATE INDEX idx_papers_status ON papers(status);



