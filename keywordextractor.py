import os 
from huggingface_hub import InferenceClient
import re 
import ast 
import json
from dotenv import load_dotenv
load_dotenv()


class KeywordExtractor:
    def __init__(self):
      self.SYSTEM_PROMPT = """You are an expert ATS (Applicant Tracking System) analyst. 
       When given a job description, extract all important keywords and group them 
      into relevant categories that make sense for that specific job.

      You must respond ONLY with a valid JSON object — no preamble, no explanation, 
      no markdown code fences. Just raw JSON.

      Example structure (categories are flexible, use whatever fits the JD):
      {
        "category_name": ["skill1", "skill2"],
        "another_category": ["skill3"]
      }

      Rules:
      - Extract the core skill or technology name from each requirement - do not create skills where there are none for eg specific technology names 
      - Choose category names that are relevant to the job
      - Use common industry standard names for skills 
      - Include skills EXACLTLY as they appear in the job description
      - Do not invent or infer skills that are not present
      - Do NOT include work authorization, visa, location, or personal interests
      - Return only the skill names as plain strings
      - Keep category names lowercase with underscores
      - Return skill names as plain strings, no underscores
      """
      self.model = InferenceClient(
          model="Qwen/Qwen2.5-72B-Instruct",
          token = os.getenv("HF_TOKEN")
      )

    def compute_priority(self, frequency, category):
        soft_categories = {"qualifications", "education", "soft_skills"}
        if category not in "".join(soft_categories) and frequency >= 3:
            return "critical"
        elif frequency >= 1 and frequency < 3:
            return "moderate"
        else:
            return "nice_to_have"
            
    def get_keywords(self, jd_text):
        try:
          response = self.model.chat.completions.create(
              messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract keywords from this job description:\n\n{jd_text}"}
            ],
            max_tokens=1000,
          )
          raw = json.loads(response.choices[0].message.content.strip())
          jd_lower = jd_text.lower()
          result = []
          for category, skills in raw.items():
              for skill in skills:
                frequency = len(re.findall(rf'\b{re.escape(skill.lower())}\b', jd_lower))
                result.append({
                    "skill": skill,
                    "category": category,
                    "frequency": frequency,
                    "priority": self.compute_priority(frequency, category)
                })
          by_category_detailed = {}
          for kw in result:
              cat = kw["category"]
              if cat not in by_category_detailed:
                  by_category_detailed[cat] = []
              by_category_detailed[cat].append(kw)

          return {
              "success": True,
              "result":{
              "by_category": by_category_detailed,
              "all_keywords": result,
              "total_found": len(result)}
          }
        except Exception as e:
            print(e)
            return {"success": False, "message": "Something went wrong"}

