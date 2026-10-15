-- =====================================================
-- Bus Reservation and Fleet Scheduling System
-- File 3: Sample Data (Realistic dataset for testing and reporting)
-- =====================================================

USE bus_system;

-- 1. Routes (12 routes across Indian cities)
INSERT INTO route (route_id, source_city, dest_city, distance_km) VALUES
(1, 'Mumbai', 'Pune', 150),
(2, 'Bengaluru', 'Chennai', 350),
(3, 'Delhi', 'Jaipur', 280),
(4, 'Hyderabad', 'Vijayawada', 275),
(5, 'Ahmedabad', 'Surat', 265),
(6, 'Chennai', 'Coimbatore', 500),
(7, 'Lucknow', 'Varanasi', 320),
(8, 'Kolkata', 'Bhubaneswar', 440),
(9, 'Pune', 'Goa', 460),
(10, 'Chandigarh', 'Shimla', 115),
(11, 'Kochi', 'Trivandrum', 205),
(12, 'Indore', 'Bhopal', 195);

-- 2. Stops (30 stops)
INSERT INTO stop (stop_id, stop_name, city) VALUES
(1, 'Dadar TT Circle', 'Mumbai'),
(2, 'Borivali West Station', 'Mumbai'),
(3, 'Swargate Bus Terminal', 'Pune'),
(4, 'Wakad Hinjawadi Flyover', 'Pune'),
(5, 'Majestic KBS', 'Bengaluru'),
(6, 'Silk Board Junction', 'Bengaluru'),
(7, 'CMBT Koyambedu', 'Chennai'),
(8, 'Guindy Kathipara', 'Chennai'),
(9, 'Kashmiri Gate ISBT', 'Delhi'),
(10, 'Dhaula Kuan Metro', 'Delhi'),
(11, 'Sindhi Camp Station', 'Jaipur'),
(12, 'MGBS Central Bus Station', 'Hyderabad'),
(13, 'Miyapur Metro', 'Hyderabad'),
(14, 'PNBS Terminal', 'Vijayawada'),
(15, 'Geeta Mandir Central', 'Ahmedabad'),
(16, 'Gandhipuram Terminal', 'Coimbatore'),
(17, 'Alambagh Bus Station', 'Lucknow'),
(18, 'Charbagh Railway Station', 'Lucknow'),
(19, 'Varanasi Cantt Terminal', 'Varanasi'),
(20, 'Esplanade Bus Stand', 'Kolkata'),
(21, 'Karunamoyee Terminal', 'Kolkata'),
(22, 'Baramunda Bus Stand', 'Bhubaneswar'),
(23, 'Mapusa Bus Stand', 'Goa'),
(24, 'Kadamba Bus Terminal Panaji', 'Goa'),
(25, 'ISBT Sector 43', 'Chandigarh'),
(26, 'Shimla ISBT', 'Shimla'),
(27, 'Ernakulam KSRTC Stand', 'Kochi'),
(28, 'Thampanoor Central', 'Trivandrum'),
(29, 'Sarwate Bus Stand', 'Indore'),
(30, 'ISBT Bhopal', 'Bhopal');

-- 3. Route Stops
INSERT INTO route_stop (route_id, stop_id, stop_order) VALUES
(1, 1, 1),
(1, 4, 2),
(1, 3, 3),
(2, 5, 1),
(2, 6, 2),
(2, 8, 3),
(2, 7, 4),
(3, 9, 1),
(3, 10, 2),
(3, 11, 3),
(4, 13, 1),
(4, 12, 2),
(4, 14, 3),
(5, 15, 1),
(6, 7, 1),
(6, 16, 2),
(7, 17, 1),
(7, 18, 2),
(7, 19, 3),
(8, 20, 1),
(8, 21, 2),
(8, 22, 3),
(9, 3, 1),
(9, 23, 2),
(9, 24, 3),
(10, 25, 1),
(10, 26, 2),
(11, 27, 1),
(11, 28, 2),
(12, 29, 1),
(12, 30, 2);



