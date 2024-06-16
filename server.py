# app.py
from flask import Flask, Response
from video_stream import VideoStream

app = Flask(__name__)

# Informations de la caméra
username = "admin"  # Remplacez par votre nom d'utilisateur
password = "L2EC5D7F"  # Remplacez par votre mot de passe
camera_ip = "192.168.1.23"  # Remplacez par l'adresse IP de votre caméra

# Initialiser le flux vidéo
video_stream = VideoStream(username, password, camera_ip)


@app.route('/video_feed')
def video_feed():
    return Response(video_stream.gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>Live Stream</title>
    </head>
    <body>
        <h1>Live Stream</h1>
        <img src="/video_feed">
    </body>
    </html>
    '''


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
