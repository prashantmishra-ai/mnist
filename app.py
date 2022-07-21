from flask import Flask, render_template, redirect, flash, request
import os
import requests
from PIL import Image
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']
UPLOADS_FOLDER = 'uploads/images/'
def file_valid(file):
    return '.' in file and \
        file.rsplit('.',1)[1] in ALLOWED_EXTENSIONS
app = Flask(__name__)
app.config['SECRET_KEY'] = 'asldjbsanfjikbwodlakn123!@'
app.config['UPLOADS_FOLDER'] = UPLOADS_FOLDER
import PIL
def score_model(dataset):
  url = 'https://adb-2545852770213014.14.azuredatabricks.net/model/mnist_tf/1/invocations'
  os.environ["DATABRICKS_TOKEN"] = "dapif1f996267465ffc54c20b3736ad61a12-2"
  headers = {'Authorization': f'Bearer {os.environ.get("DATABRICKS_TOKEN")}'}
  data_json = {'inputs' : dataset}
  response = requests.request(method='POST', headers=headers, url=url, json=data_json)
  if response.status_code != 200:
    raise Exception(f'Request failed with status {response.status_code}, {response.text}')
  return response.json()
import numpy as np
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template('index.html')
    if not 'file' in request.files:
        flash('No file part in request')
        return redirect(request.url)
    file = request.files.get('file')
    if file.filename == '':
        flash('No file Uploaded')
        return redirect(request.url)
    if file_valid(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOADS_FOLDER'],filename))
        file_path = os.path.join(app.config['UPLOADS_FOLDER'],filename)
        original = Image.open(file_path).convert('L')
        print(np.array(original))
        resized = original.resize((28,28))
        newimg = np.array(resized)/(255.0)
        reimg = newimg.reshape(-1)
        dataset = reimg.tolist()
        output = score_model([dataset])[0]
        final = output.index(max(output))
        return render_template('index.html', message=final)
    return render_template('index.html')
