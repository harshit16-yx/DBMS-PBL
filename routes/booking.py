from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime
from db import get_db_cursor, format_db_error
from mysql.connector import Error

booking_bp = Blueprint("booking", __name__)

@booking_bp.route("/search", methods=["GET"])
def search():
    """Search for scheduled trips by source, destination, and travel date."""
    source = request.args.get("source", "").strip()
    dest = request.args.get("dest", "").strip()
    travel_date = request.args.get("travel_date", "").strip()

    cities = []
    trips = []

    try:
        with get_db_cursor() as cursor:
            # Fetch distinct source and destination cities
            cursor.execute("SELECT DISTINCT source_city FROM route ORDER BY source_city;")
            sources = [r["source_city"] for r in cursor.fetchall()]
            cursor.execute("SELECT DISTINCT dest_city FROM route ORDER BY dest_city;")
            dests = [r["dest_city"] for r in cursor.fetchall()]
            cities = sorted(list(set(sources + dests)))

            # Build query for scheduled future trips
            query = """
                SELECT t.trip_id, r.source_city, r.dest_city, r.distance_km,
                       t.departure_time, t.arrival_time,
                       b.bus_id, b.reg_no, b.bus_type, b.total_seats,
                       f.base_fare,
                       (b.total_seats - COUNT(CASE WHEN bk.status = 'Confirmed' THEN bk.booking_id END)) AS available_seats
                FROM trip t
                JOIN route r ON t.route_id = r.route_id
                JOIN bus b ON t.bus_id = b.bus_id
                LEFT JOIN fare f ON f.route_id = t.route_id AND f.bus_type = b.bus_type
                LEFT JOIN booking bk ON t.trip_id = bk.trip_id
                WHERE t.status = 'Scheduled' AND t.departure_time >= NOW()
            """
            params = []

            if source:
                query += " AND r.source_city = %s"
                params.append(source)
            if dest:
                query += " AND r.dest_city = %s"
                params.append(dest)
            if travel_date:
                query += " AND DATE(t.departure_time) = %s"
                params.append(travel_date)

            query += """
                GROUP BY t.trip_id, r.source_city, r.dest_city, r.distance_km,
                         t.departure_time, t.arrival_time,
                         b.bus_id, b.reg_no, b.bus_type, b.total_seats, f.base_fare
                ORDER BY t.departure_time ASC;
            """

            cursor.execute(query, tuple(params))
            trips = cursor.fetchall()

    except Error as e:
        flash(f"Error querying trips: {format_db_error(e)}", "error")

    return render_template(
        "booking/search.html",
        cities=cities,
        trips=trips,
        selected_source=source,
        selected_dest=dest,
        selected_date=travel_date
    )

@booking_bp.route("/trip/<int:trip_id>/seats", methods=["GET"])
def view_seats(trip_id):
    """Shows interactive seat grid and passenger assignment for chosen trip."""
    trip = None
    seats = []
    booked_seat_ids = set()
    passengers = []

    try:
        with get_db_cursor() as cursor:
            # 1. Fetch trip and fare details
            cursor.execute("""
                SELECT t.trip_id, t.status AS trip_status, t.departure_time, t.arrival_time,
                       r.route_id, r.source_city, r.dest_city, r.distance_km,
                       b.bus_id, b.reg_no, b.bus_type, b.total_seats,
                       f.base_fare
                FROM trip t
                JOIN route r ON t.route_id = r.route_id
                JOIN bus b ON t.bus_id = b.bus_id
                LEFT JOIN fare f ON f.route_id = t.route_id AND f.bus_type = b.bus_type
                WHERE t.trip_id = %s;
            """, (trip_id,))
            trip = cursor.fetchone()

            if not trip:
                flash("Trip not found.", "error")
                return redirect(url_for("booking.search"))

            if trip["trip_status"] != "Scheduled":
                flash(f"This trip is {trip['trip_status']} and is not open for booking.", "warning")
                return redirect(url_for("booking.search"))

            # 2. Fetch all seats for the trip's bus
            cursor.execute("""
                SELECT seat_id, seat_no 
                FROM seat 
                WHERE bus_id = %s 
                ORDER BY LENGTH(seat_no), seat_no;
            """, (trip["bus_id"],))
            seats = cursor.fetchall()

            # 3. Fetch currently confirmed booked seats for this trip
            cursor.execute("""
                SELECT seat_id 
                FROM booking 
                WHERE trip_id = %s AND status = 'Confirmed';
            """, (trip_id,))
            booked_seat_ids = {row["seat_id"] for row in cursor.fetchall()}

            # 4. Fetch list of existing passengers for inline selector
            cursor.execute("SELECT passenger_id, name, phone, email FROM passenger ORDER BY name ASC;")
            passengers = cursor.fetchall()

    except Error as e:
        flash(f"Error loading seat data: {format_db_error(e)}", "error")
        return redirect(url_for("booking.search"))

    return render_template(
        "booking/seats.html",
        trip=trip,
        seats=seats,
        booked_seat_ids=booked_seat_ids,
        passengers=passengers
    )