-- 4. Fleet / Buses (14 buses across all types)
INSERT INTO bus (bus_id, reg_no, bus_type, total_seats, status) VALUES
(1, 'MH-12-AB-1001', 'Seater', 20, 'Active'),
(2, 'KA-01-CD-2002', 'AC Seater', 20, 'Active'),
(3, 'DL-01-EF-3003', 'Sleeper', 16, 'Active'),
(4, 'TS-09-GH-4004', 'AC Sleeper', 16, 'Active'),
(5, 'GJ-01-JK-5005', 'AC Seater', 20, 'Active'),
(6, 'TN-02-LM-6006', 'AC Sleeper', 16, 'Active'),
(7, 'MH-14-NP-7007', 'Seater', 20, 'Maintenance'),
(8, 'KA-04-QR-8008', 'Sleeper', 16, 'Active'),
(9, 'UP-32-ST-9009', 'AC Seater', 20, 'Active'),
(10, 'WB-06-UV-1010', 'AC Sleeper', 16, 'Active'),
(11, 'GA-01-WX-1111', 'Sleeper', 16, 'Active'),
(12, 'CH-01-YZ-1212', 'Seater', 20, 'Active'),
(13, 'KL-07-AB-1313', 'AC Seater', 20, 'Active'),
(14, 'MP-09-CD-1414', 'AC Sleeper', 16, 'Active');

-- 5. Seats for all 14 buses
-- Bus 1, 2, 5, 7, 9, 12, 13 (20 Seater buses: 1A..5D)
INSERT INTO seat (bus_id, seat_no) VALUES
(1, '1A'), (1, '1B'), (1, '1C'), (1, '1D'),
(1, '2A'), (1, '2B'), (1, '2C'), (1, '2D'),
(1, '3A'), (1, '3B'), (1, '3C'), (1, '3D'),
(1, '4A'), (1, '4B'), (1, '4C'), (1, '4D'),
(1, '5A'), (1, '5B'), (1, '5C'), (1, '5D'),
(2, '1A'), (2, '1B'), (2, '1C'), (2, '1D'),
(2, '2A'), (2, '2B'), (2, '2C'), (2, '2D'),
(2, '3A'), (2, '3B'), (2, '3C'), (2, '3D'),
(2, '4A'), (2, '4B'), (2, '4C'), (2, '4D'),
(2, '5A'), (2, '5B'), (2, '5C'), (2, '5D'),
(5, '1A'), (5, '1B'), (5, '1C'), (5, '1D'),
(5, '2A'), (5, '2B'), (5, '2C'), (5, '2D'),
(5, '3A'), (5, '3B'), (5, '3C'), (5, '3D'),
(5, '4A'), (5, '4B'), (5, '4C'), (5, '4D'),
(5, '5A'), (5, '5B'), (5, '5C'), (5, '5D'),
(7, '1A'), (7, '1B'), (7, '1C'), (7, '1D'),
(7, '2A'), (7, '2B'), (7, '2C'), (7, '2D'),
(7, '3A'), (7, '3B'), (7, '3C'), (7, '3D'),
(7, '4A'), (7, '4B'), (7, '4C'), (7, '4D'),
(7, '5A'), (7, '5B'), (7, '5C'), (7, '5D'),
(9, '1A'), (9, '1B'), (9, '1C'), (9, '1D'),
(9, '2A'), (9, '2B'), (9, '2C'), (9, '2D'),
(9, '3A'), (9, '3B'), (9, '3C'), (9, '3D'),
(9, '4A'), (9, '4B'), (9, '4C'), (9, '4D'),
(9, '5A'), (9, '5B'), (9, '5C'), (9, '5D'),
(12, '1A'), (12, '1B'), (12, '1C'), (12, '1D'),
(12, '2A'), (12, '2B'), (12, '2C'), (12, '2D'),
(12, '3A'), (12, '3B'), (12, '3C'), (12, '3D'),
(12, '4A'), (12, '4B'), (12, '4C'), (12, '4D'),
(12, '5A'), (12, '5B'), (12, '5C'), (12, '5D'),
(13, '1A'), (13, '1B'), (13, '1C'), (13, '1D'),
(13, '2A'), (13, '2B'), (13, '2C'), (13, '2D'),
(13, '3A'), (13, '3B'), (13, '3C'), (13, '3D'),
(13, '4A'), (13, '4B'), (13, '4C'), (13, '4D'),
(13, '5A'), (13, '5B'), (13, '5C'), (13, '5D');

