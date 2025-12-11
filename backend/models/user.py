from flask_login import UserMixin
from .. import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    head_mesh_filename = db.Column(db.String(255), nullable=True)

    # LOCKDOWN COLUMNS – ONE HUMAN ONLY
    head_mesh_signature = db.Column(db.String(128), nullable=False, default='')
    head_mesh_bound_at = db.Column(db.DateTime, nullable=True)