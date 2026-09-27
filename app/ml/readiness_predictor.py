from pathlib import Path
import joblib
import numpy as np

MODEL_PATH = Path(__file__).parent / "readiness_model.joblib"
SCALER_PATH = Path(__file__).parent / "readiness_scaler.joblib"

_model = None
_scaler = None


def _load():
    global _model, _scaler
    if _model is None or _scaler is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "readiness_model.joblib not found. Run "
                "`python -m app.ml.train_readiness_model` once from the backend/ folder first."
            )
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
    return _model, _scaler


def predict_readiness(cgpa: float, backlogs: int, internships: int, certifications: int, skill_count: int) -> float:
    model, scaler = _load()
    X = np.array([[cgpa, backlogs, internships, certifications, skill_count]])
    X_s = scaler.transform(X)
    prob = model.predict_proba(X_s)[0][1]  # probability of class "placed"
    return round(float(prob) * 100, 2)  # as a 0-100 score
