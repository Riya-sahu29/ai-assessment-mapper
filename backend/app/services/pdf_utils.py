import base64
import io
from typing import List, Tuple

from pdf2image import convert_from_bytes
from PIL import Image

DPI = 80  # good balance of OCR accuracy vs. payload size / speed

POPPLER_PATH = r"C:\Users\Sahup\Downloads\Release-26.02.0-0\poppler-26.02.0\Library\bin"

MAX_WIDTH = 1000    # resize images wider than this before sending to the model
JPEG_QUALITY = 65   # balance between payload size and OCR/handwriting readability


def file_to_page_images(filename: str, content: bytes) -> List[Image.Image]:
    """Convert an uploaded PDF or image file into a list of PIL Images (one per page)."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return convert_from_bytes(content, dpi=DPI, poppler_path=POPPLER_PATH)
    # single image upload (png/jpg/jpeg/webp) -> one "page"
    return [Image.open(io.BytesIO(content)).convert("RGB")]


def image_to_b64_png(img: Image.Image) -> str:
    """Resize + compress and encode as base64 JPEG for sending to the vision model."""
    if img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / img.width
        new_height = int(img.height * ratio)
        img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)

    buffer = io.BytesIO()
    img.convert("RGB").save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def b64_png_to_image(b64_str: str) -> Image.Image:
    return Image.open(io.BytesIO(base64.b64decode(b64_str))).convert("RGB")


def get_size(img: Image.Image) -> Tuple[int, int]:
    return img.size  # (width, height)