# compose_flask/app.py
import pytz
from flask_cors import CORS, cross_origin
import pymysql
import random
import string
from PIL import Image, ExifTags
from FaceSQL import FaceSQL
import os
import numpy as np
from flask import Flask, jsonify, request, redirect
import face_recognition
from flask import Flask
from redis import Redis
from dotenv import dotenv_values
from datetime import datetime
config = dotenv_values(".env")

app = Flask(__name__)
redis = Redis(host='redis', port=6379)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app = Flask(__name__, static_folder='pictures')
cors = CORS(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@app.route('/validate-face-preregister', methods=['POST'])
def validate_face():

    if 'file' not in request.files:
        return jsonify({"msg": "file_not_found"}), 422

    file_stream = request.files['file']

    if file_stream.filename == '':
        return jsonify({"msg": "file_not_found"}), 422

    image = Image.open(file_stream)
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] == 'Orientation':
            break

    exif = image._getexif()

    if exif:
        if exif[orientation] == 3:
            image = image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            image = image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            image = image.rotate(90, expand=True)

    newFile = "./pictures/"+file_stream.filename
    image.save(fp=newFile)

    image = face_recognition.load_image_file(newFile)

    image_face_encoding = face_recognition.face_encodings(image)

    os.remove(newFile)

    if len(image_face_encoding) > 0:
        return jsonify({"msg": "face_found"})

    else:
        return jsonify({"msg": "face_not_found"}), 422


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "foor": "bar",
    })


@app.route('/register', methods=['POST'])
def upload_image_register():

    if 'picture' not in request.files:
        return jsonify({"msg": "file_not_found"}), 422

    if 'api_token_for_web' not in request.form:
        return jsonify({"msg": "authentication_failed"}), 422

    if 'upload_id' not in request.form:
        return jsonify({"msg": "upload_id_not_found"}), 422

    file = request.files['picture']
    upload_id = request.values['upload_id']
    api_token_for_web = request.values['api_token_for_web']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        image = Image.open(file)
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = image._getexif()

        if exif and orientation in exif:
            if exif[orientation] == 3:
                image = image.rotate(180, expand=True)
            elif exif[orientation] == 6:
                image = image.rotate(270, expand=True)
            elif exif[orientation] == 8:
                image = image.rotate(90, expand=True)

        newFile = "./pictures/"+file.filename
        image.save(fp=newFile)
        return register_face(newFile, api_token_for_web, upload_id)

    else:
        return jsonify({'msg': 'file not allowed'}), 422


def encoding_FaceStr(image_face_encoding):
    encoding__array_list = image_face_encoding.tolist()
    encoding_str_list = [str(i) for i in encoding__array_list]
    encoding_str = ','.join(encoding_str_list)
    return encoding_str


def register_face(file_stream, api_token_for_web, upload_id):

    try:
        facesql = FaceSQL()
    except pymysql.Error as e:
        print("could not open connection error pymysql %d: %s" %
              (e.args[0], e.args[1]))

    personal_access_token = facesql.getUserByToken(api_token_for_web)

    if (personal_access_token == False):
        return jsonify({"msg": "authentication_failed"}), 422

    funcionario = facesql.getFuncionarioByUserId(
        personal_access_token['tokenable_id'])

    if (funcionario == False):
        return jsonify({"msg": "funcionario_not_found"}), 422

    company_id = funcionario['company_id']
    user_id = funcionario['user_id']

    image = face_recognition.load_image_file(file_stream)

    image_face_encoding = face_recognition.face_encodings(image)

    os.remove(file_stream)

    if len(image_face_encoding) > 0:

        image_face_encoding = image_face_encoding[0]

        encoding_str = encoding_FaceStr(image_face_encoding)

        now = datetime.now(pytz.timezone('America/Sao_Paulo'))
        created_at = now.strftime('%Y-%m-%d %H:%M:%S')
        updated_at = now.strftime('%Y-%m-%d %H:%M:%S')

        payload = {
            'created_at': created_at,
            'updated_at': updated_at,
            'user_id': user_id,
            'encodings': encoding_str,
            'upload_id': upload_id,
            'company_id': company_id
        }

        facesql.saveFaceData(payload)

        return jsonify(payload)

    else:
        return jsonify({
            "error": True,
            "msg": "image_wihout_face"
        }), 422


@app.route('/recognizer', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return {'error': 'no_file'}

        file = request.files['file']

        if file.filename == '':
            return {'error': 'no_file_name'}

        if file and allowed_file(file.filename):

            image = Image.open(file)
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break

            exif = image._getexif()

            if exif:
                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)

            image.thumbnail((700, 700))

            newFile = "./pictures/"+file.filename
            image.save(newFile)
            return detect_faces_in_image(newFile)

        return {'error': 'file_not_allowed', 'file': file.filename}


