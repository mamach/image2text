from flask import Flask, request, redirect, url_for, jsonify
import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import optparse
import time
from werkzeug.datastructures import ImmutableMultiDict
import pdb
import requests 
from werkzeug.utils import secure_filename

from constants import VALID_IMAGE_EXTENSIONS, WINDOWS_CHECK_COMMAND, DEFAULT_CHECK_COMMAND, TESSERACT_DATA_PATH_VAR

UPLOAD_FOLDER = '/projects/image2text_mine/uploads'
# UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

start = int(round(time.time()))

@app.route("/")
def hello_world():
    return "Hello world mahesh chandra"

@app.route('/snip', methods=['POST'])
def snip():
  if request.method == 'POST':
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return smartExtract(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename)

def smartExtract(filename, image_file_name):
    pdb.set_trace()
    return run_tesseract(filename, 'output_path', image_file_name)

def create_directory(path):
    """
    Create directory at given path if directory does not exist
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


def check_path(path):
    """
    Check if file path exists or not
    :param path:
    :return: boolean
    """
    return bool(os.path.exists(path))


def get_command():
    """
    Check OS and return command to identify if tesseract is installed or not
    :return:
    """
    if sys.platform.startswith('win'):
        return WINDOWS_CHECK_COMMAND
    return DEFAULT_CHECK_COMMAND


def run_tesseract(filename, output_path, image_file_name):
    pdb.set_trace()
    # Run tesseract
    filename_without_extension = os.path.splitext(filename)[0]
    # If no output path is provided
    pdb.set_trace()
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, filename_without_extension)
    pdb.set_trace()
    subprocess.run(['tesseract', image_file_name, temp_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with open('{}.txt'.format(temp_file), 'r', encoding="utf8") as f:
        text = f.read()
    shutil.rmtree(temp_dir)
    return text


def check_pre_requisites_tesseract():
    """
    Check if the pre-requisites required for running the tesseract application are satisfied or not
    :param : NA
    :return: boolean
    """
    check_command = get_command()
    logging.debug("Running `{}` to check if tesseract is installed or not.".format(check_command))

    result = subprocess.run([check_command, 'tesseract'], stdout=subprocess.PIPE)
    if not result.stdout:
        logging.error("tesseract-ocr missing, install `tesseract` to resolve. Refer to README for more instructions.")
        return False
    logging.debug("Tesseract correctly installed!\n")

    if sys.platform.startswith('win'):
        environment_variables = os.environ
        logging.debug(
            "Checking if the Tesseract Data path is set correctly or not.\n")
        if TESSERACT_DATA_PATH_VAR in environment_variables:
            if environment_variables[TESSERACT_DATA_PATH_VAR]:
                path = environment_variables[TESSERACT_DATA_PATH_VAR]
                logging.debug("Checking if the path configured for Tesseract Data Environment variable `{}` \
                as `{}` is valid or not.".format(TESSERACT_DATA_PATH_VAR, path))
                if os.path.isdir(path) and os.access(path, os.R_OK):
                    logging.debug("All set to go!")
                    return True
                else:
                    logging.error(
                        "Configured path for Tesseract data is not accessible!")
                    return False
            else:
                logging.error("Tesseract Data path Environment variable '{}' configured to an empty string!\
                ".format(TESSERACT_DATA_PATH_VAR))
                return False
        else:
            logging.error("Tesseract Data path Environment variable '{}' needs to be configured to point to\
            the tessdata!".format(TESSERACT_DATA_PATH_VAR))
            return False
    else:
        return True


def main(input_path, output_path):
    # Check if tesseract is installed or not
    if not check_pre_requisites_tesseract():
        return

    # Check if a valid input directory is given or not
    if not check_path(input_path):
        logging.error("Nothing found at `{}`".format(input_path))
        return

    # Create output directory
    if output_path:
        create_directory(output_path)
        logging.debug("Creating Output Path {}".format(output_path))

    # Check if input_path is directory or file
    if os.path.isdir(input_path):
        logging.debug("The Input Path is a directory.")
        # Check if input directory is empty or not
        total_file_count = len(os.listdir(input_path))
        if total_file_count == 0:
            logging.error("No files found at your input location")
            return

        # Iterate over all images in the input directory
        # and get text from each image
        other_files = 0
        successful_files = 0
        logging.info("Found total {} file(s)\n".format(total_file_count))
        for ctr, filename in enumerate(os.listdir(input_path)):
            logging.debug("Parsing {}".format(filename))
            extension = os.path.splitext(filename)[1]

            if extension.lower() not in VALID_IMAGE_EXTENSIONS:
                other_files += 1
                continue

            image_file_name = os.path.join(input_path, filename)
            print(run_tesseract(filename, output_path, image_file_name))
            successful_files += 1

        logging.info("Parsing Completed!\n")
        if successful_files == 0:
            logging.error("No valid image file found.")
            logging.error("Supported formats: [{}]".format(
                ", ".join(VALID_IMAGE_EXTENSIONS)))
        else:
            logging.info(
                "Successfully parsed images: {}".format(successful_files))
            logging.info(
                "Files with unsupported file extensions: {}".format(other_files))

    else:
        filename = os.path.basename(input_path)
        logging.debug("The Input Path is a file {}".format(filename))
        print(run_tesseract(filename, output_path, input_path))


if __name__ == '__main__':
    parser = optparse.OptionParser(usage="python main.py -p ")
    parser.add_option('-p', '--port', action='store', dest='port', help='The port to listen on.')
    app.run(host='0.0.0.0', port=8000, debug=True)

