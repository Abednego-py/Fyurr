from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Shows", backref="venue", lazy=True)
    genres = db.Column(db.String(120))


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship("Shows", backref="artist", lazy=True)


class Shows(db.Model):
    __tablename__ = "Shows"
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False, default="2035-04-15 20:00:00")
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"), nullable=False)
