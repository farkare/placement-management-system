"""
Trains a small logistic regression model that predicts placement
"readiness" (probability of getting placed) from a student's stats.

We don't have a real historical placement dataset, so this generates a
synthetic-but-realistic one using a weighted rule + random noise, then
trains on it. This is a legitimate and common approach for a student ML
project when no real labeled dataset exists yet — swap in real data
later (e.g. last year's placement records) without changing any other
code, since only this file needs to change.

Run this once (see README) to produce readiness_model.joblib, which the
API loads at request time.
"""
import numpy as np
import joblib
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

MODEL_PATH = Path(__file__).parent / "readiness_model.joblib"
SCALER_PATH = Path(__file__).parent / "readiness_scaler.joblib"

FEATURES = ["cgpa", "backlogs", "internships", "certifications", "skill_count"]


def generate_synthetic_data(n=600, seed=42):
    rng = np.random.default_rng(seed)

    cgpa = np.clip(rng.normal(7.2, 1.0, n), 4.0, 10.0)
    backlogs = rng.poisson(0.5, n)
    internships = rng.poisson(0.7, n)
    certifications = rng.poisson(1.2, n)
    skill_count = rng.integers(1, 12, n)

    # weighted "true" score that placement tends to follow, plus noise
    score = (
        0.55 * (cgpa / 10)
        - 0.35 * (backlogs / 3)
        + 0.30 * np.tanh(internships / 2)
        + 0.20 * np.tanh(certifications / 3)
        + 0.25 * np.tanh(skill_count / 6)
        + rng.normal(0, 0.12, n)
    )
    placed = (score > np.median(score)).astype(int)

    X = np.column_stack([cgpa, backlogs, internships, certifications, skill_count])
    y = placed
    return X, y


def train_and_save():
    X, y = generate_synthetic_data()
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = LogisticRegression()
    model.fit(X_train_s, y_train)
    acc = model.score(X_test_s, y_test)
    print(f"Readiness model trained. Test accuracy: {acc:.2f}")

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"Saved model to {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save()
