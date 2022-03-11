import os
from platform import machine
from flask import Flask, flash, request, redirect, url_for,render_template, get_flashed_messages
from werkzeug.utils import secure_filename
import sqlite3
from datetime import datetime
UPLOAD_FOLDER = 'D:\Test'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///query.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'lolthiskey'
database = sqlite3.connect('query.db', check_same_thread=False)
cursor = database.cursor()



def query_len():
    return len(os.listdir(UPLOAD_FOLDER))

def allowed_laser(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'dxf'
def allowed_3d(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['stl','obj']
@app.route('/')
def index():
    return render_template('index.html', query_len=query_len())
@app.route("/test" , methods=['GET', 'POST'])
def test():
    if request.method == 'POST':
        machine_type = request.form.get('machine-select')
        print(machine_type)
        return(str(machine_type))
    return render_template('test.html')
@app.route('/complete')
def upload_succesful():
    return '''
    <!doctype html>
    <title>Загрузка файлов</title>
    <h1>Ваш файл принят в очередь</h1>
    <h2>В очереди {} файлов</h2>
    '''.format(query_len())

@app.route('/laser_upload', methods=['GET', 'POST'])
def laser_upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            print(request.files)
            return redirect(request.url)
        file = request.files['file']
        material = request.form.get('material')
        thickness = request.form.get('thickness')
        pieces = request.form.get('pieces')
        print(file,material,thickness,pieces)
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_laser(file.filename):
            filename = secure_filename(file.filename)
            try:
                cursor.execute('''INSERT INTO laser(material, thick, pieces)
                              VALUES({0},{1},{2})
                '''.format(material,thickness,pieces))
                id = cursor.lastrowid
                database.commit()
                os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'],'\laser\{}\\'.format(id)))
                file.save(os.path.join(app.config['UPLOAD_FOLDER'],'\laser\{}\\'.format(id), filename))
                flash('Загружено успешно, номер заказа {}'.format(id))
            except Exception as e: 
                print(e)
                flash(e)
    return render_template('laser_upload.html')
@app.route('/print_upload', methods=['GET', 'POST'])
def print_upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        machine = request.form['machine']
        thickness = request.form['thickness']
        pieces = request.form['pieces']
        
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_3d(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'+r'\print'], filename))
            return 
    return render_template('print_upload.html')
    '''
    <!doctype html>
    <title>Загрузка файлов</title>
    <h1>Загрузите деталь</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=Файл>
      <input type=submit value=Загрузить>
    </form>
    '''

if __name__ == '__main__':


    app.debug = True
    app.run()