@booking_bp.route("/book", methods=["POST"])
def book_seat():
    """Creates a booking record and transitions immediately to the payment step."""
    trip_id = request.form.get("trip_id")
    seat_id = request.form.get("seat_id")
    passenger_type = request.form.get("passenger_type", "new")
    passenger_id = request.form.get("passenger_id")

    if not trip_id or not seat_id:
        flash("Please select a seat to proceed.", "error")
        return redirect(url_for("booking.view_seats", trip_id=trip_id or 1))

    try:
        with get_db_cursor(commit=True) as cursor:
            # Handle passenger resolution
            if passenger_type == "new":
                name = request.form.get("name", "").strip()
                phone = request.form.get("phone", "").strip()
                email = request.form.get("email", "").strip() or None

                if not name or not phone:
                    flash("Passenger Name and Phone Number are required.", "error")
                    return redirect(url_for("booking.view_seats", trip_id=trip_id))

                # Check if phone already registered to avoid constraint rejection
                cursor.execute("SELECT passenger_id FROM passenger WHERE phone = %s;", (phone,))
                existing_p = cursor.fetchone()
                if existing_p:
                    passenger_id = existing_p["passenger_id"]
                else:
                    cursor.execute("""
                        INSERT INTO passenger (name, phone, email) 
                        VALUES (%s, %s, %s);
                    """, (name, phone, email))
                    passenger_id = cursor.lastrowid
            else:
                if not passenger_id:
                    flash("Please choose a valid passenger from the list.", "error")
                    return redirect(url_for("booking.view_seats", trip_id=trip_id))

            # Insert Booking: Let MySQL UNIQUE constraint and trg_booking_check enforce validity
            cursor.execute("""
                INSERT INTO booking (trip_id, seat_id, passenger_id, status)
                VALUES (%s, %s, %s, 'Confirmed');
            """, (trip_id, seat_id, passenger_id))
            booking_id = cursor.lastrowid

            flash("Seat reserved successfully. Please complete payment to confirm your ticket.", "success")
            return redirect(url_for("booking.payment", booking_id=booking_id))

    except Error as e:
        error_msg = format_db_error(e)
        flash(f"Booking failed: {error_msg}", "error")
        return redirect(url_for("booking.view_seats", trip_id=trip_id))

