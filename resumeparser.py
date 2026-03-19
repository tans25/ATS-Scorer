import pdfplumber 
import os 



class ResumeParser:
    def __init__(self, file_path):
        self.file_path = file_path
        
    def resume_text_extractor(self):
        result = {}
        try:
            text = ''
            with pdfplumber.open(self.file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            result = {"success":True, "text": text}
        except Exception as e:
            result = {"success":False, "message":"Something went wrong"}
        return result 

    def parse_resume(self):
        result = {}
        try: 
            if not os.path.exists(self.file_path):
                return {"success":False, "message":"File not found"}
            ext = os.path.splitext(self.file_path)[-1].lower()
            if ext == ".pdf":
                result = self.resume_text_extractor()
            else:
                return {"success":False, "message":"File type not supported"}
        except Exception as e:
            result = {"success":False, "message":"Something went wrong"}
        return result 
