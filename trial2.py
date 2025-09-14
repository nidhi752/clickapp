#!/usr/bin/env python3

import os
import sys
import threading
import time
import traceback
from datetime import datetime
from pathlib import Path

import webview
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


# Database setup
def get_db_path():
    if sys.platform == "win32":
        app_data = os.environ.get('LOCALAPPDATA', os.path.expanduser('~\\AppData\\Local'))
        db_dir = Path(app_data) / 'StickyCheck'
    else:
        db_dir = Path.home() / '.local' / 'share' / 'StickyCheck'

    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / 'sticky.db'


# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sticky-notes-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{get_db_path()}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)


# Models
class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('ChecklistItem', backref='note', lazy=True, cascade='all, delete-orphan')


class ChecklistItem(db.Model):
    __tablename__ = 'checklist_items'
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.id'), nullable=False)
    text = db.Column(db.String(500), nullable=False)
    completed = db.Column(db.Boolean, default=False)


# Template
TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Sticky Notes</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #fff9c4 0%, #fff3a0 100%);
            margin: 8px; 
            color: #333;
        }
        .container { 
            background: #fff9c4; 
            border: 1px solid #e6d93a; 
            border-radius: 5px; 
            padding: 15px;
            height: calc(100vh - 30px);
            overflow-y: auto;
        }
        .header { 
            background: #f0e68c; 
            margin: -15px -15px 15px -15px; 
            padding: 10px 15px; 
            border-bottom: 1px solid #e6d93a;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .nav a { 
            background: white; 
            padding: 5px 10px; 
            text-decoration: none; 
            color: #333; 
            border-radius: 3px; 
            margin-left: 5px;
            font-size: 12px;
        }
        .form-group { margin-bottom: 15px; }
        input[type="text"] { 
            width: 100%; 
            padding: 8px; 
            border: 1px solid #d4af37; 
            border-radius: 3px;
            box-sizing: border-box;
        }
        button { 
            background: #daa520; 
            color: white; 
            border: none; 
            padding: 8px 15px; 
            border-radius: 3px; 
            cursor: pointer;
        }
        button:hover { background: #b8860b; }
        .btn-full { width: 100%; }
        .item { 
            padding: 8px; 
            margin: 5px 0; 
            background: rgba(255,255,255,0.5); 
            border-radius: 3px;
            display: flex;
            align-items: center;
        }
        .item.completed { opacity: 0.6; }
        .item.completed .text { text-decoration: line-through; }
        .item input[type="checkbox"] { margin-right: 10px; }
        .item .text { flex: 1; }
        .item .delete { 
            background: #dc3545; 
            padding: 2px 6px; 
            font-size: 12px;
            margin-left: 10px;
        }
        .note-card { 
            background: rgba(255,255,255,0.6); 
            padding: 10px; 
            margin: 8px 0; 
            border-radius: 3px; 
            border-left: 3px solid #daa520;
        }
        .note-title { margin: 0 0 5px 0; }
        .note-meta { font-size: 12px; color: #666; margin-bottom: 10px; }
        .empty { text-align: center; color: #666; padding: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>{{ title }}</h2>
            <div class="nav">
                <a href="/">🏠 Home</a>
                <a href="/notes">📋 Notes</a>
            </div>
        </div>
        {{ content|safe }}
    </div>
</body>
</html>
'''


def init_db():
    with app.app_context():
        try:
            #db.drop_all()
            db.create_all()
            print("✓ Database initialized")
            return True
        except Exception as e:
            print(f"✗ Database error: {e}")
            return False


# Routes
@app.route('/')
def home():
    content = '''
    <form method="POST" action="/create">
        <div class="form-group">
            <input type="text" name="title" placeholder="Enter note title..." required autofocus>
        </div>
        <button type="submit" class="btn-full">✨ Create New Note</button>
    </form>
    '''
    return render_template_string(TEMPLATE, title="Create Note", content=content)


@app.route('/notes')
def notes():
    all_notes = Note.query.all()
    if not all_notes:
        content = '<div class="empty">📝 No notes yet. <a href="/">Create one!</a></div>'
    else:
        content = ''
        for note in all_notes:
            completed = sum(1 for item in note.items if item.completed)
            total = len(note.items)
            content += f'''
            <div class="note-card">
                <h3 class="note-title">{note.title}</h3>
                <div class="note-meta">{completed}/{total} completed</div>
                <a href="/note/{note.id}">📝 Open</a>
                <form method="POST" action="/delete_note/{note.id}" style="display: inline; margin-left: 10px;">
                    <button type="submit" onclick="return confirm('Delete note?')" style="background: #dc3545; font-size: 12px;">🗑️</button>
                </form>
            </div>
            '''
    return render_template_string(TEMPLATE, title="All Notes", content=content)


@app.route('/create', methods=['POST'])
def create():
    title = request.form.get('title', '').strip()
    if title:
        note = Note(title=title)
        db.session.add(note)
        db.session.commit()
        return redirect(f'/note/{note.id}')
    return redirect('/')


@app.route('/note/<int:note_id>')
def view_note(note_id):
    note = Note.query.get_or_404(note_id)

    # Progress
    completed = sum(1 for item in note.items if item.completed)
    total = len(note.items)
    progress = f'<div style="text-align: center; margin-bottom: 15px; color: #666;">{completed}/{total} completed</div>' if total > 0 else ''

    # Add form
    content = progress + f'''
    <form method="POST" action="/note/{note_id}/add">
        <div class="form-group">
            <input type="text" name="text" placeholder="Add an item..." required autofocus>
        </div>
        <button type="submit" class="btn-full">+ Add Item</button>
    </form>
    '''

    # Items
    if note.items:
        for item in note.items:
            checked = 'checked' if item.completed else ''
            completed_class = ' completed' if item.completed else ''
            content += f'''
            <div class="item{completed_class}">
                <form method="POST" action="/item/{item.id}/toggle" style="display: inline;">
                    <input type="checkbox" {checked} onchange="this.form.submit()">
                </form>
                <span class="text">{item.text}</span>
                <form method="POST" action="/item/{item.id}/delete" style="display: inline;">
                    <button type="submit" class="delete" onclick="return confirm('Delete?')">×</button>
                </form>
            </div>
            '''
    else:
        content += '<div class="empty">No items yet. Add one above!</div>'

    return render_template_string(TEMPLATE, title=note.title, content=content)


@app.route('/note/<int:note_id>/add', methods=['POST'])
def add_item(note_id):
    text = request.form.get('text', '').strip()
    if text:
        item = ChecklistItem(note_id=note_id, text=text)
        db.session.add(item)
        db.session.commit()
    return redirect(f'/note/{note_id}')


@app.route('/item/<int:item_id>/toggle', methods=['POST'])
def toggle_item(item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    item.completed = not item.completed
    db.session.commit()
    return redirect(f'/note/{item.note_id}')


@app.route('/item/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    note_id = item.note_id
    db.session.delete(item)
    db.session.commit()
    return redirect(f'/note/{note_id}')


@app.route('/delete_note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return redirect('/notes')


def start_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


def main():
    print("🗒️ Starting StickyCheck...")

    # Initialize database
    if not init_db():
        return

    # Start Flask
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)

    # Test Flask
    try:
        import urllib.request
        urllib.request.urlopen('http://127.0.0.1:5000/')
        print("✓ Flask server running")
    except:
        print("✗ Flask server failed")
        return

    # Start webview - MINIMAL VERSION
    try:
        print("🚀 Opening window...")
        webview.create_window('Sticky Notes', 'http://127.0.0.1:5000/', width=400, height=500)
        webview.start()
    except Exception as e:
        print(f"✗ Webview error: {e}")


if __name__ == '__main__':
    main()