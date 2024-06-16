from flask import Flask, Response
from videoStream import VideoStream

app = Flask(__name__)

username = "admin"  # Remplacez par votre nom d'utilisateur
password = "L2EC5D7F"  # Remplacez par votre mot de passe
camera_ip = "192.168.1.23"  # Remplacez par l'adresse IP de votre caméra

video_stream = VideoStream(username, password, camera_ip)

@app.route('/video_feed')
def video_feed():
    return Response(video_stream.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
