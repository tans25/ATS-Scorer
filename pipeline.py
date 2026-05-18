from resumeparser import ResumeParser
from preprocessing import PreProcessor
from keywordextractor import KeywordExtractor
from keywordmatch import compute_keyword_score
from semanticscorer import compute_semantic_score


SEMANTIC_WEIGHT = 0.6
KEYWORD_WEIGHT = 0.4


def run_pipeline(resume_path, jd_text):
    try:
        raw_resume = ResumeParser(resume_path)
        resume_obj = raw_resume.parse_resume()
        if not resume_obj["success"]:
            return {"success": False, "message": resume_obj["message"]}

        resume_text = resume_obj["text"]
        resume_sections = resume_obj["resume_sections"]

        preprocessor_resume = PreProcessor(resume_text)
        clean_resume_full = preprocessor_resume.full_clean()

        preprocessor_jd = PreProcessor(jd_text)
        clean_jd_light = preprocessor_jd.clean_text()

        extractor = KeywordExtractor()
        keywords_result = extractor.get_keywords(jd_text)
        if not keywords_result["success"]:
            return {"success": False, "message": keywords_result["message"]}
        keywords_data = keywords_result["result"]

        keyword_result = compute_keyword_score(clean_resume_full, keywords_data["all_keywords"])

        semantic_result = compute_semantic_score(resume_sections, clean_jd_light)

        final_score = round(
            semantic_result["score"] * SEMANTIC_WEIGHT
            + keyword_result["score"] * KEYWORD_WEIGHT,
            1
        )

        result = {
            "final_score": final_score,
            "semantic_score": semantic_result["score"],
            "keyword_score": keyword_result["score"],
            "section_scores": semantic_result["section_scores"],
            "matched_keywords": keyword_result["matched"],
            "unmatched_keywords": keyword_result["unmatched"],
            "matched_count": keyword_result["matched_count"],
            "unmatched_count": keyword_result["unmatched_count"],
            "by_category": keywords_data["by_category"],
        }
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "message": "Something went wrong"}


