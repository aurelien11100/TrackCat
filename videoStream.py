import os
import cv2
import numpy as np
import tensorflow as tf

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

class VideoStream:
    def __init__(self, username, password, camera_ip, port=554):
        self.rtsp_url = f"rtsp://{username}:{password}@{camera_ip}:{port}/cam/realmonitor?channel=1&subtype=0"
        self.cap = cv2.VideoCapture(self.rtsp_url)

        # Chemins des fichiers nécessaires
        MODEL_NAME = 'ssd_mobilenet_v2_coco'
        CWD_PATH = os.getcwd()
        self.PATH_TO_CKPT = os.path.join(CWD_PATH, MODEL_NAME, 'frozen_inference_graph.pb')
        self.PATH_TO_LABELS = os.path.join(CWD_PATH, 'data', 'mscoco_label_map.pbtxt')

        # Nombre de classes que notre modèle peut détecter
        NUM_CLASSES = 90

        # Charger le modèle TensorFlow
        self.label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

        # Configurer la session TensorFlow
        self.config = tf.compat.v1.ConfigProto()
        self.config.gpu_options.per_process_gpu_memory_fraction = 0.2
        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(self.PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')
            self.sess = tf.compat.v1.Session(graph=self.detection_graph, config=self.config)

        # Déclaration des variables pour le graphe
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')

    def gen_frames(self):
        if not self.cap.isOpened():
            print("Erreur: Impossible de se connecter à la caméra.")
            return

        while True:
            success, frame = self.cap.read()
            if not success:
                break

            frame_expanded = np.expand_dims(frame, axis=0)
            (boxes, scores, classes, num) = self.sess.run(
                [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
                feed_dict={self.image_tensor: frame_expanded})

            vis_util.visualize_boxes_and_labels_on_image_array(
                frame,
                np.squeeze(boxes),
                np.squeeze(classes).astype(np.int32),
                np.squeeze(scores),
                self.category_index,
                use_normalized_coordinates=True,
                line_thickness=2,
                min_score_thresh=0.25)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
