from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_cursor, format_db_error
from mysql.connector import Error

passengers_bp = Blueprint("passengers", __name__)

@passengers_bp.route("/")
def index():
    """List and search registered passengers."""
    search_q = request.args.get("q", "").strip()
    passengers_list = []

    try:
        with get_db_cursor() as cursor:
            query = """
                SELECT p.passenger_id, p.name, p.phone, p.email,
                       COUNT(b.booking_id) AS total_bookings,
                       COALESCE(SUM(pm.amount), 0.00) AS total_spent
                FROM passenger p
                LEFT JOIN booking b ON p.passenger_id = b.passenger_id
                LEFT JOIN payment pm ON b.booking_id = pm.booking_id AND pm.status = 'Paid'
                WHERE 1=1
            """
            params = []
            if search_q:
                query += " AND (p.name LIKE %s OR p.phone LIKE %s OR p.email LIKE %s)"
                term = f"%{search_q}%"
                params.extend([term, term, term])

            query += """
                GROUP BY p.passenger_id, p.name, p.phone, p.email
                ORDER BY p.name ASC;
            """
            cursor.execute(query, tuple(params))
            passengers_list = cursor.fetchall()

    except Error as e:
        flash(f"Error fetching passengers: {format_db_error(e)}", "error")

    return render_template("passengers/index.html", passengers=passengers_list, search_query=search_q)

@passengers_bp.route("/<int:passenger_id>/edit", methods=["GET", "POST"])
def edit(passenger_id):
    """Edit passenger profile details."""
    passenger = None

    try:
        with get_db_cursor(commit=(request.method == "POST")) as cursor:
            if request.method == "POST":
                name = request.form.get("name", "").strip()
                phone = request.form.get("phone", "").strip()
                email = request.form.get("email", "").strip() or None

                cursor.execute("""
                    UPDATE passenger 
                    SET name = %s, phone = %s, email = %s
                    WHERE passenger_id = %s;
                """, (name, phone, email, passenger_id))
                flash("Passenger details updated successfully.", "success")
                return redirect(url_for("passengers.index"))

            cursor.execute("SELECT * FROM passenger WHERE passenger_id = %s;", (passenger_id,))
            passenger = cursor.fetchone()

            if not passenger:
                flash("Passenger not found.", "error")
                return redirect(url_for("passengers.index"))

    except Error as e:
        flash(f"Error updating passenger: {format_db_error(e)}", "error")

    return render_template("passengers/form.html", passenger=passenger)
