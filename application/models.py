from .database import db
from sqlalchemy import Time

class User(db.Model):
    username = db.Column(db.String(20), primary_key=True)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    full_name = db.Column(db.String(80))
    address = db.Column(db.String(200))
    pincode = db.Column(db.String(6))
    is_admin = db.Column(db.Boolean, default=False)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parking_spot.id', ondelete="CASCADE"), nullable=False)
    username = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)  # Also fixed type here!
    parking_timestamp = db.Column(db.DateTime, nullable=False)
    leaving_timestamp = db.Column(db.DateTime)
    cost_per_hour = db.Column(db.Integer, nullable=False)
    vehicle_number = db.Column(db.String(15), nullable=False)
    approx_hours = db.Column(db.Integer, nullable=False)
    wheelchair_required = db.Column(db.Boolean, default=False)

    spot = db.relationship('ParkingSpot', back_populates='reservations')


class ParkingSpot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status = db.Column(db.String(1), default='A') 
    lot = db.relationship('ParkingLot', backref='spots')

    reservations = db.relationship('Reservation', back_populates='spot', cascade="all, delete-orphan")



class ParkingLot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(10), nullable=False)
    maximum_spots = db.Column(db.Integer, nullable=False)
    closing_time = db.Column(db.Time, nullable=False)
    opening_time = db.Column(db.Time, nullable=False)


