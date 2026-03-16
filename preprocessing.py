import spacy 
import regex 
import unicodedata 
import json
import nltk 
CUSTOM_STOPWORDS = {
    "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "a", "an", "is", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "shall",
    "can", "need", "our", "your", "their", "we", "you", "they",
    "it", "this", "that", "these", "those", "by", "from", "as",
    "into", "through", "about", "between", "such", "more", "also",
    "other", "than", "then", "so", "if", "when", "where", "who",
    "which", "how", "what", "all", "any", "both", "each", "few",
    "most", "some", "own", "same", "just", "because", "while",
    "although", "not", "no", "nor", "its", "very", "per", "well"
}

class PreProcessor:
    def __init__(self, text):
        self.text = text 
        self.nlp = spacy.load("en_core_web_sm")
        self.stop_words = CUSTOM_STOPWORDS

    
    def normalization(self, text):
        cleaned_text = unicodedata.normalize('NFKC',text)
        norm_dict = {}
        with open('normalization_keys.json','r') as f:
            norm_dict = json.load(f)
        for abr, full in norm_dict.items():
            cleaned_text = regex.sub(rf'\b{regex.escape(abr)}\b', full, cleaned_text)
        return cleaned_text
    
    def lemmatize(self, text):
        doc = self.nlp(text)
        return " ".join([token.lemma_ for token in doc])
    
    def remove_stopwords(self, text):
        words = text.split()
        result = " ".join([w for w in words if w not in self.stop_words])
        return result 

    def clean_text(self):
        text = self.text.lower()
        text = text.strip()
        text_lst = text.splitlines()
        text_lst = [char for char in text_lst if len(char) > 1]
        text = ' '.join(text_lst)
        text = regex.sub(r"https?://\S+|www\.\S+", ' ', text)
        text = regex.sub(r'[^a-zA-Z0-9]', ' ', text)
        return text
    
