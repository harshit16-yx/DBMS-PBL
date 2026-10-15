from flask import Blueprint, render_template, request, flash
from db import get_db_cursor, format_db_error
from mysql.connector import Error

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/")
def index():
    """Reports and analytics navigation hub."""
    return render_template("reports/index.html")

@reports_bp.route("/occupancy")
def occupancy():
    """
    Report 13: Occupancy per trip.
    Uses VIEW v_trip_occupancy and a subquery for total stops.
    """
    report_data = []
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    vo.trip_id, vo.source_city, vo.dest_city,
                    vo.departure_time, vo.arrival_time, vo.trip_status,
                    vo.bus_type, vo.reg_no, vo.total_seats,
                    vo.booked_seats, vo.available_seats,
                    vo.occupancy_pct,
                    (SELECT COUNT(*) FROM route_stop rs WHERE rs.route_id = vo.route_id) AS intermediate_stops_count
                FROM v_trip_occupancy vo
                ORDER BY vo.departure_time DESC;
            """)
            report_data = cursor.fetchall()
    except Error as e:
        flash(f"Error generating occupancy report: {format_db_error(e)}", "error")

    return render_template("reports/occupancy.html", reports=report_data)

@reports_bp.route("/revenue")
def revenue():
    """
    Report 14: Revenue per route with optional date filtering.
    Uses VIEW v_route_revenue and subqueries.
    """
    start_date = request.args.get("start_date", "").strip()
    end_date = request.args.get("end_date", "").strip()
    report_data = []

    try:
        with get_db_cursor() as cursor:
            if start_date and end_date:
                # Filtered query for selected date range
                cursor.execute("""
                    SELECT 
                        r.route_id, r.source_city, r.dest_city, r.distance_km,
                        COUNT(DISTINCT t.trip_id) AS total_trips,
                        COUNT(DISTINCT bk.booking_id) AS total_bookings,
                        COALESCE(SUM(p.amount), 0.00) AS total_paid,
                        COALESCE(SUM(c.refund_amount), 0.00) AS total_refunded,
                        ROUND(COALESCE(SUM(p.amount), 0.00) - COALESCE(SUM(c.refund_amount), 0.00), 2) AS net_revenue,
                        (SELECT COUNT(DISTINCT f.bus_type) FROM fare f WHERE f.route_id = r.route_id) AS fare_tiers_count
                    FROM route r
                    LEFT JOIN trip t ON r.route_id = t.route_id AND DATE(t.departure_time) BETWEEN %s AND %s
                    LEFT JOIN booking bk ON t.trip_id = bk.trip_id
                    LEFT JOIN payment p ON bk.booking_id = p.booking_id
                    LEFT JOIN cancellation c ON bk.booking_id = c.booking_id
                    GROUP BY r.route_id, r.source_city, r.dest_city, r.distance_km
                    ORDER BY net_revenue DESC;
                """, (start_date, end_date))
            else:
                # Overall view using v_route_revenue
                cursor.execute("""
                    SELECT 
                        vr.route_id, vr.source_city, vr.dest_city, vr.distance_km,
                        vr.total_trips, vr.total_bookings, vr.total_paid, vr.total_refunded, vr.net_revenue,
                        (SELECT COUNT(DISTINCT f.bus_type) FROM fare f WHERE f.route_id = vr.route_id) AS fare_tiers_count
                    FROM v_route_revenue vr
                    ORDER BY vr.net_revenue DESC;
                """)
            report_data = cursor.fetchall()
    except Error as e:
        flash(f"Error generating revenue report: {format_db_error(e)}", "error")

    # Compute overall totals
    grand_paid = sum(float(r["total_paid"]) for r in report_data) if report_data else 0.0
    grand_refunded = sum(float(r["total_refunded"]) for r in report_data) if report_data else 0.0
    grand_net = grand_paid - grand_refunded

    return render_template(
        "reports/revenue.html",
        reports=report_data,
        start_date=start_date,
        end_date=end_date,
        grand_paid=grand_paid,
        grand_refunded=grand_refunded,
        grand_net=grand_net
    )

@reports_bp.route("/cancellations")
def cancellations():
    """
    Report 15: Cancellation report.
    Volume and refund amount aggregated by route and month.
    """
    report_data = []
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(c.cancelled_at, '%%Y-%%m') AS cancel_month,
                    r.route_id, r.source_city, r.dest_city,
                    COUNT(c.cancel_id) AS total_cancellations,
                    COALESCE(SUM(c.refund_amount), 0.00) AS total_refunds,
                    ROUND(AVG(c.refund_amount), 2) AS avg_refund,
                    ROUND(AVG(TIMESTAMPDIFF(HOUR, c.cancelled_at, t.departure_time)), 1) AS avg_hours_before_dep
                FROM cancellation c
                JOIN booking b ON c.booking_id = b.booking_id
                JOIN trip t ON b.trip_id = t.trip_id
                JOIN route r ON t.route_id = r.route_id
                GROUP BY DATE_FORMAT(c.cancelled_at, '%%Y-%%m'), r.route_id, r.source_city, r.dest_city
                ORDER BY cancel_month DESC, total_cancellations DESC;
            """)
            report_data = cursor.fetchall()
    except Error as e:
        flash(f"Error generating cancellation report: {format_db_error(e)}", "error")

    return render_template("reports/cancellations.html", reports=report_data)

