from flask import Flask, flash, redirect, render_template, request, url_for
from dbhelper import DB, TABLES, init_db

app = Flask(__name__)
app.secret_key = "practice-key"
init_db()


@app.route("/")
def home():
    return redirect(url_for("records", table="event"))


def names_are_valid(info, values):
    for field, value in zip(info["fields"], values):
        if field.get("letters_only") and not all(char.isalpha() or char in " '-." for char in value):
            return False
    return True


@app.route("/<table>", methods=["GET", "POST"])
def records(table):
    if table not in TABLES:
        return "Unknown table", 404
    info = TABLES[table]
    if request.method == "POST":
        values = [request.form.get(field["name"], "").strip()
                  for field in info["fields"]]

        if table == "registration":
            fee = DB.registration_fee(request.form.get("partID", ""))
            if fee is None:
                flash("Choose a valid participant.")
                return redirect(url_for("records", table=table))

            fee_index = next(
                i for i, field in enumerate(info["fields"])
                if field["name"] == "regFPaid"
            )
            values[fee_index] = str(fee)

        # No ID means add a new row; an ID means update that row.
        record_id = request.form.get("record_id")
        if not all(values):
            flash("Please fill in every field.")
        elif not names_are_valid(info, values):
            flash("Names can use letters, spaces, apostrophes, periods, and hyphens only.")
        elif record_id:
            DB.update(table, info, record_id, values)
            flash("Record updated.")
        else:
            DB.add(table, info, values)
            flash("Record added.")
        return redirect(url_for("records", table=table))
        
    

    search = request.args.get("search", "").strip()
    rows = DB.list(table, info, search)
    choices = {}
    choice_names = {}
    for field in info["fields"]:
        if "choice" in field:
            options = DB.choices(field["choice"])
            choices[field["name"]] = options
            display_fields = field.get("choice_display", [field["choice_label"]])
            choice_names[field["name"]] = {
                str(option[field["choice_id"]]): " ".join(
                    str(option[name]) for name in display_fields if option[name]
                )
                for option in options
            }
    row_values = {
        row[info["id"]]: {field["name"]: row[field["name"]] for field in info["fields"]}
        for row in rows
    }
    return render_template("crud.html", table=table, info=info, rows=rows,
                           search=search, choices=choices, choice_names=choice_names,
                           row_values=row_values, tables=TABLES)


@app.post("/<table>/delete/<int:record_id>")
def delete(table, record_id):
    if table not in TABLES:
        return "Unknown table", 404
    try:
        DB.delete(table, TABLES[table], record_id)
        flash("Record deleted.")
    except Exception:
        flash("Cannot delete this record while another record uses it.")
    return redirect(url_for("records", table=table))


if __name__ == "__main__":
    app.run(debug=True)
