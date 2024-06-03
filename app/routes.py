# app/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import User

from PIL import Image
import mimetypes

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
    files=[]
    # with sqlite3.connect(app.config['DATABASE']) as conn:
    #     c = conn.cursor()
    #     c.execute('SELECT filename FROM images')
    #     files = c.fetchall()
    return render_template('list.html', files=files)

@main.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    # with sqlite3.connect(app.config['DATABASE']) as conn:
    #     c = conn.cursor()
    #     c.execute('SELECT data FROM images WHERE filename=?', (filename,))
    #     row = c.fetchone()
    #     if row:
    #         file_data = row[0]
    #         mime_type = mimetypes.guess_type(filename)[0]
    #         if mime_type:
    #             return send_file(io.BytesIO(file_data), mimetype=mime_type)
    return 'File not found', 404

@main.route('/upload', methods=['POST'])
@login_required
def upload_file():
    files = request.files.getlist('files[]')
    for file in files:
        if file:
            filename = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            with open(file_path, 'rb') as f:
                file_data = f.read()

            im = Image.open(file_path)
            im = im.convert('RGBA')
            pixels = im.tobytes()
            rows, cols = im.size
            comps = 4

            # with sqlite3.connect(app.config['DATABASE']) as conn:
            #     c = conn.cursor()
            #     c.execute('INSERT INTO images (filename, data, rows, cols, comps) VALUES (?, ?, ?, ?, ?)', (filename, pixels, rows, cols, comps))
            #     conn.commit()

    return redirect(url_for('main.index'))