@reports_bp.route("/crew-utilization")
def crew_utilization():
    """
    Report 16: Crew utilization.
    Trips and duty hours per driver and conductor using VIEW v_crew_utilization + subquery.
    """
    drivers_data = []
    conductors_data = []

    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    v.role, v.crew_id, v.name, v.phone, v.credential,
                    v.total_trips, v.completed_trips, v.total_duty_hours,
                    (SELECT COUNT(*) FROM trip t2 
                     WHERE ((v.role = 'Driver' AND t2.driver_id = v.crew_id) OR (v.role = 'Conductor' AND t2.conductor_id = v.crew_id))
                       AND t2.status = 'Scheduled' AND t2.departure_time >= NOW()) AS upcoming_scheduled_trips
                FROM v_crew_utilization v
                ORDER BY v.role, v.total_duty_hours DESC;
            """)
            all_crew = cursor.fetchall()
            drivers_data = [c for c in all_crew if c["role"] == "Driver"]
            conductors_data = [c for c in all_crew if c["role"] == "Conductor"]
    except Error as e:
        flash(f"Error generating crew utilization report: {format_db_error(e)}", "error")

    return render_template(
        "reports/crew_utilization.html",
        drivers=drivers_data,
        conductors=conductors_data
    )

@reports_bp.route("/bus-utilization")
def bus_utilization():
    """
    Report 17: Bus fleet utilization.
    Trips and operating hours per bus vehicle using VIEW v_bus_utilization.
    """
    report_data = []
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    bus_id, reg_no, bus_type, bus_status, total_seats,
                    total_trips, completed_trips, total_running_hours
                FROM v_bus_utilization
                ORDER BY total_running_hours DESC, total_trips DESC;
            """)
            report_data = cursor.fetchall()
    except Error as e:
        flash(f"Error generating bus utilization report: {format_db_error(e)}", "error")

    return render_template("reports/bus_utilization.html", reports=report_data)

@reports_bp.route("/passenger-history")
@reports_bp.route("/passenger-history/<int:passenger_id>")
def passenger_history(passenger_id=None):
    """
    Report 18: Passenger travel & spending history.
    Full booking timeline and financial aggregates for an individual customer.
    """
    passengers_list = []
    passenger = None
    bookings_history = []
    summary = {
        "total_bookings": 0,
        "confirmed": 0,
        "cancelled": 0,
        "total_paid": 0.00,
        "total_refunded": 0.00,
        "net_spent": 0.00
    }

    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT passenger_id, name, phone FROM passenger ORDER BY name ASC;")
            passengers_list = cursor.fetchall()

            if not passenger_id and passengers_list:
                passenger_id = passengers_list[0]["passenger_id"]

            if passenger_id:
                cursor.execute("SELECT * FROM passenger WHERE passenger_id = %s;", (passenger_id,))
                passenger = cursor.fetchone()

                cursor.execute("""
                    SELECT 
                        b.booking_id, b.status AS booking_status, b.booked_at,
                        s.seat_no,
                        t.trip_id, t.departure_time, t.arrival_time, t.status AS trip_status,
                        r.source_city, r.dest_city, r.distance_km,
                        u.reg_no, u.bus_type,
                        pm.amount AS paid_amount, pm.method AS payment_method, pm.status AS payment_status,
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
                """, (passenger_id,))
                bookings_history = cursor.fetchall()

                # Calculate summaries
                summary["total_bookings"] = len(bookings_history)
                for bk in bookings_history:
                    if bk["booking_status"] == "Confirmed":
                        summary["confirmed"] += 1
                    elif bk["booking_status"] == "Cancelled":
                        summary["cancelled"] += 1
                    if bk["paid_amount"]:
                        summary["total_paid"] += float(bk["paid_amount"])
                    if bk["refund_amount"]:
                        summary["total_refunded"] += float(bk["refund_amount"])
                summary["net_spent"] = summary["total_paid"] - summary["total_refunded"]

    except Error as e:
        flash(f"Error loading passenger history: {format_db_error(e)}", "error")

    return render_template(
        "reports/passenger_history.html",
        passengers=passengers_list,
        selected_passenger=passenger,
        bookings=bookings_history,
        summary=summary
    )