def decoding_FaceStr(encoding_str):
    dlist = encoding_str.strip(' ').split(',')
    dfloat = list(map(float, dlist))
    face_encoding = np.array(dfloat)

    return face_encoding


def load_faceofdatabase():

    try:
        facesql = FaceSQL()
    except pymysql.Error as e:
        print("could not open connection error pymysql %d: %s" %
              (e.args[0], e.args[1]))

    face_encoding_strs = facesql.allFaceData()
    face_encodings = []
    usuarios = []

    for row in face_encoding_strs:
        face_encodings.append(decoding_FaceStr(row[4]))
        usuarios.append(row[2])

    return usuarios, face_encodings


def detect_faces_in_image(file_stream):
    try:
        facesql = FaceSQL()
    except pymysql.Error as e:
        print("could not open connection error pymysql %d: %s" %
              (e.args[0], e.args[1]))

    responseAll = load_faceofdatabase()

    all_face_encodings = responseAll[1]
    user_ids = responseAll[0]

    img = face_recognition.load_image_file(file_stream)
    unknown_face_encodings = face_recognition.face_encodings(img)

    if len(unknown_face_encodings) < 1:
        return jsonify({"msg": "face_not_found_on_file"}), 422

    if len(unknown_face_encodings) > 1:
        return jsonify({"msg": "too_many_faces"}), 422

    match_results = face_recognition.face_distance(
        all_face_encodings, unknown_face_encodings[0])

    os.remove(file_stream)


    for i, face_distance in enumerate(match_results):
        if (face_distance <= 0.42):
            user_id = user_ids[i]
            facial_exists = facesql.getFaceByUserId(user_id)
            users_exists = facesql.getUserById(user_id)
            upload_exists = facesql.getUploadById(facial_exists["upload_id"])
            funcionario = facesql.getFuncionarioByUserId(user_id)

            if (facial_exists and users_exists and funcionario):
                payload = {
                    "user_id": facial_exists["user_id"],
                    "face_distance": face_distance,
                    "name": users_exists["name"],
                    "email": users_exists["email"],
                    "picture_url": "https://educacao-caucaia.sfo3.digitaloceanspaces.com/" + upload_exists["file"]
                }

                if 'direction' in request.form:
                    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
                    created_at = now.strftime('%Y-%m-%d %H:%M:%S')
                    updated_at = now.strftime('%Y-%m-%d %H:%M:%S')

                    payloadPresenca = {
                        'created_at': created_at,
                        'updated_at': updated_at,
                        'direction': request.values['direction'] or 1,
                        'company_id': funcionario['company_id'],
                        'funcionario_id': funcionario['id'],
                        'ponto': created_at,
                        'frequencia_id': None
                    }

                    facesql.savePresencaData(payloadPresenca)

                return jsonify(payload)
            else:
                return jsonify({"msg": "face_doesnt_have_a_user"}), 422

    return jsonify({"msg": "face_not_found_on_database"}), 422

 

@app.route('/recognizerDefault', methods=['POST'])
def register_ponto():

    try:
        facesql = FaceSQL()
    except pymysql.Error as e:
        print("could not open connection error pymysql %d: %s" %
              (e.args[0], e.args[1]))

    api_token_for_web = request.values['api_token_for_web']

    personal_access_token = facesql.getUserByToken(api_token_for_web)

    if (personal_access_token == False):
        return jsonify({"msg": "authentication_failed"}), 422

    funcionario = facesql.getFuncionarioByUserId(
        personal_access_token['tokenable_id'])

    if (funcionario == False):
        return jsonify({"msg": "funcionario_not_found"}), 422

    company_id = funcionario['company_id']
    user_id = funcionario['user_id']

    users_exists = facesql.getUserById(user_id)
    funcionario = facesql.getFuncionarioByUserId(user_id)

    if (users_exists and funcionario):
        payload = {
            "user_id": 0,
            "face_distance": 0,
            "name": users_exists["name"],
            "email": users_exists["email"],
            "picture_url": ""
        }

        if 'direction' in request.form:
            now = datetime.now(pytz.timezone('America/Sao_Paulo'))
            created_at = now.strftime('%Y-%m-%d %H:%M:%S')
            updated_at = now.strftime('%Y-%m-%d %H:%M:%S')

            payloadPresenca = {
                'created_at': created_at,
                'updated_at': updated_at,
                'direction': request.values['direction'] or 1,
                'company_id': funcionario['company_id'],
                'funcionario_id': funcionario['id'],
                'ponto': created_at,
                'frequencia_id': None
            }

            facesql.savePresencaData(payloadPresenca)

        return jsonify(payloadPresenca)
            

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=('/root/ssl/cert.pem', '/root/ssl/key.pem'))

