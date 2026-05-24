# ATS-Scorer

A full-stack ATS resume scoring tool that analyzes how well a candidate's resume matches a job description using a hybrid ML pipeline combining semantic similarity, ontology-based skill matching, and LLM-powered keyword extraction.

## Problem
Most ATS systems reject qualified candidates because their resume doesn't contain the exact keywords the system is scanning for. A candidate who writes "applied statistical techniques" gets rejected when the JD asks for "statistics". Someone with anomaly detection experience gets flagged as missing "regression" despite the implied knowledge. This tool solves that by going beyond literal keyword matching to understand resume context.

## Architecture

```
Resume (PDF/DOCX)
      ↓
LlamaParse — structure-preserving document parsing
      ↓
parse_markdown_sections() — splits resume into labeled sections
      ↓
┌─────────────────────────────────────────────────────┐
│                   PIPELINE                          │
│                                                     │
│  Job Description                                    │
│       ↓                                             │
│  Qwen2.5-72B (HuggingFace) — keyword extraction    │
│       ↓                                             │
│  ┌────────────────┐    ┌───────────────────────┐   │
│  │ Semantic Score │    │  Keyword Match Score  │   │
│  │                │    │                       │   │
│  │ sentence-      │    │ 1. Exact match        │   │
│  │ transformers   │    │ 2. ESCO ontology      │   │
│  │ chunk-based    │    │ 3. Fuzzy match        │   │
│  │ cosine sim     │    │ 4. Semantic match     │   │
│  └──────┬─────────┘    └──────────┬────────────┘   │
│         └─────────────────────────┘                │
│                      ↓                             │
│              Weighted Combiner                     │
│           (60% semantic / 40% keyword)             │
└─────────────────────────────────────────────────────┘
      ↓
Streamlit UI — score + gap analysis
```

## Features

- 1. LlamaParse integration — preserves resume structure and extracts sections (experience, skills, education, projects) from complex PDF layouts
  2. LLM keyword extraction — Qwen2.5-72B-Instruct extracts and categorizes keywords from job descriptions using few-shot prompting, no hand-curated taxonomy needed
  3. ESCO skill ontology — Neo4j graph database loaded with 13,960 skill nodes and 5,818 relationships from the EU ESCO taxonomy, enabling implicit skill matching
  4. Four-level hybrid matching — exact → ontology → fuzzy → semantic, each with a confidence score
  5. Chunk-based semantic scoring — only high-signal resume sections (experience, skills, projects) are embedded to avoid diluting the score with contact info and dates
  6. Section classifier — trained on 9,500+ real resumes using logistic regression on sentence transformer embeddings, achieving 99% F1 across  section types, used as fallback when LlamaParse fails
  7. Streamlit UI — clean two-panel input interface with loading states and a results page showing score breakdown and prioritized gap analysis


## Tech Stack
| Component | Technology |
|---|---|
| Resume parsing | LlamaParse |
| Keyword extraction | Qwen2.5-72B-Instruct (HuggingFace Inference API) |
| Semantic scoring | sentence-transformers (all-MiniLM-L6-v2) |
| Skill ontology | Neo4j + ESCO taxonomy |
| Fuzzy matching | rapidfuzz |
| NLP preprocessing | spaCy (en_core_web_sm) |
| Section classifier | scikit-learn LogisticRegression |
| UI | Streamlit |
| Database | Neo4j (Docker) |


## Setup

1. Clone the repository
   
```bash
git clone https://github.com/yourusername/ats-scorer.git
cd ats-scorer
```

3. Create and activate virtual environment
   
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```
5. Install dependencies
   
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

6. Set up environment variables
   
```bash
cp .env.example .env
Fill in your API keys in .env:
HF_TOKEN=your_huggingface_token
LLAMA_CLOUD_API_KEY=your_llamaparse_key
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

8. Start Neo4j with Docker
   
```bash
docker-compose up -d
```
10. Load ESCO skill taxonomy
    
Download the ESCO skills dataset from https://esco.ec.europa.eu/en/use-esco/download and place skills_en.csv and skillsRelations.csv in the project root, then run:

```bash
python scripts/load_esco_to_neo4j.py
```
12. Train the section classifier (optional)
Only needed if you want the fallback section detector. Download resume_data.csv and run:

```bash
python scripts/train_section_classifier.py
```

14. Run the app
    
```bash
streamlit run app.py
```

## How It Works

**Resume Parsing**

LlamaParse converts the resume PDF/DOCX into clean markdown preserving section structure. The markdown is split on ## headers into a sections dictionary — experience, skills, education, projects etc.

**Keyword Extraction**

The full JD text is sent to Qwen2.5-72B-Instruct with a few-shot prompt instructing it to return only a JSON object of skill names grouped by category. Frequency is computed manually via regex against the actual JD text and priority is assigned in code based on frequency and category — nothing is left to the LLM to hallucinate.

**Scoring**

Two parallel signals are computed and combined:
Semantic score (60%) — only the experience, skills, and projects sections of the resume are embedded using sentence-transformers. The resume is split into fixed-size word chunks, each chunk is scored against the JD embedding, and the top-3 chunk scores are averaged. This prevents contact info and dates from diluting the score.
Keyword score (40%) — each extracted JD keyword is matched against the resume through four levels: exact string match, ESCO ontology match (checks canonical names, alt labels, and related skills up to 2 hops), fuzzy match via rapidfuzz, and semantic match via cosine similarity. Each level returns a confidence score rather than a binary result.

**Gap Analysis**

Unmatched keywords are ranked by JD frequency and category into critical, moderate, and nice-to-have — giving the user a prioritized list of what to add to their resume.

## Environment Variables

| Variable | Description |
|---|---|
| `HF_TOKEN` | HuggingFace API token for Qwen2.5 inference |
| `LLAMA_CLOUD_API_KEY` | LlamaParse API key |
| `NEO4J_URI` | Neo4j connection URI |
| `NEO4J_USER` | Neo4j username |
| `NEO4J_PASSWORD` | Neo4j password |

## Acknowledgements

- ESCO — European Skills, Competences, Qualifications and Occupations taxonomy
- LlamaIndex — LlamaParse document parsing
- HuggingFace — Qwen2.5 model inference
- sentence-transformers — semantic embeddings
