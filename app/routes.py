# app/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app, abort, session, g
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User
from app.models import Project
from app.models import MosaicTiles
from app.models import MosaicTargetImages
from app.models import MosaicPreviewImages
from app.models import Mosaic

import MosaifyPy

from PIL import Image
import mimetypes
import io
import os
import uuid

from app.common import find_number_in_array


import platform 
 
print("Printing Platform")
print(platform.uname())

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
    all_projects = Project.query.filter_by(user_id=current_user.id).all()
    projects = [proj.id for proj in all_projects]
    return render_template('home.html', projects=projects)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/list')
@login_required
def list_files():
    # Query the MosaicTiles table for all filenames
    filenames = MosaicTiles.query.with_entities(MosaicTiles.filename).all()
    # Extract filenames from the result tuples
    files = [file.filename for file in filenames]
    files.sort()

    return render_template('list.html', files=files)

@main.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    # Query the MosaicTiles table for the data where the filename matches
    file_entry = MosaicTiles.query.filter_by(filename=filename).first()
    
    if file_entry:

        img = Image.frombytes("RGB", (file_entry.rows, file_entry.cols), file_entry.data) 
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_entry.filename)
        img.save(file_path)

        file_data = None
        with open(file_path, 'rb') as f:
            file_data = f.read()

        os.remove(file_path)

        if None != file_data:
            mime_type = mimetypes.guess_type(filename)[0]
            
            if mime_type:
                return send_file(io.BytesIO(file_data), mimetype=mime_type, as_attachment=True, download_name=filename)
            else:
                abort(400, description="MIME type could not be determined.")
    else:
        abort(404, description="File not found.")

    return 'File not found', 404

@main.route('/mosaify')
@login_required
def mosaify():
    all_projects = Project.query.filter_by(user_id=current_user.id).all()
    projects = [proj.id for proj in all_projects]

    current_project_id = session['current_project_id']
    filenames = MosaicTiles.query.with_entities(MosaicTiles.filename).filter_by(project_id=current_project_id).all()
    files = [file.filename for file in filenames]

    target_filenames = MosaicTargetImages.query.with_entities(MosaicTargetImages.filename).filter_by(project_id=current_project_id).all()
    target_files = [file.filename for file in target_filenames]

    return render_template('mosaify.html', projects=projects, files=files, target_files=target_files)

@main.route('/mosaify_previous/<project_id>')
@login_required
def mosaify_previous(project_id):
    all_projects = Project.query.filter_by(user_id=current_user.id).all()
    projects = [int(proj.id) for proj in all_projects]

    if None != find_number_in_array(projects, int(project_id)):
        session['current_project_id'] = project_id
    else:
        print("not found", projects, project_id)


    return redirect(url_for('main.mosaify'))


@main.route('/mosaify_new')
@login_required
def mosaify_new():
    new_project = Project(user_id=current_user.id)

    db.session.add(new_project)
    db.session.commit()

    # Store the project ID in the session
    session['current_project_id'] = new_project.id

    return render_template('mosaify.html')

@main.route('/upload_tilefiles', methods=['POST'])
@login_required
def upload_tilefiles():
    files = request.files.getlist('files[]')
    for file in files:
        if file:
            filename = file.filename
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                with Image.open(file_path) as im:
                    # Process the image here
                    im = im.convert('RGB')
                    data = im.tobytes()
                    rows, cols = im.size
                    comps = 3

                    current_project_id = session['current_project_id']

                    new_file = MosaicTiles(
                        project_id=current_project_id,  # You need to set the appropriate project_id here
                        user_id=current_user.id,
                        filename=filename,
                        data=data,
                        rows=rows,
                        cols=cols,
                        comps=comps
                    )

                    # Add the new file to the session and commit
                    db.session.add(new_file)
                    db.session.commit()
                os.remove(file_path)
            except IOError:
                print("An error occurred while trying to open the image.")

    return redirect(url_for('main.mosaify'))

