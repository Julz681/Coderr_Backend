# Coderr Backend

This repository contains the **backend** of the Coderr platform, built with **Django 5** and **Django REST Framework (DRF)**.  
It provides a complete REST API that powers the Coderr frontend (Vanilla JS).

---

## Features

- **Authentication**
  - Token-based authentication
  - User registration & login
  - Two user types: `customer` and `business`

- **Profiles**
  - Retrieve and update user profiles
  - List all business and customer profiles
  - Profile fields are never `null`, but empty strings if unset

- **Offers**
  - Business users can create, update, and delete offers
  - Every offer requires **exactly 3 details**: `basic`, `standard`, `premium`
  - Supports filtering, searching, and ordering

- **Orders**
  - Customers can create orders based on `OfferDetail`
  - Business users can update order status (`in_progress`, `completed`, `cancelled`)
  - Admin (staff) users can delete orders
  - Extra endpoints for in-progress and completed order counts

- **Reviews**
  - Customers can leave **exactly one review per business**
  - Reviews can be listed, updated, or deleted by their creator
  - Ratings from 1 to 5

- **Statistics**
  - Aggregated platform data (`review_count`, `average_rating`, `business_profile_count`, `offer_count`)

---

## Tech Stack

- **Python** 3.12+
- **Django** 5
- **Django REST Framework (DRF)**
- **SQLite** (default, can be replaced with PostgreSQL/MySQL)
- **django-filter**
- **django-cors-headers**
- **Pillow**

---

## Project Structure

core/ # Django project (settings, urls, pagination)
users_app/ # Authentication & user profiles
offers_app/ # Offers & offer details
orders_app/ # Orders (customer ↔ business)
reviews_app/ # Reviews (customers → business)
stats_app/ # Platform statistics

yaml
Code kopieren

Each app has an `api/` folder containing:
- `serializers.py`
- `views.py`
- `urls.py`
- `permissions.py`

---

## Installation & Setup

Clone the repository and set up your virtual environment:

```bash
git clone https://github.com/your-username/coderr-backend.git
cd coderr-backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create an admin user
python manage.py createsuperuser

# Start the development server
python manage.py runserver
By default, the API will be available at: http://127.0.0.1:8000/api/

Authentication
This project uses token authentication.
After registration or login, the response contains a token that must be included in every request:



API Endpoints Overview
Authentication
POST /api/registration/ – Register a new user

POST /api/login/ – Login and receive a token

Profiles
GET /api/profile/{user_id}/ – Retrieve a profile

PATCH /api/profile/{user_id}/ – Update your own profile

GET /api/profiles/business/ – List all business profiles

GET /api/profiles/customer/ – List all customer profiles

Offers
GET /api/offers/ – List all offers (filterable & searchable)

POST /api/offers/ – Create a new offer (business only)

GET /api/offers/{id}/ – Retrieve an offer

PATCH /api/offers/{id}/ – Update your offer

DELETE /api/offers/{id}/ – Delete your offer

GET /api/offerdetails/{id}/ – Retrieve details of a specific offer detail

Orders
GET /api/orders/ – List all orders of the authenticated user

POST /api/orders/ – Create an order (customer only)

PATCH /api/orders/{id}/ – Update order status (business only)

DELETE /api/orders/{id}/ – Delete order (staff only)

GET /api/order-count/{business_user_id}/ – Count in-progress orders

GET /api/completed-order-count/{business_user_id}/ – Count completed orders

Reviews
GET /api/reviews/ – List reviews (with filters)

POST /api/reviews/ – Create a review (customer only)

PATCH /api/reviews/{id}/ – Update your review

DELETE /api/reviews/{id}/ – Delete your review

Statistics
GET /api/base-info/ – Global platform statistics

