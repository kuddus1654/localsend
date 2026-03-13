-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 22, 2026 at 04:30 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `swiftcare`
--

-- --------------------------------------------------------

--
-- Table structure for table `ambulances`
--

CREATE TABLE `ambulances` (
  `id` int(11) NOT NULL,
  `type` varchar(100) DEFAULT NULL,
  `base_fare` decimal(10,2) DEFAULT NULL,
  `price_per_km` decimal(10,2) DEFAULT NULL,
  `equipment` text DEFAULT NULL,
  `image` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `ambulances`
--

INSERT INTO `ambulances` (`id`, `type`, `base_fare`, `price_per_km`, `equipment`, `image`) VALUES
(1, 'Basic Ambulance', 500.00, 25.00, 'Stretcher, Oxygen', NULL),
(2, 'ICU Ambulance', 1500.00, 50.00, 'Ventilator, Cardiac Monitor', NULL),
(3, 'Oxygen Ambulance', 800.00, 30.00, 'Oxygen Cylinder', NULL),
(5, 'ABC', 400.00, 15.00, 'Oxygen ', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `driver_id` int(11) DEFAULT NULL,
  `ambulance_id` int(11) DEFAULT NULL,
  `pickup_location` text DEFAULT NULL,
  `drop_location` text DEFAULT NULL,
  `distance` decimal(10,2) DEFAULT NULL,
  `fare` decimal(10,2) DEFAULT NULL,
  `status` enum('pending','assigned','on_the_way','reached','completed','cancelled') DEFAULT 'pending',
  `booking_type` enum('emergency','scheduled') DEFAULT 'emergency',
  `booking_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `payment_status` enum('pending','verifying','paid','failed') DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `bookings`
--

INSERT INTO `bookings` (`id`, `user_id`, `driver_id`, `ambulance_id`, `pickup_location`, `drop_location`, `distance`, `fare`, `status`, `booking_type`, `booking_date`, `payment_status`) VALUES
(1, 2, 1, 3, 'jaljalj;al', 'ajf;laj', 6.50, 995.00, 'completed', 'emergency', '2026-02-17 13:18:22', 'paid'),
(2, 3, 1, 2, 'Andheri ', 'Jogeshwari ', 10.00, 2000.00, 'completed', 'emergency', '2026-02-17 13:46:02', 'pending'),
(3, 3, 1, 2, 'Andheri ', 'Jogeshwari ', 10.00, 2000.00, 'completed', 'emergency', '2026-02-17 13:46:02', 'pending'),
(4, 3, 1, 5, 'Andheri ', 'Jogeshwari ', 10.00, 550.00, 'completed', 'emergency', '2026-02-17 13:55:37', 'pending'),
(6, 2, 1, 1, 'dbgs', 'sg g', 55.00, 1875.00, 'completed', 'emergency', '2026-02-22 14:38:03', 'paid'),
(7, 2, NULL, 1, ' n', 'hfd', 6.00, 650.00, 'pending', 'emergency', '2026-02-22 15:03:20', 'paid');

-- --------------------------------------------------------

--
-- Table structure for table `cms`
--

CREATE TABLE `cms` (
  `id` int(11) NOT NULL,
  `section` varchar(100) DEFAULT NULL,
  `content` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cms`
--

INSERT INTO `cms` (`id`, `section`, `content`) VALUES
(1, 'upi_id', 'admin@upi');

-- --------------------------------------------------------

--
-- Table structure for table `drivers`
--

CREATE TABLE `drivers` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `ambulance_id` int(11) DEFAULT NULL,
  `status` enum('online','offline') DEFAULT 'offline',
  `documents` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `drivers`
--

INSERT INTO `drivers` (`id`, `name`, `email`, `phone`, `password`, `ambulance_id`, `status`, `documents`, `created_at`) VALUES
(1, 'Test Driver', 'driver@swiftcare.com', '7777777777', 'e10adc3949ba59abbe56e057f20f883e', NULL, 'online', NULL, '2026-02-17 13:16:33');

-- --------------------------------------------------------

--
-- Table structure for table `driver_earnings`
--

CREATE TABLE `driver_earnings` (
  `id` int(11) NOT NULL,
  `driver_id` int(11) DEFAULT NULL,
  `booking_id` int(11) DEFAULT NULL,
  `amount` decimal(10,2) DEFAULT NULL,
  `date` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `hospitals`
--

CREATE TABLE `hospitals` (
  `id` int(11) NOT NULL,
  `name` varchar(150) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `emergency_status` enum('available','unavailable') DEFAULT 'available',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `hospitals`
--

INSERT INTO `hospitals` (`id`, `name`, `address`, `phone`, `emergency_status`, `created_at`) VALUES
(1, 'hospital test 1', 'af gaagga   fgga', '25812364', 'available', '2026-02-17 13:27:08');

-- --------------------------------------------------------

--
-- Table structure for table `pathology_bookings`
--

CREATE TABLE `pathology_bookings` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `test_id` int(11) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `booking_date` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('pending','collected','completed') DEFAULT 'pending',
  `payment_status` enum('pending','verifying','paid','failed') DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pathology_bookings`
--

INSERT INTO `pathology_bookings` (`id`, `user_id`, `test_id`, `address`, `booking_date`, `status`, `payment_status`) VALUES
(2, 2, 1, 'aadf faf', '2026-02-17 17:16:54', 'pending', 'pending'),
(3, 2, 1, 'yyh', '2026-02-17 17:30:39', 'completed', 'pending'),
(4, 2, 1, 'yehh', '2026-02-22 14:34:58', 'pending', 'pending'),
(5, 2, 1, 'ys', '2026-02-22 14:35:31', 'pending', 'pending'),
(6, 2, 1, 'hfd', '2026-02-22 14:37:36', 'completed', 'pending'),
(7, 2, 1, 'hddh', '2026-02-22 14:45:34', 'pending', 'pending'),
(8, 2, 1, 'bgf', '2026-02-22 14:47:41', 'completed', 'pending');

-- --------------------------------------------------------

--
-- Table structure for table `pathology_tests`
--

CREATE TABLE `pathology_tests` (
  `id` int(11) NOT NULL,
  `test_name` varchar(150) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `pathology_tests`
--

INSERT INTO `pathology_tests` (`id`, `test_name`, `description`, `price`, `created_at`) VALUES
(1, 'blood test ', 'cbc ,mr,etc', 200.00, '2026-02-17 13:26:20');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `password` varchar(255) DEFAULT NULL,
  `role` enum('user','admin') DEFAULT 'user',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `status` enum('active','blocked') DEFAULT 'active'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `name`, `email`, `phone`, `password`, `role`, `created_at`, `status`) VALUES
(1, 'Admin', 'admin@swiftcare.com', '9999999999', 'e10adc3949ba59abbe56e057f20f883e', 'admin', '2026-02-17 13:16:33', 'active'),
(2, 'Test User', 'user@swiftcare.com', '8888888888', 'e10adc3949ba59abbe56e057f20f883e', 'user', '2026-02-17 13:16:33', 'active'),
(3, 'Gausiya Shaikh ', 'user@gausiya.com', '1234567891', '4a557cfb1d4d6d0150231c3a66f09945', 'user', '2026-02-17 13:40:29', 'active');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ambulances`
--
ALTER TABLE `ambulances`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `driver_id` (`driver_id`),
  ADD KEY `ambulance_id` (`ambulance_id`);

--
-- Indexes for table `cms`
--
ALTER TABLE `cms`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `drivers`
--
ALTER TABLE `drivers`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- Indexes for table `driver_earnings`
--
ALTER TABLE `driver_earnings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `driver_id` (`driver_id`),
  ADD KEY `booking_id` (`booking_id`);

--
-- Indexes for table `hospitals`
--
ALTER TABLE `hospitals`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pathology_bookings`
--
ALTER TABLE `pathology_bookings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `test_id` (`test_id`);

--
-- Indexes for table `pathology_tests`
--
ALTER TABLE `pathology_tests`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ambulances`
--
ALTER TABLE `ambulances`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `bookings`
--
ALTER TABLE `bookings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `cms`
--
ALTER TABLE `cms`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `drivers`
--
ALTER TABLE `drivers`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `driver_earnings`
--
ALTER TABLE `driver_earnings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `hospitals`
--
ALTER TABLE `hospitals`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `pathology_bookings`
--
ALTER TABLE `pathology_bookings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `pathology_tests`
--
ALTER TABLE `pathology_tests`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`id`),
  ADD CONSTRAINT `bookings_ibfk_3` FOREIGN KEY (`ambulance_id`) REFERENCES `ambulances` (`id`);

--
-- Constraints for table `driver_earnings`
--
ALTER TABLE `driver_earnings`
  ADD CONSTRAINT `driver_earnings_ibfk_1` FOREIGN KEY (`driver_id`) REFERENCES `drivers` (`id`),
  ADD CONSTRAINT `driver_earnings_ibfk_2` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`);

--
-- Constraints for table `pathology_bookings`
--
ALTER TABLE `pathology_bookings`
  ADD CONSTRAINT `pathology_bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `pathology_bookings_ibfk_2` FOREIGN KEY (`test_id`) REFERENCES `pathology_tests` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
