import mysql.connector
from mysql.connector import pooling, Error
from contextlib import contextmanager
from config import Config

_pool = None

def get_connection_pool():
    """Initializes or returns the MySQL connection pool."""
    global _pool
    if _pool is None:
        try:
            _pool = pooling.MySQLConnectionPool(
                pool_name=Config.DB_POOL_NAME,
                pool_size=Config.DB_POOL_SIZE,
                pool_reset_session=True,
                host=Config.DB_HOST,
                port=Config.DB_PORT,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD,
                database=Config.DB_NAME,
                autocommit=False
            )
        except Error:
            # Pool creation deferred if MySQL service is starting or configured dynamically
            return None
    return _pool

def get_connection():
    """Gets a connection from pool or creates a direct connection."""
    pool = get_connection_pool()
    if pool:
        try:
            return pool.get_connection()
        except Error:
            pass
    # Fallback to direct connection if pool exhausted or unavailable
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        autocommit=False
    )

@contextmanager
def get_db_cursor(commit=False, dictionary=True):
    """
    Context manager providing a dictionary cursor and managing commits/rollbacks/cleanup.
    Guarantees connection is closed or returned to the pool safely.
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=dictionary)
        yield cursor
        if commit:
            conn.commit()
    except Error as e:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise e
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass

def format_db_error(e: Error) -> str:
    """
    Translates raw MySQL errors and trigger SIGNALs into clean, human-readable user messages.
    Preserves exact trigger messages raised by MySQL triggers (SQLSTATE 45000).
    """
    if not isinstance(e, Error):
        return str(e)
    
    error_msg = e.msg if hasattr(e, "msg") else str(e)
    error_code = e.errno if hasattr(e, "errno") else None
    sqlstate = e.sqlstate if hasattr(e, "sqlstate") else None

    # 1. Custom Trigger Signal (SQLSTATE 45000)
    # The application must NOT re-implement business rules; it displays the trigger's message directly.
    if sqlstate == "45000":
        return error_msg

    # 2. Duplicate Entry Violations (MySQL Error 1062)
    if error_code == 1062:
        if "uq_one_booking_per_seat" in error_msg:
            return "This seat is already booked for this trip."
        elif "uq_route" in error_msg:
            return "A route between these source and destination cities already exists."
        elif "uq_stop" in error_msg:
            return "A stop with this name already exists in this city."
        elif "uq_route_order" in error_msg:
            return "Another stop already holds this sequence order for the route."
        elif "uq_seat" in error_msg:
            return "A seat with this label already exists on this bus."
        elif "uq_fare" in error_msg:
            return "A fare for this route and bus type already exists."
        elif "reg_no" in error_msg:
            return "A bus with this registration number already exists."
        elif "license_no" in error_msg:
            return "A driver with this license number already exists."
        elif "phone" in error_msg:
            return "A crew member or passenger with this phone number already exists."
        elif "email" in error_msg:
            return "A passenger with this email address already exists."
        return f"Duplicate entry error: {error_msg}"

    # 3. Foreign Key Constraints (MySQL Errors 1451, 1452)
    if error_code == 1451:
        return "Cannot delete or modify this item because it is referenced by existing trips, bookings, or stops."
    if error_code == 1452:
        return "Referenced record (such as bus, route, or crew member) does not exist."

    # 4. Check Constraint Failures (MySQL Error 3819)
    if error_code == 3819:
        if "chk_route_cities" in error_msg:
            return "Source and destination cities cannot be identical."
        elif "chk_route_distance" in error_msg:
            return "Route distance must be greater than zero."
        elif "chk_trip_times" in error_msg:
            return "Trip arrival time must be later than departure time."
        elif "chk_fare" in error_msg:
            return "Base fare must be a positive amount."
        elif "chk_bus_seats" in error_msg:
            return "Total seats must be greater than zero."
        elif "chk_payment_amount" in error_msg:
            return "Payment amount must be greater than zero."
        return f"Data constraint validation failed: {error_msg}"

    # Fallback message
    return error_msg
