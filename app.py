from flask import Flask,flash,redirect,render_template,request,session
from flask_session import Session
from werkzeug.security import check_password_hash,generate_password_hash
from dotenv import load_dotenv
import os
load_dotenv()
from werkzeug.utils import secure_filename
from flask import send_from_directory
from cs50 import SQL
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if session.get("user_id") is None:
            return redirect("/")
        return f(*args,**kwargs)
    return decorated_function
app=Flask(__name__)
app.secret_key=os.getenv("SECRET_KEY","local-dev-placeholder")
app.config['MAX_CONTENT_LENGTH']=16*1024*1024
UPLOAD_FOLDER='uploads'
os.makedirs(UPLOAD_FOLDER,exist_ok=True)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)
import os


db_url = os.environ.get("DATABASE_URL", "sqlite:///scholarlibrary.db")


if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

db = SQL(db_url)

@app.route("/")
def index():

    return render_template("index.html")

@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form.get("username")

        password=request.form.get("password")
        if not username  or not password:
            return "You need to fill in all lines"
        if len(password)<8:
            return " Your password must be 8 character at least"
        hash=generate_password_hash(password)
        db.execute("INSERT INTO users(username,hash) VALUES(%s,%s)",username,hash)
        return redirect("/login")
    else:
        return render_template("register.html")
@app.route("/login",methods=["GET","POST"])
def login():
    session.clear()
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        if not username or not password:
            return" Need username and password"
        rows=db.execute("SELECT * FROM users WHERE username=%s",username)
        if len(rows)!=1 or not check_password_hash(rows[0]["hash"],password):
            return" Invalid Username or Password"
        session["user_id"]=rows[0]["id"]
        session["username"]=rows[0]["username"]
        return redirect("/")
    else:
        return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]


    papers_count = db.execute("SELECT COUNT(*) as count FROM papers WHERE user_id = %s", user_id)
    total_papers = papers_count[0]["count"] if papers_count else 0

    completed_count = db.execute("SELECT COUNT(*) as count FROM papers WHERE user_id = %s AND LOWER(status) = 'completed'", user_id)
    completed = completed_count[0]["count"] if completed_count else 0

    notes_count = db.execute("SELECT COUNT(*) as count FROM notes WHERE paper_id IN (SELECT id FROM papers WHERE user_id = %s)", user_id)
    total_notes = notes_count[0]["count"] if notes_count else 0


    papers = db.execute("SELECT * FROM papers WHERE user_id = %s", user_id)
    for paper in papers:
        paper_tags=db.execute(""" SELECT tags.name FROM tags JOIN paper_tags ON tags.id=paper_tags.tag_id WHERE paper_tags.paper_id=%s""",paper["id"])
        paper["tag_list"]=[t["name"] for t in paper_tags]
    for paper in papers:

        paper["notes"] = db.execute("SELECT * FROM notes WHERE paper_id = %s ORDER BY id DESC", paper["id"])

    return render_template("dashboard.html",
                        papers=papers,
                        total_papers=total_papers,
                        completed=completed,
                        total_notes=total_notes)


@app.route("/update_status/<int:paper_id>", methods=["POST", "GET"])
@login_required
def update_status(paper_id):
    paper = db.execute("SELECT * FROM papers WHERE id = %s AND user_id = %s", paper_id, session["user_id"])
    if len(paper) != 1:
        return "Paper could not be found"


    current_status = paper[0]["status"].lower() if paper[0]["status"] else "reading"
    new_status = "completed" if current_status == "reading" else "reading"

    db.execute("UPDATE papers SET status = %s WHERE id = %s", new_status, paper_id)
    return redirect("/dashboard")
@app.route("/add_paper",methods=["GET","POST"])
@login_required
def add_paper():
    if request.method=="POST":
        title=request.form.get("title")
        authors=request.form.get("authors")
        year=request.form.get("year")
        status=request.form.get("status") or "reading"
        tldr=request.form.get("tldr")
        tags=request.form.get("tags")

        if not title:
            return "Title is required",400
        file=request.files.get("pdf")
        pdf_path=None
        if file and file.filename!='':
            filename=secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            pdf_path=filename

        paper_id = db.execute("INSERT INTO papers (user_id, title, authors, year, status, tldr, tags, pdf_path) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id", session["user_id"], title, authors, year, status, tldr, tags, pdf_path)
        
        if tags:
           tag_list=[t.strip() for t in tags.split(",") if t.strip()]
           for tag_name in tag_list:
                existing=db.execute("SELECT id FROM tags WHERE name=%s",tag_name)
                if len(existing)==0:
                   tag_id = db.execute("INSERT INTO tags (name) VALUES (%s) ", tag_name)
                else:
                  tag_id=existing[0]["id"]
                db.execute("INSERT INTO paper_tags (paper_id,tag_id) VALUES(%s,%s)",paper_id,tag_id)

        return redirect("/dashboard")
    return render_template("add_paper.html")