-- Bus 3, 4, 6, 8, 10, 11, 14 (16 Sleeper buses: L1..L8, U1..U8)
INSERT INTO seat (bus_id, seat_no) VALUES
(3, 'L1'), (3, 'L2'), (3, 'L3'), (3, 'L4'), (3, 'L5'), (3, 'L6'), (3, 'L7'), (3, 'L8'),
(3, 'U1'), (3, 'U2'), (3, 'U3'), (3, 'U4'), (3, 'U5'), (3, 'U6'), (3, 'U7'), (3, 'U8'),
(4, 'L1'), (4, 'L2'), (4, 'L3'), (4, 'L4'), (4, 'L5'), (4, 'L6'), (4, 'L7'), (4, 'L8'),
(4, 'U1'), (4, 'U2'), (4, 'U3'), (4, 'U4'), (4, 'U5'), (4, 'U6'), (4, 'U7'), (4, 'U8'),
(6, 'L1'), (6, 'L2'), (6, 'L3'), (6, 'L4'), (6, 'L5'), (6, 'L6'), (6, 'L7'), (6, 'L8'),
(6, 'U1'), (6, 'U2'), (6, 'U3'), (6, 'U4'), (6, 'U5'), (6, 'U6'), (6, 'U7'), (6, 'U8'),
(8, 'L1'), (8, 'L2'), (8, 'L3'), (8, 'L4'), (8, 'L5'), (8, 'L6'), (8, 'L7'), (8, 'L8'),
(8, 'U1'), (8, 'U2'), (8, 'U3'), (8, 'U4'), (8, 'U5'), (8, 'U6'), (8, 'U7'), (8, 'U8'),
(10, 'L1'), (10, 'L2'), (10, 'L3'), (10, 'L4'), (10, 'L5'), (10, 'L6'), (10, 'L7'), (10, 'L8'),
(10, 'U1'), (10, 'U2'), (10, 'U3'), (10, 'U4'), (10, 'U5'), (10, 'U6'), (10, 'U7'), (10, 'U8'),
(11, 'L1'), (11, 'L2'), (11, 'L3'), (11, 'L4'), (11, 'L5'), (11, 'L6'), (11, 'L7'), (11, 'L8'),
(11, 'U1'), (11, 'U2'), (11, 'U3'), (11, 'U4'), (11, 'U5'), (11, 'U6'), (11, 'U7'), (11, 'U8'),
(14, 'L1'), (14, 'L2'), (14, 'L3'), (14, 'L4'), (14, 'L5'), (14, 'L6'), (14, 'L7'), (14, 'L8'),
(14, 'U1'), (14, 'U2'), (14, 'U3'), (14, 'U4'), (14, 'U5'), (14, 'U6'), (14, 'U7'), (14, 'U8');

-- 6. Crew: Drivers (14 drivers)
INSERT INTO driver (driver_id, name, license_no, phone) VALUES
(1, 'Ramesh Patil', 'DL-MH-1998-0012', '9823011111'),
(2, 'Suresh Kumar', 'DL-KA-2001-0023', '9845022222'),
(3, 'Rajesh Sharma', 'DL-DL-2005-0034', '9811033333'),
(4, 'Venkat Reddy', 'DL-TS-2008-0045', '9849044444'),
(5, 'Praveen Patel', 'DL-GJ-2010-0056', '9898055555'),
(6, 'Murugan Selvam', 'DL-TN-2012-0067', '9840066666'),
(7, 'Anil Shinde', 'DL-MH-2015-0078', '9822077777'),
(8, 'Harish Gowda', 'DL-KA-2018-0089', '9844088888'),
(9, 'Ashok Yadav', 'DL-UP-2016-0090', '9415099999'),
(10, 'Subhash Mondal', 'DL-WB-2014-0101', '9830100000'),
(11, 'Ganesh Naik', 'DL-GA-2017-0112', '9823111111'),
(12, 'Baljinder Singh', 'DL-CH-2019-0123', '9876122222'),
(13, 'Thomas Mathew', 'DL-KL-2020-0134', '9847133333'),
(14, 'Dinesh Joshi', 'DL-MP-2021-0145', '9826144444');

