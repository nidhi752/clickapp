# 🗒️ StickyCheck – Desktop Sticky Notes App

StickyCheck is a lightweight **desktop sticky notes app** built with **Flask, SQLite, and PyWebView**.  
It lets you create multiple sticky notes with checklists, tick items off, and manage tasks in a simple popup-style window.

---

## ✨ Features
- Create and manage multiple sticky notes.
- Add checklist items to each note.
- Tick off completed tasks (with line-through).
- Delete individual items or entire notes.
- See completion progress (e.g., `3/5 completed`).
- Clean **sticky-note inspired UI**.
- Runs as a **standalone desktop app** via `pywebview`.

---

## 🛠 Requirements
- Python **3.9+**
- Microsoft **Edge WebView2 Runtime** (Windows only, usually pre-installed; [download here](https://developer.microsoft.com/en-us/microsoft-edge/webview2/#download-section))

---

## ⚙️ Setup & Installation

1. **Clone or download** this repository.
2. Create and activate a virtual environment:

   **Windows (PowerShell):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS/Linux (bash/zsh):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies inside the venv:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Running the App

With the virtual environment **activated**, run:

```bash
python trial2.py
```

* The app starts a **local Flask server** on `http://127.0.0.1:5000`.
* A **desktop window** opens automatically via PyWebView.

---

## 📦 Packaging into an EXE (Windows)

To distribute StickyCheck without needing a venv:

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed trial2.py
```

* The `.exe` will appear in the `dist/` folder.
* Double-click it to run StickyCheck like a normal Windows app (no venv needed).

---

## 🔄 Auto-Start on Windows

To make StickyCheck launch automatically when your PC starts:

1. Build the `.exe` (see above).
2. Press `Win + R`, type `shell:startup`, and hit Enter.
3. Copy your built `.exe` into the folder that opens.

Now StickyCheck will start automatically at login.

---

## 📂 Project Structure

```
trial2.py           # Main application code
requirements.txt    # Python dependencies
README.md           # Documentation
.venv/              # Virtual environment (local, not shared)
```

---

## ⚠️ Notes
* The app stores its database in:
  * **Windows**: `%LOCALAPPDATA%\StickyCheck\sticky.db`
  * **Linux/macOS**: `~/.local/share/StickyCheck/sticky.db`
* Deleting the database file will **reset all notes**.

