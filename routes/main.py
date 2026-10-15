from flask import Blueprint, render_template, flash
from db import get_db_cursor, format_db_error
from mysql.connector import Error

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    metrics = {
        "total_routes": 0,
        "active_buses": 0,
        "scheduled_trips": 0,
        "confirmed_bookings": 0,
        "net_revenue": 0.00
    }
    upcoming_trips = []
    recent_bookings = []

    try:
        with get_db_cursor() as cursor:
            # 1. Total Routes
            cursor.execute("SELECT COUNT(*) AS cnt FROM route;")
            row = cursor.fetchone()
            metrics["total_routes"] = row["cnt"] if row else 0

            # 2. Active Buses
            cursor.execute("SELECT COUNT(*) AS cnt FROM bus WHERE status = 'Active';")
            row = cursor.fetchone()
            metrics["active_buses"] = row["cnt"] if row else 0

            # 3. Scheduled Trips
            cursor.execute("SELECT COUNT(*) AS cnt FROM trip WHERE status = 'Scheduled';")
            row = cursor.fetchone()
            metrics["scheduled_trips"] = row["cnt"] if row else 0

            # 4. Confirmed Bookings
            cursor.execute("SELECT COUNT(*) AS cnt FROM booking WHERE status = 'Confirmed';")
            row = cursor.fetchone()
            metrics["confirmed_bookings"] = row["cnt"] if row else 0

            # 5. Total Net Revenue (Paid - Refunded)
            cursor.execute("""
                SELECT 
                    COALESCE((SELECT SUM(amount) FROM payment WHERE status = 'Paid'), 0.00)
                    -
                    COALESCE((SELECT SUM(refund_amount) FROM cancellation), 0.00) AS net_revenue;
            """)
            row = cursor.fetchone()
            metrics["net_revenue"] = float(row["net_revenue"]) if row and row["net_revenue"] else 0.00

            # Upcoming Trips for Quick View
            cursor.execute("""
                SELECT t.trip_id, r.source_city, r.dest_city, b.reg_no, b.bus_type,
                       t.departure_time, t.arrival_time, t.status
                FROM trip t
                JOIN route r ON t.route_id = r.route_id
                JOIN bus b ON t.bus_id = b.bus_id
                WHERE t.status = 'Scheduled' AND t.departure_time >= NOW()
                ORDER BY t.departure_time ASC
                LIMIT 5;
            """)
            upcoming_trips = cursor.fetchall()

            # Recent Confirmed Bookings
            cursor.execute("""
                SELECT bk.booking_id, p.name AS passenger_name, p.phone,
                       r.source_city, r.dest_city, s.seat_no, bk.booked_at,
                       t.departure_time
                FROM booking bk
                JOIN passenger p ON bk.passenger_id = p.passenger_id
                JOIN trip t ON bk.trip_id = t.trip_id
                JOIN route r ON t.route_id = r.route_id
                JOIN seat s ON bk.seat_id = s.seat_id
                WHERE bk.status = 'Confirmed'
                ORDER BY bk.booked_at DESC
                LIMIT 5;
            """)
            recent_bookings = cursor.fetchall()

    except Error as e:
        flash(f"Database notice: {format_db_error(e)}. Please ensure MySQL is running and the database is initialized.", "warning")

    return render_template(
        "index.html",
        metrics=metrics,
        upcoming_trips=upcoming_trips,
        recent_bookings=recent_bookings
    )
