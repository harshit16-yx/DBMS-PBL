from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_cursor, format_db_error
from mysql.connector import Error

admin_bp = Blueprint("admin", __name__)

# =====================================================
# 1. ROUTES & STOPS MANAGEMENT
# =====================================================

@admin_bp.route("/routes", methods=["GET"])
def routes():
    """List all routes with stop counts and assigned fares."""
    routes_list = []
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT r.route_id, r.source_city, r.dest_city, r.distance_km,
                       COUNT(DISTINCT rs.stop_id) AS stops_count,
                       COUNT(DISTINCT t.trip_id) AS trips_count
                FROM route r
                LEFT JOIN route_stop rs ON r.route_id = rs.route_id
                LEFT JOIN trip t ON r.route_id = t.route_id
                GROUP BY r.route_id, r.source_city, r.dest_city, r.distance_km
                ORDER BY r.route_id ASC;
            """)
            routes_list = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching routes: {format_db_error(e)}", "error")

    return render_template("admin/routes.html", routes=routes_list)

@admin_bp.route("/routes/new", methods=["POST"])
def new_route():
    """Create a new route."""
    source = request.form.get("source_city", "").strip()
    dest = request.form.get("dest_city", "").strip()
    distance = request.form.get("distance_km", "").strip()

    try:
        with get_db_cursor(commit=True) as cursor:
            # Let DB CHECK constraints (chk_route_cities, chk_route_distance) and UNIQUE uq_route enforce rules
            cursor.execute("""
                INSERT INTO route (source_city, dest_city, distance_km)
                VALUES (%s, %s, %s);
            """, (source, dest, distance))
        flash(f"Route '{source} to {dest}' created successfully.", "success")
    except Error as e:
        flash(f"Could not create route: {format_db_error(e)}", "error")

    return redirect(url_for("admin.routes"))

@admin_bp.route("/routes/<int:route_id>/stops", methods=["GET", "POST"])
def route_stops(route_id):
    """Manage and order intermediate stops for a route."""
    route_data = None
    assigned_stops = []
    available_stops = []

    try:
        with get_db_cursor(commit=(request.method == "POST")) as cursor:
            cursor.execute("SELECT * FROM route WHERE route_id = %s;", (route_id,))
            route_data = cursor.fetchone()

            if not route_data:
                flash("Route not found.", "error")
                return redirect(url_for("admin.routes"))

            if request.method == "POST":
                action = request.form.get("action")
                if action == "add":
                    stop_id = request.form.get("stop_id")
                    stop_order = request.form.get("stop_order")
                    cursor.execute("""
                        INSERT INTO route_stop (route_id, stop_id, stop_order)
                        VALUES (%s, %s, %s);
                    """, (route_id, stop_id, stop_order))
                    flash("Stop assigned to route successfully.", "success")
                elif action == "delete":
                    stop_id = request.form.get("stop_id")
                    cursor.execute("""
                        DELETE FROM route_stop 
                        WHERE route_id = %s AND stop_id = %s;
                    """, (route_id, stop_id))
                    flash("Stop removed from route.", "success")

            # Fetch assigned stops
            cursor.execute("""
                SELECT rs.stop_id, rs.stop_order, s.stop_name, s.city
                FROM route_stop rs
                JOIN stop s ON rs.stop_id = s.stop_id
                WHERE rs.route_id = %s
                ORDER BY rs.stop_order ASC;
            """, (route_id,))
            assigned_stops = cursor.fetchall()

            # Fetch all master stops for dropdown
            cursor.execute("SELECT stop_id, stop_name, city FROM stop ORDER BY city, stop_name;")
            available_stops = cursor.fetchall()

    except Error as e:
        flash(f"Error updating route stops: {format_db_error(e)}", "error")

    return render_template(
        "admin/route_stops.html",
        route=route_data,
        assigned_stops=assigned_stops,
        available_stops=available_stops
    )

@admin_bp.route("/stops/new", methods=["POST"])
def new_stop():
    """Create a new master stop."""
    name = request.form.get("stop_name", "").strip()
    city = request.form.get("city", "").strip()
    return_to = request.form.get("return_to", url_for("admin.routes"))

    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO stop (stop_name, city) VALUES (%s, %s);", (name, city))
        flash(f"Stop '{name}' in {city} created.", "success")
    except Error as e:
        flash(f"Could not create stop: {format_db_error(e)}", "error")

    return redirect(return_to)

# =====================================================
# 2. FARES MATRIX
# =====================================================

@admin_bp.route("/fares", methods=["GET", "POST"])
def fares():
    """View and configure base fares per route and bus type."""
    fares_list = []
    routes_list = []
    bus_types = ["Seater", "Sleeper", "AC Seater", "AC Sleeper"]

    try:
        with get_db_cursor(commit=(request.method == "POST")) as cursor:
            if request.method == "POST":
                route_id = request.form.get("route_id")
                bus_type = request.form.get("bus_type")
                base_fare = request.form.get("base_fare")

                # Insert or update fare
                cursor.execute("""
                    INSERT INTO fare (route_id, bus_type, base_fare)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE base_fare = VALUES(base_fare);
                """, (route_id, bus_type, base_fare))
                flash("Fare configured successfully.", "success")

            # Fetch all fares
            cursor.execute("""
                SELECT f.fare_id, f.route_id, f.bus_type, f.base_fare,
                       r.source_city, r.dest_city, r.distance_km
                FROM fare f
                JOIN route r ON f.route_id = r.route_id
                ORDER BY r.source_city, r.dest_city, f.bus_type;
            """)
            fares_list = cursor.fetchall()

            # Fetch routes for selector
            cursor.execute("SELECT route_id, source_city, dest_city FROM route ORDER BY source_city;")
            routes_list = cursor.fetchall()

    except Error as e:
        flash(f"Fare operation error: {format_db_error(e)}", "error")

    return render_template(
        "admin/fares.html",
        fares=fares_list,
        routes=routes_list,
        bus_types=bus_types
    )

# =====================================================
# 3. FLEET & BUS MANAGEMENT (AUTO-GENERATE SEATS)
# =====================================================

@admin_bp.route("/buses", methods=["GET", "POST"])
def buses():
    """Manage buses, auto-generate seats upon bus addition, and toggle statuses."""
    buses_list = []

    if request.method == "POST":
        reg_no = request.form.get("reg_no", "").strip().upper()
        bus_type = request.form.get("bus_type")
        total_seats = int(request.form.get("total_seats", 20))
        status = request.form.get("status", "Active")

        try:
            with get_db_cursor(commit=True) as cursor:
                # 1. Insert bus record
                cursor.execute("""
                    INSERT INTO bus (reg_no, bus_type, total_seats, status)
                    VALUES (%s, %s, %s, %s);
                """, (reg_no, bus_type, total_seats, status))
                new_bus_id = cursor.lastrowid

                # 2. Auto-generate seats for the bus
                seat_records = []
                if "Sleeper" in bus_type:
                    half = total_seats // 2
                    # Lower berths
                    for i in range(1, half + 1):
                        seat_records.append((new_bus_id, f"L{i}"))
                    # Upper berths
                    for i in range(1, (total_seats - half) + 1):
                        seat_records.append((new_bus_id, f"U{i}"))
                else:
                    # Seater layout: 1A, 1B, 1C, 1D ...
                    cols = ["A", "B", "C", "D"]
                    count = 0
                    row = 1
                    while count < total_seats:
                        for col in cols:
                            if count >= total_seats:
                                break
                            seat_records.append((new_bus_id, f"{row}{col}"))
                            count += 1
                        row += 1

                for b_id, s_no in seat_records:
                    cursor.execute("INSERT INTO seat (bus_id, seat_no) VALUES (%s, %s);", (b_id, s_no))

            flash(f"Bus '{reg_no}' ({bus_type}) created with {len(seat_records)} auto-generated seats.", "success")
            return redirect(url_for("admin.buses"))

        except Error as e:
            flash(f"Failed to add bus: {format_db_error(e)}", "error")

    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT b.bus_id, b.reg_no, b.bus_type, b.total_seats, b.status,
                       COUNT(DISTINCT s.seat_id) AS seats_count,
                       COUNT(DISTINCT t.trip_id) AS trips_count
                FROM bus b
                LEFT JOIN seat s ON b.bus_id = s.bus_id
                LEFT JOIN trip t ON b.bus_id = t.bus_id
                GROUP BY b.bus_id, b.reg_no, b.bus_type, b.total_seats, b.status
                ORDER BY b.bus_id ASC;
            """)
            buses_list = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching fleet: {format_db_error(e)}", "error")

    return render_template("admin/buses.html", buses=buses_list)

