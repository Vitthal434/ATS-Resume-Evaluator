"""Utilities for reading resume files and normalizing resume text."""

import string

import PyPDF2
import docx
import nltk

nltk.download("stopwords")
from nltk.corpus import stopwords


def read_pdf(file):
    """Extract and return text from an uploaded PDF resume."""
    try:
        text = ""
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            text += page.extract_text()

        return text
    except Exception as exc:
        raise ValueError("Unable to read PDF resume.") from exc


def read_docx(file):
    """Extract and return text from an uploaded DOCX resume."""
    try:
        document = docx.Document(file)
        return " ".join([paragraph.text for paragraph in document.paragraphs])
    except Exception as exc:
        raise ValueError("Unable to read DOCX resume.") from exc


def clean_text(text):
    """Normalize text by lowercasing, removing punctuation, and filtering stopwords."""
    try:
        english_stopwords = stopwords.words("english")
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        words = text.split()
        words = [word for word in words if word not in english_stopwords]
        return " ".join(words)
    except Exception as exc:
        raise ValueError("Unable to clean resume text.") from exc
