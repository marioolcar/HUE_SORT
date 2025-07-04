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
    <title>HUE SORT</title>
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
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
            cursor: pointer;
        }
        .image-item img {
            width: 100%;
            height: 200px;
            border-radius: 8px;
            object-fit: cover;
            transition: all 0.3s ease;
        }
        .image-item p {
            margin-top: 10px;
            font-size: 0.95em;
            color: #444;
            word-wrap: break-word;
        }

        /* Modal */
        .modal {
            display: none;
            position: fixed;
            z-index: 999;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.85);
            justify-content: center;
            align-items: center;
        }
        .modal-content img {
            max-height: 90vh;
            max-width: 90vw;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .close, .nav-btn {
            position: absolute;
            top: 20px;
            color: white;
            font-size: 30px;
            font-weight: bold;
            background: rgba(0,0,0,0.3);
            padding: 10px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
        }
        .close {
            right: 30px;
        }
        .nav-btn {
            top: 50%;
            transform: translateY(-50%);
        }
        #prevBtn {
            left: 30px;
        }
        #nextBtn {
            right: 30px;
        }

        @media screen and (max-width: 500px) {
            .image-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <h1>Dominantne boje i sortiranje po tonu</h1>
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

# Image grid with modal trigger
for i, item in enumerate(image_data_sorted):
    html += f"""
    <div class="image-item" onclick="openModal({i})">
        <img src="data:image/jpeg;base64,{item['base64']}" alt="Slika {i+1}">
        <p><strong>{i+1}. {item['filename']}</strong><br>Hue: {item['hue']:.2f}</p>
    </div>
    """

# Modal HTML
html += """
</div>

<div id="modal" class="modal" onclick="backgroundClose(event)">
    <button class="close" onclick="closeModal()">&times;</button>
    <button class="nav-btn" id="prevBtn" onclick="prevImage(event)">&#10094;</button>
    <div class="modal-content" id="modal-content">
        <img id="modal-img" src="" alt="Fullscreen slika">
    </div>
    <button class="nav-btn" id="nextBtn" onclick="nextImage(event)">&#10095;</button>
</div>

<script>
    const images = ["""

# pics into base64 for HTML
html += ",".join([f'"data:image/jpeg;base64,{item["base64"]}"' for item in image_data_sorted])

html += """];
    let currentIndex = 0;

    function openModal(index) {
        currentIndex = index;
        const modal = document.getElementById("modal");
        const modalImg = document.getElementById("modal-img");
        modalImg.src = images[currentIndex];
        modal.style.display = "flex";
    }

    function closeModal() {
        document.getElementById("modal").style.display = "none";
    }

    function backgroundClose(event) {
        if (event.target.id === "modal") {
            closeModal();
        }
    }

    function nextImage(event) {
        event.stopPropagation();
        currentIndex = (currentIndex + 1) % images.length;
        document.getElementById("modal-img").src = images[currentIndex];
    }

    function prevImage(event) {
        event.stopPropagation();
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        document.getElementById("modal-img").src = images[currentIndex];
    }

    // Keyboard navigation
    document.addEventListener("keydown", function(event) {
        const modal = document.getElementById("modal");
        if (modal.style.display === "flex") {
            if (event.key === "ArrowRight") nextImage(event);
            else if (event.key === "ArrowLeft") prevImage(event);
            else if (event.key === "Escape") closeModal();
        }
    });
</script>

</body>
</html>
"""


# === 5. SAVE HTML ===
with open("output.html", "w", encoding="utf-8") as f:
    f.write(html)

print("HTML generiran: output.html")
