# ecommerce_unnati_Labs

# Deep Store — Modern E-Commerce Platform

A full-stack, responsive e-commerce web application built using **Django** and styled with modern CSS/Bootstrap. Features full product catalog browsing, search & categorization, cart management, user reviews, wishlist functionality, an administrative analytics dashboard, and **Razorpay** payment gateway integration.

🌐 **Live Demo:** [https://ecommerce-unnati.onrender.com/](https://ecommerce-unnati.onrender.com/)

---

## ✨ Features

- **Product Catalog & Discovery:** Filter products by categories or search keywords dynamically with instant results.
- **Cart & Order Flow:** Session-based cart persistence for guest and authenticated users with order summary calculation.
- **Payment Gateway:** Full Razorpay integration supporting real-time payment handling and dynamic callback validation.
- **Customer Engagement:** Product reviews, rating systems, and interactive wishlist management.
- **Admin Analytics Dashboard:** Custom business portal highlighting revenue metrics, order totals, low-stock warnings, and recent activity.
- **Production-Ready Deployment:** Hosted on Render with WhiteNoise static collection and media routing.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.12, Django 6.0
- **Database:** SQLite (Development / Deployment)
- **Static & Media Asset Delivery:** WhiteNoise, Django URL routing
- **WSGI HTTP Server:** Gunicorn
- **Payment Processing:** Razorpay API Client
- **Hosting / PaaS:** Render

---

## 📁 Project Structure

```text
ecommerce_unnati/
├── ecommerce_core/         # Project configuration (settings, WSGI, URLs)
├── shop/                   # Core application
│   ├── migrations/         # Database migrations
│   ├── static/             # Custom CSS, JS, styling assets
│   ├── templates/shop/     # HTML templates (catalog, cart, checkout, dashboard)
│   ├── models.py           # Database models (Product, Category, Order, Cart, etc.)
│   ├── views.py            # Business logic and request controllers
│   ├── urls.py             # Application URL routing
│   └── forms.py            # Form validation
├── media/                  # Uploaded product media files
├── db.sqlite3              # Database instance
├── requirements.txt        # Python package dependencies
└── manage.py