-- 7. Crew: Conductors (14 conductors)
INSERT INTO conductor (conductor_id, name, phone) VALUES
(1, 'Mahesh Jadhav', '9765011111'),
(2, 'Anand Swamy', '9742022222'),
(3, 'Deepak Verma', '9717033333'),
(4, 'Srinivas Rao', '9701044444'),
(5, 'Jignesh Shah', '9727055555'),
(6, 'Karthik Raja', '9789066666'),
(7, 'Santosh Kale', '9763077777'),
(8, 'Chethan Kumar', '9731088888'),
(9, 'Ravi Mishra', '9415199999'),
(10, 'Tapan Das', '9830200000'),
(11, 'Pramod Dessai', '9823211111'),
(12, 'Harpreet Kaur', '9876222222'),
(13, 'Joseph Antony', '9847233333'),
(14, 'Rakesh Tiwari', '9826244444');

-- 8. Fares (Complete matrix for all 12 routes and 4 bus types)
INSERT INTO fare (route_id, bus_type, base_fare) VALUES
-- Route 1: Mumbai - Pune
(1, 'Seater', 300.00),
(1, 'Sleeper', 450.00),
(1, 'AC Seater', 500.00),
(1, 'AC Sleeper', 700.00),
-- Route 2: Bengaluru - Chennai
(2, 'Seater', 550.00),
(2, 'Sleeper', 750.00),
(2, 'AC Seater', 850.00),
(2, 'AC Sleeper', 1100.00),
-- Route 3: Delhi - Jaipur
(3, 'Seater', 400.00),
(3, 'Sleeper', 600.00),
(3, 'AC Seater', 650.00),
(3, 'AC Sleeper', 900.00),
-- Route 4: Hyderabad - Vijayawada
(4, 'Seater', 450.00),
(4, 'Sleeper', 650.00),
(4, 'AC Seater', 700.00),
(4, 'AC Sleeper', 950.00),
-- Route 5: Ahmedabad - Surat
(5, 'Seater', 350.00),
(5, 'Sleeper', 500.00),
(5, 'AC Seater', 550.00),
(5, 'AC Sleeper', 750.00),
-- Route 6: Chennai - Coimbatore
(6, 'Seater', 600.00),
(6, 'Sleeper', 850.00),
(6, 'AC Seater', 950.00),
(6, 'AC Sleeper', 1250.00),
-- Route 7: Lucknow - Varanasi
(7, 'Seater', 420.00),
(7, 'Sleeper', 620.00),
(7, 'AC Seater', 680.00),
(7, 'AC Sleeper', 920.00),
-- Route 8: Kolkata - Bhubaneswar
(8, 'Seater', 580.00),
(8, 'Sleeper', 800.00),
(8, 'AC Seater', 900.00),
(8, 'AC Sleeper', 1150.00),
-- Route 9: Pune - Goa
(9, 'Seater', 650.00),
(9, 'Sleeper', 900.00),
(9, 'AC Seater', 1000.00),
(9, 'AC Sleeper', 1350.00),
-- Route 10: Chandigarh - Shimla
(10, 'Seater', 250.00),
(10, 'Sleeper', 380.00),
(10, 'AC Seater', 420.00),
(10, 'AC Sleeper', 580.00),
-- Route 11: Kochi - Trivandrum
(11, 'Seater', 320.00),
(11, 'Sleeper', 480.00),
(11, 'AC Seater', 530.00),
(11, 'AC Sleeper', 720.00),
-- Route 12: Indore - Bhopal
(12, 'Seater', 280.00),
(12, 'Sleeper', 420.00),
(12, 'AC Seater', 470.00),
(12, 'AC Sleeper', 640.00);

