# video_stream.py
import cv2


class VideoStream:
    def __init__(self, username, password, camera_ip, port=554):
        self.rtsp_url = f"rtsp://{username}:{password}@{camera_ip}:{port}/cam/realmonitor?channel=1&subtype=0"
        self.cap = cv2.VideoCapture(self.rtsp_url)

    def gen_frames(self):
        if not self.cap.isOpened():
            print("Erreur: Impossible de se connecter à la caméra.")
            return
        while True:
            success, frame = self.cap.read()
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
