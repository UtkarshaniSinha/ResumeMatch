import io

import pdfplumber

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

# every real PDF file starts with these bytes
PDF_SIGNATURE = b"%PDF-"


class PDFError(Exception):
    # message of this error is shown directly to the user
    pass


def check_pdf_file(file_bytes):
    if len(file_bytes) == 0:
        raise PDFError("The file is empty. Please upload your resume as a PDF.")

    if len(file_bytes) > MAX_FILE_SIZE:
        raise PDFError("The file is too large. The maximum size is 2 MB.")

    # don't trust the .pdf extension, anyone can rename a file
    if not file_bytes.startswith(PDF_SIGNATURE):
        raise PDFError("This is not a real PDF file. Please upload a PDF.")


def extract_text_from_pdf(file_bytes):
    check_pdf_file(file_bytes)

    pages_text = []
    try:
        # BytesIO lets pdfplumber read the file from memory, so nothing is saved to disk
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    pages_text.append(page_text)
    except Exception:
        # starts with %PDF- but the rest of the file is broken
        raise PDFError("We could not read this PDF. It may be damaged.")

    full_text = "\n".join(pages_text).strip()

    # no text usually means it's a scanned image
    if full_text == "":
        raise PDFError(
            "No text found in this PDF. If it is a scanned image, "
            "please upload a PDF exported from Word or Google Docs."
        )

    return full_text
