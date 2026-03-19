from resumeparser import ResumeParser
from preprocessing import PreProcessor

def run_pipeline(resume_path, jd_text):
    result = {}
    try:
        raw_resume = ResumeParser(resume_path)
        resume_obj = raw_resume.parse_resume()
        if resume_obj["success"]:
            resume_text = resume_obj["text"]
            preprocessor_resume = PreProcessor(resume_text)
            clean_resume_light = preprocessor_resume.clean_text()
            clean_resume_full = preprocessor_resume.full_clean()
        else:
            return {"success": False, "message": resume_obj["message"]}

        preprocessor_jd = PreProcessor(jd_text)
        clean_jd_light = preprocessor_jd.clean_text()
        clean_jd_full = preprocessor_jd.full_clean()

        result = {
            "resume_light": clean_resume_light,
            "resume_full": clean_resume_full,
            "jd_light": clean_jd_light,
            "jd_full": clean_jd_full
        }
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "message": "Something went wrong"}


