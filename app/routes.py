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

import Mosaify

from PIL import Image
import mimetypes
import io
import os
import uuid
import zlib

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

    current_project_id = session['current_project_id']
    filenames = MosaicTiles.query.with_entities(MosaicTiles.filename, MosaicTiles.id).filter_by(project_id=current_project_id).all()
    files = [file.id for file in filenames]

    return render_template('list.html', files=files)

@main.route('/tile_uploads/<id>')
@login_required
def uploaded_tile_file(id):
    # Query the MosaicTiles table for the data where the filename matches
    file_entry = MosaicTiles.query.filter_by(id=id).first()

    if file_entry:

        d = zlib.decompress(file_entry.data)
        img = Image.frombytes("RGB", (file_entry.rows, file_entry.cols), d)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_entry.filename)
        img.save(file_path)

        file_data = None
        with open(file_path, 'rb') as f:
            file_data = f.read()

        os.remove(file_path)

        if None != file_data:
            mime_type = mimetypes.guess_type(file_entry.filename)[0]

            if mime_type:
                return send_file(io.BytesIO(file_data), mimetype=mime_type, as_attachment=True, download_name=file_entry.filename)
            else:
                abort(400, description="MIME type could not be determined.")
    else:
        abort(404, description="File not found.")

    return 'File not found', 404

@main.route('/mosaic_preview_uploads/<id>')
@login_required
def uploaded_mosaic_image_preview_file(id):
    # Query the MosaicTiles table for the data where the filename matches
    file_entry = MosaicPreviewImages.query.filter_by(id=id).first()

    if file_entry:

        d = zlib.decompress(file_entry.data)
        img = Image.frombytes("RGB", (file_entry.rows, file_entry.cols), d)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_entry.filename)
        img.save(file_path)

        file_data = None
        with open(file_path, 'rb') as f:
            file_data = f.read()

        os.remove(file_path)

        if None != file_data:
            mime_type = mimetypes.guess_type(file_entry.filename)[0]

            if mime_type:
                return send_file(io.BytesIO(file_data), mimetype=mime_type, as_attachment=True, download_name=file_entry.filename)
            else:
                abort(400, description="MIME type could not be determined.")
    else:
        abort(404, description="File not found.")

    return 'File not found', 404

@main.route('/mosaic_uploads/<id>')
@login_required
def uploaded_mosaic_image_file(id):
    # Query the MosaicTiles table for the data where the filename matches
    file_entry = Mosaic.query.filter_by(id=id).first()

    if file_entry:
        if None != file_entry.data:
            mime_type = mimetypes.guess_type(file_entry.filename)[0]

            if mime_type:
                d = zlib.decompress(file_entry.data)
                return send_file(io.BytesIO(d), mimetype=mime_type, as_attachment=True, download_name=file_entry.filename)
            else:
                abort(400, description="MIME type could not be determined.")
    else:
        abort(404, description="File not found.")

    return 'File not found', 404

@main.route('/target_uploads/<id>')
@login_required
def uploaded_target_file(id):
    # Query the MosaicTiles table for the data where the filename matches
    file_entry = MosaicTargetImages.query.filter_by(id=id).first()

    if file_entry:

        d = zlib.decompress(file_entry.data)
        img = Image.frombytes("RGB", (file_entry.rows, file_entry.cols), d)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_entry.filename)
        img.save(file_path)

        file_data = None
        with open(file_path, 'rb') as f:
            file_data = f.read()

        os.remove(file_path)

        if None != file_data:
            mime_type = mimetypes.guess_type(file_entry.filename)[0]

            if mime_type:
                return send_file(io.BytesIO(file_data), mimetype=mime_type, as_attachment=True, download_name=file_entry.filename)
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
    filenames = MosaicTiles.query.with_entities(MosaicTiles.filename, MosaicTiles.id).filter_by(project_id=current_project_id).all()
    files = [file.id for file in filenames]

    target_filenames = MosaicTargetImages.query.with_entities(MosaicTargetImages.filename, MosaicTargetImages.id).filter_by(project_id=current_project_id).all()
    target_files = [file.id for file in target_filenames]

    mosaic_image_preview = MosaicPreviewImages.query.with_entities(MosaicPreviewImages.id).filter_by(project_id=current_project_id).first()
    mosaic_image_preview_id = None
    if mosaic_image_preview and len(mosaic_image_preview) > 0:
        mosaic_image_preview_id = mosaic_image_preview[0]

    mosaic_image = Mosaic.query.with_entities(Mosaic.id).filter_by(project_id=current_project_id).first()
    mosaic_image_id = None
    if mosaic_image and len(mosaic_image) > 0:
        mosaic_image_id = mosaic_image[0]

    return render_template('mosaify.html', projects=projects, files=files, target_files=target_files, mosaic_image_preview_id=mosaic_image_preview_id, mosaic_image_id=mosaic_image_id)

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
            filename = os.path.basename(file.filename)
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
                        data=zlib.compress(data),
                        rows=rows,
                        cols=cols,
                        comps=comps
                    )

                    # Add the new file to the session and commit
                    db.session.add(new_file)
                    db.session.commit()
            except IOError:
                print("An error occurred while trying to open the image.")

            os.remove(file_path)

    return redirect(url_for('main.mosaify'))