@admin_bp.route("/buses/<int:bus_id>/status", methods=["POST"])
def update_bus_status(bus_id):
    """Update bus operational status (Active, Maintenance, Retired)."""
    new_status = request.form.get("status")
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("UPDATE bus SET status = %s WHERE bus_id = %s;", (new_status, bus_id))
        flash("Bus status updated.", "success")
    except Error as e:
        flash(f"Error updating bus status: {format_db_error(e)}", "error")
    return redirect(url_for("admin.buses"))

@admin_bp.route("/buses/<int:bus_id>/delete", methods=["POST"])
def delete_bus(bus_id):
    """Attempt bus deletion. Foreign key constraints block buses with existing trips."""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM seat WHERE bus_id = %s;", (bus_id,))
            cursor.execute("DELETE FROM bus WHERE bus_id = %s;", (bus_id,))
        flash("Bus and seats removed successfully.", "success")
    except Error as e:
        flash(f"Cannot delete bus: {format_db_error(e)}", "error")
    return redirect(url_for("admin.buses"))

# =====================================================
# 4. CREW MANAGEMENT (DRIVERS & CONDUCTORS)
# =====================================================

@admin_bp.route("/crew", methods=["GET", "POST"])
def crew():
    """Manage drivers and conductors."""
    drivers_list = []
    conductors_list = []

    if request.method == "POST":
        crew_role = request.form.get("role")
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()

        try:
            with get_db_cursor(commit=True) as cursor:
                if crew_role == "driver":
                    license_no = request.form.get("license_no", "").strip().upper()
                    cursor.execute("""
                        INSERT INTO driver (name, license_no, phone)
                        VALUES (%s, %s, %s);
                    """, (name, license_no, phone))
                    flash(f"Driver '{name}' added successfully.", "success")
                else:
                    cursor.execute("""
                        INSERT INTO conductor (name, phone)
                        VALUES (%s, %s);
                    """, (name, phone))
                    flash(f"Conductor '{name}' added successfully.", "success")
            return redirect(url_for("admin.crew"))
        except Error as e:
            flash(f"Failed to add crew member: {format_db_error(e)}", "error")

    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT d.driver_id, d.name, d.license_no, d.phone,
                       COUNT(t.trip_id) AS trips_count
                FROM driver d
                LEFT JOIN trip t ON d.driver_id = t.driver_id
                GROUP BY d.driver_id, d.name, d.license_no, d.phone
                ORDER BY d.name;
            """)
            drivers_list = cursor.fetchall()

            cursor.execute("""
                SELECT c.conductor_id, c.name, c.phone,
                       COUNT(t.trip_id) AS trips_count
                FROM conductor c
                LEFT JOIN trip t ON c.conductor_id = t.conductor_id
                GROUP BY c.conductor_id, c.name, c.phone
                ORDER BY c.name;
            """)
            conductors_list = cursor.fetchall()
    except Error as e:
        flash(f"Error fetching crew: {format_db_error(e)}", "error")

    return render_template("admin/crew.html", drivers=drivers_list, conductors=conductors_list)

# =====================================================
# 5. TRIP SCHEDULING (SURFACES TRIGGER OVERLAPS)
# =====================================================

@admin_bp.route("/trips", methods=["GET"])
def trips():
    """List scheduled and active trips with status/route filters."""
    status_filter = request.args.get("status", "")
    route_filter = request.args.get("route_id", "")
    trips_list = []
    routes_list = []

    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT route_id, source_city, dest_city FROM route ORDER BY source_city;")
            routes_list = cursor.fetchall()

            query = """
                SELECT t.trip_id, t.status, t.departure_time, t.arrival_time,
                       r.source_city, r.dest_city,
                       b.reg_no, b.bus_type,
                       d.name AS driver_name,
                       c.name AS conductor_name,
                       COUNT(CASE WHEN bk.status = 'Confirmed' THEN bk.booking_id END) AS booked_count,
                       b.total_seats
                FROM trip t
                JOIN route r ON t.route_id = r.route_id
                JOIN bus b ON t.bus_id = b.bus_id
                JOIN driver d ON t.driver_id = d.driver_id
                JOIN conductor c ON t.conductor_id = c.conductor_id
                LEFT JOIN booking bk ON t.trip_id = bk.trip_id
                WHERE 1=1
            """
            params = []
            if status_filter:
                query += " AND t.status = %s"
                params.append(status_filter)
            if route_filter:
                query += " AND t.route_id = %s"
                params.append(route_filter)

            query += """
                GROUP BY t.trip_id, t.status, t.departure_time, t.arrival_time,
                         r.source_city, r.dest_city, b.reg_no, b.bus_type,
                         d.name, c.name, b.total_seats
                ORDER BY t.departure_time DESC;
            """
            cursor.execute(query, tuple(params))
            trips_list = cursor.fetchall()

    except Error as e:
        flash(f"Error loading trips: {format_db_error(e)}", "error")

    return render_template(
        "admin/trips.html",
        trips=trips_list,
        routes=routes_list,
        status_filter=status_filter,
        route_filter=route_filter
    )

@admin_bp.route("/trips/new", methods=["GET", "POST"])
def new_trip():
    """
    Schedule a new trip.
    Directly exercises DB trigger trg_trip_overlap_ins to detect driver/conductor/bus clashes!
    """
    routes_list = []
    buses_list = []
    drivers_list = []
    conductors_list = []

    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT route_id, source_city, dest_city FROM route ORDER BY source_city;")
            routes_list = cursor.fetchall()
            cursor.execute("SELECT bus_id, reg_no, bus_type FROM bus WHERE status = 'Active' ORDER BY reg_no;")
            buses_list = cursor.fetchall()
            cursor.execute("SELECT driver_id, name, phone FROM driver ORDER BY name;")
            drivers_list = cursor.fetchall()
            cursor.execute("SELECT conductor_id, name, phone FROM conductor ORDER BY name;")
            conductors_list = cursor.fetchall()
    except Error as e:
        flash(f"Error loading resources: {format_db_error(e)}", "error")

    if request.method == "POST":
        route_id = request.form.get("route_id")
        bus_id = request.form.get("bus_id")
        driver_id = request.form.get("driver_id")
        conductor_id = request.form.get("conductor_id")
        departure_time = request.form.get("departure_time")
        arrival_time = request.form.get("arrival_time")

        try:
            with get_db_cursor(commit=True) as cursor:
                # Trigger trg_trip_overlap_ins runs automatically here.
                # If an overlap occurs, MySQL SIGNALs '45000' and our format_db_error displays it.
                cursor.execute("""
                    INSERT INTO trip (route_id, bus_id, driver_id, conductor_id, departure_time, arrival_time, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Scheduled');
                """, (route_id, bus_id, driver_id, conductor_id, departure_time, arrival_time))
            
            flash("Trip scheduled successfully without conflict.", "success")
            return redirect(url_for("admin.trips"))

        except Error as e:
            flash(f"Scheduling Conflict: {format_db_error(e)}", "error")

    return render_template(
        "admin/trip_form.html",
        routes=routes_list,
        buses=buses_list,
        drivers=drivers_list,
        conductors=conductors_list
    )

@admin_bp.route("/trips/<int:trip_id>/status", methods=["POST"])
def update_trip_status(trip_id):
    """Change trip status (Scheduled, Running, Completed, Cancelled)."""
    new_status = request.form.get("status")
    try:
        with get_db_cursor(commit=True) as cursor:
            # trg_trip_overlap_upd runs on status update
            cursor.execute("UPDATE trip SET status = %s WHERE trip_id = %s;", (new_status, trip_id))
        flash(f"Trip #{trip_id} status updated to '{new_status}'.", "success")
    except Error as e:
        flash(f"Error updating trip: {format_db_error(e)}", "error")
    return redirect(url_for("admin.trips"))
