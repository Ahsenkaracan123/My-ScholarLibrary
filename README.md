# My ScholarLibrary

#### Video Demo: <https://youtu.be/Qytex1QsXzQ?si=vf5QAMUNYP1CrBbx>
**Live Demo:** https://my-scholarlibrary.onrender.com

#### Description:

My ScholarLibrary is a personal research management web application built with
Flask, SQLite, JavaScript and Bootstrap. It was created to solve a real problem I
noticed while doing academic research: keeping track of papers, PDFs, and
personal notes across multiple projects quickly becomes overwhelming, and
existing tools like Mendeley are often too heavy, too automated, or rely on
external APIs to fetch papers. My ScholarLibrary takes a simpler approach
every user manually adds their own papers, which means there is no
dependency on any external academic database or API, and the platform stays
lightweight and fully under the user's control.

The core idea behind the project is to give researchers a single place where they can save a paper's title, authors, and
year, attach the actual PDF file, write a one-sentence TL;DR takeaway,
organize papers by custom tags, track whether they are still reading or have
completed a paper, and keep personal notes tied to each paper.My primary goal is to minimze time researchers spend on document and note organization,allowing them to focus directly on academic output. All of this data is stored in a relational SQLite database with seven interconnected tables: users, papers, notes, tags, paper_tags, ratings, and related_papers.

## Features

**User Accounts.** Users can register with a username and password.
Passwords are never stored in plain text; they are hashed using Werkzeug's
`generate_password_hash` before being saved, and verified with
`check_password_hash` during login. Sessions are managed with Flask-Session,
and every protected route is guarded by a custom `login_required` decorator
adapted from CS50's own Finance project, ensuring that a user cannot access
another user's dashboard, papers, or notes simply by guessing a URL.

**Dashboard.** After logging in, users land on a dashboard that shows
real-time statistics: total papers, completed papers, papers currently being
read, and the total number of notes across all papers. These numbers are
calculated live with SQL COUNT queries, including a JOIN between the
notes and papers tables to count notes belonging only to the logged-in
user's papers.

**Adding Papers.** The /add_paper route lets a user enter a paper's title,
authors, publication year, and optionally attach a PDF file. PDF files are
saved to the server's uploads folder using Werkzeug's
secure_filename function to prevent unsafe file names, and the file path
is stored in the database so the PDF can be reopened later directly from the
dashboard.

**Tags.** Instead of a fixed list of categories, users can type any
comma-separated tags they like when adding a paper (for example
"Cybersecurity, NeuralNetworks"). The backend splits this input, checks
whether each tag already exists in the tags table, reuses it if so, or
creates a new one if not, and then links the paper to the tag through the
paper_tags join table a classic many-to-many relationship. This design
means the tagging system is completely open-ended and grows naturally as the
user's research library grows.

**Reading Status.** Each paper has a status of either "reading" or
"completed". A single button on the dashboard toggles the status between the
two, updating the database immediately and refreshing the dashboard
statistics.

**Read and Note.** When users click this button the screen splits view in two.
 The left panel renders the PDF live,right panel allows to take real-time notes directly alongside to paper.
 Every note added in database and users can edit or delete these notes.

**TL;DR Takeaways.** Every paper can have a short, one-sentence takeaway
that is editable at any time. This was one of the most important features to
me personally, because when revisiting old research months later, a
one-line summary is often more useful than trying to remember an entire
paper's argument. The TL;DR box on the dashboard includes an "Update TL;DR"
button that takes the user to the notes page, where the takeaway can be
rewritten and saved instantly.

**Personal Notes.** Beyond the TL;DR, users can write and save longer,
free-form notes for each paper. Notes are stored in their own table, linked
to a paper's ID, and ordered by creation date so the most recent note always
appears first.

**Search and Filtering.** The dashboard includes a live search box where users can find papers by typing their title or authors, alongside status filter buttons (All / Completed / Reading), implemented with client-side JavaScript embedded in HTML templates, so users can quickly narrow down their paper list without reloading the page.

**To Cite** Users can click To Cite button to add new custom tags about their papers.

**Sample Content & Credits**The academic papers and PDF documents used within ScholarHub are included solely for demonstration, layout testing, and literature management evaluation. All intellectual property, research content, and original writing belong to their respective authors and publishers.

## Project Structure

- **app.py** - The main Flask application server containing all backend routes, session management, and business logic. It handles user authentication, routes data between SQLite and the front-end templates, manages PDF file uploads securely, and processes dynamic updates (such as changing reading status or saving paper takeaways).
- **schema.sql** - Contains the complete DDL (Data Definition Language) for the relational SQLite database. It defines all seven interconnected tables (`users`, `papers`, `notes`, `tags`, `paper_tags`, `ratings`, and `related_papers`), enforcing primary/foreign key constraints, data integrity, and indexes for fast database querying.
- **scholarlibrary.db** - The active SQLite database file where user profiles, uploaded paper metadata, custom tags, and personal research notes are persistently stored.
- **templates/** - A collection of Jinja2 HTML templates extending a unified `layout.html` to provide a consistent, responsive user interface:
  - **layout.html** - The base layout template containing the primary navigation bar, head metadata, CSS/JS scripts, and core structural layout for all pages.
  - **index.html / dashboard.html** - The main user dashboard presenting real-time summary metrics (total papers, completed, reading, notes count), paper cards, filter buttons, and live search.
  - **add_paper.html** - The input interface for creating new paper entries, allowing users to submit title, authors, publication year, custom tags, TL;DR summaries, and attach PDF documents.
  - **view_paper.html** - A dedicated workspace view for reading uploaded PDF papers side-by-side with taking notes and reviewing paper details.
  - **edit_paper.html** - Form template that pre-fills existing paper metadata for easy editing and updating.
  - **add_note.html** - Interface dedicated to adding new structured personal research notes tied to a specific paper.
  - **update_tldr.html** - A quick-edit form designed specifically for rewriting and saving a paper's one-sentence takeaway.
  - **add_tags.html** - Interface for creating, linking, and managing custom open-ended tags across the user's research library.
  - **login.html / register.html** - Authentication templates allowing users to securely log in or create new accounts with client-side form validation.
- **static/style.css** - Custom CSS stylesheet defining the overall modern dark-purple aesthetic, neon accent effects, custom cards, buttons, and layout responsiveness.
- **static/uploads/** - Secure server-side directory used to store user-uploaded PDF files, referenced dynamically by file path in the database.





## Design Decisions

I chose not to integrate any external paper-fetching API (such as
Semantic Scholar or CrossRef) on purpose. Many academic papers are behind
paywalls or are not indexed everywhere, so relying on an API would mean some
papers simply could not be added. By letting users upload their own PDFs and
type in their own metadata, the platform works for any paper, from any
source, without exception.

I also debated whether to hard-code a fixed list of tag categories, but
decided against it in favor of free-text, comma-separated tags that get
normalized and deduplicated on the backend. This keeps the system flexible
for users across very different academic fields.

Finally, the dark purple theme was a deliberate stylistic choice to make
the platform feel more like a focused "research workspace" than a plain
form-based CRUD app, since the entire goal of the project is to reduce the
friction of managing a growing pile of PDFs.

## Acknowledgements

This project was built as my CS50x final project. I used Claude (Anthropic)
as AI assistant to help debug syntax
errors and suggest UI
improvements. I also used Google Gemini for  at a couple of
points during development. All code was written, tested, and understood by
me personally, in line with CS50's policy on AI-assisted final projects.

## License

© 2026 Ahsen Karacan. All rights reserved.
This project was created as a final project for Harvard's CS50: Introduction to Computer Science.
