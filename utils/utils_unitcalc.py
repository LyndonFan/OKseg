import cv2
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse
from PIL import Image

def unit_cal(img_path="utils/metric/metric.png", ksize=6):
    # read image and preprocessing
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((ksize, ksize), np.uint8)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    post_img = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # set the range of edge width
    img_width = img.shape[1]
    min_edge, max_edge = img_width/20, img_width/10
    # screen the boundary
    contours, _ = cv2.findContours(post_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    edges = []
    for obj in contours:
        perimeter = cv2.arcLength(obj, True)
        approx = cv2.approxPolyDP(obj, 0.02*perimeter, True)# acquire corner coordinates
        corner_num = len(approx)
        x, y, w, h = cv2.boundingRect(approx)
        # screening process
        if corner_num == 4 and w == h:
            if w >= min_edge and w <= max_edge:
                edges.append(w)
        else:
            continue
    len_unit = np.argmax(np.bincount(edges))
    square_unit = np.square(len_unit)
    # write the parameters into file
    param_filename = "utils/units.py"
    try:
        os.remove(param_filename)
    except:
        pass
    with open(param_filename, 'w') as file:
        file.write(f"length_unit = {len_unit}\n")
        file.write(f"square_unit = {square_unit}")
    return f"Unit file generated successfully, the length unit: {len_unit} pixels; the area unit: {square_unit} pixels."

# for webui use
def unit_cal_ui(image_pil, ksize=6):
    # convert pil into cv2
    img = cv2.cvtColor(np.asarray(image_pil), cv2.COLOR_RGB2BGR)
    # calculation
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel = np.ones((ksize, ksize), np.uint8)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    post_img = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # set the range of edge width
    img_width = img.shape[1]
    min_edge, max_edge = img_width/20, img_width/10
    # screen the boundary
    contours, _ = cv2.findContours(post_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    edges = []
    for obj in contours:
        perimeter = cv2.arcLength(obj, True)
        approx = cv2.approxPolyDP(obj, 0.02*perimeter, True)# acquire corner coordinates
        corner_num = len(approx)
        x, y, w, h = cv2.boundingRect(approx)
        # screening process
        if corner_num == 4 and w == h:
            if w >= min_edge and w <= max_edge:
                edges.append(w)
        else:
            continue
    len_unit = np.argmax(np.bincount(edges))
    square_unit = np.square(len_unit)
    # write the parameters into file
    param_filename = "utils/units.py"
    try:
        os.remove(param_filename)
    except:
        pass
    with open(param_filename, 'w') as file:
        file.write(f"length_unit = {len_unit}\n")
        file.write(f"square_unit = {square_unit}")
    return f"Unit file generated successfully, the length unit: {len_unit} pixels/mm; the area unit: {square_unit} pixels/mm^2."


# params setting
def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument("--img_path", type=str, default="utils/metric/metric.png", help="image path")
    parser.add_argument("--ksize", type=int, default=6, help="setting kernel size for close process")
    opt = parser.parse_args()
    return opt

def main(opt):
    try:
        unit_cal(**vars(opt))
        print("unit file generated.")
    except:
        print("Please ensure the metric-using image 'metric.png' has been put in 'utils/metric/' folder.")

if __name__ == "__main__":
    opt = parse_opt()
    main(opt)