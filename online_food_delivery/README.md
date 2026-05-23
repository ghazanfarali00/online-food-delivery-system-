# 🍔 FoodExpress — Online Food Delivery System

A full-featured desktop application for online food delivery built with **Python Tkinter** and **SQLite**.

## 📋 Features

### Multi-Role System
- **Customer** — Browse restaurants, add to cart, place orders, track status, leave reviews
- **Vendor** — Manage restaurant profile, menu items, process orders
- **Admin** — Dashboard analytics, user management, review moderation, support tickets
- **Delivery Person** — Accept orders, update delivery status, track deliveries

### Key Functionality
- ✅ User Registration & Authentication (with password reset via security questions)
- ✅ Restaurant Browsing with Search & Filter
- ✅ Cart Management (add/remove/update quantity)
- ✅ Order Placement with multiple payment methods (COD, Card, Wallet)
- ✅ Order Tracking (Placed → Preparing → Out for Delivery → Delivered)
- ✅ Ratings & Reviews
- ✅ Notification System
- ✅ Admin Dashboard with Analytics
- ✅ Menu Management for Vendors
- ✅ Delivery Queue Management
- ✅ Help & Support with FAQ and Ticket System
- ✅ Address Management

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.x |
| GUI Framework | Tkinter (built-in) |
| Database | SQLite3 (built-in) |
| Testing | unittest |
| Architecture | MVC (Model-View-Controller) |

## 📁 Project Structure

```
online_food_delivery/
├── main.py                  # Entry point
├── config.py                # Configuration & constants
├── database.py              # SQLite connection & schema
├── models/                  # Data models (CRUD operations)
├── views/                   # Tkinter UI screens
├── controllers/             # Business logic
├── utils/                   # Validators, helpers, exceptions
├── tests/                   # Unit tests
├── requirements.txt
└── README.md
```

## 🚀 How to Run

1. **Clone the repository:**
```bash
git clone <repository-url>
cd online_food_delivery
```

2. **Run the application:**
```bash
python main.py
```

No external dependencies required! Everything uses Python standard library.

3. **Run tests:**
```bash
python -m pytest tests/ -v
# OR
python -m unittest discover tests/ -v
```

## 🔑 Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@foodexpress.com | admin123 |
| Customer | sara@gmail.com | customer123 |
| Vendor | ali@kitchen.com | vendor123 |
| Delivery | ahmed@rider.com | delivery123 |

## 📐 Software Engineering Concepts Applied

### 1. Design Pattern — MVC Architecture
- **Models**: Handle database CRUD operations
- **Views**: Tkinter GUI screens
- **Controllers**: Business logic layer

### 2. Refactoring
- DRY principle — Reusable components (cards, forms, tables)
- Single Responsibility Principle — Each module has one purpose
- Clean code with docstrings and type hints
- Constants extracted to `config.py`

### 3. Exception Handling
- Custom exception hierarchy (`FoodDeliveryException` base class)
- Specific exceptions: `AuthenticationError`, `ValidationError`, `OrderError`, `DatabaseError`
- All database operations wrapped in try-except
- User-friendly error messages via messagebox

### 4. Unit Testing
- 40+ test cases covering models, controllers, validators, and database
- Tests use isolated temporary databases
- Run with: `python -m unittest discover tests/ -v`

### 5. Input Validation
- Email, phone, password, price, quantity, and rating validation
- All user inputs validated before processing

### 6. Version Control (Git)
- Clean commit history
- Proper `.gitignore` for Python projects
- Organized project structure

## 📄 License

This project is created for educational purposes — Software Construction & Development course.
