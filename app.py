#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ================================================================
#   Copyright (C) 2023 * Ltd. All rights reserved.
#   Project ：report-export 
#   File name   : app.py
#   Author      : yulin
#   Created date: 2023-03-18 14:46:36
#   Editor      : yulin
#   Modify Time : 2023-03-18 14:46:36
#   Version     : 1.0
#   Description : 图片转PDF
# ================================================================

import time
from flask import Flask, request, send_file
from PIL import Image
import requests
from io import BytesIO
from check_black_to_pdf_export import insert_images_to_pdf

app = Flask(__name__)


@app.route('/image-to-pdf', methods=['POST'])
def convert_image_to_pdf():
    start_time = time.time()

    image_url = request.form.get('image_url')

    if not image_url:
        return {"error": "image_url is required"}, 400

    try:
        # 从 URL 下载图像
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content))

        # 将图像保存为临时 JPEG 文件
        temp_image = BytesIO()
        image.save(temp_image, "JPEG")
        temp_image.seek(0)

        # 转换图像为 PDF 文件流
        pdf_stream = insert_images_to_pdf(temp_image,)

        # 计算耗时
        elapsed_time = time.time() - start_time
        print(f"Total processing time: {elapsed_time:.2f} seconds")

        # 返回 PDF 文件流作为响应
        return send_file(pdf_stream, as_attachment=True)

    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)
