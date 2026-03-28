#!/usr/bin/env python3
"""Export a static version of the site into `docs/` for GitHub Pages or other static hosts.

Usage: python3 scripts/export_static.py

The script copies HTML, styles, scripts and images into `docs/` and generates a
static `blog.html` by reading posts from the SQLite DB (`data.db`) or `posts.json`.
"""
from pathlib import Path
import sqlite3
import json
import shutil
import os
import markdown as md

ROOT = Path(__file__).resolve().parent.parent
DB_FILE = ROOT / 'data.db'
LEGACY_POSTS = ROOT / 'posts.json'
OUT = ROOT / 'docs'


def load_posts():
    posts = []
    if DB_FILE.exists():
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        rows = conn.execute('SELECT id,title,content,created_at,header_image FROM posts ORDER BY id DESC').fetchall()
        for r in rows:
            posts.append({'id': r['id'], 'title': r['title'], 'content': r['content'], 'created_at': r['created_at'], 'header_image': r['header_image']})
        conn.close()
    elif LEGACY_POSTS.exists():
        with open(LEGACY_POSTS,'r',encoding='utf-8') as f:
            try:
                items = json.load(f)
            except Exception:
                items = []
        for p in items:
            posts.append({'id': p.get('id'), 'title': p.get('title'), 'content': p.get('content'), 'created_at': p.get('created_at'), 'header_image': p.get('header_image')})
    return posts


def render_blog_html(posts):
    def fmt_date(s):
        return s or ''

    posts_html = []
    for p in posts:
        content_html = md.markdown(p.get('content') or '')
        header_img = p.get('header_image')
        header_html = f'<img src="{header_img}" alt="" style="max-width:100%;height:auto;margin-top:.5rem;border-radius:6px">' if header_img else ''
        item = f'''<article class="card" id="post-{p.get('id')}" style="margin-bottom:1rem">
  <div style="display:flex;justify-content:space-between;align-items:center">
    <h2 style="margin:0">{p.get('title')}</h2>
    <time style="color:var(--muted);font-size:.95rem">{fmt_date(p.get('created_at'))}</time>
  </div>
  {header_html}
  <div style="margin-top:.5rem;color:var(--muted)">{content_html}</div>
</article>'''
        posts_html.append(item)

    posts_joined = '\n'.join(posts_html) or '<p>No posts yet.</p>'

    # basic blog template (keeps header/footer and styles from root site)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Blog — Jack Johnson</title>
  <link rel="alternate" type="application/rss+xml" title="RSS" href="/feed.xml">
  <link rel="icon" href="/images/alien.png">
  <link rel="stylesheet" href="styles/style.css">
</head>
<body>
  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="/">
        <img src="/images/jack-linkedin.png" alt="Jack Johnson" class="nav-avatar">
        Jack Johnson
      </a>
      <nav class="site-nav">
        <ul>
          <li><a href="/index.html">Home</a></li>
          <li><a href="/projects.html">Projects</a></li>
          <li><a href="/blog" aria-current="page">Blog</a></li>
        </ul>
      </nav>
    </div>
  </header>

  <main class="page container">
    <section class="card">
      <h1>Blog</h1>
      <p class="lead">Thoughts, updates, and project notes.</p>
      <div id="posts">{posts_joined}</div>
    </section>
  </main>

  <footer class="site-footer">
    <div class="container">
      <p>© 2026 Jack Johnson — <a href="/index.html">Home</a> · <a href="/projects.html">Projects</a></p>
    </div>
  </footer>
</body>
</html>'''


def copy_assets():
    # files/dirs to copy
    to_copy = ['index.html', 'projects.html', 'styles', 'scripts', 'images', 'README.md', 'favicon.ico']
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for name in to_copy:
        src = ROOT / name
        dest = OUT / name
        if not src.exists():
            continue
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copy2(src, dest)


def write_blog(posts):
    html = render_blog_html(posts)
    target = OUT / 'blog'
    # ensure /blog path works as a file - create blog/index.html
    (OUT / 'blog').mkdir(parents=True, exist_ok=True)
    with open(OUT / 'blog' / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    # also write top-level /blog.html for convenience
    with open(OUT / 'blog.html', 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    posts = load_posts()
    print(f'Loaded {len(posts)} posts')
    copy_assets()
    write_blog(posts)
    print(f'Wrote static site to {OUT} — open {OUT}/index.html and {OUT}/blog.html')


if __name__ == '__main__':
    main()
