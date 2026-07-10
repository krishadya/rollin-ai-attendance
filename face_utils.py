import cv2
from pathlib import Path

FACES_DIR = Path("data/faces")
FACES_DIR.mkdir(parents=True, exist_ok=True)


def capture_face_image(student_identifier):
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        return None, "Could not open webcam."

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return None, "Could not capture image."

    image_path = FACES_DIR / f"{student_identifier}.jpg"
    cv2.imwrite(str(image_path), frame)

    return str(image_path), None