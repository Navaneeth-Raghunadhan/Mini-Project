diff --git a/README.md b/README.md
index 99d25aeb2bd5e51aed72843785796717a93f948b..172fde1d7070cfd9be62ae2920f5b24756d9951c 100644
--- a/README.md
+++ b/README.md
@@ -1,5 +1,94 @@
-# My-First-Github-Repository
+# FocusFlow - Study Planner Web App
 
-Hi! I'm Navaneeth Raghunadhan , an upcoming software engineer!
-I could say that I am an intermediate in coding and I'm learning how to use Github !
-I am planning on making this Repository for the simple calculator i made using python
+FocusFlow is a beginner-friendly Flask + SQLite web app that helps students plan their study tasks.
+
+## Features
+
+- User registration and login
+- Dashboard with:
+  - Today's tasks
+  - Upcoming deadlines
+  - Completion progress
+- Task manager:
+  - Add task
+  - Edit task
+  - Delete task
+  - Mark complete / pending
+- Modern, responsive UI with soft gradients, rounded cards, and smooth button/card animations
+
+## Tech Stack
+
+- **Backend:** Flask (Python)
+- **Database:** SQLite
+- **Frontend:** HTML, CSS, JavaScript
+
+## Project Structure
+
+```text
+.
+├── app.py
+├── focusflow.db (auto-created on first run)
+├── static/
+│   ├── css/style.css
+│   └── js/main.js
+└── templates/
+    ├── base.html
+    ├── home.html
+    ├── login.html
+    ├── register.html
+    ├── dashboard.html
+    └── tasks.html
+```
+
+## Setup & Run
+
+1. Create and activate a virtual environment (optional but recommended):
+
+   ```bash
+   python3 -m venv .venv
+   source .venv/bin/activate
+   ```
+
+2. Install dependencies:
+
+   ```bash
+   pip install flask werkzeug
+   ```
+
+3. Run the app:
+
+   ```bash
+   python app.py
+   ```
+
+4. Open in browser:
+
+   ```
+   http://127.0.0.1:5000
+   ```
+
+## Database Tables
+
+### `users`
+
+- `id`
+- `username`
+- `email`
+- `password`
+
+### `tasks`
+
+- `id`
+- `user_id`
+- `title`
+- `subject`
+- `deadline`
+- `status`
+
+
+## Troubleshooting
+
+- **TemplateNotFound: home.html**
+  - Ensure the `templates/` folder is in the same project directory as `app.py`.
+  - Run the app from the project folder: `python app.py`.
+  - This project already uses absolute template/static paths in `app.py` to avoid cwd-related template lookup issues.
