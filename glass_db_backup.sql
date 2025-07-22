-- MySQL dump 10.13  Distrib 9.4.0, for Win64 (x86_64)
--
-- Host: localhost    Database: glass_db
-- ------------------------------------------------------
-- Server version	9.4.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `defects`
--

DROP TABLE IF EXISTS `defects`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `defects` (
  `PO` varchar(255) DEFAULT NULL,
  `Tag` varchar(255) DEFAULT NULL,
  `Size` varchar(255) DEFAULT NULL,
  `Quantity` int DEFAULT NULL,
  `Scratch_Location` varchar(255) DEFAULT NULL,
  `Scratch_Type` varchar(255) DEFAULT NULL,
  `Glass_Type` varchar(255) DEFAULT NULL,
  `Rack_Type` varchar(255) DEFAULT NULL,
  `Vendor` varchar(255) DEFAULT NULL,
  `Date` date DEFAULT NULL,
  `Note` text,
  `ImageData` longblob
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `defects`
--

LOCK TABLES `defects` WRITE;
/*!40000 ALTER TABLE `defects` DISABLE KEYS */;
INSERT INTO `defects` VALUES ('33537','161406','30.3125 x 71.4375',1,'Unknown','Scratched','i89/IS20/SUNGUARD','A-frame','Cardinal CG','2025-07-11','',_binary '\r'),('33158','159527','24.3125 x 85.4375',1,'Unknown','Scratched','i89/IS20/SUNGUARD','A-frame','Cardinal CG','2025-07-11','',_binary '\r'),('33342','160476','29.6825 x 70.6825',1,'Unknown','Scratched','LOWE 272','A-frame','Cardinal CG','2025-07-11','',_binary '\r'),('33342','160476','29.6825 x 70.6825',1,'Unknown','Scratched','CLEAR','A-frame','Cardinal CG','2025-07-11','',_binary '\r'),('33410','160494','29.8125 x 71.4375',1,'Unknown','Scratched','LOWE 272','A-frame','Cardinal CG','2025-07-11','',_binary '\r'),('33158','159527','24.3125 x 85.4375',1,'Unknown','Scratched','i89/IS20/SUNGUARD','A-frame','Cardinal CG','2025-07-11','',_binary '\r'),('33622','161728','23.813 x 69.438',1,'Top Center','Scratched','i89/IS20/SUNGUARD','A-frame','Cardinal CG','2025-07-14','',_binary '\r'),('33484','160744','40.5 x 69.4375',1,'Unknown','Production Issue','CLEAR','A-frame','Cardinal CG','2025-07-11','',_binary '\r'),('33484','160744','40.5 x 69.4375',1,'Unknown','Production Issue','LOWE 272','A-frame','Cardinal CG','2025-07-11','',_binary '\r'),('33582','161503','27.5 x 70.9375',1,'Unknown','Production Issue','CLEAR','A-frame','Cardinal CG','2025-07-11','',_binary '\r'),('33582','161503','27.5 x 70.9375',1,'Unknown','Production Issue','LOWE 272','A-frame','Cardinal CG','2025-07-11','',_binary '\r'),('-','159659-1','8 3/4 x 79 1/2',1,'Center','Stain Mark','CLEAR','Other','Cardinal CG','2025-07-18','Sealed IG Unit',_binary '\r');
/*!40000 ALTER TABLE `defects` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-07-22 11:44:07
