from pathlib import Path
import numpy as np
from deepface import DeepFace

FACES_DIR = Path("data/faces")
EMBEDDINGS_DIR = Path("data/embeddings")

FACES_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)


def save_face_embedding(student_identifier):
    image_path = FACES_DIR / f"{student_identifier}.jpg"
    embedding_path = EMBEDDINGS_DIR / f"{student_identifier}.npy"

    if not image_path.exists():
        return None, "Face image not found."

    try:
        result = DeepFace.represent(
            img_path=str(image_path),
            model_name="Facenet",
            detector_backend="mtcnn",
            enforce_detection=True
    )

        embedding = np.array(result[0]["embedding"])
        np.save(embedding_path, embedding)

        return str(embedding_path), None

    except Exception as e:
        return None, str(e)