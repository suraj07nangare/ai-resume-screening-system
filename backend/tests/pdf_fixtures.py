import io

from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def make_text_pdf_bytes(text: str) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    for line in text.split("\n"):
        pdf.drawString(50, y, line)
        y -= 15
    pdf.save()
    buffer.seek(0)
    return buffer.read()


def make_scanned_pdf_bytes(text: str) -> bytes:
    image = Image.new("RGB", (1000, 1300), color="white")
    draw = ImageDraw.Draw(image)
    y = 40
    for line in text.split("\n"):
        draw.text((40, y), line, fill="black")
        y += 30

    buffer = io.BytesIO()
    image.save(buffer, format="PDF")
    buffer.seek(0)
    return buffer.read()