@app.route("/add_tags/<int:paper_id>", methods=["GET","POST"])
@login_required
def add_tags(paper_id):
    paper=db.execute("SELECT * FROM papers WHERE id=%s AND user_id=%s",paper_id,session["user_id"])
    if len(paper)!=1:
        return "Paper not found"
    if request.method=="POST":
        tags=request.form.get("tags")
        if tags:
            tag_list=[t.strip() for t in tags.split(",") if t.strip()]
            for tag_name in tag_list:
                existing=db.execute("SELECT id FROM tags WHERE name=%s",tag_name)
                if len(existing)==0:
                    tag_id = db.execute("INSERT INTO tags (name) VALUES (%s) ", tag_name)
                else:
                    tag_id=existing[0]["id"]
                already_linked=db.execute("SELECT * FROM paper_tags WHERE paper_id=%s AND tag_id=%s",paper_id,tag_id)
                if len(already_linked)==0:
                    db.execute("INSERT INTO paper_tags(paper_id,tag_id) VALUES(%s,%s)",paper_id,tag_id)
        return redirect("/dashboard")
    current_tags = db.execute("""SELECT tags.name FROM tags JOIN paper_tags ON tags.id=paper_tags.tag_id WHERE paper_tags.paper_id=%s""", paper_id)

    return render_template("add_tags.html",paper=paper[0],current_tags=current_tags)
@app.route("/update_tldr/<int:paper_id>",methods=["GET","POST"])
@login_required
def update_tldr(paper_id):
    paper=db.execute("SELECT * FROM papers WHERE id= %s AND user_id= %s",paper_id,session["user_id"])
    if len(paper)!=1:
       return "Paper not found",404
    if request.method=="POST":

       tldr=request.form.get("tldr")
       if not tldr or not tldr.strip():
           return "TL;DR cannot be empty",400
       db.execute("UPDATE papers SET tldr=%s WHERE id=%s AND user_id=%s",tldr.strip(),paper_id,session["user_id"])
       return redirect("/dashboard")
    return render_template("update_tldr.html",paper=paper[0])


@app.route("/add_note/<int:paper_id>",methods=["GET","POST"])
@login_required
def add_note(paper_id):
    paper=db.execute("SELECT * FROM papers WHERE id=%s AND user_id=%s",paper_id,session["user_id"])
    if len(paper)!=1:
       return "paper couldn't find"
    if request.method=="POST":
       content=request.form.get("content")
       if not content:
          return "Content cannot be empty"
       new_tldr=request.form.get("tldr")
       if new_tldr is not None:
           db.execute("UPDATE papers SET tldr=%s WHERE id=%s",new_tldr,paper_id)
       db.execute("INSERT INTO notes(paper_id,content) VALUES(%s,%s)",paper_id,content)
       return redirect("/dashboard")
    return render_template("add_note.html",paper=paper[0])   

@app.route("/pdf/<path:filename>")
@login_required
def serve_pdf(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)
@app.route("/view_paper/<int:paper_id>",methods=["GET","POST"])
@login_required
def view_paper(paper_id):
    paper=db.execute("SELECT * FROM papers WHERE id=%s AND user_id=%s",paper_id,session["user_id"])
    if len(paper)!=1:
        return "Paper not found",404
    if request.method=="POST":
        note_content=request.form.get("note_content")
        if note_content and note_content.strip():
            db.execute("INSERT INTO notes(paper_id,content) VALUES(%s,%s)",paper_id,note_content.strip())
        return redirect(f"/view_paper/{paper_id}")
    notes=db.execute("SELECT * FROM notes WHERE paper_id=%s  ORDER BY id DESC",paper_id)
    return  render_template("view_paper.html",paper=paper[0],notes=notes)
@app.route("/delete_note/<int:note_id>",methods=["POST"])
@login_required
def delete_note(note_id):
    note = db.execute("""SELECT notes.paper_id FROM notes
                          JOIN papers ON notes.paper_id = papers.id
                          WHERE notes.id=%s AND papers.user_id=%s""",
                          note_id, session["user_id"])
    if note:
        paper_id = note[0]["paper_id"]
        db.execute("DELETE FROM notes WHERE id=%s", note_id)
        return redirect(f"/view_paper/{paper_id}")
    return redirect("/dashboard")
@app.route("/edit_note/<int:note_id>",methods=["POST"])
@login_required
def edit_note(note_id):
    new_content = request.form.get("note_content")
    note = db.execute("""SELECT notes.paper_id FROM notes
                          JOIN papers ON notes.paper_id = papers.id
                          WHERE notes.id=%s AND papers.user_id=%s""",
                          note_id, session["user_id"])
    if note and new_content:
        paper_id = note[0]["paper_id"]
        db.execute("UPDATE notes SET content=%s WHERE id=%s", new_content, note_id)
        return redirect(f"/view_paper/{paper_id}")
    return redirect("/dashboard")
@app.route("/delete_paper/<int:paper_id>",methods=["POST"])
@login_required
def delete_paper(paper_id):
    paper = db.execute("SELECT id FROM papers WHERE id=%s AND user_id=%s",
                        paper_id, session["user_id"])
    if not paper:
        return redirect("/dashboard")
    db.execute("DELETE FROM paper_tags WHERE paper_id=%s", paper_id)
    db.execute("DELETE FROM notes WHERE paper_id=%s", paper_id)
    db.execute("DELETE FROM papers WHERE id=%s AND user_id=%s", paper_id, session["user_id"])
    return redirect("/dashboard")
@app.route("/edit_paper/<int:paper_id>",methods=["GET","POST"])
@login_required
def edit_paper(paper_id):
    if request.method=="POST":
        title=request.form.get("title")
        authors=request.form.get("authors")
        year=request.form.get("year")
        if not title:
            return render_template("error.html",message="Title is required")
        db.execute("UPDATE papers SET title=%s,authors=%s,year=%s WHERE id=%s AND user_id=%s",title,authors,year,paper_id,session["user_id"])
        return redirect("/dashboard")
    else:
        papers=db.execute("SELECT * FROM papers WHERE id=%s AND user_id=%s",paper_id,session["user_id"])
        if not papers:
            return redirect("/dashboard")
        return render_template("edit_paper.html",paper=papers[0])






