# FastAPI-Online-Course-Platform

A complete **FastAPI backend project** for managing an online course platform.  
This project allows users to browse courses, enroll students, manage wishlists, search/filter/sort courses, and handle enrollments.

Built using **FastAPI**, **Pydantic**, and in-memory data storage.

---

## Link
http://127.0.0.1:8000/docs#/

## Features

### Course Management
- View all available courses
- View course by ID
- Add new courses
- Update course price and seats
- Delete courses
- Course summary statistics

### Enrollment Management
- Enroll students into courses
- Coupon discounts
- Early-bird discount system
- Gift enrollments
- View all enrollments
- Search enrollments
- Sort enrollments
- Paginate enrollments

### Wishlist System
- Add courses to wishlist
- Remove wishlist items
- View wishlist
- Enroll all wishlist courses at once

### Advanced Browsing
- Search courses
- Filter by category / level / price / seats
- Sort by price / title / seats
- Pagination
- Combined browse endpoint

---

## Tech Stack

- Python
- FastAPI
- Uvicorn
- Pydantic

---

## Project Structure

```bash
LearnHub/
│── main.py
│── requirements.txt
│── README.md
