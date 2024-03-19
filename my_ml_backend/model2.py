from typing import List, Dict, Optional
from label_studio_ml.model import LabelStudioMLBase
import cv2
import sys 
sys.path.append("./PaddleOCR")
from doctr.models import ocr_predictor
from doctr.io import DocumentFile
import os
from PIL import Image
import pandas as pd
import numpy as np
import requests
from io import BytesIO
import math


global_ocr_instance = ocr_predictor(
    # A sticking point 
    # Initialization of PaddleOCR parameters, here the model has been moved to the outside to avoid printing the model parameters each time it is loaded,
    # otherwise the entire page would be filled with model parameters.
    det_arch='db_resnet50', 
    reco_arch='crnn_vgg16_bn',
    pretrained = True, 
    assume_straight_pages=False,
    preserve_aspect_ratio=True, 
    # Other inference parameters need to be adjusted according to the situation.
)

class NewModel(LabelStudioMLBase):
    def __init__(self, project_id=None, **kwargs):
        super(NewModel, self).__init__(**kwargs)
        self.ocr = global_ocr_instance
        self.token = "376641251a1be5a6d94******5767b2113c1afe"

    def predict(self, tasks, **kwargs):
        results = []
        for task in tasks:
            """ Pitfall 2: Reading the image file. Although Label Studio and the template are on the same server, they use different ports. This results in:
            (1) When downloading images into Label Studio, it is not possible to load images directly from the template server directory;
            (2) The model backend cannot directly read images downloaded from Label Studio.  The directory of downloaded images directly displayed in the source 
            is '/data/upload/12/bf68a25f-0034.jpg', As a result, we've chosen to use queries to obtain the data. There's also a little catch here: 
            each account has a different token, which must be included in the query.
            """
            image_path = task['data']['ocr']
            image_url = "http://localhost:8080"+image_path
            image = self.load_image_from_url(image_url, self.token)
            # Processing images with an OCR template
            # ocr_results = self.ocr.ocr(np.array(image), cls=True)
            # Webpage
            webpage_doc = DocumentFile.from_url(image)
            ocr_results = self.ocr(webpage_doc)

            # Convert OCR results to the format required by Label Studio
            predictions = []
            """Pitfall 3: the ID must be included. As mentioned above, the OCR task has three results. Without the ID, the frontend will display three separate results."""
            ocr_id=0
            for result in ocr_results[0]:
                points, text_score = result
                text, score = text_score

                x,y, width, height, rotation = self.convert_points_to_relative_xywhr(points, np.array(image))
                """"Pitfall 4: The coordinates of the displayed area are not absolute pixel positions, but relative ones.
                Consequently, they must be converted into percentages and must be numbers between 0 and 100. 
                That's why there's a coordinate conversion function below."""

                # Labels component prediction.
                label_prediction = {
                    'from_name':'label',
                    'id':str(ocr_id),
                    'to_name':'image',
                    'type': 'labels',
                    'value':{
                        'x':x,
                        'y':y,
                        'width':width,
                        'height':height,
                        'roation':rotation
                        
                    }
                }

                # Prediction of rectangle component (TextArea)
                rectangle_prediction = {
                    'from_name': 'bbox',
                    'id':str(ocr_id),
                    'to_name':'image',
                    'type':'rectangle',
                    'value':{
                        'x':x,
                        'y':y,
                        'width':width,
                        'height':height,
                        'rotation':rotation,
                    }
                }

                # TextArea component prediction
                textarea_prediction = {
                    'from_name': 'transcription',
                    'id':str(ocr_id),
                    'to_name':'image',
                    'type':'textarea',
                    'value':{
                        'x':x,
                        'y':y,
                        'width':width,
                        'height':height,
                        'rotation':rotation,
                        'text':[text]
                    }
                }

                predictions.extend([label_prediction, rectangle_prediction, text_area_prediction])
                ocr_id += 1

            results.append({
                'result':predictions
            })

        return results

    def load_image_from_url(self, url, token):
        headers = {'Authorization': f"Token {token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            return image
        else:
            raise Exception(f"Error loading image from {url}")


    def convert_points_to_relative_xywhr(self, points, image):
        """
        Convert a list of points representing a rectangle to relative x, y, width, height and rotation.
        The values are relative to the dimensions of the given image. 

        Points are expected to be in the order: top-left, top-right, bottom-right, bottom-lef. 

        The rotation is calculated as the clockwise angle between the top edge and the horizontal line. 

        Args:
        - points (list of lists): A list of four points, each point is a list of two coordinates [x,y].
        - image (numpy array): An image array.

        Returns:
        - tuple: (x,y, width, height, rotation) where x and y are the relative coordinates of the top-left point, 
        width and height are the relative dimensions of the rectangle, and rotation is the angle in degrees.
        """
        # Extracting points
        top_left, top_right, bottom_right, bottom_left = points

        # Image dimensions
        img_height, img_width = image.shape[:2]

        # Calculate width and height of the rectangle
        width = math.sqrt((top_right[0]-top_left[0])**2 + (top_right[1] - top_left[1])**2)
        height = math.sqrt((bottom_right[0] - top_right[0])**2 + (bottom_right[1] - top_right[1])**2)

        # Calculate rotation in radians
        dx = top_right[0] - top_left[0]
        dy = top_right[1] - top_left[1]
        angle_radians = math.atan2(dy, dx)

        # Convert rotation to degrees
        rotation = math.degrees(angle_radians)

        # The top-left point is the origin (x,y)
        x, y = top_left

        # Convert dimensions to relative values (percentage of image dimensions)
        rel_x = x / img_width * 100
        rel_y = y / img_width * 100
        rel_width = width / img_width * 100
        rel_height = height / img_height * 100

        return rel_x, rel_y, rel_width, rel_height, rotation