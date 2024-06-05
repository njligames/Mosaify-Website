# app/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app, abort, session
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User
from app.models import Project
from app.models import ProjectData

from PIL import Image
import mimetypes
import io
import os
import uuid

main = Blueprint('main', __name__)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/home')
@login_required
def home():
    return render_template('home.html')

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/list')
@login_required
def list_files():
    # Query the ProjectData table for all filenames
    filenames = ProjectData.query.with_entities(ProjectData.filename).all()
    # Extract filenames from the result tuples
    files = [file.filename for file in filenames]

    return render_template('list.html', files=files)

@main.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    # Query the ProjectData table for the data where the filename matches
    file_entry = ProjectData.query.filter_by(filename=filename).first()
    
    if file_entry:
        file_data = file_entry.data
        mime_type = mimetypes.guess_type(filename)[0]
        
        if mime_type:
            return send_file(io.BytesIO(file_data), mimetype=mime_type, as_attachment=True, download_name=filename)
        else:
            abort(400, description="MIME type could not be determined.")
    else:
        abort(404, description="File not found.")

    # return 'File not found', 404

@main.route('/mosaify')
@login_required
def mosaify():
    all_projects = Project.query.filter_by(user_id=current_user.id).all()
    projects = [proj.id for proj in all_projects]
    return render_template('mosaify.html', projects=projects)

@main.route('/mosaify_new')
@login_required
def mosaify_new():
    new_project = Project(user_id=current_user.id)

    db.session.add(new_project)
    db.session.commit()

    # Store the project ID in the session
    session['project_id'] = new_project.id

    return render_template('mosaify.html')

@main.route('/upload', methods=['POST'])
@login_required
def upload_file():
    files = request.files.getlist('files[]')
    for file in files:
        if file:
            filename = file.filename
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            with open(file_path, 'rb') as f:
                file_data = f.read()

            # im = Image.open(file_path)
            # im = im.convert('RGBA')
            # pixels = im.tobytes()
            # rows, cols = im.size
            # comps = 4

            project_id = session['project_id']

            new_file = ProjectData(
                project_id=project_id,  # You need to set the appropriate project_id here
                user_id=current_user.id,
                filename=filename,
                data=file_data
            )

            # Add the new file to the session and commit
            db.session.add(new_file)
            db.session.commit()

            os.remove(file_path)

    return redirect(url_for('main.mosaify'))
