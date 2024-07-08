# app/models.py

from app import db, bcrypt, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    projects = db.relationship('Project', backref='user', lazy=True)

class Project(db.Model):
    id                    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id               = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    mosaic_tiles          = db.relationship('MosaicTiles', backref='project', lazy=True)
    mosaic_target_images  = db.relationship('MosaicTargetImages', backref='project', lazy=True)
    mosaic_preview_images = db.relationship('MosaicPreviewImages', backref='project', lazy=True)
    mosaic                = db.relationship('Mosaic', backref='project', lazy=True)

# This will hold all of the tiles that will be used to create a mosaic.
class MosaicTiles(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String, nullable=False)
    rows = db.Column(db.Integer, nullable=False)
    cols = db.Column(db.Integer, nullable=False)
    comps = db.Column(db.Integer, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

# This will hold the mosaic target images.
class MosaicTargetImages(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String, nullable=False)
    rows = db.Column(db.Integer, nullable=False)
    cols = db.Column(db.Integer, nullable=False)
    comps = db.Column(db.Integer, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

# This will hold the mosaic preview images.
class MosaicPreviewImages(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String, nullable=False)
    rows = db.Column(db.Integer, nullable=False)
    cols = db.Column(db.Integer, nullable=False)
    comps = db.Column(db.Integer, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

# This will hold the binary data of the final mosaic that was created.
class Mosaic(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String, nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)