@main.route('/upload_targetfiles', methods=['POST'])
@login_required
def upload_targetfiles():
    files = request.files.getlist('files[]')
    for file in files:
        if file:
            filename = file.filename
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            try:
                with Image.open(file_path) as im:
                    # Process the image here
                    im = im.convert('RGB')
                    data = im.tobytes()
                    rows, cols = im.size
                    comps = 3

                    current_project_id = session['current_project_id']

                    new_file = MosaicTargetImages(
                        project_id=current_project_id,  # You need to set the appropriate project_id here
                        user_id=current_user.id,
                        filename=filename,
                        data=data,
                        rows=rows,
                        cols=cols,
                        comps=comps
                    )

                    # Add the new file to the session and commit
                    db.session.add(new_file)
                    db.session.commit()

                os.remove(file_path)

            except IOError:
                print("An error occurred while trying to open the image.")

    return redirect(url_for('main.mosaify'))

def get_current_project():
    if 'current_project_id' in session:
        current_project_id = session['current_project_id']
        return Project.query.filter_by(id=current_project_id, user_id=current_user.id).first()
    return None

@main.before_request
def load_current_project():
    if current_user.is_authenticated:
        g.current_project = get_current_project()
    else:
        g.current_project = None

@main.route('/mosaify_run')
@login_required
def mosaify_run():

    filenames = MosaicTiles.query.with_entities(MosaicTiles.filename).all()
    files = [file.filename for file in filenames]

    all_projects = Project.query.filter_by(user_id=current_user.id).all()
    projects = [proj.id for proj in all_projects]

    target_files = []

    current_project_id = session['current_project_id']
    target_queried_data = MosaicTiles.query.with_entities(MosaicTiles.id, MosaicTiles.filename, MosaicTiles.data, MosaicTiles.rows, MosaicTiles.cols, MosaicTiles.comps).filter_by(project_id=current_project_id).all()
    # There really should only be one.
    for id_target, filename_target, data_target, rows_target, cols_target, comps_target in target_queried_data:
        target_files.append(filename_target)

        queried_data = MosaicTiles.query.with_entities(MosaicTiles.id, MosaicTiles.filename, MosaicTiles.data, MosaicTiles.rows, MosaicTiles.cols, MosaicTiles.comps).filter_by(project_id=current_project_id).all()

        mosaify = MosaifyPy.Mosaify()
        mosaify.setTileSize(8)
        for id, filename, data, rows, cols, comps in queried_data:
            mosaify.addTileImage(cols, rows, comps, data, filename, id)

        if mosaify.generate(rows_target, cols_target, comps_target, data_target):
            preview_path = MosaifyPy.getMosaicPreviewPath(mosaify)
            main_path = MosaifyPy.getMosaicPath()
            print('\n\n\n\n\nIS generated')
            print(preview_path)
            print(main_path)
            print('\n\n\n\n\n')

            try:
                with Image.open(preview_path) as im:
                    # Process the image here
                    im = im.convert('RGB')
                    data = im.tobytes()
                    rows, cols = im.size
                    comps = 3

                    new_file = MosaicPreviewImages(
                        project_id=current_project_id,  # You need to set the appropriate project_id here
                        user_id=current_user.id,
                        filename=filename,
                        data=data,
                        rows=rows,
                        cols=cols,
                        comps=comps
                    )

                    # Add the new file to the session and commit
                    db.session.add(new_file)
                    db.session.commit()

                os.remove(preview_path)

                with open(main_path, 'rb') as f:
                    file_data = f.read()

                    new_file = Mosaic(
                        project_id=current_project_id,  # You need to set the appropriate project_id here
                        user_id=current_user.id,
                        data=data
                    )

                    # Add the new file to the session and commit
                    db.session.add(new_file)
                    db.session.commit()

                os.remove(main_path)

            except IOError:
                print("An error occurred while trying to open the image.")

        else:
            print("not generated")

    return render_template('mosaify.html', projects=projects, files=files, target_files=target_files)
