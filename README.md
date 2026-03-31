# Vehicle Parking App

A web-based multi-user parking management system built using **Flask**, **Jinja2**, **SQLite**, and **Bootstrap**.  
The application supports both **Admin** and **User** roles, allowing efficient management of parking lots, parking spots, and vehicle reservations.

## About the Project

The Vehicle Parking App is designed to simplify the process of managing parking spaces and reservations through a user-friendly web interface. It allows administrators to create and manage parking lots and parking spots, while users can search for available parking, book spots, and release them when leaving.

This project follows the **MVC (Model-View-Controller)** pattern and demonstrates core full-stack development concepts including authentication, CRUD operations, database relationships, session handling, and dynamic web rendering.

## Features

### User Features
- User registration and login
- View available parking lots
- Search parking lots by location or pincode
- Book a parking spot
- Release a booked parking spot
- View reservation history
- Automatic parking cost calculation based on time

### Admin Features
- Admin login
- Add, edit, and delete parking lots
- Add and manage parking spots
- View and manage parking data
- Search records by:
  - Location
  - Pincode
  - User ID
  - Vehicle number

### General Features
- Clean UI using Bootstrap
- Session-based login handling
- Relational database design using SQLite
- Structured backend routing using Flask

## Tech Stack

### Languages & Frameworks
- Python
- Flask
- Jinja2
- HTML
- CSS
- Bootstrap

### Database & Tools
- SQLite
- Flask-SQLAlchemy
- Flask-Session

## Project Structure

```bash
Vehicle_Parking_App/
│
├── app.py
├── templates/
│   ├── *.html
│
├── static/
│   ├── style.css
│
├── instance/
│   ├── database.db
│
├── api.yaml
└── README.md
```
## Database Schema

The project uses four main tables:

### 1. User
- `username` (Primary Key)
- `email` (Unique, Not Null)
- `password` (Not Null)
- `full_name`
- `address`
- `pincode`
- `is_admin` (Boolean)

### 2. ParkingLot
- `id` (Primary Key)
- `location`
- `pincode`
- `price_per_hour`

### 3. ParkingSpot
- `id` (Primary Key)
- `lot_id` (Foreign Key → ParkingLot)
- `status` (Available / Occupied)
## Architecture

This project follows the **MVC Pattern**:

- **Models**: Database tables and relationships
- **Views**: HTML templates rendered using Jinja2
- **Controllers**: Flask routes handling application logic
- **Static Files**: CSS and Bootstrap for styling

## How to Run the Project

### 1. Clone the repository
```bash
git clone <your-repository-link>
cd <your-project-folder>
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Activate the Virtual environment 
```bash
venv\Scripts\activate
```

### 4. Install dependencies 
```bash
pip install flask flask-sqlalchemy flask-session
```

### 5. Run the application 
```bash
python app.py
```

### 6. Open in browsers
```bash
http://127.0.0.1:5000/
```
