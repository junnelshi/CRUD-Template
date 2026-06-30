# How to use this on exam day

This is a fully working, tested Flask + SQLite CRUD app with 3 tables and
4 pages. It already runs end-to-end (login → add → edit → delete → compute
a fee → view a filtered report with totals). Your job is NOT to write new
code — it's to **rename things** to match whatever the real spec gives you.

## The shape of this template (and why it should fit most specs)

| In this template | What it represents          | In your real exam it will be... |
|---|---|---|
| `Group_` table     | A simple master table        | e.g. Events, Courses, Categories |
| `Person` table     | A master table with a Foreign Key to Group_ | e.g. Participants, Students, Members |
| `Entry` table       | A transaction table with a computed value | e.g. Registration, Orders, Bookings |
| `/monitoring`       | Read-only filter + COUNT()/SUM()/formula | Almost every exam has one of these |

If the real spec has a different number of tables, it's usually still 2
master tables + 1 transaction table — just copy/paste an extra block if
there's a 4th, or delete the Entry section if there's only 2.

## Step-by-step rename process (do this in order)

**1. Look at the real data dictionary first.** Write down, on paper, the
3 tables and every column name, in order. This is your map.

**2. In `dbhelper.py`:**
   - Rename `Group_` / `Person` / `Entry` to the real table names.
   - Rename every column (`groupID` → `evCode`, `groupName` → `evName`, etc.)
     in `init_database()` first — keep column ORDER the same as the real
     spec so you don't mix up positions later.
   - Then use Find & Replace (Ctrl+H) for each function name and column
     name through the rest of the file — `add_group` → `add_event`,
     `get_all_groups` → `get_all_events`, etc.
   - **Don't rewrite the SQL logic** — only the names change. The
     INSERT/UPDATE/DELETE/SELECT shape is already correct.

**3. In `app.py`:**
   - Update the `from dbhelper import (...)` line to match your renamed
     functions.
   - Find & Replace route names and URLs (`/group` → `/events`, etc.)
   - Find & Replace `request.form.get("groupName")` etc. to match your
     real `<input name="...">` fields once you write the HTML forms.
   - **The one part with real logic** is inside `entry_page()` — this
     line:
     ```python
     entryAmount = base_fee - (base_fee * rate)
     ```
     Replace this with whatever formula the real spec gives you. Read
     it twice before typing — these formulas are usually exactly stated,
     e.g. `regFPaid = evRFee - (evRFee * partDRate)`. Match it exactly.
   - In `monitoring()`, the aggregate formulas (`count`, `total_paid`,
     `total_discount`) follow the same find-and-replace approach — but
     double check the discount formula against the real spec, since
     `(count * full_fee) - total_paid` was written for THIS template's
     formula, not necessarily the real one.

**4. In `templates/*.html`:**
   - Rename `<input name="...">` to match your form field names.
   - Rename table headers and `{{ g['groupName'] }}` etc. to match.
   - Don't touch `base.html`, `style.css`, or `script.js` unless you want
     to — they're name-agnostic and will keep working no matter what you
     rename the entities to.

## Quick sanity checklist before you start adapting

- [ ] Run `python app.py` BEFORE you change anything, log in with
      `admin` / `admin`, and click through all 4 pages once. Confirm it
      works as-is. This proves your Python/Flask install is working,
      separate from whatever bugs you might introduce while renaming.
- [ ] After renaming `dbhelper.py`, delete `database.db` if it exists
      and restart the app — otherwise it'll still have the OLD schema
      cached and you'll get `OperationalError: no such column`.
- [ ] Rename one table fully (both files) before touching the next —
      don't try to rename everything everywhere at once.

## Account system (Users table) — new

There's now a full account/login system separate from the 3 exam-pattern
tables above:

- **Create**: anyone can register at `/register` (linked from the login page).
- **Read**: a logged-in user sees their own profile at `/account`.
- **Update**: same page, `/account/edit` — change first/last name, email,
  username, and optionally a new password (leave password blank to keep
  the current one).
- **Delete**: `/account/delete` permanently removes the account and logs
  the user out.

Passwords are hashed with `werkzeug.security.generate_password_hash` /
`check_password_hash` — never stored as plain text. A default account
(`admin` / `admin`) is seeded automatically the first time the app runs,
so login still works out of the box even before anyone registers.

**Running `python app.py` now automatically opens your browser to the
login page** after about 1 second. If the real exam's spec says to log in
as a specific seeded account, just change the seed values inside
`init_database()` in `dbhelper.py` to match.

## Files in this folder

```
app.py                 - all routes (rename per the table above)
dbhelper.py             - all database functions (rename per the table above)
templates/
  base.html             - shared layout/nav — usually no changes needed
  login.html            - login form, links to register — usually no changes needed
  register.html         - create-account form — usually no changes needed
  account.html          - view/update/delete own profile — usually no changes needed
  group.html            - list+add+edit+delete for table 1
  person.html           - list+add+edit+delete for table 2 (has FK dropdown)
  entry.html            - create+read for table 3 (has computed value)
  monitoring.html       - filter + aggregate report
static/
  style.css             - all styling — no changes needed
  script.js             - delete-confirmation — no changes needed
```

Login credentials baked in for testing: **admin / admin**
(change the seed in `dbhelper.py`'s `init_database()` if your exam
specifies a different account).
"# CRUD-Template" 
