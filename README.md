# Bus Reservation and Fleet Scheduling System

A full-stack web application built for a university DBMS project using **Python (Flask)** and **MySQL 8.0.16+**.

---

## 1. System Architecture & Core Principles

This application strictly implements the **database-first architecture**:
* **Database as Single Source of Truth:** All domain rules (seat duplicate prevention, driver/conductor/bus conflict resolution, fare verification, cancellation refund tiers) are strictly enforced by MySQL constraints, generated columns, and triggers.
* **No Business Logic Duplication in Application Layer:** The Flask backend acts as an orchestrator. It executes parameterized SQL and translates raw MySQL signals (`SIGNAL SQLSTATE '45000'`, duplicate key `1062`, foreign key `1451`) into clear, user-friendly UI banners.
* **Calm Office-Style UI:** Responsive interface built with Jinja2 templates, a unified vanilla CSS design system (navy/slate/teal palette, generous spacing, clean tables, no heavy frameworks or animations), and vanilla JavaScript for interactive cabin seat selection.

---

## 2. Windows Setup & Installation Guide

### Prerequisites
1. **Python 3.10+** (Python 3.13 is verified).
2. **MySQL Server 8.0.16+** (MySQL 8.0.16 or higher is required for `CHECK` constraints and stored generated columns).

---

### Step 1: Open PowerShell in the Project Directory
```powershell
cd "c:\Users\Harshit Palla\Documents\DBMS\bus_app"
```

---

### Step 2: Create and Activate Python Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`)*

---

### Step 3: Install Required Python Packages
```powershell
pip install -r requirements.txt
```

---

### Step 4: Configure Database Connection (`.env`)
A default `.env` file is provided in `bus_app/`. Ensure the credentials match your local MySQL Server:
```ini
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=bus_system

SECRET_KEY=bus-system-secret-key-change-in-prod-2026
FLASK_DEBUG=True
FLASK_PORT=5000
```

---

### Step 5: Initialize and Seed the Database
Run the included database initialization script:
```powershell
python init_db.py
```
This script automatically executes:
1. `sql/schema.sql`: Creates database `bus_system`, 13 tables, CHECK constraints, stored generated columns, indexes, and all 5 triggers.
2. `sql/views.sql`: Creates the analytical views (`v_trip_occupancy`, `v_route_revenue`, `v_crew_utilization`, `v_bus_utilization`).
3. `sql/sample_data.sql`: Seeds 6 routes, 16 stops, 8 buses with generated seats, 8 drivers, 8 conductors, complete fares, 15 passengers, 15 trips (past and future), and ~30 bookings/payments.

*(Alternative manual execution via MySQL CLI:)*
```powershell
mysql -u root -p < sql/schema.sql
mysql -u root -p < sql/views.sql
mysql -u root -p < sql/sample_data.sql
```

---

### Step 6: Start the Flask Application
```powershell
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 3. Interactive Demo Script (Click-by-Click Guide)

Follow this step-by-step testing script to demonstrate all five core database and application behaviors:

### Flow 1: Search, Reserve Seat, Pay, and Issue Ticket
1. In the top navigation bar, click **Book Trip** (or visit `/booking/search`).
2. Filter by:
   * **Source City:** `Mumbai`
   * **Destination City:** `Pune`
   * Click **Search Available Trips**.
3. Locate Trip #7 (or any Scheduled trip) and click **Select Seats**.
4. You will see the **Bus Cabin Seating Layout**:
   * Click an available white seat (e.g. `2A` or `3A`).
   * Notice the seat turns navy blue and the selected seat label updates.
5. In the passenger section:
   * Select **New Passenger** and enter:
     * Name: `Sunil Gavaskar`
     * Phone: `9899001122`
   * Click **Proceed to Payment &rarr;**.
6. On the **Payment Page**:
   * Notice the **Base Fare** is **read-only** (e.g. `₹300.00`), automatically retrieved from the fare matrix.
   * Select Payment Method: `UPI`.
   * Click **Confirm Payment & Issue Ticket**.
7. The system redirects to the **Boarding Pass & Ticket**:
   * Displays the printable ticket with booking reference, passenger info, seat number, and payment status.
   * Click **Print Ticket** to view the clean printable layout.

---

### Flow 2: Rejecting Duplicate Seat Booking (Concurrency Protection)
1. Open a new Incognito window or separate browser tab.
2. Navigate to `http://127.0.0.1:5000/booking/search`.
3. Open the **same trip** used in Flow 1.
4. Try to book the seat you just confirmed in Flow 1 (it is now greyed out as `Booked`).
5. Even if two users click simultaneously or submit a forged POST request for that seat:
   * The database's unique constraint `uq_one_booking_per_seat UNIQUE (trip_id, active_seat)` rejects the insertion.
   * The application intercepts MySQL Error `1062` and displays a clean error banner:
     > **"Error: This seat is already booked for this trip."**