-- 9. Passengers (15 realistic passengers)
INSERT INTO passenger (passenger_id, name, phone, email) VALUES
(1, 'Aarav Mehta', '9820011223', 'aarav.mehta@example.com'),
(2, 'Diya Sharma', '9820022334', 'diya.sharma@example.com'),
(3, 'Rohan Verma', '9820033445', 'rohan.verma@example.com'),
(4, 'Ananya Iyer', '9820044556', 'ananya.iyer@example.com'),
(5, 'Kavya Nair', '9820055667', 'kavya.nair@example.com'),
(6, 'Aditya Kulkarni', '9820066778', 'aditya.kulkarni@example.com'),
(7, 'Sneha Deshmukh', '9820077889', 'sneha.deshmukh@example.com'),
(8, 'Vikram Reddy', '9820088990', 'vikram.reddy@example.com'),
(9, 'Pooja Joshi', '9820099001', 'pooja.joshi@example.com'),
(10, 'Rahul Gupta', '9820100112', 'rahul.gupta@example.com'),
(11, 'Neha Trivedi', '9820111223', 'neha.trivedi@example.com'),
(12, 'Sanjay Patel', '9820122334', 'sanjay.patel@example.com'),
(13, 'Meera Pillai', '9820133445', 'meera.pillai@example.com'),
(14, 'Karan Malhotra', '9820144556', 'karan.malhotra@example.com'),
(15, 'Priya Sundaram', '9820155667', 'priya.sundaram@example.com');

-- 10. Trips (21 trips: past, running, and future scheduled)
-- Note: All trips are initialized as 'Scheduled' so bookings can be reserved (enforced by trg_booking_check).
-- Past trips (1-5) and active trip (6) are updated to 'Completed'/'Running' after bookings are inserted.
INSERT INTO trip (trip_id, route_id, bus_id, driver_id, conductor_id, departure_time, arrival_time, status) VALUES
-- Past Trips (to be marked Completed after bookings)
(1, 1, 1, 1, 1, NOW() - INTERVAL 72 HOUR, NOW() - INTERVAL 68 HOUR, 'Scheduled'),
(2, 2, 2, 2, 2, NOW() - INTERVAL 48 HOUR, NOW() - INTERVAL 42 HOUR, 'Scheduled'),
(3, 3, 3, 3, 3, NOW() - INTERVAL 50 HOUR, NOW() - INTERVAL 44 HOUR, 'Scheduled'),
(4, 4, 4, 4, 4, NOW() - INTERVAL 30 HOUR, NOW() - INTERVAL 24 HOUR, 'Scheduled'),
(5, 5, 5, 5, 5, NOW() - INTERVAL 26 HOUR, NOW() - INTERVAL 21 HOUR, 'Scheduled'),

-- Active Trip (to be marked Running after bookings)
(6, 1, 1, 7, 7, NOW() - INTERVAL 1 HOUR, NOW() + INTERVAL 3 HOUR, 'Scheduled'),

-- Future Scheduled Trips (Far Future >= 24h: 90% refund tier testing)
(7, 1, 1, 1, 1, NOW() + INTERVAL 36 HOUR, NOW() + INTERVAL 40 HOUR, 'Scheduled'),
(8, 2, 2, 2, 2, NOW() + INTERVAL 30 HOUR, NOW() + INTERVAL 36 HOUR, 'Scheduled'),
(9, 3, 3, 3, 3, NOW() + INTERVAL 48 HOUR, NOW() + INTERVAL 54 HOUR, 'Scheduled'),

-- Future Scheduled Trips (Medium Future 6-24h: 50% refund tier testing)
(10, 4, 4, 4, 4, NOW() + INTERVAL 14 HOUR, NOW() + INTERVAL 20 HOUR, 'Scheduled'),
(11, 5, 5, 5, 5, NOW() + INTERVAL 10 HOUR, NOW() + INTERVAL 15 HOUR, 'Scheduled'),

-- Future Scheduled Trips (Near Future < 6h: 0% refund tier testing)
(12, 1, 1, 7, 7, NOW() + INTERVAL 3 HOUR, NOW() + INTERVAL 7 HOUR, 'Scheduled'),
(13, 6, 6, 6, 6, NOW() + INTERVAL 4 HOUR, NOW() + INTERVAL 12 HOUR, 'Scheduled'),