@booking_bp.route("/payment/<int:booking_id>", methods=["GET", "POST"])
def payment(booking_id):
    """Payment verification step with read-only fare enforced by database triggers."""
    try:
        with get_db_cursor() as cursor:
            # Fetch booking & trip info
            cursor.execute("""
                SELECT b.booking_id, b.status AS booking_status, b.booked_at,
                       s.seat_no,
                       p.passenger_id, p.name AS passenger_name, p.phone, p.email,
                       t.trip_id, t.departure_time, t.arrival_time,
                       r.source_city, r.dest_city,
                       u.reg_no, u.bus_type,
                       f.base_fare,
                       pm.payment_id, pm.status AS payment_status, pm.amount AS paid_amount
                FROM booking b
                JOIN seat s ON b.seat_id = s.seat_id
                JOIN passenger p ON b.passenger_id = p.passenger_id
                JOIN trip t ON b.trip_id = t.trip_id
                JOIN bus u ON t.bus_id = u.bus_id
                JOIN route r ON t.route_id = r.route_id
                LEFT JOIN fare f ON f.route_id = t.route_id AND f.bus_type = u.bus_type
                LEFT JOIN payment pm ON b.booking_id = pm.booking_id
                WHERE b.booking_id = %s;
            """, (booking_id,))
            booking_info = cursor.fetchone()

            if not booking_info:
                flash("Booking record not found.", "error")
                return redirect(url_for("booking.search"))

            # If already paid, take directly to ticket
            if booking_info["payment_id"] and booking_info["payment_status"] == "Paid":
                return redirect(url_for("booking.ticket", booking_id=booking_id))

    except Error as e:
        flash(f"Database error: {format_db_error(e)}", "error")
        return redirect(url_for("booking.search"))

    if request.method == "POST":
        method = request.form.get("method")
        fare_amount = booking_info["base_fare"]

        if not method or method not in ("Cash", "Card", "UPI", "NetBanking", "Wallet", "EMI"):
            flash("Please choose a valid payment method.", "error")
            return render_template("booking/payment.html", booking=booking_info)

        try:
            with get_db_cursor(commit=True) as cursor:
                # Insert payment record with exact fare amount
                # Trigger trg_payment_check will validate that NEW.amount == fare.base_fare
                cursor.execute("""
                    INSERT INTO payment (booking_id, amount, method, status)
                    VALUES (%s, %s, %s, 'Paid');
                """, (booking_id, fare_amount, method))

            flash("Payment processed successfully! Your booking is confirmed.", "success")
            return redirect(url_for("booking.ticket", booking_id=booking_id))

        except Error as e:
            flash(f"Payment verification failed: {format_db_error(e)}", "error")
            return render_template("booking/payment.html", booking=booking_info)

    return render_template("booking/payment.html", booking=booking_info)

