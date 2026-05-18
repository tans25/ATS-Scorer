import re 

def compute_keyword_score(resume_text, all_keywords):
    resume_lower = resume_text.lower()
    matched = []
    unmatched = []

    for kw in all_keywords:
        skill = kw['skill'].lower()
        found = bool(re.search(rf'\b{re.escape(skill)}\b', resume_lower))
        if found:
            matched.append(kw)
        else:
            unmatched.append(kw)
    total= len(all_keywords)
    matched_score = round((len(matched) / total)*100, 1) if total > 0 else 0.0 
    result = {
        "score": matched_score,
        "matched": matched, 
        "unmatched": unmatched,
        "matched_count": len(matched),
        "unmatched_count": len(unmatched)
    }

    return result