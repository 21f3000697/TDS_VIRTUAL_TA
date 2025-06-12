import base64
import io
import cv2
import numpy as np
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def decode_base64_image(base64_str: str) -> np.ndarray:
    try:
        img_data = base64.b64decode(base64_str)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        raise ValueError("Invalid base64 image") from e

def extract_text_from_image(base64_str: str) -> str:
    image = decode_base64_image(base64_str)
    pil_img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    text = pytesseract.image_to_string(pil_img)
    return text.strip()
