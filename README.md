# ATS Resume Evaluator

An intelligent **Applicant Tracking System (ATS) Resume Evaluator** built using **Python**, **Flask**, and **Natural Language Processing (NLP)**. The application analyzes resumes against job descriptions, calculates an ATS compatibility score, identifies missing skills, and provides personalized recommendations to improve the chances of getting shortlisted.

---

## Features

- Resume Upload (PDF & DOCX)
- ATS Compatibility Score
- Resume & Job Description Similarity Analysis
- Missing Skills Detection
- Skill Match Percentage
- Experience Evaluation
- Resume Improvement Suggestions
- Job Role Recommendations
- Downloadable PDF Report
- Clean and Responsive User Interface

---

## Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask

### Libraries

- PyPDF2
- python-docx
- scikit-learn
- nltk
- reportlab

---

## Project Workflow

```
Upload Resume
        │
        ▼
Extract Resume Text
        │
        ▼
Upload Job Description
        │
        ▼
NLP Processing
        │
        ▼
ATS Score Calculation
        │
        ▼
Skill Matching
        │
        ▼
Missing Skill Detection
        │
        ▼
Generate Recommendations
        │
        ▼
Export PDF Report
```

---

## Folder Structure

```
ATS-Resume-Evaluator
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── templates/
│
├── uploads/
│
├── app.py
├── matcher.py
├── resume_parser.py
├── report_generator.py
├── job_recommender.py
├── requirements.txt
└── README.md
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/Vitthal434/ATS-Resume-Evaluator.git
```

Move into the project

```bash
cd ATS-Resume-Evaluator
```

Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Run

```bash
python app.py
```

Open

```
http://127.0.0.1:5000
```

---

## Future Improvements

- AI-based Resume Suggestions
- Resume Grammar Analysis
- Multiple Resume Comparison
- Resume Ranking
- LinkedIn Profile Analyzer
- AI Career Guidance
- Cloud Deployment

---

## Author

**Vaibhav Pandey**

GitHub

https://github.com/Vitthal434

---

## License

This project is licensed under the **MIT License**.

See the [LICENSE](LICENSE) file for more details.