-- Additional Scheduled Trips on other routes
(14, 2, 8, 8, 8, NOW() + INTERVAL 28 HOUR, NOW() + INTERVAL 34 HOUR, 'Scheduled'),
(15, 6, 6, 6, 6, NOW() + INTERVAL 52 HOUR, NOW() + INTERVAL 60 HOUR, 'Scheduled'),

-- New route trips (future scheduled, using new buses/drivers/conductors)
(16, 7, 9, 9, 9, NOW() + INTERVAL 24 HOUR, NOW() + INTERVAL 30 HOUR, 'Scheduled'),
(17, 8, 10, 10, 10, NOW() + INTERVAL 32 HOUR, NOW() + INTERVAL 40 HOUR, 'Scheduled'),
(18, 9, 11, 11, 11, NOW() + INTERVAL 20 HOUR, NOW() + INTERVAL 28 HOUR, 'Scheduled'),
(19, 10, 12, 12, 12, NOW() + INTERVAL 26 HOUR, NOW() + INTERVAL 30 HOUR, 'Scheduled'),
(20, 11, 13, 13, 13, NOW() + INTERVAL 18 HOUR, NOW() + INTERVAL 22 HOUR, 'Scheduled'),
(21, 12, 14, 14, 14, NOW() + INTERVAL 40 HOUR, NOW() + INTERVAL 44 HOUR, 'Scheduled');

