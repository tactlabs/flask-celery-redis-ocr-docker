import logging
import os
import uuid
import yaml
from collections import Counter
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from werkzeug.utils import secure_filename

from celery.result import AsyncResult
from celery.utils.log import get_task_logger
from flask import Flask, redirect, render_template, request, send_from_directory, jsonify
from flask_celery import make_celery

from pytesseract import image_to_string
from PIL import Image

config_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, "config.yml"))
config = yaml.load(open(config_path))

app = Flask(__name__)
app.config.update(config)

celery = make_celery(app)

logger = logging.getLogger(__name__)
celery_logger = get_task_logger(__name__)

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(app.config['LOGFILE'])
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)


def set_logger(logger):
    """Setup logger."""
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


logger = set_logger(logger)
celery_logger = set_logger(celery_logger)


@app.route('/')
def index():
    """Start page."""
    return render_template('index.html')


def allowed_file(filename):
    """Check format of the file."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/upload', methods=['POST'])
def upload():
    """Upload file endpoint."""
    if request.method == 'POST':
        if not request.files.get('file', None):
            msg = 'the request contains no file'
            logger.error(msg)
            return render_template('exception.html', text=msg)

        file = request.files['file']
        if file and not allowed_file(file.filename):
            msg = f'the file {file.filename} has wrong extention'
            logger.error(msg)
            return render_template('exception.html', text=msg)

        path = os.path.abspath(os.path.join(
            os.getcwd(), os.pardir, app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
        filename, file_extension = os.path.splitext(path)

        # Set the uploaded file a uuid name
        #filename_uuid = str(uuid.uuid4()) + file_extension
        filename_uuid = 'one' + file_extension
        logger.info(f' filename_uuid: {filename_uuid}')
        path_uuid = os.path.abspath(os.path.join(os.getcwd(), os.pardir, app.config['UPLOAD_FOLDER'], filename_uuid))

        file.save(path_uuid)
        #file.save('one.png')
        logger.info(f'the file {file.filename} has been successfully saved as {filename_uuid}')
        
        #return redirect('/process/' + filename_uuid)

        task = processing.delay(filename_uuid)

        result = {
            'taskid' : task.task_id
        }

        return jsonify(result)


@app.route('/process/<taskid>')
def task_processing(taskid):
    """Process the image endpoint."""

    async_result = AsyncResult(id=taskid, app=celery)
    content = async_result.get()

    logger.info(f' content {content}')

    result = {
        'taskid' : taskid,
        'status' : async_result.state,
        'content' : content
    }

    return jsonify(result)


@app.route('/result/<filename>')
def send_image(filename):
    """Show result endpoint."""
    return send_from_directory(os.path.abspath(os.path.join(os.getcwd(), os.pardir, app.config['RESULT_FOLDER'])),
                               filename)


def rgb2hex(rgb):
    """Convert color code from RGB to HEX."""
    hex_code = "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    return hex_code


@celery.task(name='celery.processing')
def processing(filename):
    """Celery function for the image processing."""

    filename_uuid = 'one.jpg'
    path_uuid = os.path.abspath(os.path.join(os.getcwd(), os.pardir, app.config['UPLOAD_FOLDER'], filename_uuid))

    content = image_to_string(Image.open(path_uuid))

    logger.info(f' content {content}')
    
    return content


if __name__ == "__main__":
    app.run(host="0.0.0.0")


'''
    Sources:
        https://stackoverflow.com/questions/30753040/retrieve-task-result-by-id-in-celery
'''