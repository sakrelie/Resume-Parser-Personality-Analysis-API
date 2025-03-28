from fastapi import FastAPI, File, UploadFile, HTTPException
import PyPDF2
import os
import uvicorn
import subprocess
import logging
import re
import spacy
from collections import Counter

# Install requirements.txt
subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
subprocess.run(["pip", "install", "spacy"], check=True)
subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)

# Load Spacy NLP model
nlp = spacy.load("en_core_web_sm")

# Initialize FastAPI app
app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to clean extracted text
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return clean_text(text)
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return None

def extract_name(text, doc=None):
    lines = text.splitlines()
    name_candidates = []

    for line in lines[:10]:
        line = line.strip()
        if line and not any(char.isdigit() for char in line):
            words = line.split()
            if 2 <= len(words) <= 6:
                if words[0][0].isupper():
                    name_candidates.append(line)

    return max(name_candidates, key=lambda x: len(x.split()), default=None)


# Function to extract entities (name, email, phone, skills, previous jobs, highest education)
def extract_entities(text):
    doc = nlp(text)
    name = extract_name(text, doc)
    email = None
    phone = None
    skills = set()
    previous_jobs = set()
    highest_education = None

    email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if email_match:
        email = email_match.group(0)

    phone_match = re.search(r'\(?\d{3}\)?[-.\s]?[\d]{3}[-.\s]?[\d]{4}', text)
    if phone_match:
        phone = phone_match.group(0)

    skill_keywords = {"Python", "Java", "SQL", "Machine Learning", "AI", "Data Analysis", "Excel", "Cloud", "Project Management", "Marketing", "JavaScript", "C++", "C#", "R", "Swift", "TypeScript", "Ruby", "Kotlin", "Go", "PHP", "Data Engineering", "Data Visualization", "Predictive Analytics", "Big Data", "ETL", "Statistical Analysis", "Deep Learning", "Natural Language Processing", "Neural Networks", "Time Series Analysis", "AWS", "Google Cloud Platform", "Microsoft Azure", "Docker", "Kubernetes", "CI/CD Pipelines", "Terraform", "Serverless Computing", "Site Reliability Engineering", "Jenkins", "NoSQL", "MongoDB", "PostgreSQL", "Firebase", "Redis", "GraphQL", "Cassandra", "Hadoop", "Apache Spark", "Elasticsearch", "Ethical Hacking", "Penetration Testing", "Cryptography", "Network Security", "Firewall Management", "Intrusion Detection", "Secure Coding", "Identity & Access Management", "Cyber Threat Intelligence", "Blockchain Security", "Agile Methodologies", "Scrum", "Test-Driven Development", "Microservices", "RESTful APIs", "Software Architecture", "Full Stack Development", "Backend Development", "Frontend Development", "Version Control", "Business Intelligence", "Agile Project Management", "Risk Management", "Scrum Master", "Product Management", "Business Strategy", "Lean Methodology", "Digital Transformation", "Six Sigma", "Financial Modeling", "SEO", "SEM", "Google Ads", "Social Media Marketing", "Email Marketing", "Growth Hacking", "Copywriting", "Content Strategy", "A/B Testing", "Influencer Marketing"}
    for token in doc:
        if token.text in skill_keywords:
            skills.add(token.text)

    job_titles = {"Software Engineer", "Data Analyst", "Project Manager", "Marketing Manager", "Consultant", "Researcher", "Data Scientist", "Machine Learning Engineer", "AI Engineer", "Cloud Engineer", "DevOps Engineer", "Full Stack Developer", "Backend Developer", "Frontend Developer", "Cybersecurity Analyst", "Penetration Tester", "Database Administrator", "Systems Architect", "Business Intelligence Analyst", "Product Manager", "UX/UI Designer", "Financial Analyst", "IT Support Specialist", "Network Engineer", "Site Reliability Engineer", "Business Analyst", "Quality Assurance Engineer", "Scrum Master", "Blockchain Developer", "Software Architect", "Embedded Systems Engineer", "Technical Writer", "Digital Marketing Specialist", "SEO Specialist", "Social Media Manager", "Content Strategist", "Growth Hacker", "Data Engineer", "AI Research Scientist", "Cloud Solutions Architect", "Security Engineer", "IoT Engineer", "Automation Engineer", "Ethical Hacker", "Game Developer", "Computer Vision Engineer", "NLP Engineer", "Robotics Engineer", "Supply Chain Analyst", "Operations Manager", "Risk Analyst", "Sales Engineer", "E-commerce Manager", "Financial Risk Manager", "Actuary", "Economist", "Healthcare Data Analyst", "Environmental Analyst", "Policy Analyst", "CRM Manager", "HR Analyst", "Technical Recruiter", "IT Consultant", "Software Development Manager", "IT Auditor", "Biomedical Engineer", "GIS Analyst", "Energy Analyst", "Legal Analyst", "Cybersecurity Consultant"}
    for title in job_titles:
        if title.lower() in text.lower():
            previous_jobs.add(title)

    education_keywords = ["high school", "diploma", "bachelor", "master", "phd", "associate", "graduate certificate"]
    education_fields = []
    for sentence in re.split(r'(?<=[.?!])\s+', text.lower()):
        if any(degree in sentence for degree in education_keywords):
            education_fields.append(sentence.strip())

    education_hierarchy = ["phd", "master", "graduate certificate", "bachelor", "associate", "diploma", "high school"]
    for level in education_hierarchy:
        for edu in education_fields:
            if level in edu:
                highest_education = level.title()
                break
        if highest_education:
            break

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": list(skills),
        "previous_jobs": list(previous_jobs),
        "highest_education": highest_education
    }