-- 11. Bookings & Payments (~30 bookings matching exact fares)
-- Trip 1 (Completed, Route 1, Bus 1 Seater -> Fare 300.00)
-- Seats on Bus 1: 1A(1), 1B(2), 1C(3), 1D(4)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(1, 1, 1, 1, 'Confirmed'),
(2, 1, 2, 2, 'Confirmed'),
(3, 1, 3, 3, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(1, 1, 300.00, 'UPI', 'Paid'),
(2, 2, 300.00, 'Card', 'Paid'),
(3, 3, 300.00, 'Cash', 'Paid');

-- Trip 2 (Completed, Route 2, Bus 2 AC Seater -> Fare 850.00)
-- Seats on Bus 2: 1A(21), 1B(22)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(4, 2, 21, 4, 'Confirmed'),
(5, 2, 22, 5, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(4, 4, 850.00, 'NetBanking', 'Paid'),
(5, 5, 850.00, 'UPI', 'Paid');

-- Trip 3 (Completed, Route 3, Bus 3 Sleeper -> Fare 600.00)
-- Seats on Bus 3: L1(141), L2(142)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(6, 3, 141, 6, 'Confirmed'),
(7, 3, 142, 7, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(6, 6, 600.00, 'Card', 'Paid'),
(7, 7, 600.00, 'UPI', 'Paid');

-- Trip 4 (Completed, Route 4, Bus 4 AC Sleeper -> Fare 950.00)
-- Seats on Bus 4: L1(157), L2(158)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(8, 4, 157, 8, 'Confirmed'),
(9, 4, 158, 9, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(8, 8, 950.00, 'NetBanking', 'Paid'),
(9, 9, 950.00, 'Card', 'Paid');

-- Trip 5 (Completed, Route 5, Bus 5 AC Seater -> Fare 550.00)
-- Seats on Bus 5: 1A(41), 1B(42)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(10, 5, 41, 10, 'Confirmed'),
(11, 5, 42, 11, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(10, 10, 550.00, 'Wallet', 'Paid'),
(11, 11, 550.00, 'UPI', 'Paid');

-- Trip 7 (Scheduled +36h, Route 1, Bus 1 Seater -> Fare 300.00)
-- Seats on Bus 1: 2A(5), 2B(6), 2C(7), 2D(8), 3A(9)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(12, 7, 5, 1, 'Confirmed'),
(13, 7, 6, 2, 'Confirmed'),
(14, 7, 7, 12, 'Confirmed'),
(15, 7, 8, 13, 'Confirmed'),
(16, 7, 9, 14, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(12, 12, 300.00, 'UPI', 'Paid'),
(13, 13, 300.00, 'Card', 'Paid'),
(14, 14, 300.00, 'Cash', 'Paid'),
(15, 15, 300.00, 'NetBanking', 'Paid'),
(16, 16, 300.00, 'UPI', 'Paid');

-- Trip 8 (Scheduled +30h, Route 2, Bus 2 AC Seater -> Fare 850.00)
-- Seats on Bus 2: 2A(25), 2B(26), 2C(27)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(17, 8, 25, 3, 'Confirmed'),
(18, 8, 26, 4, 'Confirmed'),
(19, 8, 27, 5, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(17, 17, 850.00, 'Card', 'Paid'),
(18, 18, 850.00, 'UPI', 'Paid'),
(19, 19, 850.00, 'EMI', 'Paid');

-- Trip 9 (Scheduled +48h, Route 3, Bus 3 Sleeper -> Fare 600.00)
-- Seats on Bus 3: L3(143), L4(144)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(20, 9, 143, 6, 'Confirmed'),
(21, 9, 144, 7, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(20, 20, 600.00, 'UPI', 'Paid'),
(21, 21, 600.00, 'Card', 'Paid');

-- Trip 10 (Scheduled +14h [Medium 6-24h], Route 4, Bus 4 AC Sleeper -> Fare 950.00)
-- Seats on Bus 4: L3(159), L4(160), L5(161)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(22, 10, 159, 8, 'Confirmed'),
(23, 10, 160, 9, 'Confirmed'),
(24, 10, 161, 15, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(22, 22, 950.00, 'UPI', 'Paid'),
(23, 23, 950.00, 'NetBanking', 'Paid'),
(24, 24, 950.00, 'Card', 'Paid');

-- Trip 11 (Scheduled +10h [Medium 6-24h], Route 5, Bus 5 AC Seater -> Fare 550.00)
-- Seats on Bus 5: 2A(45), 2B(46)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(25, 11, 45, 10, 'Confirmed'),
(26, 11, 46, 11, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(25, 25, 550.00, 'Cash', 'Paid'),
(26, 26, 550.00, 'UPI', 'Paid');

-- Trip 12 (Scheduled +3h [Near <6h], Route 1, Bus 1 Seater -> Fare 300.00)
-- Seats on Bus 1: 3B(10), 3C(11)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(27, 12, 10, 12, 'Confirmed'),
(28, 12, 11, 13, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(27, 27, 300.00, 'UPI', 'Paid'),
(28, 28, 300.00, 'Card', 'Paid');

-- Trip 13 (Scheduled +4h [Near <6h], Route 6, Bus 6 AC Sleeper -> Fare 1250.00)
-- Seats on Bus 6: L1(173), L2(174)
INSERT INTO booking (booking_id, trip_id, seat_id, passenger_id, status) VALUES
(29, 13, 173, 14, 'Confirmed'),
(30, 13, 174, 15, 'Confirmed');
INSERT INTO payment (payment_id, booking_id, amount, method, status) VALUES
(29, 29, 1250.00, 'NetBanking', 'Paid'),
(30, 30, 1250.00, 'UPI', 'Paid');

-- 12. Cancellations to exercise DB triggers:
-- Notice: Triggers trg_cancel_policy & trg_cancel_after calculate refund & update statuses automatically!
-- Booking 16: Trip 7 is in +36h (>24h). Cancelling now -> 90% refund (300 * 0.90 = 270.00)
INSERT INTO cancellation (booking_id, cancelled_at) VALUES
(16, NOW());

-- Booking 24: Trip 10 is in +14h (6-24h). Cancelling now -> 50% refund (950 * 0.50 = 475.00)
INSERT INTO cancellation (booking_id, cancelled_at) VALUES
(24, NOW());

-- Booking 28: Trip 12 is in +3h (<6h). Cancelling now -> 0% refund (300 * 0 = 0.00)
INSERT INTO cancellation (booking_id, cancelled_at) VALUES
(28, NOW());

-- 13. Update historical trips to Completed and Running after reservations were booked
UPDATE trip SET status = 'Completed' WHERE trip_id IN (1, 2, 3, 4, 5);
UPDATE trip SET status = 'Running' WHERE trip_id = 6;

