from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_text_similarity(resume_text, job_description):
    """
    Calculate TF-IDF cosine similarity between resume and job description.

    Returns a score from 0 to 100.
    """

    resume_text = (resume_text or "").strip()
    job_description = (job_description or "").strip()

    if not resume_text or not job_description:
        return 0.0

    documents = [resume_text, job_description]

    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))

    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
    except ValueError:
        return 0.0

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

    return round(float(similarity) * 100, 2)
