import streamlit as st
import json
from PIL import Image, ImageDraw
import os

# Load COCO JSON annotation
@st.cache_data
def load_annotations(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)

    image_id_map = {img['file_name']: img for img in data['images']}
    annotations_by_id = {}
    for ann in data['annotations']:
        img_id = ann['image_id']
        if img_id not in annotations_by_id:
            annotations_by_id[img_id] = []
        annotations_by_id[img_id].append(ann)

    categories = {cat["id"]: cat["name"] for cat in data["categories"]}
    return image_id_map, annotations_by_id, categories

# Draw bounding boxes
def draw_bboxes(image, anns, categories):
    draw = ImageDraw.Draw(image)
    for ann in anns:
        x, y, w, h = ann["bbox"]
        cat_id = ann["category_id"]
        cat_name = categories.get(cat_id, "unknown")
        draw.rectangle([x, y, x + w, y + h], outline="red", width=3)
        draw.text((x, y - 10), cat_name, fill="red")
    return image

# Streamlit UI
st.title("📦 COCO Annotation Viewer")

json_file = "Raccoon.v38-416x416-resize.coco/train/_annotations.coco.json"
image_id_map, annotations_by_id, categories = load_annotations(json_file)

# Dropdown to select multiple images from JSON dataset
image_list = list(image_id_map.keys())
selected_files = st.multiselect("Choose one or more images from JSON dataset", image_list)

# Upload multiple images manually
uploaded_imgs = st.file_uploader("Upload one or more images (optional)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# Priority: uploaded images → selected images from JSON
if uploaded_imgs:
    for uploaded_img in uploaded_imgs:
        img_name = uploaded_img.name
        image = Image.open(uploaded_img).convert("RGB")
        st.image(image, caption=f"Uploaded: {img_name}", use_column_width=True)

        # Match filename
        matching_key = next((k for k in image_id_map if img_name in k), None)

        if matching_key:
            img_id = image_id_map[matching_key]['id']
            anns = annotations_by_id.get(img_id, [])
            if anns:
                image_with_boxes = draw_bboxes(image.copy(), anns, categories)
                st.image(image_with_boxes, caption=f"{img_name} with Bounding Boxes", use_column_width=True)
            else:
                st.warning(f"No annotations found for uploaded image: {img_name}")
        else:
            st.error(f"Uploaded image {img_name} not found in annotation JSON.")

elif selected_files:
    for selected_file in selected_files:
        img_info = image_id_map[selected_file]
        img_path = os.path.join("images", selected_file)  # assume images stored locally in 'images/' folder
        if os.path.exists(img_path):
            image = Image.open(img_path).convert("RGB")
            img_id = img_info['id']
            anns = annotations_by_id.get(img_id, [])
            image_with_boxes = draw_bboxes(image.copy(), anns, categories)
            st.image(image_with_boxes, caption=f"{selected_file} with Bounding Boxes", use_column_width=True)
        else:
            st.warning(f"Image file `{img_path}` not found locally.")