#!/usr/bin/env python3
# pip install -U PyMuPDF
# install https://imagemagick.org/index.php (for windows install also https://ghostscript.com/releases/gsdnld.html)


import fitz
import os
import time
import subprocess
from typing import List, Tuple

import cfg
import my_log
import my_gemini
from utils import async_run, get_codepage, platform, get_tmp_fname, remove_file, remove_dir


def extract_images_from_pdf_with_imagemagick(data: bytes) -> List[bytes]:
    '''
    Extracts all images from a PDF using ImageMagick.

    Args:
        data: The content of the PDF file as bytes.

    Returns:
        A list of bytes, where each element is the byte content of an image found in the PDF.
    '''
    source = get_tmp_fname() + '.pdf'
    target = get_tmp_fname()
    images = []
    try:
        with open(source, 'wb') as f:
            f.write(data)
        os.mkdir(target)

        CMD = 'magick' if 'windows' in platform().lower() else 'convert'
        path_separator = '\\' if 'windows' in platform().lower() else '/'

        cmd = f"{CMD} -density 150 {source} {target}{path_separator}%003d.jpg"

        with subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding = get_codepage()) as proc:
            stdout, stderr = proc.communicate()
        if stderr:
            my_log.log2(f"my_pdf:extract_images_from_pdf_with_imagemagick: Error processing PDF: {stderr}")

        for file in os.listdir(target):
            with open(os.path.join(target, file), 'rb') as f:
                images.append(f.read())

    except Exception as error:
        my_log.log2(f"my_pdf:extract_images_from_pdf_with_imagemagick: Error processing PDF: {error}")

    remove_dir(target)
    remove_file(source)

    return images


def extract_images_from_pdf_bytes(pdf_bytes: bytes) -> List[bytes]:
    """
    Extracts all images from a PDF given as bytes.

    Args:
        pdf_bytes: The content of the PDF file as bytes.

    Returns:
        A list of bytes, where each element is the byte content of an image found in the PDF.
    """
    # try to extract images from pdf with imagemagick
    image_list_bytes = extract_images_from_pdf_with_imagemagick(pdf_bytes)
    if image_list_bytes:
        return image_list_bytes

    try:
        pdf_file = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_index in range(len(pdf_file)):
            page = pdf_file.load_page(page_index)
            images_on_page = page.get_images(full=True)
            for image_info in images_on_page:
                xref = image_info[0]
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]
                image_list_bytes.append(image_bytes)
    except Exception as error:
        my_log.log2(f"my_pdf:extract_images_from_pdf_bytes: Error processing PDF: {error}")
    return image_list_bytes


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extracts all text content from a PDF given as bytes.

    Args:
        pdf_bytes: The content of the PDF file as bytes.

    Returns:
        A string containing all the text content extracted from the PDF.
    """
    text_content = ""
    try:
        pdf_file = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_number in range(pdf_file.page_count):
            page = pdf_file.load_page(page_number)
            text_content += page.get_text()
    except TypeError as error_type:
        if "'module' object is not callable" not in str(error_type):
            my_log(f"my_pdf:extract_text_from_pdf_bytes:type_error: Error processing PDF: {error_type}")
    except Exception as error:
        my_log(f"my_pdf:extract_text_from_pdf_bytes: Error processing PDF: {error}")
    return text_content


@async_run
def process_image_ocr(image: bytes, index: int, results) -> Tuple[str, int]:
    """
    Performs OCR on a single image using my_gemini.ocr_page.

    Args:
        image: The image data as bytes.
        index: The index of the image in the original list.
    """
    text = my_gemini.ocr_page(image)
    results[index] = text or 'EMPTY MARKER 4975934685'


def get_text(data: bytes) -> str:
    """
    Extract text from pdf
    if no text, OCR images with gemini using 8 threads
    """
    text = extract_text_from_pdf_bytes(data)
    if len(text) < 100:
        images = extract_images_from_pdf_bytes(data)
        results = {}
        index = 0
        LIMIT = cfg.LIMIT_PDF_OCR if hasattr(cfg, 'LIMIT_PDF_OCR') else 50
        for image in images[:LIMIT]:
            process_image_ocr(image, index, results)
            index += 1

        while len(results) != len(images):
            time.sleep(1)

        # remove empty markers
        results = {k: v for k, v in results.items() if v != 'EMPTY MARKER 4975934685'}

        # convert to list sorted ny index
        results = sorted(results.items(), key=lambda x: x[0])

        text = '\n'.join([v for _, v in results])

    return text


if __name__ == "__main__":
    my_gemini.load_users_keys()
    with open("c:/Users/User/Downloads/1.pdf", "rb") as f:
        data = f.read()
        print(get_text(data))
