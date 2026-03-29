from flask import Flask, request, jsonify, send_from_directory, session
from pathlib import Path
import sqlite3
import json
import os
import uuid
import markdown as md
from flask_session import Session
from werkzeug.utils import secure_filename

ROOT = Path(__file__).parent
DB_FILE = ROOT / 'data.db'
LEGACY_POSTS = ROOT / 'posts.json'

app = Flask(__name__, static_folder='')
app.config['SESSION_TYPE'] = 'filesystem'
# allow overriding the dev secret and admin creds via environment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-please-change')
# folder for uploaded header images
app.config['UPLOAD_FOLDER'] = str(ROOT / 'images')
Session(app)

# admin credentials (use environment variables in production)
ADMIN_USER = os.environ.get('ADMIN_USER', 'admin')
ADMIN_PWD = os.environ.get('ADMIN_PWD', 'password')

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now')),
        header_image TEXT
    )''')
    conn.commit()
    # migrate legacy posts.json if exists and DB empty
    c.execute('SELECT COUNT(*) as cnt FROM posts')
    cnt = c.fetchone()['cnt']
    if cnt == 0 and LEGACY_POSTS.exists():
        with open(LEGACY_POSTS,'r',encoding='utf-8') as f:
            try:
                items = json.load(f)
            except Exception:
                items = []
        for p in reversed(items):
            c.execute('INSERT INTO posts (title,content,created_at) VALUES (?,?,?)', (p.get('title','Untitled'), p.get('content',''), p.get('created_at') or None))
        conn.commit()
    # ensure columns exist for older DBs by checking pragma
    cols = [r['name'] for r in conn.execute("PRAGMA table_info('posts')").fetchall()]
    if 'created_at' not in cols:
        try:
            conn.execute("ALTER TABLE posts ADD COLUMN created_at TEXT")
            conn.commit()
        except Exception:
            pass
    if 'header_image' not in cols:
        try:
            conn.execute("ALTER TABLE posts ADD COLUMN header_image TEXT")
            conn.commit()
        except Exception:
            pass
    conn.close()

init_db()

def require_auth():
    return session.get('user') == ADMIN_USER

@app.route('/api/posts', methods=['GET'])
def api_get_posts():
    conn = get_db()
    rows = conn.execute('SELECT id,title,content,created_at,header_image FROM posts ORDER BY id DESC').fetchall()
    posts = []
    for r in rows:
        posts.append({'id': r['id'], 'title': r['title'], 'content': r['content'], 'html': md.markdown(r['content']), 'created_at': r['created_at'], 'header_image': r['header_image']})
    conn.close()
    return jsonify(posts)

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    if data.get('user') == ADMIN_USER and data.get('pwd') == ADMIN_PWD:
        session['user'] = ADMIN_USER
        return jsonify({'ok': True})
    return jsonify({'error':'invalid'}), 401

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({'ok': True})

@app.route('/api/posts', methods=['POST'])
def api_create_post():
    if not require_auth():
        return jsonify({'error':'unauthorized'}), 401
    data = request.json or {}
    title = data.get('title','Untitled')
    content = data.get('content','')
    header_image = data.get('header_image')
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO posts (title,content,created_at,header_image) VALUES (?,?,datetime("now"),?)', (title, content, header_image))
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return jsonify({'id': pid, 'title': title, 'content': content, 'header_image': header_image}), 201


@app.route('/feed.xml')
def feed():
    # generate a simple RSS feed from posts
    conn = get_db()
    rows = conn.execute('SELECT id,title,content,created_at FROM posts ORDER BY id DESC LIMIT 20').fetchall()
    items = []
    for r in rows:
        pub = r['created_at'] or ''
        title = r['title']
        content = md.markdown(r['content'])
        link = f"{request.url_root.rstrip('/')}/blog#post-{r['id']}"
        items.append(f"<item><title>{title}</title><link>{link}</link><guid>{link}</guid><pubDate>{pub}</pubDate><description><![CDATA[{content}]]></description></item>")
    conn.close()
    rss = f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><rss version=\"2.0\"><channel><title>Jack Johnson Blog</title><link>{request.url_root}</link><description>Recent posts by Jack Johnson</description>{''.join(items)}</channel></rss>"
    return app.response_class(rss, mimetype='application/rss+xml')

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def api_update_post(post_id):
    if not require_auth():
        return jsonify({'error':'unauthorized'}), 401
    data = request.json or {}
    title = data.get('title')
    content = data.get('content')
    header_image = data.get('header_image')
    conn = get_db()
    c = conn.cursor()
    c.execute('UPDATE posts SET title=?, content=?, header_image=? WHERE id=?', (title, content, header_image, post_id))
    conn.commit()
    conn.close()
    return jsonify({'id': post_id, 'title': title, 'content': content, 'header_image': header_image})


@app.route('/api/upload', methods=['POST'])
def api_upload():
    if not require_auth():
        return jsonify({'error':'unauthorized'}), 401
    if 'file' not in request.files:
        return jsonify({'error':'no file'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error':'no filename'}), 400
    filename = secure_filename(f.filename)
    # avoid collisions
    name = f"{uuid.uuid4().hex}_{filename}"
    dest = os.path.join(app.config['UPLOAD_FOLDER'], name)
    f.save(dest)
    # return the relative path to use in posts
    url = f"/images/{name}"
    return jsonify({'url': url})

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def api_delete_post(post_id):
    if not require_auth():
        return jsonify({'error':'unauthorized'}), 401
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM posts WHERE id=?', (post_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


@app.route('/admin')
def admin_page():
    return send_from_directory('.', 'admin.html')

@app.route('/')
def index_page():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
