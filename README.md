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

- Frontend: Web-based user interface
- Backend: Django REST API
- Database: PostgreSQL
- Payment Gateway: M-Pesa via Daraja API
- Hosting Platform: Render

---

## 6. System Architecture

### 6.1 High-Level Architecture

