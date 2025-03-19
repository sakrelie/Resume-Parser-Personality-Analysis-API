
# **Resume Parser & Personality Analysis API**
🚀 *A FastAPI-based NLP application that extracts structured data from resumes and performs personality analysis based on text content.*

## **📌 Project Overview**
This API processes PDF resumes to extract:
- **Personal Information** (Name, Email, Phone Number)
- **Skills & Previous Job Titles**
- **Personality Traits** (Big Five Analysis)
- **Complete Resume Text Extraction**

The backend is powered by **FastAPI**, **Spacy NLP**, and **PyPDF2**, making it **fast, scalable, and accurate**.

---

## **📊 Features**
### **1️⃣ PDF Resume Processing**
- Extracts raw text from uploaded PDFs.
- Cleans text for better NLP processing.

### **2️⃣ Named Entity Recognition (NER)**
- Detects **Name, Email, Phone Number**.
- Extracts **Skills** and **Job Titles** based on pre-defined sets.

### **3️⃣ Personality Analysis**
- Analyzes resume text using **word frequency matching**.
- Classifies personality based on the **Big Five Traits**:
  - **Openness**
  - **Conscientiousness**
  - **Extraversion**
  - **Agreeableness**
  - **Neuroticism**

### **4️⃣ REST API with FastAPI**
- Supports **PDF uploads**.
- Returns **structured JSON output**.
- Runs on **localhost:8000** by default.

---

## **🛠️ Installation & Setup**
### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/yourusername/Resume-Parser-API.git
cd Resume-Parser-API
