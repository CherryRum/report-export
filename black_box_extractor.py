#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# ================================================================
#   Copyright (C) 2023 * Ltd. All rights reserved.
#   Project ：report-export 
#   File name   : black_box_extractor.py
#   Author      : yulin
#   Created date: 2023-03-18 15:01:59
#   Editor      : yulin
#   Modify Time : 2023-03-18 15:01:59
#   Version     : 1.0
#   Description :
# ================================================================
import os

import cv2
import numpy as np


class BlackBoxExtractor:

    def __init__(self, image):
        self.image = image

    def find_black_boxes(self, width=50, height=50):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, threshold = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        black_boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > width and h > height:  # 只保留宽度和高度大于 50 像素的矩形区域
                black_boxes.append((x, y, w, h))

        return black_boxes

    # 使用Sobel 算子
    def find_contours_with_sobel(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        sobel_x = cv2.Sobel(blurred, cv2.CV_64F, 1, 0, ksize=5)
        sobel_y = cv2.Sobel(blurred, cv2.CV_64F, 0, 1, ksize=5)
        sobel = cv2.addWeighted(sobel_x, 0.5, sobel_y, 0.5, 0)
        sobel = np.uint8(np.absolute(sobel))
        thresh = cv2.threshold(sobel, 30, 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    # 使用scharr 算子
    def find_contours_with_scharr(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        scharr_x = cv2.Scharr(blurred, cv2.CV_64F, 1, 0)
        scharr_y = cv2.Scharr(blurred, cv2.CV_64F, 0, 1)
        scharr = cv2.addWeighted(scharr_x, 0.5, scharr_y, 0.5, 0)
        scharr = np.uint8(np.absolute(scharr))
        thresh = cv2.threshold(scharr, 30, 255, cv2.THRESH_BINARY)[1]
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        return contours

    def crop_and_save_black_boxes(self, output_directory):
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        cropped_images = []
        sorted_contours = sorted(self.find_contours(), key=lambda ctr: cv2.boundingRect(ctr)[1])

        for i, contour in enumerate(sorted_contours):
            x, y, w, h = cv2.boundingRect(contour)
            cropped_image = self.image[y:y + h, x:x + w]
            cropped_images.append(cropped_image)

        return cropped_images


