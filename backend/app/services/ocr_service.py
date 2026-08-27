from typing import Any, Dict, List

import pytesseract
from PIL import Image


def get_word_boxes(img: Image.Image) -> List[Dict[str, Any]]:
    """
    Run Tesseract OCR and return word-level bounding boxes in pixel coords.
    Used only on the ANSWER SHEET, to later locate where AI-transcribed
    answer text physically sits on the page (for highlighting).
    """
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    boxes = []
    for i in range(len(data["text"])):
        text = data["text"][i].strip()
        if not text:
            continue
        # tesseract confidence is -1 for non-text regions; skip junk
        try:
            conf = float(data["conf"][i])
        except (ValueError, TypeError):
            conf = -1
        if conf < 0:
            continue
        boxes.append({
            "text": text,
            "left": data["left"][i],
            "top": data["top"][i],
            "width": data["width"][i],
            "height": data["height"][i],
            "conf": conf,
        })
    return boxes