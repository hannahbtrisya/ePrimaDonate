# ePrimaDonate

A web-based mosque donation management system developed using Django to digitalize donation processing, improve transparency, and support administrative reporting.

## Project Overview

ePrimaDonate is a final year project system designed to manage mosque donations digitally. It supports multiple user roles including Donors, Treasurer, and Chairman, each with different permissions and access levels.

The system allows donors to contribute via multiple payment methods while enabling administrators to manage, approve, and generate detailed donation reports.

## Key Features

### Donor Module
- Register and login system
- Make donations with category selection
- Upload payment proof (QR payments)
- View donation history
- Update personal profile
- Receive digital receipts

### Treasurer Module
- Manage donation transactions
- Review and approve/reject donations
- Manage donation categories (pending approval workflow)
- Generate monthly and annual donation reports
- Export reports as PDF

### Chairman Module
- Approve or reject donation type requests
- View donor list
- Monitor system activity logs
- Access donation reports

## Technologies Used

- Django (Python)
- MySQL Database
- HTML, CSS, JavaScript
- ReportLab / PDF generation tools

## System Highlights

- Role-based access control (RBAC)
- Secure authentication system
- Automated digital receipt generation
- Donation tracking and reporting system
- Approval workflow for donation categories

## Limitations

- Chart visualization feature was not fully implemented due to technical constraints
- System currently deployed locally but is deployment-ready

## Purpose

This project was developed as a final year academic requirement to demonstrate full-stack web development, database management, and real-world system design for donation management.
