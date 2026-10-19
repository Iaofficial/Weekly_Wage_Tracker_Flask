
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

app = Flask(__name__)
app.secret_key = "replace-with-your-own-secret-key"


def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Ilyas@909047",
        database="weekly_profit_tracker"
    )


def get_week_start(value):
    try:
        selected_date = date.fromisoformat(value)
    except (ValueError, TypeError):
        selected_date = date.today()

    # Monday is the first day of the week
    return selected_date - timedelta(days=selected_date.weekday())


@app.route("/")
def index():
    selected = request.args.get("week", date.today().isoformat())
    monday = get_week_start(selected)
    sunday = monday + timedelta(days=6)

    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id, work_date, earnings, petrol,
                   other_expenses, notes,
                   earnings - petrol - other_expenses AS profit
            FROM daily_records
            WHERE work_date BETWEEN %s AND %s
            ORDER BY work_date DESC, id DESC
        """, (monday, sunday))

        records = cursor.fetchall()

        cursor.execute("""
            SELECT
                COALESCE(SUM(earnings), 0) AS total_earnings,
                COALESCE(SUM(petrol), 0) AS total_petrol,
                COALESCE(SUM(other_expenses), 0) AS total_other
            FROM daily_records
            WHERE work_date BETWEEN %s AND %s
        """, (monday, sunday))

        summary = cursor.fetchone()

    finally:
        cursor.close()
        db.close()

    summary["total_profit"] = (
        summary["total_earnings"]
        - summary["total_petrol"]
        - summary["total_other"]
    )

    return render_template(
        "index.html",
        records=records,
        summary=summary,
        week_start=monday.isoformat(),
        week_end=sunday.isoformat(),
        selected_week=selected
    )


@app.route("/add", methods=["POST"])
def add_record():
    work_date = request.form.get("work_date", "")
    notes = request.form.get("notes", "").strip()

    try:
        parsed_date = date.fromisoformat(work_date)

        earnings = Decimal(request.form.get("earnings", ""))
        petrol = Decimal(request.form.get("petrol", ""))
        other = Decimal(request.form.get("other_expenses", ""))

    except (ValueError, TypeError, InvalidOperation):
        flash("Please enter a valid date and expense amounts.", "error")
        return redirect(url_for("index"))

    amounts = [earnings, petrol, other]

    if (
        any(not amount.is_finite() for amount in amounts)
        or any(amount < 0 or amount > Decimal("99999999.99")
               for amount in amounts)
        or len(notes) > 255
    ):
        flash("Amounts must be non-negative and within the allowed limit.", "error")
        return redirect(url_for("index", week=work_date))

    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO daily_records
                (work_date, earnings, petrol, other_expenses, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (parsed_date, earnings, petrol, other, notes))

        db.commit()
        flash("Daily record saved successfully!", "success")

    except mysql.connector.Error:
        db.rollback()
        flash("Unable to save the record. Please try again.", "error")

    finally:
        cursor.close()
        db.close()

    return redirect(url_for("index", week=work_date))


@app.route("/delete/<int:record_id>", methods=["POST"])
def delete_record(record_id):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(
            "DELETE FROM daily_records WHERE id = %s",
            (record_id,)
        )
        db.commit()

        if cursor.rowcount:
            flash("Daily record deleted.", "success")
        else:
            flash("Record not found.", "error")

    except mysql.connector.Error:
        db.rollback()
        flash("Unable to delete the record.", "error")

    finally:
        cursor.close()
        db.close()

    return redirect(url_for(
        "index",
        week=request.form.get("week", date.today().isoformat())
    ))


if __name__ == "__main__":
    app.run(debug=True)
