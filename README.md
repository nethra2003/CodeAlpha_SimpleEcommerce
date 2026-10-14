# 🛍️ NovaCart – Django E-Commerce Website

NovaCart is a full-stack e-commerce web application built using Django, HTML, CSS, and JavaScript. It provides a simple and user-friendly shopping experience with product browsing, cart management, checkout, order tracking, wishlists, and product reviews.

## ✨ Features

- 🛒 **Product Catalog:** Browse products with search, category filters, and sorting.
- 📦 **Product Details:** View product descriptions, prices, images, and ratings.
- 🛍️ **Shopping Cart:** Add, update, and remove products from the cart.
- 🔐 **User Authentication:** Register, log in, and manage a user account.
- 💳 **Checkout:** Place orders with delivery details and stock validation.
- 📋 **Order Management:** View order history, order details, and order status.
- 🚚 **Order Tracking:** Track progress from order placement to delivery.
- ❤️ **Wishlist:** Save favorite products for later.
- ⭐ **Product Reviews:** Rate products and write reviews.
- ⚙️ **Admin Dashboard:** Manage products, orders, and store data through Django Admin.
- 📱 **Responsive Design:** Browse the store on desktop and mobile screens.

## 🧰 Tech Stack

- **Backend:** Python, Django
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** SQLite for local development
- **Image Handling:** Pillow
- **Version Control:** Git and GitHub

## 📁 Project Structure

```text
CodeAlpha_SimpleEcommerce/
├── config/                 # Django project settings and URLs
├── store/                  # Products, cart, orders, reviews and views
│   └── migrations/         # Database migrations
├── templates/              # HTML templates
│   ├── registration/       # Login and signup pages
│   └── store/               # Store pages
├── static/
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript
│   └── images/             # Static website images
├── media/                  # Locally uploaded product images (not committed)
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites

Install the following on your computer:

- Python 3.12 or another version compatible with the dependencies
- Git
- A web browser

### 1. Clone the repository

```bash
git clone https://github.com/nethra2003/CodeAlpha_SimpleEcommerce.git
cd CodeAlpha_SimpleEcommerce
```
### 2. Create a virtual environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```
### 4. Initialize the database

```bash
python manage.py migrate
```
### 5. Create an administrator account

```bash
python manage.py createsuperuser
```
Follow the prompts to create your username and password.

### 6. Start the development server

```bash
python manage.py runserver
```

Open the application in your browser:

**http://127.0.0.1:8000/**
