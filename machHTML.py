import cv2
import numpy as np
import sys
import os
from glob import glob
from sklearn.cluster import KMeans
import base64
from io import BytesIO
from PIL import Image

# === 1. UČITAJ SLIKE ===

try:
    FOLDER_PATH = sys.argv[1]
except IndexError:
    print("Molimo navedite putanju do foldera sa slikama kao argument.")
    sys.exit(1)

image_paths = glob(os.path.join(FOLDER_PATH, '*.jpg'))  # ili *.png
images = [cv2.imread(path) for path in image_paths]

# === 2. FUNKCIJE ZA ANALIZU ===

def resize_for_analysis(image, size=(100, 100)):
    return cv2.resize(image, size)

def dominant_color(image, k=3):
    img = resize_for_analysis(image)
    img = img.reshape((-1, 3))
    kmeans = KMeans(n_clusters=k, n_init='auto').fit(img)
    return kmeans.cluster_centers_[0]  # RGB

def brightness(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv[..., 2].mean()

def hue(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    return hsv[..., 0].mean()

def image_to_base64(img_bgr):
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(img_rgb)
    buffer = BytesIO()
    pil_img.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

# === 3. ANALIZIRAJ I SORTIRAJ SLIKE ===

image_data = []
for path, img in zip(image_paths, images):
    d_color = dominant_color(img)
    bright = brightness(img)
    h = hue(img)
    image_data.append({
        'path': path,
        'filename': os.path.basename(path),
        'image': img,
        'dominant_color': d_color,
        'brightness': bright,
        'hue': h,
        'base64': image_to_base64(img)
    })

image_data_sorted = sorted(image_data, key=lambda x: x['hue'])

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % (int(rgb[2]), int(rgb[1]), int(rgb[0]))  # BGR to RGB

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Pregled slika i boja</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background-color: #f9f9f9;
            margin: 0;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 40px;
        }
        .color-strip {
            display: flex;
            flex-wrap: nowrap;
            overflow-x: auto;
            margin-bottom: 40px;
            border: 1px solid #ddd;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .color-block {
            width: 60px;
            height: 50px;
            flex: 0 0 auto;
            position: relative;
            cursor: pointer;
        }
        .color-block:hover .tooltip {
            opacity: 1;
            visibility: visible;
        }
        .tooltip {
            position: absolute;
            bottom: -35px;
            left: 50%;
            transform: translateX(-50%);
            background-color: #333;
            color: #fff;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s;
            z-index: 10;
        }

        .image-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 25px;
            justify-items: center;
        }
        .image-item {
            background: #fff;
            border-radius: 12px;
            padding: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            text-align: center;
            width: 100%;
            box-sizing: border-box;
            transition: transform 0.2s ease;
        }
        .image-item:hover {
            transform: scale(1.02);
        }
        .image-item img {
            width: 100%;
            height: 200px;
            border-radius: 8px;
            object-fit: cover;
        }
        .image-item p {
            margin-top: 10px;
            font-size: 0.95em;
            color: #444;
            word-wrap: break-word;
        }

        @media screen and (max-width: 1000px) {
            .image-grid {
                grid-template-columns: repeat(3, 1fr);
            }
        }
        @media screen and (max-width: 700px) {
            .image-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        @media screen and (max-width: 500px) {
            .image-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <h1>Dominantne boje i slike sortirane po Hue</h1>
    <div class="color-strip">
"""

# Color strip with tooltip
for item in image_data_sorted:
    color = np.uint8(item['dominant_color']).tolist()
    hex_color = rgb_to_hex(color)
    html += f'''
        <div class="color-block" style="background-color: rgb({color[2]}, {color[1]}, {color[0]});">
            <div class="tooltip">{hex_color}</div>
        </div>
    '''

html += "</div>\n<div class='image-grid'>\n"

# Image grid
for i, item in enumerate(image_data_sorted):
    html += f"""
    <div class="image-item">
        <img src="data:image/jpeg;base64,{item['base64']}" alt="Slika {i+1}">
        <p><strong>{i+1}. {item['filename']}</strong><br>Hue: {item['hue']:.2f}</p>
    </div>
    """

html += "</div>\n</body>\n</html>"



# === 5. SAVE HTML ===
with open("output.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML generiran: output.html")
