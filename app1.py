#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ================================================================
#   Copyright (C) 2023 * Ltd. All rights reserved.
#   Project ：report-export 
#   File name   : app1.py
#   Author      : yulin
#   Created date: 2023-03-18 15:07:56
#   Editor      : yulin
#   Modify Time : 2023-03-18 15:07:56
#   Version     : 1.0
#   Description :
# ================================================================

import os
import io
import cv2
import time
import shutil
import tempfile
import logging
import numpy as np
from PIL import Image
from flask import Flask, request, send_file
from black_box_extractor import BlackBoxExtractor
from image_to_pdf import ImageToPDFConverter

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route('/upload', methods=['POST'])
def upload():
    start_time = time.time()

    # 检查是否有文件上传
    if 'file' not in request.files:
        return 'No file uploaded', 400

    # 读取上传的文件
    file = request.files['file']
    img_bytes = io.BytesIO(file.read())
    img = Image.open(img_bytes).convert("RGB")
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # 提取黑框
    extractor_start_time = time.time()
    extractor = BlackBoxExtractor(img)
    cropped_images = extractor.crop_and_save_black_boxes('output/black_box')
    extractor_end_time = time.time()

    # 创建 PDF 文件
    pdf_converter_start_time = time.time()
    pdf_converter = ImageToPDFConverter(cropped_images)
    output_dir = tempfile.mkdtemp()
    output_filename = os.path.join(output_dir, 'output.pdf')
    pdf_converter.convert_images_to_pdf(output_filename)
    pdf_converter_end_time = time.time()

    # 将 PDF 文件作为响应发送
    with open(output_filename, 'rb') as f:
        pdf_data = f.read()

    shutil.rmtree(output_dir)
    response = send_file(io.BytesIO(pdf_data), mimetype='application/pdf', as_attachment=True)

    end_time = time.time()
    logger.info(f"Total time: {end_time - start_time:.2f} seconds")
    logger.info(f"Extractor time: {extractor_end_time - extractor_start_time:.2f} seconds")
    logger.info(f"PDF converter time: {pdf_converter_end_time - pdf_converter_start_time:.2f} seconds")

    return response


if __name__ == '__main__':
    app.run(debug=True)
