from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone


db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    registration_date = db.Column(db.DateTime(), unique=False, nullable=False, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(), unique=False, nullable=True, default=datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favorite = db.relationship("Favorites", back_populates="users", uselist=True)


    def __repr__(self):
        return '<User %r>' % self.username

    def serialize(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "email": self.email,
        }
    
    def serialize_fav(self):
        return {
            "id": self.id,
            "email": self.email,
            "favorites": list(map(lambda item: item.serialize(), self.favorite))
        }


class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diameter = db.Column(db.String(180), unique=False, nullable=True)
    rotation_period = db.Column(db.String(180), unique=False, nullable=True)
    orbital_period = db.Column(db.String(180), unique=False, nullable=True)
    gravity = db.Column(db.String(180), unique=False, nullable=True)
    population = db.Column(db.String(180), unique=False, nullable=True)
    climate = db.Column(db.String(100), unique=False, nullable=True)
    terrain = db.Column(db.String(100), unique=False, nullable=True)
    surface_water = db.Column(db.String(180), unique=False, nullable=True)
    created_at = db.Column(db.DateTime(), unique=False, nullable=True, default=datetime.now(timezone.utc))
    name = db.Column(db.String(100), unique=False, nullable=True)
    url = db.Column(db.String(200), unique=False, nullable=True)
    description = db.Column(db.Text(), unique=False, nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "gravity": self.gravity,
            "population": self.population,
            "climate": self.climate,
            "terrain": self.terrain,
            "surface_water": self.surface_water,
            "created_at": self.created_at,
            "url": self.url,
            "description": self.description,
        }

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.String(100), unique=False, nullable=True)
    hair_color = db.Column(db.String(100), unique=False, nullable=True)
    skin_color = db.Column(db.String(100), unique=False, nullable=True)
    eye_color = db.Column(db.String(100), unique=False, nullable=True)
    birth_year = db.Column(db.String(100), unique=False, nullable=True)
    gender = db.Column(db.String(100), unique=False, nullable=True)
    created_at = db.Column(db.DateTime(), unique=False, nullable=True, default=datetime.now(timezone.utc))
    edited_at = db.Column(db.DateTime(), unique=False, nullable=True, default=datetime.now(timezone.utc))
    name = db.Column(db.String(100), unique=False, nullable=True)
    homeworld_id = db.Column(db.Integer, db.ForeignKey("planet.id"), unique=False, nullable=True)
    url = db.Column(db.String(200), unique=False, nullable=True)

    def serialize(self):
        return  {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender,
            "created_at": self.created_at,
            "edited_at": self.edited_at,
            "url": self.url,
        }

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=False, nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey("planet.id"), unique=False, nullable=True)
    people_id = db.Column(db.Integer, db.ForeignKey("people.id"), unique=False, nullable=True)

    users = db.relationship("User", backref="favorites")

    def serialize(self):
        return {
            "user_id": self.user_id,
            "planet_id": self.planet_id,
            "people_id": self.people_id,
        }