@booking_bp.route("/ticket/<int:booking_id>")
def ticket(booking_id):
    """Renders printable ticket confirmation with trip and transaction details."""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT b.booking_id, b.status AS booking_status, b.booked_at,
                       s.seat_no,
                       p.name AS passenger_name, p.phone, p.email,
                       t.trip_id, t.departure_time, t.arrival_time, t.status AS trip_status,
                       r.source_city, r.dest_city, r.distance_km,
                       u.reg_no, u.bus_type,
                       pm.payment_id, pm.amount, pm.method, pm.paid_at, pm.status AS payment_status,
                       c.cancel_id, c.cancelled_at, c.refund_amount
                FROM booking b
                JOIN seat s ON b.seat_id = s.seat_id
                JOIN passenger p ON b.passenger_id = p.passenger_id
                JOIN trip t ON b.trip_id = t.trip_id
                JOIN bus u ON t.bus_id = u.bus_id
                JOIN route r ON t.route_id = r.route_id
                LEFT JOIN payment pm ON b.booking_id = pm.booking_id
                LEFT JOIN cancellation c ON b.booking_id = c.booking_id
                WHERE b.booking_id = %s;
            """, (booking_id,))
            ticket_data = cursor.fetchone()

            if not ticket_data:
                flash("Ticket record not found.", "error")
                return redirect(url_for("booking.search"))

    except Error as e:
        flash(f"Error loading ticket: {format_db_error(e)}", "error")
        return redirect(url_for("booking.search"))

    return render_template("booking/ticket.html", ticket=ticket_data)

@booking_bp.route("/my-bookings")
def my_bookings():
    """Allows passenger to look up their reservations by phone number."""
    phone = request.args.get("phone", "").strip()
    bookings = []
    passenger = None

    if phone:
        try:
            with get_db_cursor() as cursor:
                cursor.execute("SELECT passenger_id, name, phone, email FROM passenger WHERE phone = %s;", (phone,))
                passenger = cursor.fetchone()

                if passenger:
                    cursor.execute("""
                        SELECT b.booking_id, b.status AS booking_status, b.booked_at,
                               s.seat_no,
                               t.trip_id, t.departure_time, t.arrival_time, t.status AS trip_status,
                               r.source_city, r.dest_city,
                               u.reg_no, u.bus_type,
                               pm.amount, pm.method, pm.status AS payment_status,
                               c.refund_amount, c.cancelled_at
                        FROM booking b
                        JOIN seat s ON b.seat_id = s.seat_id
                        JOIN trip t ON b.trip_id = t.trip_id
                        JOIN bus u ON t.bus_id = u.bus_id
                        JOIN route r ON t.route_id = r.route_id
                        LEFT JOIN payment pm ON b.booking_id = pm.booking_id
                        LEFT JOIN cancellation c ON b.booking_id = c.booking_id
                        WHERE b.passenger_id = %s
                        ORDER BY b.booked_at DESC;
                    """, (passenger["passenger_id"],))
                    bookings = cursor.fetchall()
                else:
                    flash(f"No passenger account found with phone number: {phone}", "info")

        except Error as e:
            flash(f"Error fetching reservations: {format_db_error(e)}", "error")

    now = datetime.now()
    return render_template(
        "booking/my_bookings.html",
        phone=phone,
        passenger=passenger,
        bookings=bookings,
        now=now
    )

@booking_bp.route("/cancel/<int:booking_id>", methods=["GET", "POST"])
def cancel_booking(booking_id):
    """
    Cancellation workflow:
    Previews departure time, remaining hours, and refund tier.
    Inserts cancellation and relies completely on trg_cancel_policy & trg_cancel_after.
    """
    booking = None

    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT b.booking_id, b.status AS booking_status,
                       s.seat_no,
                       p.phone, p.name AS passenger_name,
                       t.departure_time, t.arrival_time,
                       r.source_city, r.dest_city,
                       u.reg_no,
                       pm.amount AS paid_amount, pm.status AS payment_status
                FROM booking b
                JOIN seat s ON b.seat_id = s.seat_id
                JOIN passenger p ON b.passenger_id = p.passenger_id
                JOIN trip t ON b.trip_id = t.trip_id
                JOIN bus u ON t.bus_id = u.bus_id
                JOIN route r ON t.route_id = r.route_id
                LEFT JOIN payment pm ON b.booking_id = pm.booking_id
                WHERE b.booking_id = %s;
            """, (booking_id,))
            booking = cursor.fetchone()

            if not booking:
                flash("Booking record not found.", "error")
                return redirect(url_for("booking.my_bookings"))

            if booking["booking_status"] != "Confirmed":
                flash(f"Booking #{booking_id} is already cancelled.", "warning")
                return redirect(url_for("booking.my_bookings", phone=booking["phone"]))

    except Error as e:
        flash(f"Database error: {format_db_error(e)}", "error")
        return redirect(url_for("booking.my_bookings"))

    # Compute preview metrics for display
    now = datetime.now()
    departure = booking["departure_time"]
    diff_hours = (departure - now).total_seconds() / 3600.0

    if diff_hours <= 0:
        tier_text = "Departure has already passed. Cancellations are strictly rejected."
        expected_refund_pct = 0
    elif diff_hours >= 24:
        tier_text = "24 hours or more before departure: 90% Refund"
        expected_refund_pct = 90
    elif diff_hours >= 6:
        tier_text = "Between 6 and 24 hours before departure: 50% Refund"
        expected_refund_pct = 50
    else:
        tier_text = "Less than 6 hours before departure: 0% Refund (No Refund)"
        expected_refund_pct = 0

    paid_amt = float(booking["paid_amount"] or 0)
    expected_refund_amt = paid_amt * (expected_refund_pct / 100.0)

    if request.method == "POST":
        try:
            with get_db_cursor(commit=True) as cursor:
                # Insert cancellation record.
                # The database trigger trg_cancel_policy computes NEW.refund_amount
                # and trg_cancel_after marks booking 'Cancelled' and payment 'Refunded'.
                cursor.execute("""
                    INSERT INTO cancellation (booking_id, cancelled_at)
                    VALUES (%s, NOW());
                """, (booking_id,))

                # Read back the actual refund calculated by MySQL trigger
                cursor.execute("""
                    SELECT refund_amount, cancelled_at 
                    FROM cancellation 
                    WHERE booking_id = %s;
                """, (booking_id,))
                cancellation_record = cursor.fetchone()
                refund_amount = cancellation_record["refund_amount"] if cancellation_record else expected_refund_amt

            flash(f"Booking #{booking_id} cancelled. Refund of ₹{float(refund_amount):.2f} has been processed according to policy.", "success")
            return redirect(url_for("booking.my_bookings", phone=booking["phone"]))

        except Error as e:
            flash(f"Cancellation rejected by database: {format_db_error(e)}", "error")
            return redirect(url_for("booking.my_bookings", phone=booking["phone"]))

    return render_template(
        "booking/cancel_confirm.html",
        booking=booking,
        diff_hours=round(diff_hours, 1),
        tier_text=tier_text,
        expected_refund_amt=expected_refund_amt
    )
