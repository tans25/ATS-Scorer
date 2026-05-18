import numpy as np 
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pickle 
from resumeparser import ResumeParser
from preprocessing import PreProcessor

model = SentenceTransformer("all-MiniLM-L6-v2")
ANCHORS = {
    "experience":     "work experience employment history job responsibilities achievements",
    "education":      "education academic background university degree graduation",
    "skills":         "technical skills tools programming languages frameworks",
    "projects":       "projects portfolio personal work open source built created",
    "summary":        "professional summary objective profile about me overview",
    "certifications": "certifications awards achievements licenses recognition",
    "other":          "miscellaneous additional information volunteer interests hobbies"
}

class ResumeSectionDetector:
    def __init__(self, text):
        self.section_classifier, self.label_encoder = self.load_models()
        self.text = text 

    def load_models(self):
        with open('models/resume_section_classifier.pkl', 'rb') as f:
            clf = pickle.load(f)
        with open('models/label_encoder.pkl', 'rb') as f:
            le = pickle.load(f)
        return clf, le 
    
    def clean_lines(self, text, chunk_size=15):
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            if len(chunk.strip()) > 20:
                chunks.append(chunk)
        return chunks 

    def embed_text(self, chunks):
        return model.encode(chunks, batch_size=32, show_progress_bar=False)
    
    def main(self):
        chunks = self.clean_lines(self.text)
        embeddings = self.embed_text(chunks)
        predictions = self.section_classifier.predict(embeddings)
        labels = self.label_encoder.inverse_transform(predictions)
        sections: dict[str, list[str]] = {}
        for chunk, label in zip(chunks, labels):
            if label not in sections:
                sections[label] = []
            sections[label].append(chunk)
        return {label: " ".join(chunks) for label, chunks in sections.items()}
    

# text = 'tanaya joshi   240 726 0166   college park  md 20740       tansjoshi25 gmail com        tanaya joshi       tans25  summary  aspiring data scientist with experience building end to end data driven applications using large datasets  skilled in  developing and deploying containerized solutions using docker  with a strong foundation in data processing and  analysis using python  experienced in building and automating data pipelines in distributed environments using apache  spark  and working with diverse databases including mongodb  mysql  and postgresql  proficient in machine learning  workflows  and developing restful apis using flask to serve data driven insights    experience  university of maryland college park   college of information  research assistant                                                                                                               jan 2026   present    developing a multimodal deep learning model  text   image  for narrative and frame analysis across 10 000  news  and social media posts  integrating vision language models  vlms  and pytorch for metaphor identification     fine tuned bert based llms for social discourse analysis  achieving improved metaphor detection accuracy for  large scale media perception studies      performed image processing on 60k images using vlms and generated textual description for each image     built a web scraping pipeline using beautifulsoup and python to collect and preprocess 50 000  media texts and  images for downstream natural language processing model training   ltimindtree limited  software engineer                                                                                                            june 2023   august 2025     built ml driven chaos engineering pipelines analyzing large scale server telemetry data  cpu  memory  disk  i o   reducing mean time to detect anomalies by  30  through real time alerting  automated highlights  and interactive  data visualisations      applied statistical methods to perform post attack system behavior analysis and used encoder based ml models to  identify anomalies  failure patterns  and performance degradation in distributed server environments reducing  false positive alert rate by 20     developed and deployed restful apis with flask to display system monitoring and analytics for internal dashboards by  leveraging oop and data structure concepts for efficient data handling  manipulation  and api call infrastructure      integrated prometheus  loki  and grafana to collect and visualize real time infrastructure metrics across distributed  services hosted both on and off premises      designed data processing pipelines using apache spark to analyze large infrastructure logs stored in aws s3 and  generate system health reports  improving operational insights    contributed to gitlab ci cd pipelines for automated build  test  and deployment of java backend microservices in  containerized environments  improving release reliability   project highlights  analysis of public framing and perception of ai  on going       developed ml and nlp models to extract metaphors from news media  leveraging multimodal approaches  and vision language models  vlms  to analyze public perception of ai      applied frame analysis techniques on images and accompanying captions in news articles to detect and interpret  metaphors  integrating text and visual information for comprehensive metaphor identification   feature based recommendation system for youtube video optimization     analyzed how technical and content level video characteristics  bitrate  duration  frame rate  category  influence  user engagement on youtube      performed extensive feature engineering and exploratory data analysis on 17k  videos to identify patterns   outliers  and key drivers of engagement      applied random forest to predict engagement metrics and interpret feature importance using shap and  correlation analysis   skills    programming and scripting languages  python  java  html  css  javascript  typescript    databases  sql  mongodb  postgresql     tools and frameworks  scikit learn  pytorch  spark  pandas  numpy node js  flask  bootstrap  docker  kubernetes   prometheus  loki  grafana  oauth 2 0  github  gitlab  education  university of maryland  college park  college park  md  master s in data science  gpa  4 0                                                                                                aug 2025   present'
obj = ResumeParser('/Users/tanayapravinjoshi/Downloads/TanayaJoshiResume_DS.docx.pdf')
text = obj.parse_resume()
resume_text = text["text"]
preprocessor_resume = PreProcessor(resume_text)
clean_resume_light = preprocessor_resume.clean_text()
print(clean_resume_light)
# section_detector = ResumeSectionDetector(text)
# result = section_detector.main()
# print(result)
