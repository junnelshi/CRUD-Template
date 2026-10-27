# Library CRUD App

A small Flask app for managing authors, books, students, and borrowing records. It uses SQLite and creates `Library.db` beside `app.py` the first time it starts.

## Run on Windows

1. Install Python 3 from [python.org](https://www.python.org/downloads/). During setup, enable **Add Python to PATH**.
2. Copy the project folder to the PC. Keep `app.py`, `dbhelper.py`, `requirements.txt`, and the `static` and `templates` folders together.
3. Open PowerShell in the project folder and run:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   py -m pip install -r requirements.txt
   py app.py
   ```

4. Open <http://127.0.0.1:5000> in a browser on that PC.
5. Press `Ctrl+C` in PowerShell to stop the app.

If PowerShell blocks activation, use Command Prompt instead:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
py -m pip install -r requirements.txt
py app.py
```

## Database and portability

- `Library.db` is created automatically when the app starts. If it is absent, the app starts with an empty database.
- To bring existing records, copy `Library.db` alongside `app.py` while the app is stopped. Keep a backup before moving or replacing it.
- The `sqlite3.exe` file is not needed to run the app; Python includes the SQLite support this project uses.
- The `.venv` folder is specific to the computer where it was created. Recreate it on each PC using the commands above.
- The app is configured for local use on the same PC. It is not set up as a public website or for other computers to connect over a network.
