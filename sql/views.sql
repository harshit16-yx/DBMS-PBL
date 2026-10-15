-- =====================================================
-- Bus Reservation and Fleet Scheduling System
-- File 2: Views (v_trip_occupancy, v_route_revenue, v_crew_utilization, v_bus_utilization)
-- =====================================================

USE bus_system;

-- 1. Trip Occupancy View (Used by Occupancy Report)
CREATE OR REPLACE VIEW v_trip_occupancy AS
SELECT 
    t.trip_id,
    t.route_id,
    r.source_city,
    r.dest_city,
    t.departure_time,
    t.arrival_time,
    t.status AS trip_status,
    b.bus_id,
    b.reg_no,
    b.bus_type,
    b.total_seats,
    COUNT(CASE WHEN bk.status = 'Confirmed' THEN bk.booking_id END) AS booked_seats,
    (b.total_seats - COUNT(CASE WHEN bk.status = 'Confirmed' THEN bk.booking_id END)) AS available_seats,
    ROUND((COUNT(CASE WHEN bk.status = 'Confirmed' THEN bk.booking_id END) * 100.0) / b.total_seats, 2) AS occupancy_pct
FROM trip t
JOIN route r ON t.route_id = r.route_id
JOIN bus b ON t.bus_id = b.bus_id
LEFT JOIN booking bk ON t.trip_id = bk.trip_id
GROUP BY t.trip_id, t.route_id, r.source_city, r.dest_city, t.departure_time, t.arrival_time, t.status, b.bus_id, b.reg_no, b.bus_type, b.total_seats;

-- 2. Route Revenue Summary View (Used by Revenue Report)
CREATE OR REPLACE VIEW v_route_revenue AS
SELECT 
    r.route_id,
    r.source_city,
    r.dest_city,
    r.distance_km,
    COUNT(DISTINCT t.trip_id) AS total_trips,
    COUNT(DISTINCT bk.booking_id) AS total_bookings,
    COALESCE(SUM(p.amount), 0.00) AS total_paid,
    COALESCE(SUM(c.refund_amount), 0.00) AS total_refunded,
    ROUND(COALESCE(SUM(p.amount), 0.00) - COALESCE(SUM(c.refund_amount), 0.00), 2) AS net_revenue
FROM route r
LEFT JOIN trip t ON r.route_id = t.route_id
LEFT JOIN booking bk ON t.trip_id = bk.trip_id
LEFT JOIN payment p ON bk.booking_id = p.booking_id
LEFT JOIN cancellation c ON bk.booking_id = c.booking_id
GROUP BY r.route_id, r.source_city, r.dest_city, r.distance_km;

-- 3. Crew Utilization Summary View (Driver & Conductor Duty Hours)
CREATE OR REPLACE VIEW v_crew_utilization AS
SELECT 
    'Driver' AS role,
    d.driver_id AS crew_id,
    d.name,
    d.phone,
    d.license_no AS credential,
    COUNT(t.trip_id) AS total_trips,
    COALESCE(SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END), 0) AS completed_trips,
    COALESCE(ROUND(SUM(TIMESTAMPDIFF(MINUTE, t.departure_time, t.arrival_time)) / 60.0, 2), 0.00) AS total_duty_hours
FROM driver d
LEFT JOIN trip t ON d.driver_id = t.driver_id AND t.status <> 'Cancelled'
GROUP BY d.driver_id, d.name, d.phone, d.license_no
UNION ALL
SELECT 
    'Conductor' AS role,
    c.conductor_id AS crew_id,
    c.name,
    c.phone,
    'N/A' AS credential,
    COUNT(t.trip_id) AS total_trips,
    COALESCE(SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END), 0) AS completed_trips,
    COALESCE(ROUND(SUM(TIMESTAMPDIFF(MINUTE, t.departure_time, t.arrival_time)) / 60.0, 2), 0.00) AS total_duty_hours
FROM conductor c
LEFT JOIN trip t ON c.conductor_id = t.conductor_id AND t.status <> 'Cancelled'
GROUP BY c.conductor_id, c.name, c.phone;

-- 4. Bus Utilization Summary View (Fleet Operating Hours)
CREATE OR REPLACE VIEW v_bus_utilization AS
SELECT 
    b.bus_id,
    b.reg_no,
    b.bus_type,
    b.status AS bus_status,
    b.total_seats,
    COUNT(t.trip_id) AS total_trips,
    COALESCE(SUM(CASE WHEN t.status = 'Completed' THEN 1 ELSE 0 END), 0) AS completed_trips,
    COALESCE(ROUND(SUM(TIMESTAMPDIFF(MINUTE, t.departure_time, t.arrival_time)) / 60.0, 2), 0.00) AS total_running_hours
FROM bus b
LEFT JOIN trip t ON b.bus_id = t.bus_id AND t.status <> 'Cancelled'
GROUP BY b.bus_id, b.reg_no, b.bus_type, b.status, b.total_seats;
