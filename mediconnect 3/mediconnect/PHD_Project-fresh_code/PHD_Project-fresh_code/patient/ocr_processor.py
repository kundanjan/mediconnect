import re
import pytesseract
from PIL import Image
from django.conf import settings
import os


def extract_text_from_image(image_path: str) -> str:
    try:
        _initialize_tesseract()
        image = Image.open(image_path)
        if image.mode != 'L':
            image = image.convert('L')
        raw_text = pytesseract.image_to_string(image)
        return _clean_text(raw_text)
    except FileNotFoundError:
        raise FileNotFoundError(f"Image file not found: {image_path}")
    except Exception as e:
        print(f"OCR processing error: {str(e)}")
        raise Exception(f"Failed to process image: {str(e)}")


def _initialize_tesseract():
    bundled_path = os.path.join(settings.BASE_DIR, 'Tesseract-OCR', 'tesseract.exe')
    if os.path.exists(bundled_path):
        pytesseract.pytesseract.tesseract_cmd = bundled_path
        tessdata = os.path.join(settings.BASE_DIR, 'Tesseract-OCR', 'tessdata')
        if os.path.exists(tessdata):
            os.environ['TESSDATA_PREFIX'] = tessdata
        return
    paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        '/usr/local/bin/tesseract',
        '/usr/bin/tesseract'
    ]
    for path in paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return
    raise Exception("Tesseract OCR not found. Please install Tesseract.")


def _clean_text(raw_text: str) -> str:
    text = raw_text
    text = re.sub(r'[^a-zA-Z0-9\s\n\/\-\:\.]', '', text)
    text = text.replace(',', '\n')
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    return text.strip()