---

### Flow 3: Rejecting Overlapping Driver / Bus Schedule
1. In the top navigation, click **Admin &rarr; Trip Scheduling**.
2. Click **+ Schedule New Trip**.
3. Choose:
   * **Route:** `Mumbai &rarr; Pune`
   * **Bus:** `MH-12-AB-1001` (Bus #1)
   * **Driver:** `Ramesh Patil` (Driver #1)
   * **Conductor:** `Mahesh Jadhav` (Conductor #1)
4. Set times that conflict with an existing trip of Driver #1 (for example, departure and arrival overlapping with Trip #7):
   * Departure: `2026-10-10 10:00`
   * Arrival: `2026-10-10 14:00`
5. Click **Schedule Trip Service**.
6. The database trigger `trg_trip_overlap_ins` detects that Driver #1 or Bus #1 already has a scheduled trip during that interval.
7. The application intercepts the trigger signal and displays the exact database message:
   > **"Scheduling Conflict: Driver already has an overlapping trip"** (or *"Bus already has an overlapping trip"*).

---

### Flow 4: Tiered Cancellation Policy & Automated Refund
1. In top navigation, click **My Bookings**.
2. Enter passenger phone: `9820011223` (Aarav Mehta) and click **Search Bookings**.
3. The table displays his bookings across different time windows:
   * **Scenario A (&ge; 24h before departure):**
     * Click **Cancel** on a trip scheduled >24 hours out.
     * The confirmation page displays: `Policy Tier: 24 hours or more before departure: 90% Refund`.
     * Click **Confirm Cancellation**.
     * MySQL trigger `trg_cancel_policy` computes `NEW.refund_amount = paid * 0.90`.
     * MySQL trigger `trg_cancel_after` updates `booking.status = 'Cancelled'` and `payment.status = 'Refunded'`.
     * Flash banner displays: *"Booking #... cancelled. Refund of ₹... has been processed according to policy."*
   * **Scenario B (6 to 24h before departure):**
     * Booking on trip scheduled 14h out qualifies for the **50% Refund Tier**.
   * **Scenario C (< 6h before departure):**
     * Booking on trip scheduled 3h out qualifies for **0% Refund (No Refund)**.
   * **Scenario D (Past departure):**
     * If a cancellation is attempted after trip departure time, trigger `trg_cancel_policy` raises `SIGNAL SQLSTATE '45000'` with message:
       > **"Cannot cancel after departure"**

---

### Flow 5: Analytical Reports & SQL Views
1. Click **Reports** in the navigation bar.
2. Explore each report:
   * **Trip Occupancy (`/reports/occupancy`):** View total vs booked seats and occupancy progress bars powered by SQL View `v_trip_occupancy` with a subquery counting intermediate stops.
   * **Route Revenue (`/reports/revenue`):** View collections, refunds, and net margins powered by SQL View `v_route_revenue`. Test the **Start Date** and **End Date** filters.
   * **Cancellation Report (`/reports/cancellations`):** View cancellation counts and refund totals grouped by month and route.
   * **Crew Utilization (`/reports/crew-utilization`):** View duty hours and trips completed for drivers and conductors powered by SQL View `v_crew_utilization`.
   * **Bus Utilization (`/reports/bus-utilization`):** View vehicle running hours and completed trips powered by SQL View `v_bus_utilization`.
   * **Passenger History (`/reports/passenger-history`):** Select any customer from the dropdown to view their entire travel history and spending ledger.

---

## 4. Feature to Database Object Mapping Table

| Application Feature | Database Table(s) Involved | Enforcing Constraint / Trigger / View | Role in Business Rule Enforcement |
|---|---|---|---|
| **Trip Search & Availability** | `trip`, `route`, `bus`, `booking`, `fare` | `trip.status = 'Scheduled'`, `bk.status = 'Confirmed'` | Only open trips are displayed; available seats dynamically calculated by subtracting confirmed bookings. |
| **Seat Duplicate Prevention** | `booking`, `seat` | `active_seat` (Stored Generated Column), `uq_one_booking_per_seat` (UNIQUE) | Stored column evaluates to `seat_id` only when status is 'Confirmed' (NULL otherwise). MySQL UNIQUE constraint prevents duplicate active bookings for the same seat while allowing re-booking after cancellation. |
| **Seat & Trip Validation** | `booking`, `seat`, `trip` | Trigger `trg_booking_check` | Aborts insert if seat belongs to a different bus or if trip is not in 'Scheduled' status. |
| **Exact Fare Payment** | `payment`, `booking`, `trip`, `bus`, `fare` | Trigger `trg_payment_check`, `chk_payment_amount` | Aborts insert if payment amount does not match `fare.base_fare` for the trip's route and bus type. |
| **Cancellation Policy** | `cancellation`, `booking`, `trip`, `payment` | Trigger `trg_cancel_policy` | Enforces tiered refund computation based on hours remaining until departure (90%, 50%, 0%) and strictly blocks post-departure cancellations. |
| **Post-Cancellation Updates** | `booking`, `payment`, `cancellation` | Trigger `trg_cancel_after` | Automatically frees the seat (`booking.status = 'Cancelled'`) and marks payment status as `'Refunded'`. |
| **Trip Overlap Prevention (Insert)** | `trip` | Trigger `trg_trip_overlap_ins` | Blocks overlapping trip schedules for driver, conductor, or bus. |
| **Trip Overlap Prevention (Update)** | `trip` | Trigger `trg_trip_overlap_upd` | Blocks overlapping trip schedules when editing or updating existing trips. |
| **Route Integrity** | `route` | `chk_route_cities`, `chk_route_distance`, `uq_route` | Ensures source and destination differ, distance > 0, and unique city pairs. |
| **Fleet Seat Auto-Generation** | `bus`, `seat` | `chk_bus_seats`, `uq_seat` | Automatically generates seat records (e.g. 1A..5D or L1..U8) when bus is created; enforces positive seat count. |
| **Trip Time Validity** | `trip` | `chk_trip_times` | Enforces `arrival_time > departure_time`. |
| **Trip Occupancy Report** | `trip`, `route`, `bus`, `booking` | View `v_trip_occupancy` + Subquery | Aggregates booked vs total seats, calculates occupancy rate percentage. |
| **Route Revenue Report** | `route`, `trip`, `booking`, `payment`, `cancellation` | View `v_route_revenue` | Computes gross paid fares, refunds distributed, and net revenue. |
| **Crew Duty Hours Report** | `driver`, `conductor`, `trip` | View `v_crew_utilization` + Subquery | Calculates total duty hours and completed trips using `TIMESTAMPDIFF`. |
| **Bus Running Hours Report** | `bus`, `trip` | View `v_bus_utilization` | Aggregates operational running hours and trip counts per vehicle. |

---

## 5. Security & Code Quality Highlights

1. **Strict SQL Parameterization:** Every single database statement uses `%s` placeholders. String formatting / interpolation is never used.
2. **Safe Resource Management:** Connection pooling with context managers ensures cursors and connections are properly closed and returned to the pool, transactions committed on success, and rolled back on exceptions.
3. **Trigger-First Error Surfacing:** Friendly UI flash banners display the database trigger's exact message text rather than generic stack traces.
4. **Complete Implementation:** No placeholders, no TODOs, and no mock data in the codebase.
