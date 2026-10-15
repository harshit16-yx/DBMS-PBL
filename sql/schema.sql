-- =====================================================
-- Bus Reservation and Fleet Scheduling System
-- File 1: Schema (tables, constraints, indexes, triggers)
-- Database: MySQL 8.0.16+
-- =====================================================

DROP DATABASE IF EXISTS bus_system;
CREATE DATABASE bus_system;
USE bus_system;

-- ---------- MASTER TABLES ----------

CREATE TABLE route (
    route_id     INT AUTO_INCREMENT PRIMARY KEY,
    source_city  VARCHAR(50) NOT NULL,
    dest_city    VARCHAR(50) NOT NULL,
    distance_km  INT NOT NULL,
    CONSTRAINT chk_route_cities   CHECK (source_city <> dest_city),
    CONSTRAINT chk_route_distance CHECK (distance_km > 0),
    CONSTRAINT uq_route UNIQUE (source_city, dest_city)
);

CREATE TABLE stop (
    stop_id    INT AUTO_INCREMENT PRIMARY KEY,
    stop_name  VARCHAR(80) NOT NULL,
    city       VARCHAR(50) NOT NULL,
    CONSTRAINT uq_stop UNIQUE (stop_name, city)
);

CREATE TABLE route_stop (
    route_id    INT NOT NULL,
    stop_id     INT NOT NULL,
    stop_order  INT NOT NULL,
    PRIMARY KEY (route_id, stop_id),
    CONSTRAINT uq_route_order UNIQUE (route_id, stop_order),
    CONSTRAINT chk_stop_order CHECK (stop_order > 0),
    FOREIGN KEY (route_id) REFERENCES route(route_id),
    FOREIGN KEY (stop_id)  REFERENCES stop(stop_id)
);

CREATE TABLE bus (
    bus_id       INT AUTO_INCREMENT PRIMARY KEY,
    reg_no       VARCHAR(20) NOT NULL UNIQUE,
    bus_type     ENUM('Seater','Sleeper','AC Seater','AC Sleeper') NOT NULL,
    total_seats  INT NOT NULL,
    status       ENUM('Active','Maintenance','Retired') NOT NULL DEFAULT 'Active',
    CONSTRAINT chk_bus_seats CHECK (total_seats > 0)
);

CREATE TABLE seat (
    seat_id  INT AUTO_INCREMENT PRIMARY KEY,
    bus_id   INT NOT NULL,
    seat_no  VARCHAR(5) NOT NULL,
    CONSTRAINT uq_seat UNIQUE (bus_id, seat_no),
    FOREIGN KEY (bus_id) REFERENCES bus(bus_id)
);

CREATE TABLE driver (
    driver_id   INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(80) NOT NULL,
    license_no  VARCHAR(30) NOT NULL UNIQUE,
    phone       VARCHAR(15) NOT NULL UNIQUE
);

CREATE TABLE conductor (
    conductor_id  INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(80) NOT NULL,
    phone         VARCHAR(15) NOT NULL UNIQUE
);

CREATE TABLE fare (
    fare_id    INT AUTO_INCREMENT PRIMARY KEY,
    route_id   INT NOT NULL,
    bus_type   ENUM('Seater','Sleeper','AC Seater','AC Sleeper') NOT NULL,
    base_fare  DECIMAL(8,2) NOT NULL,
    CONSTRAINT chk_fare CHECK (base_fare > 0),
    CONSTRAINT uq_fare UNIQUE (route_id, bus_type),
    FOREIGN KEY (route_id) REFERENCES route(route_id)
);

CREATE TABLE passenger (
    passenger_id  INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(80) NOT NULL,
    phone         VARCHAR(15) NOT NULL UNIQUE,
    email         VARCHAR(100) UNIQUE
);

-- ---------- TRANSACTION TABLES ----------

