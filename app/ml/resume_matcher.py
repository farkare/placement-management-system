"""
Resume <-> Job Description matching.

Approach: TF-IDF vectorization + cosine similarity. This is computed fresh
for every (resume_text, jd_text) pair — no persistent model needed, so
there's nothing to train or retrain as new drives/resumes come in.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def compute_match_score(resume_text: str, jd_text: str) -> float:
    resume_text = (resume_text or "").strip()
    jd_text = (jd_text or "").strip()

    if not resume_text or not jd_text:
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
    except ValueError:
        # happens if both texts are only stopwords / empty after cleaning
        return 0.0

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(similarity) * 100, 2)  # as a 0-100 score
