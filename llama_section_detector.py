from llama_cloud import LlamaCloud
import os 

class LlamaResumeSectionDetector:
    def __init__(self):
        self.client = LlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY"))
    
    def parse_markdown_sections(self, markdown_text):
        HEADER_MAP = {
            "summary":            "summary",
            "experience":         "experience",
            "project highlights": "projects",
            "projects":           "projects",
            "skills":             "skills",
            "education":          "education",
            "certifications":     "certifications",
            "extracurricular":    "extracurricular",
        }
        sections = {}
        current_header = "other"
        current_lines = []
        for line in markdown_text.split("\n"):
            if line.startswith("## "):
                if current_lines:
                    sections[current_header] = "\n".join(current_lines).strip()
                raw_header = line.replace("## ", "").strip().lower()
                current_header = HEADER_MAP.get(raw_header, raw_header)
                current_lines = []
            else:
                current_lines.append(line)

        if current_lines:
            sections[current_header] = "\n".join(current_lines).strip()

        return sections

    
    def detect_sections(self, file_path): 
        file = self.client.files.create(file=file_path, purpose="parse")
        result = self.client.parsing.parse(
            file_id=file.id, 
            tier="agentic",
            version="latest",
            expand=["markdown"]
        )
        resume_sections = result.markdown.pages[0].markdown
        sections = self.parse_markdown_sections(resume_sections)
        return sections