CREATE TABLE trip (
    trip_id         INT AUTO_INCREMENT PRIMARY KEY,
    route_id        INT NOT NULL,
    bus_id          INT NOT NULL,
    driver_id       INT NOT NULL,
    conductor_id    INT NOT NULL,
    departure_time  DATETIME NOT NULL,
    arrival_time    DATETIME NOT NULL,
    status          ENUM('Scheduled','Running','Completed','Cancelled')
                    NOT NULL DEFAULT 'Scheduled',
    CONSTRAINT chk_trip_times CHECK (arrival_time > departure_time),
    FOREIGN KEY (route_id)     REFERENCES route(route_id),
    FOREIGN KEY (bus_id)       REFERENCES bus(bus_id),
    FOREIGN KEY (driver_id)    REFERENCES driver(driver_id),
    FOREIGN KEY (conductor_id) REFERENCES conductor(conductor_id)
);

-- Rule: one ACTIVE booking per seat per trip.
-- active_seat is seat_id only while status = 'Confirmed', else NULL.
-- UNIQUE ignores NULLs, so a cancelled seat can be booked again.
CREATE TABLE booking (
    booking_id    INT AUTO_INCREMENT PRIMARY KEY,
    trip_id       INT NOT NULL,
    seat_id       INT NOT NULL,
    passenger_id  INT NOT NULL,
    booked_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status        ENUM('Confirmed','Cancelled') NOT NULL DEFAULT 'Confirmed',
    active_seat   INT GENERATED ALWAYS AS
                  (IF(status = 'Confirmed', seat_id, NULL)) STORED,
    CONSTRAINT uq_one_booking_per_seat UNIQUE (trip_id, active_seat),
    FOREIGN KEY (trip_id)      REFERENCES trip(trip_id),
    FOREIGN KEY (seat_id)      REFERENCES seat(seat_id),
    FOREIGN KEY (passenger_id) REFERENCES passenger(passenger_id)
);

CREATE TABLE payment (
    payment_id  INT AUTO_INCREMENT PRIMARY KEY,
    booking_id  INT NOT NULL UNIQUE,
    amount      DECIMAL(8,2) NOT NULL,
    method      ENUM('Cash','Card','UPI','NetBanking','Wallet','EMI') NOT NULL,
    paid_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status      ENUM('Paid','Refunded') NOT NULL DEFAULT 'Paid',
    CONSTRAINT chk_payment_amount CHECK (amount > 0),
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id)
);

CREATE TABLE cancellation (
    cancel_id      INT AUTO_INCREMENT PRIMARY KEY,
    booking_id     INT NOT NULL UNIQUE,
    cancelled_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    refund_amount  DECIMAL(8,2) NOT NULL DEFAULT 0,
    CONSTRAINT chk_refund CHECK (refund_amount >= 0),
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id)
);

-- ---------- INDEXES (frequently searched columns) ----------

CREATE INDEX idx_route_cities  ON route(source_city, dest_city);
CREATE INDEX idx_trip_route_dt ON trip(route_id, departure_time);
CREATE INDEX idx_trip_driver   ON trip(driver_id, departure_time);
CREATE INDEX idx_trip_conductor ON trip(conductor_id, departure_time);
CREATE INDEX idx_trip_bus      ON trip(bus_id, departure_time);
CREATE INDEX idx_booking_pass  ON booking(passenger_id);

-- ---------- TRIGGERS (business rules CHECK cannot handle) ----------

DELIMITER $$

-- Rule: no overlapping duties for driver, conductor or bus
CREATE TRIGGER trg_trip_overlap_ins BEFORE INSERT ON trip
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT 1 FROM trip
               WHERE driver_id = NEW.driver_id AND status <> 'Cancelled'
                 AND NEW.departure_time < arrival_time
                 AND NEW.arrival_time > departure_time) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Driver already has an overlapping trip';
    END IF;
    IF EXISTS (SELECT 1 FROM trip
               WHERE conductor_id = NEW.conductor_id AND status <> 'Cancelled'
                 AND NEW.departure_time < arrival_time
                 AND NEW.arrival_time > departure_time) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Conductor already has an overlapping trip';
    END IF;
    IF EXISTS (SELECT 1 FROM trip
               WHERE bus_id = NEW.bus_id AND status <> 'Cancelled'
                 AND NEW.departure_time < arrival_time
                 AND NEW.arrival_time > departure_time) THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Bus already has an overlapping trip';
    END IF;
END$$

