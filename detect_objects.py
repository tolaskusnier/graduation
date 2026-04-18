#model deteksi
from imageai.Detection import ObjectDetection

def detect(input_image, output_image, model_path):
    # img = None  # ✅ always defined
    detector = ObjectDetection()
    detector.setModelTypeAsYOLOv3()
    detector.setModelPath(model_path)
    detector.loadModel()

    detections = detector.detectObjectsFromImage(
        input_image=input_image,
        output_image_path=output_image,
        minimum_percentage_probability=30
    )

    return detections