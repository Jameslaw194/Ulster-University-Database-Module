-- Create the database
CREATE DATABASE CarServiceDB;
GO

-- Switch to the new database
USE CarServiceDB;
GO

-- Create the tables
CREATE TABLE Customer (
    customer_id VARCHAR(10) PRIMARY KEY,
    cust_forenames VARCHAR(100) NOT NULL,
    cust_surname VARCHAR(100) NOT NULL,
    cust_email VARCHAR(255) NOT NULL UNIQUE,
    cust_phoneno VARCHAR(15) NOT NULL
);

CREATE TABLE Car (
    registration VARCHAR(10) PRIMARY KEY,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    date_of_manufacture DATE NOT NULL
);

CREATE TABLE Employee (
    employee_id VARCHAR(10) PRIMARY KEY,
    emp_forenames VARCHAR(100) NOT NULL,
    emp_surname VARCHAR(100) NOT NULL,
    emp_phone VARCHAR(15) NOT NULL,
    grade VARCHAR(20) NOT NULL
);

CREATE TABLE Service (
    service_id VARCHAR(12) PRIMARY KEY,
    dropoff_date DATE NOT NULL,
    dropoff_time TIME(0) NOT NULL,
    work_required VARCHAR(MAX) NOT NULL,
    milage INT NOT NULL,
    next_service DATE NULL,
    registration VARCHAR(10) NOT NULL, -- Links to Car.registration
    customer_id VARCHAR(10) NOT NULL, -- Links to Customer.customer_id
    CONSTRAINT FK_Service_Car FOREIGN KEY (registration) REFERENCES Car (registration),
    CONSTRAINT FK_Service_Customer FOREIGN KEY (customer_id) REFERENCES Customer (customer_id)
);

CREATE TABLE ServiceEmployee (
    service_id VARCHAR(12) NOT NULL,
    employee_id VARCHAR(10) NOT NULL,
    time_spent TIME(0) NOT NULL,
    PRIMARY KEY (service_id, employee_id),
    CONSTRAINT FK_ServiceEmployee_Service FOREIGN KEY (service_id) REFERENCES Service (service_id),
    CONSTRAINT FK_ServiceEmployee_Employee FOREIGN KEY (employee_id) REFERENCES Employee (employee_id)
);
GO
