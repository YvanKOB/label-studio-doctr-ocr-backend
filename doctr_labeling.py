from urllib.parse import urlparse
from uuid import uuid4
from label_studio_ml.model import LabelStudioMLBase, ModelResponse
from label_studio_ml.utils import get_image_local_path, DATA_UNDEFINED_NAME
import logging
import boto3
from botocore.exceptions import ClientError
import os
import torch
from doctr.io import DocumentFile
from doctr.models import ocr_predictor, from_hub
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# Label Studio
LABEL_STUDIO_HOST = os.environ.get("LABEL_STUDIO_HOST", "http://0.0.0.0:8080")  # TODO: change me
LABEL_STUDIO_ACCESS_TOKEN = os.environ.get("LABEL_STUDIO_ACCESS_TOKEN", "6f206c188db5267cbd59bb8c7b3a7b3d41ed5890")  # TODO: change me

# S3 credentials
AWS_ENDPOINT_URL = os.environ.get('AWS_ENDPOINT_URL')
AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS = os.environ.get('AWS_SECRET_ACCESS')


class DoctrMLBackend(LabelStudioMLBase):

    predictor = ocr_predictor(
            det_arch="db_resnet50",
            # provides the largest covered vocabulary at the moment
            #reco_arch=from_hub("Felix92/doctr-torch-parseq-multilingual-v1"),
            reco_arch="parseq",
            det_bs=4,
            reco_bs=1024,
            assume_straight_pages=False,  # cover also rotated pages (range: -90 to 90 degrees)
            pretrained=True)
    predictor = predictor.cuda().half() if torch.cuda.is_available() else predictor

    @staticmethod
    def _get_image_url(image_url):
        if image_url.startswith('s3://'):
            r = urlparse(image_url, allow_fragments=False)
            bucket_name = r.netloc
            key = r.path.lstrip('/')
            client = boto3.client('s3',
                                  endpoint_url=AWS_ENDPOINT_URL,
                                  aws_access_key_id=AWS_ACCESS_KEY,
                                  aws_secret_access_key=AWS_SECRET_ACCESS,
                                  )
            try:
                image_url = client.generate_presigned_url(
                    ClientMethod='get_object',
                    Params={'Bucket': bucket_name, 'Key': key}
                )
            except ClientError as exc:
                logger.warning(f'Can\'t generate presigned URL for {image_url}. Reason: {exc}')
        return image_url

    def predict(self, tasks: List[Dict], context: Optional[Dict] = None, **kwargs):
        """
        Returns the list of predictions based on input list of tasks for 1 image
        """
        logger.info(f"Predicting {len(tasks)} tasks")
        logger.info(f"Context: {context}")
        if not context or not context.get('result'):
            return []

        # TODO: image loading broken
        task = tasks[0]
        self.from_name, self.to_name, self.value = self.get_first_tag_occurence('TextArea', 'Image')
        image_url = self._get_image_url(task['data'].get(self.value) or task['data'].get(DATA_UNDEFINED_NAME))
        img_path = get_image_local_path(
            image_url,
            label_studio_access_token=LABEL_STUDIO_ACCESS_TOKEN,
            label_studio_host=LABEL_STUDIO_HOST
        )

        # TODO: batch processing
        doc = DocumentFile.from_images([img_path])
        result = self.predictor(doc)
        logger.info(f"Predicted {len(result.pages)} pages")

        predictions = []

        for page in result.pages:

            label_studio_result_format = []
            h, w = page.dimensions
            confs = []
            for block in page.blocks:
                for line in block.lines:
                    for word in line.words:
                        confs.append(word.confidence)
                        coords = word.geometry
                        if len(coords) == 4:
                            x_coords = [coords[i] for i in range(0, len(coords), 2)]
                            y_coords = [coords[i] for i in range(1, len(coords), 2)]
                            points = [[x_coords[0], y_coords[0]], [x_coords[1], y_coords[1]], [x_coords[2], y_coords[2]], [x_coords[3], y_coords[3]]]
                        else:
                            (xmin, ymin), (xmax, ymax) = coords
                            points = [[xmin, ymin], [xmax, ymin], [xmax, ymax], [xmin, ymax]]

                        # Adding dict to prediction
                        # random ID
                        label_id = str(uuid4())[:9]
                        label_studio_result_format.append({
                        # must add one for the polygon
                            'original_width': w,
                            'original_height': h,
                            'image_rotation': 0,
                            'value': {
                                'points': points,
                            },
                            'id': label_id,
                            'from_name': self.from_name,
                            'to_name': self.to_name,
                            'type': 'polygon',
                            'origin': 'manual',
                            'score': word.confidence,
                        })
                        # and one for the transcription
                        label_studio_result_format.append({
                            'original_width': w,
                            'original_height': h,
                            'image_rotation': 0,
                            'value': {
                                'points': points,
                                'labels': ["Text"],
                                "text": [
                                    word.value
                                ]
                            },
                            'id': label_id,
                            'from_name': self.from_name,
                            'to_name': self.to_name,
                            'type': 'textarea',
                            'origin': 'manual',
                            'score': word.confidence,
                        })
            predictions.append({"result": label_studio_result_format, "score": sum(confs) / len(confs)})

        return ModelResponse(predictions=predictions)
