CREATE DATABASE  IF NOT EXISTS `dry_leak_test_data`;
USE `dry_leak_test_data`;

-- MySQL dump 10.13  Distrib 8.0.36, for Win64 (x86_64)
-- Host: OHMLAP0362    Database: bundle_leak_test
-- Server version	8.0.36
-- 
-- Table structure for table `Bundle dry leak test`
--
DROP TABLE IF EXISTS `Bundle dry leak test`;
CREATE TABLE `Bundle dry leak test` (
  `SrNo` int NOT NULL AUTO_INCREMENT,
  `Month` varchar(100) DEFAULT NULL,
  `Week` int DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `Start Time` time DEFAULT NULL,
  `End Time` time DEFAULT NULL,
  `Day` varchar(100) DEFAULT NULL,
  `Shift` enum('A','B','C','G') DEFAULT NULL,
  `Operator Name` varchar(100) DEFAULT NULL,
  
  `Bundle no` varchar(100) DEFAULT NULL,
   -- `Retest` int DEFAULT NULL,
  `Bin Category` varchar(100) DEFAULT NULL,
  `Stack bundle assembly sequence` varchar(100) DEFAULT NULL,
  `Plate SI No` varchar(100) DEFAULT NULL,
  
  `CL anode at 30psi` varchar(100) DEFAULT NULL,
  `OBL anode at 30psi` varchar(100) DEFAULT NULL,
  `CL anode at 50psi` varchar(100) DEFAULT NULL,
  `OBL anode at 50psi` varchar(100) DEFAULT NULL,
  
  `CL cathode at 50psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 50psi` varchar(100) DEFAULT NULL,
  `CL cathode at 100psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 100psi` varchar(100) DEFAULT NULL,
  `CL cathode at 150psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 150psi` varchar(100) DEFAULT NULL,
  `CL cathode at 200psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 200psi` varchar(100) DEFAULT NULL,
  `CL cathode at 250psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 250psi` varchar(100) DEFAULT NULL,
  
  `Accepted` INT DEFAULT NULL,
  `Rejected` INT DEFAULT NULL,
  `Status` varchar(1000) DEFAULT NULL,
  `Reason for rejection` varchar(1000) DEFAULT NULL,
  -- `Status` varchar(100) DEFAULT NULL,
  `Initial observations on the replaced parts/rejections` varchar(1000) DEFAULT NULL,
  `Method changes` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`SrNo`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

--
-- Table structure for table `Stack dry leak test`
--
DROP TABLE IF EXISTS `Stack dry leak test`;
CREATE TABLE `Stack dry leak test` (
  `SrNo` int NOT NULL AUTO_INCREMENT,
  `Month` varchar(100) DEFAULT NULL,
  `Week` int DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `Start Time` time DEFAULT NULL,
  `End Time` time DEFAULT NULL,
  `Day` varchar(100) DEFAULT NULL,
  `Shift` enum('A','B','C','G') DEFAULT NULL,
  `Operator Name` varchar(100) DEFAULT NULL,
  
  `Stack No` varchar(100) DEFAULT NULL,
   -- `Retest` int DEFAULT NULL,
   `Torque` varchar(10) DEFAULT NULL,
   
   `CL anode at 30psi` varchar(100) DEFAULT NULL,
  `OBL anode at 30psi` varchar(100) DEFAULT NULL,
  `CL anode at 50psi` varchar(100) DEFAULT NULL,
  `OBL anode at 50psi` varchar(100) DEFAULT NULL,
  
  `CL cathode at 30psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 30psi` varchar(100) DEFAULT NULL,
  `CL cathode at 50psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 50psi` varchar(100) DEFAULT NULL,
  `CL cathode at 100psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 100psi` varchar(100) DEFAULT NULL,
  `CL cathode at 150psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 150psi` varchar(100) DEFAULT NULL,
  `CL cathode at 200psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 200psi` varchar(100) DEFAULT NULL,
  `CL cathode at 250psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 250psi` varchar(100) DEFAULT NULL,
  `CL cathode at 300psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 300psi` varchar(100) DEFAULT NULL,
  `CL cathode at 350psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 350psi` varchar(100) DEFAULT NULL,
  `CL cathode at 400psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 400psi` varchar(100) DEFAULT NULL,
  `CL cathode at 450psi` varchar(100) DEFAULT NULL,
  `OBL cathode at 450psi` varchar(100) DEFAULT NULL,
  
  `Accepted` INT DEFAULT NULL,
  `Rejected` INT DEFAULT NULL,
  `Status` varchar(100) DEFAULT NULL,
  -- `FPY in %` INT DEFAULT NULL, 
  `Resistance range > 5 ohms` varchar(100) DEFAULT NULL,
  `Remarks` varchar(1000) DEFAULT NULL,
  `Observations` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`SrNo`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

Select * from `Stack dry leak test`;


