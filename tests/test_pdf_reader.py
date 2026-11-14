import os

import pytest

from app.services.pdf_reader import MAX_FILE_SIZE, PDFError, extract_text_from_pdf

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def read_fixture(name):
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()


def test_reads_text_from_real_pdf():
    text = extract_text_from_pdf(read_fixture("sample_resume.pdf"))
    assert "Priya Sharma" in text
    assert "EDUCATION" in text


def test_rejects_empty_or_too_big_file():
    with pytest.raises(PDFError, match="empty"):
        extract_text_from_pdf(b"")

    too_big = b"%PDF-" + b"0" * MAX_FILE_SIZE
    with pytest.raises(PDFError, match="too large"):
        extract_text_from_pdf(too_big)


def test_rejects_text_file_renamed_to_pdf():
    with pytest.raises(PDFError, match="not a real PDF"):
        extract_text_from_pdf(read_fixture("not_a_pdf.pdf"))


def test_rejects_broken_pdf():
    with pytest.raises(PDFError, match="could not read"):
        extract_text_from_pdf(read_fixture("broken.pdf"))


def test_rejects_pdf_with_no_text():
    with pytest.raises(PDFError, match="No text found"):
        extract_text_from_pdf(read_fixture("blank.pdf"))
