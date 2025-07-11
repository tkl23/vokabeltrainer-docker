
CREATE DATABASE IF NOT EXISTS vokabeltrainer;
USE vokabeltrainer;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    role ENUM('admin','teacher','student') DEFAULT 'student'
);

CREATE TABLE IF NOT EXISTS vokabel (
    id INT AUTO_INCREMENT PRIMARY KEY,
    deutsch VARCHAR(64) NOT NULL,
    englisch VARCHAR(64) NOT NULL,
    schwierigkeitsgrad ENUM('leicht','mittel','schwer') NOT NULL
);

CREATE TABLE IF NOT EXISTS fortschritt (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    vokabel_id INT NOT NULL,
    korrekt INT DEFAULT 0
);
