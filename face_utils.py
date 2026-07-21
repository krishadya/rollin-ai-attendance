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

    except Exception as error:
        return None, str(error)


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def generate_embedding_from_image(image_path):
    try:
        result = DeepFace.represent(
            img_path=str(image_path),
            model_name="Facenet",
            detector_backend="mtcnn",
            enforce_detection=True
        )

        embedding = np.array(result[0]["embedding"])
        return embedding, None

    except Exception as error:
        return None, str(error)


def recognize_face(image_path, threshold=0.70):
    input_embedding, error = generate_embedding_from_image(image_path)

    if error:
        return None, error

    best_match = None
    best_score = -1

    for embedding_file in EMBEDDINGS_DIR.glob("*.npy"):
        saved_embedding = np.load(embedding_file)
        score = cosine_similarity(input_embedding, saved_embedding)

        if score > best_score:
            best_score = score
            best_match = embedding_file.stem

    if best_match is None:
        return None, "No registered faces found."

    confidence = round(best_score * 100, 2)

    if best_score >= threshold:
        return {
            "student_id": best_match,
            "score": best_score,
            "confidence": confidence,
            "status": "recognized"
        }, None

    return {
        "student_id": best_match,
        "score": best_score,
        "confidence": confidence,
        "status": "unknown"
    }, None
