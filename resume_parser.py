"""Utilities for reading resume files and normalizing resume text."""

import string

import PyPDF2
import docx

ENGLISH_STOPWORDS = {
    "a",
    "about",
    "above",
    "after",
    "again",
    "against",
    "ain",
    "all",
    "am",
    "an",
    "and",
    "any",
    "are",
    "aren",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "below",
    "between",
    "both",
    "but",
    "by",
    "can",
    "couldn",
    "d",
    "did",
    "didn",
    "do",
    "does",
    "doesn",
    "doing",
    "don",
    "down",
    "during",
    "each",
    "few",
    "for",
    "from",
    "further",
    "had",
    "hadn",
    "has",
    "hasn",
    "have",
    "haven",
    "having",
    "he",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "i",
    "if",
    "in",
    "into",
    "is",
    "isn",
    "it",
    "its",
    "itself",
    "just",
    "ll",
    "m",
    "ma",
    "me",
    "mightn",
    "more",
    "most",
    "mustn",
    "my",
    "myself",
    "needn",
    "no",
    "nor",
    "not",
    "now",
    "o",
    "of",
    "off",
    "on",
    "once",
    "only",
    "or",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "re",
    "s",
    "same",
    "shan",
    "she",
    "should",
    "shouldn",
    "so",
    "some",
    "such",
    "t",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "through",
    "to",
    "too",
    "under",
    "until",
    "up",
    "ve",
    "very",
    "was",
    "wasn",
    "we",
    "were",
    "weren",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "will",
    "with",
    "won",
    "wouldn",
    "y",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
}


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
        text = text.lower()
        text = text.translate(str.maketrans("", "", string.punctuation))
        words = text.split()
        words = [word for word in words if word not in ENGLISH_STOPWORDS]
        return " ".join(words)
    except Exception as exc:
        raise ValueError("Unable to clean resume text.") from exc
