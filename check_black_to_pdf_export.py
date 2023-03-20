import concurrent.futures
import io
import time
import cv2
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Image as DocImage, Spacer, PageBreak


def find_gray_frames(image_path, min_area=1000, lower_threshold=50, upper_threshold=150, gray_threshold=225):
    # Load the image and convert it to grayscale
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a threshold to convert near-black pixels to pure black
    _, threshold_gray = cv2.threshold(gray, gray_threshold, 255, cv2.THRESH_BINARY_INV)

    # Apply Canny edge detection
    edges = cv2.Canny(threshold_gray, lower_threshold, upper_threshold)

    # Find contours in the binary image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    gray_frames = []

    for contour in contours:
        area = cv2.contourArea(contour)

        # Filter out small contours
        if area >= min_area:
            left, upper, width, height = cv2.boundingRect(contour)
            gray_frames.append((left, upper, left + width, upper + height))

    return gray_frames


def sort_coordinates(coordinates_list):
    # Sort the coordinates vertically (from top to bottom)
    coordinates_list.sort(key=lambda x: x[1])
    return coordinates_list


def process_image(image_path, coordinates, doc):
    left, upper, right, lower = coordinates

    full_image = Image.open(image_path)
    cropped_image = full_image.crop((left, upper, right, lower))

    cropped_image = cropped_image.convert("RGB")

    image_width, image_height = cropped_image.size
    aspect = image_height / float(image_width)

    target_width = min(doc.pagesize[0] * 0.8, image_width)
    target_height = target_width * aspect

    image_data = io.BytesIO()
    cropped_image.save(image_data, format='JPEG', quality=90)

    return DocImage(image_data, width=target_width, height=target_height, hAlign='CENTER')


def insert_images_to_pdf(image_path, coordinates_list, pdf_path):
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Process images using multiple threads
        results = list(executor.map(process_image, [image_path] * len(coordinates_list), coordinates_list,
                                    [doc] * len(coordinates_list)))

        for i, pdf_image in enumerate(results):
            story.append(pdf_image)

            if i < len(coordinates_list) - 1:
                story.append(Spacer(1, 12))
                story.append(PageBreak())

    doc.build(story)


# 以下为测试
input_image_path = 'screenshot.png'
start = time.time()
gray_frame_coordinates = find_gray_frames(input_image_path)
end = time.time()
print("获取图像执行时间：", end - start)
output_pdf_path = 'output.pdf'
sorted_coordinates = sort_coordinates(gray_frame_coordinates)
end1 = time.time()
print("排序执行时间：", end1 - end)
insert_images_to_pdf(input_image_path, sorted_coordinates, output_pdf_path)
end2 = time.time()
print("插入执行时间：", end2 - end1)
