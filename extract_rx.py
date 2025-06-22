#!/usr/bin/env python3
import os
import sys
import cv2
import numpy as np  # Add this import
import pytesseract
import re
import json
import logging
from symspellpy import SymSpell, Verbosity
try:
    from pdf2image import convert_from_path
    HAS_PDF_SUPPORT = True
except ImportError:
    HAS_PDF_SUPPORT = False
    print("Warning: pdf2image not installed. PDF processing unavailable.")
    print("Run: pip install pdf2image")
    print("And ensure poppler-utils is installed on your system")

#Configuration
BASE_DIR       = os.path.dirname(__file__)
FREQ_DICT      = os.path.join(BASE_DIR, 'dictionary', 'pharmacy_dict.txt')
MED_DICT       = os.path.join(BASE_DIR, 'dictionary', 'medicine_names.txt')

# 1. Simple confusions map for common OCR misreads
_CONFUSIONS = {
    '0': ['O'], '1': ['l','I'], '5': ['S'], '8': ['B'],
}

#
def _init_symspell(freq_dict_path=FREQ_DICT):
    sym = SymSpell(max_dictionary_edit_distance=1, prefix_length=7)
    sym.load_dictionary(freq_dict_path, term_index=0, count_index=1)
    return sym

def _load_med_dict(med_dict_path=MED_DICT):
    with open(med_dict_path, encoding='utf8') as f:
        return {line.strip().lower() for line in f if line.strip()}

def _preprocess(path):
    # Check if the file is a PDF
    if path.lower().endswith('.pdf'):
        if not HAS_PDF_SUPPORT:
            raise RuntimeError("PDF support not available. Please install pdf2image.")
            
        # Convert first page of the PDF to an image
        pages = convert_from_path(path, first_page=1, last_page=1)
        if not pages:
            raise ValueError("Could not convert PDF to image")
            
        # Convert PIL image to OpenCV format
        img = np.array(pages[0])
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        # Process as before for regular images
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Could not read image file: {path}")
    
    # Continue with your existing preprocessing
    blur = cv2.medianBlur(img, 3)
    _, bw = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return bw

def _ocr(image):
    return pytesseract.image_to_string(image, config='--oem 1 --psm 6')

def _correct(text, sym):
    tokens = re.findall(r"\w+|\W+", text)
    out    = []
    for t in tokens:
        # skip units
        if re.fullmatch(r"\d*\s*(?:mg|g|ml)", t, re.IGNORECASE):
            out.append(t)
        elif t.isalpha():
            s = sym.lookup(t, Verbosity.CLOSEST, max_edit_distance=1)
            out.append(s[0].term if s else t)
        else:
            out.append(t)
    return ''.join(out)

def _extract(text, med_dict):
    """
    Simply returns the full transcribed text without specific extraction
    
    Parameters:
    text (str): OCR text from the prescription
    med_dict (set): Dictionary of medication names
    
    Returns:
    dict: Contains the full text along with any recognized medications
    """
    # Find any medications that might be in the text
    recognized_meds = [m for m in med_dict if m in text.lower()]
    
    return {
        'full_text': text,
        'recognized_medications': recognized_meds if recognized_meds else None
    }

def process_image(image_path):
    """ Electron & CLI both call this. """
    img  = _preprocess(image_path)
    raw  = _ocr(img)
    sym  = _init_symspell()
    corr = _correct(raw, sym)
    meds = _load_med_dict()
    return _extract(corr, meds)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: extract_rx.py <imagePath>', file=sys.stderr)
        sys.exit(1)

    image = sys.argv[1]
    result = process_image(image)
    
    # Print human-readable output when run directly
    print("OCR RESULTS")
    
    # Format the full text with proper line breaks
    full_text = result['full_text']
    # Replace multiple newlines with a single one and trim extra whitespace
    formatted_text = re.sub(r'\n+', '\n', full_text).strip()
    # Add proper paragraph indentation
    formatted_text = '\n'.join(f"    {line}" for line in formatted_text.split('\n'))
    
    print("\nEXTRACTED TEXT:")
    print(formatted_text)
