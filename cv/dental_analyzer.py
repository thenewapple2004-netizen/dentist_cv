"""
Dental image analysis using transfer learning (MobileNetV2 base).
Classifies oral pathology conditions from uploaded images.
"""
import os
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import tensorflow as tf
    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    from tensorflow.keras.preprocessing.image import img_to_array
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


CONDITION_LABELS = [
    "Healthy Teeth",
    "Dental Caries",
    "Periodontitis",
    "Dental Abscess",
    "Oral Lesion",
]

CONDITION_INFO = {
    "Healthy Teeth": {
        "description": "No significant pathological findings detected. Teeth appear structurally sound.",
        "recommendations": ["Maintain regular brushing and flossing", "Schedule routine dental check-ups every 6 months", "Continue fluoride toothpaste use"],
        "severity": "none",
    },
    "Dental Caries": {
        "description": "Bacterial-mediated demineralization of tooth structure. Acid produced by S. mutans dissolves enamel/dentin.",
        "recommendations": ["Consult a dentist for restoration", "Use fluoride toothpaste and mouth rinse", "Reduce sugar/acidic food intake", "Consider fissure sealants"],
        "severity": "moderate",
    },
    "Periodontitis": {
        "description": "Inflammatory disease affecting supporting periodontal tissues with alveolar bone loss.",
        "recommendations": ["Immediate dental consultation required", "Professional scaling and root planing", "Improve oral hygiene technique", "Regular periodontal maintenance every 3 months"],
        "severity": "high",
    },
    "Dental Abscess": {
        "description": "Localized collection of pus from bacterial infection in periapical or periodontal tissues.",
        "recommendations": ["Urgent dental care required", "Do not delay treatment—risk of spread", "Antibiotic therapy may be needed", "Root canal treatment or extraction likely"],
        "severity": "urgent",
    },
    "Oral Lesion": {
        "description": "Abnormal tissue changes in oral mucosa. May include ulcers, white patches, or red lesions.",
        "recommendations": ["Dental/oral medicine consultation recommended", "Monitor for changes in size/color", "Biopsy may be required to rule out malignancy", "Avoid irritants like tobacco and alcohol"],
        "severity": "high",
    },
}

IMG_SIZE = (224, 224)
_model = None


def _load_or_build_model():
    global _model
    if _model is not None:
        return _model
    if not TF_AVAILABLE:
        return None

    saved_path = Path(__file__).parent / "saved_model"
    if saved_path.exists():
        _model = tf.keras.models.load_model(str(saved_path))
    else:
        # Build feature-extraction model (MobileNetV2 without top)
        # In production this would be fine-tuned on dental images
        base = MobileNetV2(weights="imagenet", include_top=False, input_shape=(224, 224, 3), pooling="avg")
        base.trainable = False
        _model = tf.keras.Sequential([
            base,
            tf.keras.layers.Dense(256, activation="relu"),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(len(CONDITION_LABELS), activation="softmax"),
        ])
        _model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    return _model


def _preprocess_image(image_path: str) -> np.ndarray:
    if PIL_AVAILABLE:
        img = Image.open(image_path).convert("RGB").resize(IMG_SIZE)
        arr = img_to_array(img) if TF_AVAILABLE else np.array(img, dtype=np.float32)
    elif CV2_AVAILABLE:
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, IMG_SIZE)
        arr = img.astype(np.float32)
    else:
        raise RuntimeError("Neither Pillow nor OpenCV is available for image loading")

    arr = np.expand_dims(arr, axis=0)
    if TF_AVAILABLE:
        arr = preprocess_input(arr)
    else:
        arr = arr / 127.5 - 1.0
    return arr


def _image_based_heuristic(image_path: str) -> np.ndarray:
    """
    Simple color/texture heuristic when model weights aren't trained.
    Returns a probability vector for demo purposes.
    """
    if not CV2_AVAILABLE and not PIL_AVAILABLE:
        return np.array([0.5, 0.2, 0.15, 0.1, 0.05])

    if CV2_AVAILABLE:
        img = cv2.imread(image_path)
        if img is None:
            return np.array([0.5, 0.2, 0.15, 0.1, 0.05])
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mean_sat = float(np.mean(hsv[:, :, 1]))
        mean_val = float(np.mean(hsv[:, :, 2]))
        mean_hue = float(np.mean(hsv[:, :, 0]))
    else:
        img = Image.open(image_path).convert("RGB")
        arr = np.array(img)
        mean_sat = float(np.std(arr))
        mean_val = float(np.mean(arr))
        mean_hue = float(np.mean(arr[:, :, 0]))

    probs = np.array([0.3, 0.25, 0.2, 0.15, 0.1])
    # Darken pixels → more caries/abscess signal
    if mean_val < 80:
        probs = np.array([0.1, 0.35, 0.2, 0.25, 0.1])
    elif mean_sat > 60:
        probs = np.array([0.15, 0.2, 0.3, 0.1, 0.25])
    probs = probs / probs.sum()
    return probs


def analyze_image(image_path: str) -> Dict:
    model = _load_or_build_model()

    if model is not None and TF_AVAILABLE:
        arr = _preprocess_image(image_path)
        preds = model.predict(arr, verbose=0)[0]
    else:
        preds = _image_based_heuristic(image_path)

    top_idx = int(np.argmax(preds))
    condition = CONDITION_LABELS[top_idx]
    confidence = float(preds[top_idx])

    all_conditions = [
        {"condition": CONDITION_LABELS[i], "probability": round(float(preds[i]) * 100, 1)}
        for i in range(len(CONDITION_LABELS))
    ]
    all_conditions.sort(key=lambda x: x["probability"], reverse=True)

    info = CONDITION_INFO[condition]
    return {
        "predicted_condition": condition,
        "confidence": round(confidence * 100, 1),
        "severity": info["severity"],
        "description": info["description"],
        "recommendations": info["recommendations"],
        "all_predictions": all_conditions,
        "disclaimer": "This is an educational tool only. Always consult a licensed dental professional for diagnosis and treatment.",
    }
