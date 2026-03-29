#!/usr/bin/env python3
"""Export a static version of the site into `docs/` for GitHub Pages or other static hosts.

Usage: python3 scripts/export_static.py

The script copies HTML, styles, scripts and images into `docs/` for static hosting.
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
    def main():
      copy_assets()
      print(f'Wrote static site to {OUT} — open {OUT}/index.html')

    if __name__ == '__main__':
      main()
</article>'''
