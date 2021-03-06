
import io
import os

import bcrypt
from flask import Flask, render_template, url_for, request, session, redirect
from flask import send_from_directory
from flask_pymongo import PyMongo
# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types
from werkzeug.utils import secure_filename
from gtts import gTTS


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'google_application_credentials.json'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = './'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
Description = ''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


app = Flask(__name__, static_folder="images")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MONGO_DBNAME'] = 'engr6313'
app.config['MONGO_URI'] = 'mongodb://Linhongyi:lhy520zf@ds249325.mlab.com:49325/engr6313'

mongo = PyMongo(app)


@app.route('/')
def index():
    if 'username' in session:
        print("You are logged in! ")
        # return 'You are logged in !' + session['username'] + render_template('upload.html')
        return  render_template('upload.html')
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))
    return 'Invalid username/password combination'


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name': request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name': request.form['username'], 'password': hashpass})
            session['username'] = request.form['username']
            return redirect(url_for('index'))

        return 'That username already exists!'

    return render_template('register.html')


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    global Description, Description
    global Music_path, Music_path
    client = vision.ImageAnnotatorClient()
    image_dir = os.path.join(APP_ROOT, 'images')
    if not os.path.isdir(image_dir):
        os.mkdir(image_dir)

    file = request.files['file']
    uploaded_filename = secure_filename(file.filename)
    print("Receive {0} file from user.".format(uploaded_filename))

    destination = "/".join([image_dir, uploaded_filename])
    file.save(destination)
    print("Saved {0} to {1}.".format(uploaded_filename, destination))

    # Loads the image into memory
    file_name = os.path.join(
        os.path.dirname(__file__),
        destination)
    with io.open(file_name, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    # Performs label detection on the image file
    labels = client.label_detection(image=image).label_annotations
    print(labels)
    for label in labels:
        mongo.db.information_image.insert({'filename': uploaded_filename, 'Label': label.description, 'Score': label.score})
        Description = Description + label.description + ' '

    tts = gTTS(text=Description, lang='en')
    tts.save("./images/" + file.filename + ".mp3")
    Music_path = file.filename + ".mp3"

    label_scores = list(map(lambda label: label.score, labels))

    print('The following label has been save to mongodb: {0}'.format(label_scores))

    return render_template("complete.html", image_name=uploaded_filename, labels=labels, Music_path=Music_path)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True,host='0.0.0.0')