CREATE TRIGGER trg_trip_overlap_upd BEFORE UPDATE ON trip
FOR EACH ROW
BEGIN
    IF NEW.status <> 'Cancelled' THEN
        IF EXISTS (SELECT 1 FROM trip
                   WHERE driver_id = NEW.driver_id AND trip_id <> NEW.trip_id
                     AND status <> 'Cancelled'
                     AND NEW.departure_time < arrival_time
                     AND NEW.arrival_time > departure_time) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Driver already has an overlapping trip';
        END IF;
        IF EXISTS (SELECT 1 FROM trip
                   WHERE conductor_id = NEW.conductor_id AND trip_id <> NEW.trip_id
                     AND status <> 'Cancelled'
                     AND NEW.departure_time < arrival_time
                     AND NEW.arrival_time > departure_time) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Conductor already has an overlapping trip';
        END IF;
        IF EXISTS (SELECT 1 FROM trip
                   WHERE bus_id = NEW.bus_id AND trip_id <> NEW.trip_id
                     AND status <> 'Cancelled'
                     AND NEW.departure_time < arrival_time
                     AND NEW.arrival_time > departure_time) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Bus already has an overlapping trip';
        END IF;
    END IF;
END$$

-- Rule: seat must belong to the trip's bus, and trip must still be open
CREATE TRIGGER trg_booking_check BEFORE INSERT ON booking
FOR EACH ROW
BEGIN
    DECLARE v_bus INT;
    DECLARE v_seat_bus INT;
    DECLARE v_status VARCHAR(20);
    SELECT bus_id, status INTO v_bus, v_status FROM trip WHERE trip_id = NEW.trip_id;
    SELECT bus_id INTO v_seat_bus FROM seat WHERE seat_id = NEW.seat_id;
    IF v_bus <> v_seat_bus THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Seat does not belong to the bus of this trip';
    END IF;
    IF v_status <> 'Scheduled' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Trip is not open for booking';
    END IF;
END$$

-- Rule: payment amount must equal the fare of that trip
CREATE TRIGGER trg_payment_check BEFORE INSERT ON payment
FOR EACH ROW
BEGIN
    DECLARE v_fare DECIMAL(8,2);
    SELECT f.base_fare INTO v_fare
    FROM booking b
    JOIN trip t ON t.trip_id = b.trip_id
    JOIN bus  u ON u.bus_id  = t.bus_id
    JOIN fare f ON f.route_id = t.route_id AND f.bus_type = u.bus_type
    WHERE b.booking_id = NEW.booking_id;
    IF v_fare IS NULL OR NEW.amount <> v_fare THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Payment amount does not match the fare';
    END IF;
END$$

-- Rule: cancellation policy
--   24 hours or more before departure -> 90% refund
--   6 to 24 hours before departure    -> 50% refund
--   less than 6 hours                 -> no refund
--   after departure                   -> not allowed
CREATE TRIGGER trg_cancel_policy BEFORE INSERT ON cancellation
FOR EACH ROW
BEGIN
    DECLARE v_dep DATETIME;
    DECLARE v_paid DECIMAL(8,2);
    DECLARE v_status VARCHAR(20);
    DECLARE v_hours INT;
    SELECT t.departure_time, b.status INTO v_dep, v_status
    FROM booking b JOIN trip t ON t.trip_id = b.trip_id
    WHERE b.booking_id = NEW.booking_id;
    IF v_status <> 'Confirmed' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Booking is already cancelled';
    END IF;
    IF v_dep <= NEW.cancelled_at THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot cancel after departure';
    END IF;
    SELECT COALESCE(SUM(amount), 0) INTO v_paid
    FROM payment WHERE booking_id = NEW.booking_id;
    SET v_hours = TIMESTAMPDIFF(HOUR, NEW.cancelled_at, v_dep);
    SET NEW.refund_amount = v_paid * CASE
        WHEN v_hours >= 24 THEN 0.90
        WHEN v_hours >= 6  THEN 0.50
        ELSE 0 END;
END$$

-- After cancelling: free the seat and mark payment refunded
CREATE TRIGGER trg_cancel_after AFTER INSERT ON cancellation
FOR EACH ROW
BEGIN
    UPDATE booking SET status = 'Cancelled' WHERE booking_id = NEW.booking_id;
    UPDATE payment SET status = 'Refunded' WHERE booking_id = NEW.booking_id;
END$$

DELIMITER ;