@main.route('/upload_targetfiles', methods=['POST'])
@login_required
def upload_targetfiles():
    files = request.files.getlist('files[]')
    for file in files:
        if file:
            filename = os.path.basename(file.filename)
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
                        data=zlib.compress(data),
                        rows=rows,
                        cols=cols,
                        comps=comps
                    )

                    # Add the new file to the session and commit
                    db.session.add(new_file)
                    db.session.commit()
            except IOError:
                print("An error occurred while trying to open the image.")

            os.remove(file_path)

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

    fileids = MosaicTiles.query.with_entities(MosaicTiles.id).all()
    files = [file.id for file in fileids]

    all_projects = Project.query.filter_by(user_id=current_user.id).all()
    projects = [proj.id for proj in all_projects]

    target_files = []

    current_project_id = session['current_project_id']

    target_queried_data = MosaicTargetImages.query.with_entities(MosaicTargetImages.id, MosaicTargetImages.filename, MosaicTargetImages.data, MosaicTargetImages.rows, MosaicTargetImages.cols, MosaicTargetImages.comps).filter_by(project_id=current_project_id).all()
    # There really should only be one.

    if len(target_queried_data) == 0:
        abort(404, description="No Target Found.")

    my_target = target_queried_data[0]

    # print(my_target)

    target_files.append(my_target.id)

    queried_data = MosaicTiles.query.with_entities(MosaicTiles.id, MosaicTiles.filename, MosaicTiles.data, MosaicTiles.rows, MosaicTiles.cols, MosaicTiles.comps).filter_by(project_id=current_project_id).all()

    print(Mosaify)
    mosaify = Mosaify.Mosaify()
    mosaify.setTileSize(8)
    for id, filename, data, rows, cols, comps in queried_data:
        d = zlib.decompress(data)
        mosaify.addTileImage(cols, rows, comps, d, filename, id)

    print("Generating the Mosaic...")

    # entries = MosaicPreviewImages.query(MosaicPreviewImages).filter(MosaicPreviewImages.project_id == current_project_id).all()
    entries = MosaicPreviewImages.query.filter_by(project_id=current_project_id).all()
    for entry in entries:
        if entry:
            # If an entry is found, delete it
            db.session.delete(entry)
            db.session.commit()

    # entries = Mosaic.query(Mosaic).filter(Mosaic.project_id == current_project_id).all()
    entries = Mosaic.query.filter_by(project_id=current_project_id).all()
    for entry in entries:
        if entry:
            # If an entry is found, delete it
            db.session.delete(entry)
            db.session.commit()

    mosaic_image_preview_id = None
    mosaic_image_id = None
    d = zlib.decompress(my_target.data)
    if mosaify.generate(my_target.rows, my_target.cols, my_target.comps, d):
        preview_path = mosaify.getMosaicPreviewPath()
        main_path = mosaify.getMosaicPath()
        print('Mosaic was generated SUCCESSFULLY')

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
                    filename=os.path.basename(preview_path),
                    data=zlib.compress(data),
                    rows=rows,
                    cols=cols,
                    comps=comps
                )

                # Add the new file to the session and commit
                db.session.add(new_file)
                db.session.commit()

            # print("preview_path", preview_path)
            os.remove(preview_path)

            with open(main_path, 'rb') as f:
                data = f.read()

                # new_file = Mosaic(
                #     project_id=current_project_id,  # You need to set the appropriate project_id here
                #     user_id=current_user.id,
                #     data=zlib.compress(data),
                #     filename=os.path.basename(main_path)
                # )

                # # Add the new file to the session and commit
                # db.session.add(new_file)
                # db.session.commit()

            # print(main_path)
            os.remove(main_path)

        except IOError:
            abort(404, description="An error occurred while trying to open the image.")

        mosaic_image_preview = MosaicPreviewImages.query.with_entities(MosaicPreviewImages.id).filter_by(project_id=current_project_id).first()
        if mosaic_image_preview and len(mosaic_image_preview) > 0:
            mosaic_image_preview_id = mosaic_image_preview[0]

        # mosaic_image = Mosaic.query.with_entities(Mosaic.id).filter_by(project_id=current_project_id).first()
        # if mosaic_image and len(mosaic_image) > 0:
        #     mosaic_image_id = mosaic_image[0]

        print("preview", mosaic_image_preview[0])
        # print("mosaic", mosaic_image[0])

    else:
        print("not generated")

    return render_template('mosaify.html', projects=projects, files=files, target_files=target_files, mosaic_image_preview_id=mosaic_image_preview_id, mosaic_image_id=mosaic_image_id)