# Function to analyze personality based on word usage
def analyze_personality(text):
    words = text.lower().split()
    word_counts = Counter(words)

    personality_traits = {
        "Openness": ["creative", "curious", "imaginative", "abstract", "intellectual", "artistic", "inventive", "philosophical", "experimental", "visionary", "research", "analysis", "design", "strategy", "learning", "explore", "innovation", "conceptual", "problem-solving"],
        "Conscientiousness": ["organized", "efficient", "goal", "planning", "disciplined", "responsible", "systematic", "methodical", "dependable", "hardworking", "deadline", "accuracy", "execution", "management", "detail-oriented", "structured", "documentation", "consistency", "workflow"],
        "Extraversion": ["outgoing", "energetic", "talkative", "social", "assertive", "expressive", "enthusiastic", "bold", "lively", "cheerful", "networking", "collaboration", "leadership", "presentation", "public speaking", "team player", "client-facing", "relationship-building"],
        "Agreeableness": ["kind", "trustworthy", "helpful", "friendly", "compassionate", "considerate", "cooperative", "generous", "empathetic", "nurturing", "mentorship", "teamwork", "support", "customer service", "listening", "collaborate", "partnership", "engagement"],
        "Neuroticism": ["anxious", "stressed", "worried", "emotional", "insecure", "self-conscious", "moody", "irritable", "nervous", "tense", "pressure", "deadline stress", "overwhelmed", "workload", "uncertain", "burnout", "frustration", "demanding"]
    }

    results = {}
    for trait, keywords in personality_traits.items():
        score = sum(word_counts[word] for word in keywords if word in word_counts)
        results[trait] = score

    return results

@app.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        file_location = f"temp_{file.filename}"
        with open(file_location, "wb") as f:
            f.write(file.file.read())

        extracted_text = extract_text_from_pdf(file_location)
        os.remove(file_location)

        if extracted_text is None:
            raise HTTPException(status_code=500, detail="Failed to extract text from PDF.")

        entities = extract_entities(extracted_text)
        personality_results = analyze_personality(extracted_text)

        return {
            "filename": file.filename,
            "extracted_text": extracted_text,
            "entities": entities,
            "personality_analysis": personality_results
        }
    except HTTPException as http_err:
        return {"error": http_err.detail}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {"error": "Internal server error"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
