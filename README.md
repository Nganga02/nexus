# PROJECT NEXUS

## Project Documentation

---

## 1. Introduction

The Property Booking System is a web-based application designed to automate the process of booking rental properties and making payments online. The system allows users to browse available properties, make bookings, and complete payments using M-Pesa through the Daraja API.

This project addresses inefficiencies in traditional property booking systems by providing a secure, reliable, and real-time booking and payment solution.

---

## 2. Problem Statement

Many property booking processes are still handled manually or through loosely integrated systems, leading to:

- Double booking of properties
- Delayed or untraceable payments
- Poor user experience
- Lack of real-time booking confirmation

There is a need for a centralized system that integrates property management with a trusted mobile payment platform.

---

## 3. Project Objectives

### 3.1 Main Objective
To design and implement a property booking system with integrated mobile payments using M-Pesa.

### 3.2 Specific Objectives
- Allow users to view and book available properties online
- Integrate M-Pesa payments using the Daraja API
- Allow for a booking to be tied to more than one guest
- Automate booking confirmation after successful payment
- Maintain secure records of bookings and transactions
- Prevent double booking of properties

---

## 4. Scope of the Project

### 4.1 Included
- User registration and authentication
- Property listing and availability management
- Online booking system
- M-Pesa payment integration
- Payment confirmation and booking status updates
- Database-backed transaction records

### 4.2 Excluded
- Property valuation
- Legal documentation management
- Physical access control systems

---

## 5. System Overview

The system is built using a client-server architecture:

- Backend: Django REST API
- Database: PostgreSQL
- Payment Gateway: M-Pesa via Daraja API
- Hosting Platform: Render

---

## 6. System Architecture

### 6.1 High-Level Architecture

When the user accesses the django web interface they are able to interact with the API.

---

## 7. Technology Stack

### 7.2 Backend
- Django
- Django REST Framework

### 7.3 Database
- PostgreSQL

### 7.4 Payment Gateway
- M-Pesa Daraja API provided by :contentReference[oaicite:0]{index=0}

### 7.5 Deployment
- Render Cloud Platform

---

## 8. Functional Requirements

### 8.1 User Management
- User registration
- User login and authentication

### 8.2 Property Management
- Add and manage properties (admin)
- View available properties (users)

### 8.3 Booking Management
- Create property bookings
- Prevent double booking
- Track booking status

### 8.4 Payment Processing
- Initiate M-Pesa STK Push
- Handle payment callbacks
- Confirm or cancel bookings based on payment status

---

## 9. Non-Functional Requirements

- Security: Secure payment handling and data storage
- Performance: Fast booking and payment response
- Reliability: Accurate transaction processing
- Scalability: Ability to handle multiple users and bookings
- Availability: Publicly accessible callback endpoints

---

## 10. Database Design

### 10.1 Entities

#### User
- id
- name
- id_photo
- email
- phone_number
- password
- role
- credit_score

#### Property
- id
- owner fk(User)
- name
- description
- location
- price_per_night
- amenities
- availability_status

#### Booking
- id
- user_ids
- property_id
- booking_date
- status
- check_in
- check_out
- balance_due
- total_price

#### Payment
- id
- checkout_request_id
- booking_id
- phone_number
- amount
- mpesa_receipt_number
- transaction_status
- timestamp

---

## 11. Booking and Payment Workflow

1. User selects a property
2. User submits a booking request
3. Booking is created with status `PENDING`
4. User proceeds to create a payment with specified amount
4. Backend initiates M-Pesa STK Push
5. User enters M-Pesa PIN
6. Daraja processes the transaction
7. Callback is sent to the system
8. Booking status is updated:
   - `PROCESSING` if a payment was successful but balance hasn't been cleared
   - `CONFIRMED` if payment is successful
   - `CANCELED` if payment fails

---

## 12. Daraja API Integration

### 12.1 Daraja API Overview
Daraja is an API that enables developers to integrate M-Pesa payment services into applications.

### 12.2 APIs Used
- OAuth Token Generation
- STK Push Request
- STK Push Callback Handling

### 12.3 Callback Handling
- Daraja sends a POST request to a public callback URL
- The backend validates the response
- Payment metadata is extracted
- A payment's checkout request id is matched to the callback's body checkout request id 
- Booking and payment records are updated

---

## 13. Security Considerations

- Environment variables used for sensitive credentials
- HTTPS used for callback URLs
- Validation of payment callback payloads
- Database transactions for atomic updates
- Role-based access control

---

## 14. Deployment

### 14.1 Platform
- Render Web Service for Django
- Render PostgreSQL Service for database

### 14.2 Deployment Steps
1. Push code to GitHub
2. Connect repository to Render
3. Configure environment variables
4. Deploy backend service
5. Run database migrations

---

## 15. Challenges Encountered

- Database connectivity configuration on cloud platform
- Daraja callback URL accessibility
- Handling asynchronous payment responses
- Preventing duplicate bookings during payment delay

---

## 16. Solutions Implemented

- Correct PostgreSQL host configuration
- Use of public HTTPS callback URLs
- Transaction-based booking updates
- Extensive logging for debugging

---

## 17. Testing

### 17.1 Functional Testing
- Booking creation
- Payment initiation
- Callback handling

### 17.2 Integration Testing
- Backend to Daraja API communication
- Database updates after payment confirmation

---

## 18. Results and Achievements

- Successful end-to-end booking and payment workflow
- Reliable M-Pesa integration
- Secure and scalable backend system
- Improved user experience and transaction transparency

---

## 19. Future Enhancements

- Admin dashboard
- Booking analytics and reports
- Email and SMS notifications
- Refund handling
- Mobile application support

---

## 20. Conclusion

The Property Booking System successfully automates property reservations and integrates mobile payments using M-Pesa. The system demonstrates practical application of backend development, payment gateway integration, and cloud deployment, making it suitable for real-world property management scenarios.

---

## 21. References

- Django Documentation
- Django REST Framework Documentation
- Safaricom Daraja API Documentation
- PostgreSQL Documentation
- Render Deployment Documentation

---


