"""One-off generator for binary PDF test fixtures (run manually, output is committed).

Run: .venv/Scripts/python.exe tests/fixtures/generate_pdf_fixtures.py
"""

from pathlib import Path

import fitz

FIXTURES_DIR = Path(__file__).parent


def make_text_pdf() -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Hello from a PDF! This fixture has real extractable text.")
    doc.save(FIXTURES_DIR / "sample_text.pdf")
    doc.close()


def make_corrupted_pdf() -> None:
    (FIXTURES_DIR / "corrupted.pdf").write_bytes(b"%PDF-1.4\nthis is not a valid pdf body\n%%EOF")


def make_password_protected_pdf() -> None:
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Secret content behind a password.")
    doc.save(
        FIXTURES_DIR / "password_protected.pdf",
        encryption=fitz.PDF_ENCRYPT_AES_256,
        user_pw="secret",
        owner_pw="secret-owner",
    )
    doc.close()


def make_image_only_pdf() -> None:
    doc = fitz.open()
    page = doc.new_page()
    # A filled rectangle drawn as vector graphics — no text layer at all.
    page.draw_rect(fitz.Rect(50, 50, 400, 300), color=(0, 0, 0), fill=(0.2, 0.6, 0.9))
    doc.save(FIXTURES_DIR / "image_only.pdf")
    doc.close()


if __name__ == "__main__":
    make_text_pdf()
    make_corrupted_pdf()
    make_password_protected_pdf()
    make_image_only_pdf()
    print("Fixtures written to", FIXTURES_DIR)
