from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

RELEVANT_SECTIONS = {"experience", "skills", "projects", "summary"}


def normalize_score(cosine_score):
    min_expected = 0.3
    max_expected = 0.85
    normalized = (cosine_score - min_expected) / (max_expected - min_expected)
    return round(float(np.clip(normalized * 100, 0, 100)), 1)


def compute_semantic_score(resume_sections, jd_text):
    section_texts = []
    section_names = []
    for name, text in resume_sections.items():
        if name.lower() in RELEVANT_SECTIONS and text.strip():
            section_texts.append(text.strip())
            section_names.append(name)

    if not section_texts:
        return {"score": 0.0, "section_scores": {}}

    section_embeddings = model.encode(section_texts)
    jd_embedding = model.encode([jd_text])

    similarities = cosine_similarity(section_embeddings, jd_embedding).flatten()

    section_scores = {
        section_names[i]: round(float(similarities[i]), 4)
        for i in range(len(section_names))
    }

    avg_cosine = float(np.mean(similarities))
    score = normalize_score(avg_cosine)

    return {"score": score, "section_scores": section_scores}