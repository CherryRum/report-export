import io
import cv2
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image
from concurrent.futures import ThreadPoolExecutor


def _convert_image_to_pdf_page(img, output_filename):
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    pdf_page = canvas.Canvas(output_filename, pagesize=A4)
    img_width, img_height = pil_img.size

    pdf_page_width, pdf_page_height = A4
    scale = min(pdf_page_width / img_width, pdf_page_height / img_height)

    img_width = img_width * scale
    img_height = img_height * scale

    x = (pdf_page_width - img_width) / 2
    y = (pdf_page_height - img_height) / 2

    pdf_page.drawImage(pil_img, x, y, img_width, img_height)
    pdf_page.showPage()
    pdf_page.save()


class ImageToPDFConverter:

    def __init__(self, cropped_images):
        self.cropped_images = cropped_images

    def convert_images_to_pdf(self, output_filename):
        with ThreadPoolExecutor() as executor:
            for i, img in enumerate(self.cropped_images):
                page_filename = f"{output_filename}_page_{i}.pdf"
                executor.submit(_convert_image_to_pdf_page, img, page_filename)