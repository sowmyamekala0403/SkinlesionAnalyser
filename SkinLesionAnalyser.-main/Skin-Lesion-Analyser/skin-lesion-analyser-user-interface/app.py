import os
import base64
from flask import Flask, render_template, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename


# # Inference should use the config with parameters that are used in training
from detectron2 import model_zoo
from detectron2.engine import DefaultTrainer
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.utils.visualizer import ColorMode
import matplotlib.pyplot as plt
from detectron2.utils.visualizer import Visualizer
import cv2
import pickle

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-InstanceSegmentation/mask_rcnn_X_101_32x8d_FPN_3x.yaml"))
cfg.MODEL.WEIGHTS = "/home/harinath/Documents/SkinCancerDetectron/model_final.pth"  # initialize from model zoo
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 2  
cfg.MODEL.DEVICE = 'cpu'

# # cfg now already contains everything we've set previously. We changed it a little bit for inference:
# cfg.MODEL.WEIGHTS = "../input/d/sashikanthreddy/skin-models/models/model_0019999.pth"  # path to the model we just trained
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5 # set a custom testing threshold
predictor = DefaultPredictor(cfg)
count = 0
def predict(filepath):
    # from detectron2.utils.visualizer import ColorMode
    with open('/home/harinath/Documents/SkinCancerDetectron/region_metadata.pkl', 'rb') as f:
        loaded_data = pickle.load(f)
    im = cv2.imread(filepath)
    # f_name=d["file_name"].split("/")[-1]
    outputs = predictor(im)  # format is documented at https://detectron2.readthedocs.io/tutorials/models.html#model-output-format
    v = Visualizer(im[:, :, ::-1],
                metadata=loaded_data, 
                scale=1, 
                instance_mode=ColorMode.SEGMENTATION   # remove the colors of unsegmented pixels. This option is only available for segmentation models
    )
    out = v.draw_instance_predictions(outputs["instances"].to("cpu"))
    image_path = os.path.join('/home/harinath/Documents/SkinCancerDetectron/predictions', f'predicted_image_{filepath.split("uploads/")[1]}')
    cv2.imwrite(image_path, out.get_image()[:, :, ::-1])
    

    return image_path

app = Flask(__name__)

# Define the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

count = 0
def save_file(file,count):
  """
  Saves the uploaded file to the uploads directory.

  Args:
      file (werkzeug.datastructures.FileStorage): Uploaded file object.

  Returns:
      str: Filename or None if there's an error.
  """
  if not file:
    return None
  count+=1
  filepath = os.path.join('./uploads', str(count))
  try:
    file.save(filepath)
    return filepath
  except Exception as e:
    print(f"Error saving file: {e}")
    return None


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file:
        # Save the uploaded file
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        # Make prediction
        prediction_path = predict(file_path)

        with open(prediction_path, 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

        # Return the result (including analyzed image)
        return jsonify({'analyzed_image': encoded_image})

if __name__ == '__main__':
    app.run(debug=True)
