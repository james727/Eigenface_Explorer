import os
from flask import Flask, render_template, session, redirect, url_for, request, flash
from flask.ext.script import Manager, Shell
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from flask.ext.uploads import UploadSet, configure_uploads, IMAGES
from wtforms import StringField, SubmitField, FileField, HiddenField
from flask.ext.wtf.file import FileAllowed, FileRequired
from wtforms.validators import Required
from werkzeug.utils import secure_filename
import flask_resize
import json
import process_image

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

manager = Manager(app)
bootstrap = Bootstrap(app)
app.config['RESIZE_URL'] = ''
app.config['RESIZE_ROOT'] = './'
app.config['RESIZE_CACHE_DIR'] = 'static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
flask_resize.Resize(app)

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class FileForm(Form):
    photo = FileField('Your Photo')
    submit = SubmitField('Process Photo')

class CropForm(Form):
    x1 = HiddenField('x1')
    y1 = HiddenField('y1')
    x2 = HiddenField('x2')
    y2 = HiddenField('y2')
    width = HiddenField('width')
    height = HiddenField('height')
    submit = SubmitField('Crop photo and submit for processing')


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
def index():
    form = FileForm()
    files = get_eigenface_photo_paths(30)
    if request.method == 'POST':
        filename = secure_filename(form.photo.data.filename)
        if filename == '':
            flash('Please select a photo to upload!')
        elif not allowed_file(filename):
            flash('Your file must be a standard png or jpeg!')
        else:
            form.photo.data.save('static/'+filename)
            image_url = url_for('static', filename = filename)
            messages = json.dumps({'image_name': image_url})
            session['messages'] = messages
            return redirect(url_for('.upload'))
    else:
        filename = None
    return render_template('index.html', form = form, filename = filename, files = files)

@app.route('/eigenfaces', methods = ['GET','POST'])
def eigenfaces():
    messages = json.loads(session['messages'])
    images_path = messages['images_path']
    cropped_image_url = '/'+messages['cropped_image_url']
    files = []
    for f in os.listdir(images_path):
        file_number = int(f.split('.')[0])
        file_tuple = (file_number, images_path+str(f))
        files.append(file_tuple)
    files = [x[1] for x in sorted(files, key = lambda x: x[0])]
    return render_template('eigenfaces.html', files = files, cropped_image_url = cropped_image_url)

@app.route('/upload', methods=['GET','POST'])
def upload():
    crop_form = CropForm()
    messages = json.loads(session['messages'])
    image_url = messages['image_name']
    if request.method == 'POST':
        x1, y1, x2, y2 = crop_form.x1.data, crop_form.y1.data, crop_form.x2.data, crop_form.y2.data
        if x1 != '':
            w, h = crop_form.width.data, crop_form.height.data
            cropped_image_url = process_image.crop_and_save_image(image_url, x1,y1,x2,y2,w,h)
            image_projections_path = process_image.eigenface_components(cropped_image_url)
            messages = json.dumps({'images_path': image_projections_path, 'cropped_image_url': cropped_image_url})
            session['messages'] = messages
            return redirect(url_for('.eigenfaces'))
        else:
            flash('Please crop the photo to include only your face before proceeding!')
    return render_template('upload.html', form = crop_form, image_name = image_url)

@app.route('/about', methods = ['GET'])
def about():
    return render_template('about.html')

@app.route('/contact', methods = ['GET'])
def contact():
    return render_template('contact.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_eigenface_photo_paths(i):
    path = 'static/eigenface_images/'
    files = []
    for j in range(i):
        files.append(path+str(j)+'.jpg')
    return files

if __name__ == '__main__':
    app.run(debug=True)
