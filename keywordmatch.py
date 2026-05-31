import re 
from rapidfuzz import fuzz 
from py2neo import Graph
from dotenv import load_dotenv
import os 

load_dotenv()

graph = Graph(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)

RELATION_WEIGHTS = {
    "ESSENTIAL": 0.9, 
    "OPTIONAL": 0.7
}

def get_related_skill(skill_name):
    query = """
            MATCH (s:Skill)-[r:ESSENTIAL|OPTIONAL*1..2]-(related:Skill)
            WHERE s.name = $name OR $name IN split(s.alt_labels, '|')
            RETURN related.name as name, 
            related.alt_labels as alts, 
            type(last(r)) as relation_type
            """
    try: 
        results = graph.run(query, name=skill_name.lower()).data()
        related = []
        for r in results:
            weight = RELATION_WEIGHTS.get(r["relation_type"], 0.7)
            alts = r["alts"].split("|") if r["alts"] else []
            related.append({
                "name": r["name"],
                "weight": weight,
                "alts": [a.strip() for a in alts]
            })
        return related 
    except Exception as e:
        print(e)
        return []

def fuzzy_match(skill, resume_text, threshold=85):
    skill_words = len(skill.split())
    resume_words = resume_text.split()
    for i in range(len(resume_words) - skill_words + 1):
        window = " ".join(resume_words[i:i+skill_words+1])
        if fuzz.partial_ratio(skill, window.lower()) >= threshold:
            return True 
    return False 


def is_skill_present(skill, resume_text):
    skill_lower = skill.lower()
    resume_lower = resume_text.lower()

    try:
        # Level 1: Exact search 
        if re.search(rf'\b{re.escape(skill_lower)}\b', resume_lower):
            return {"found": True, "match_type": "exact", "score": 1.0}
        
        # Level 2: ESCO Ontology match 
        related_skills = get_related_skill(skill_lower)
        if len(related_skills) != 0:
            for skill in related_skills:
                if re.search(rf'\b{re.escape(skill["name"])}\b', resume_lower):
                    return {"found": True, "match_type": "ontology", "score": skill["weight"]}
                
                for alt in skill["alts"]:
                    if re.search(rf'\b{re.escape(alt.lower())}\b', resume_lower):
                        return {"found": True, "match_type": "ontology_alt", "score": skill["weight"]}
        
        # Level 3: Fuzzy matching 
        fuzzy_matched = fuzzy_match(skill_lower, resume_lower)
        if fuzzy_matched:
            return {"found": True, "match_type": "fuzzy", "score": 0.6}
        
        return {"found": False, "match_type": "none", "score": 0}
    except Exception as e:
        print(e)
        return {"found": False, "match_type": "none", "score": 0}

def compute_keyword_score(resume_text, all_keywords):
    matched = []
    unmatched = []
    matched_score = 0 

    try:
        for kw in all_keywords:
            result = is_skill_present(kw['skill'], resume_text)
            entry = {
                **kw, 
                "match_score": result["score"],
                "match_type": result["match_type"]
            }
            if result["found"]:
                matched.append(entry)
            else:
                unmatched.append(entry)
        total= len(all_keywords)
        matched_score = round(sum(m["match_score"] for m in matched) / total * 100, 1) if total > 0 else 0.0  
    except Exception as e:
        print(e)
    result = {
        "score": matched_score,
        "matched": matched, 
        "unmatched": unmatched,
        "matched_count": len(matched),
        "unmatched_count": len(unmatched)
    }
    return result 
