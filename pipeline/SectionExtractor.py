import os
import re
import json
import math
import numpy as np
import tempfile
import torch
import fitz # PyMuPDF
from PIL import Image
from PostProcess import PostProcess
from paddleocr import FormulaRecognition, PaddleOCRVL

class SectionCrop:
    @staticmethod
    def crop(coordinates):
        if not coordinates:
            return []

        input_path = coordinates[0]["input_path"]
        doc = fitz.open(input_path)

        dpi = 250
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)

        cropped_images = []
        for page_data in coordinates:
            page_idx = page_data["page_idx"]
            if page_idx >= len(doc):
                continue

            page = doc[page_idx]

            for box in page_data["boxes"]:
                x0, y0, x1, y1 = box["pdf_bbox"]
                clip = fitz.Rect(x0, y0, x1, y1)

                pix = page.get_pixmap(matrix=mat, clip=clip)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                cropped_images.append({
                    "page_idx": page_idx,
                    "order": box["order"],
                    "label": box["label"],
                    "image": img
                })

        doc.close()
        return cropped_images

    @staticmethod
    def save_images(cropped_images, output_path, input_path):
        os.makedirs(output_path, exist_ok=True)
        pdf_name = os.path.splitext(os.path.basename(input_path))[0]
        
        for i, crop_data in enumerate(cropped_images, start=1):
            label = crop_data["label"]
            image = crop_data["image"]
            
            filename = f"{pdf_name}_{label}_{i}.png"
            image_path = os.path.join(output_path, filename)
            image.save(image_path)

class TextExtract:
    def __init__(self):
        self.extracted_text = None
        self.empty_regions = None
        self.input_path = None
        self.post_processor = PostProcess()

    def map_words_to_boxes(self, page, layout_boxes):
        all_words = page.get_text("words")
        
        box_contents = {i: [] for i in range(len(layout_boxes))}

        for word in all_words:
            wx0, wt, wx1, wb, text = word[0], word[1], word[2], word[3], word[4]
            
            word_area = (wx1 - wx0) * (wb - wt) + 1e-9
            
            candidates = []
            for idx, box in enumerate(layout_boxes):
                bx0, bt, bx1, bb = box["pdf_bbox"]
                
                ix0 = max(wx0, bx0)
                it  = max(wt, bt)
                ix1 = min(wx1, bx1)
                ib  = min(wb, bb)
                
                if ix1 > ix0 and ib > it:
                    inter_area = (ix1 - ix0) * (ib - it)
                    iow_score = inter_area / word_area
                    box_area = (bx1 - bx0) * (bb - bt)
                    candidates.append({
                        "idx": idx,
                        "iow": iow_score,
                        "area": box_area
                    })
            
            if candidates:
                best_box = sorted(candidates, key=lambda x: (-x["iow"], x["area"]))[0]
                box_contents[best_box["idx"]].append(text)

        return box_contents

    def extract(self, layout_results):
        final_output = []
        empty_output = []
            
        self.input_path = layout_results[0]["input_path"]
        
        doc = fitz.open(self.input_path)
        
        for page_data in layout_results:
            page_idx = page_data.get("page_idx", 0)
            if page_idx >= len(doc): break
            
            page = doc[page_idx]
            boxes = page_data.get("boxes", [])
            
            box_contents = self.map_words_to_boxes(page, boxes)
            
            page_boxes = []
            page_empty_boxes = []
            for idx, box in enumerate(boxes):
                text_list = box_contents[idx]
                region = box.copy()
                
                if text_list:
                    raw_text = " ".join(text_list)
                    region["result"] = self.post_processor.process(raw_text)
                else:
                    region["result"] = ""
                    page_empty_boxes.append(region.copy())
                
                page_boxes.append(region)
            
            final_output.append({
                "input_path": self.input_path,
                "page_idx": page_idx,
                "image_size": page_data.get("image_size"),
                "pdf_size": page_data.get("pdf_size"),
                "boxes": page_boxes
            })
            
            if page_empty_boxes:
                empty_output.append({
                    "input_path": self.input_path,
                    "page_idx": page_idx,
                    "image_size": page_data.get("image_size"),
                    "pdf_size": page_data.get("pdf_size"),
                    "boxes": page_empty_boxes
                })

        doc.close()
        self.extracted_text = final_output
        self.empty_regions = empty_output
        return final_output, empty_output

    def save_results(self, output_path):
        if not self.extracted_text:
            return

        os.makedirs(output_path, exist_ok=True)
            
        pdf_name = os.path.splitext(os.path.basename(self.input_path))[0]
            
        json_path = os.path.join(output_path, f"{pdf_name}_text_results.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.extracted_text, f, ensure_ascii=False, indent=4)
            
        empty_path = os.path.join(output_path, f"{pdf_name}_text_empty_coordinates.json")
        with open(empty_path, "w", encoding="utf-8") as f:
            json.dump(self.empty_regions, f, ensure_ascii=False, indent=4)

class TableExtract:
    def __init__(self):
        self.results = None
        self.input_path = None

    def extract(self, table_coordinates):
        if not table_coordinates:
            return []
        self.input_path = table_coordinates[0]["input_path"]
        cropped = SectionCrop.crop(table_coordinates)
        # TODO: feed cropped images to TableFormer model
        self.results = cropped
        return cropped

    def save_results(self, output_path):
        if not self.results:
            return
        SectionCrop.save_images(self.results, output_path, self.input_path)

class MathExtract:
    def __init__(self, model="PP-FormulaNet_plus-L"):
        self.model = FormulaRecognition(model_name=model)
        self.results = None
        self.input_path = None

    def extract(self, math_coordinates):
        self.input_path = math_coordinates[0]["input_path"]
        cropped_info = SectionCrop.crop(math_coordinates)
        if not cropped_info:
            return []
            
        # FormulaRecognition only supports numpy.ndarray or str
        images = [np.array(c["image"]) for c in cropped_info]
        # predict returns a list of results. For PP-FormulaNet, it's a list of strings (LaTeX formulas).
        predictions = self.model.predict(input=images, batch_size=4)
        
        # Mapping predictions back to the original structure
        predictions = list(predictions)
        final_output = []
        pred_idx = 0
        for page_data in math_coordinates:
            new_page = page_data.copy()
            new_boxes = []
            for box in page_data.get("boxes", []):
                new_box = box.copy()
                if pred_idx < len(predictions):
                    new_box["result"] = predictions[pred_idx].json["res"].get("rec_formula", "")
                    pred_idx += 1
                else:
                    new_box["result"] = ""
                new_boxes.append(new_box)
            new_page["boxes"] = new_boxes
            final_output.append(new_page)
            
        self.results = final_output
        return final_output

    def save_results(self, output_path):
        if not self.results or not self.input_path:
            return

        os.makedirs(output_path, exist_ok=True)
        pdf_name = os.path.splitext(os.path.basename(self.input_path))[0]
        json_path = os.path.join(output_path, f"{pdf_name}_math_results.json")
        
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.results, ensure_ascii=False, indent=4).replace('\\\\', '\\'))

class VLMExtract:
    def __init__(self):
        self.model = PaddleOCRVL()
        self.input_path = None
        self.cropped_images = None       

    def partial_extract(self, empty_coordinates):
        self.input_path = empty_coordinates[0]["input_path"]
        cropped_info = SectionCrop.crop(empty_coordinates)
        self.cropped_images = cropped_info
        if not cropped_info:
            return []

        images=[np.array(c["image"]) for c in cropped_info]
        predictions = self.model.predict(input=images)

        final_output = []
        pred_idx = 0
        for page_data in empty_coordinates:
            new_page = page_data.copy()
            new_boxes = []
            for box in page_data.get("boxes", []):
                new_box = box.copy()
                if pred_idx < len(predictions):
                    res_json = predictions[pred_idx].json["res"]
                    blocks = res_json.get("parsing_res_list", [])
                    new_box["result"] = "\n".join(b["block_content"] for b in blocks if b.get("block_content"))
                    pred_idx += 1
                else:
                    new_box["result"] = ""
                new_boxes.append(new_box)
            new_page["boxes"] = new_boxes
            final_output.append(new_page)

        self.empty_results = final_output
        return final_output

    def full_extract(self, input_path):
        self.input_path = input_path
        self.full_results = self.model.predict(input=input_path)
        return self.full_results        


    def save_partial_results(self, output_path):
        if not self.cropped_images or not hasattr(self, 'empty_results'):
            return
        
        SectionCrop.save_images(self.cropped_images, output_path, self.input_path)

        os.makedirs(output_path, exist_ok=True)
            
        pdf_name = os.path.splitext(os.path.basename(self.input_path))[0]
            
        json_path = os.path.join(output_path, f"{pdf_name}_text_empty_results.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.empty_results, f, ensure_ascii=False, indent=4)
    
    
    def save_full_results(self, output_path):
        if not hasattr(self, 'full_results') or not self.full_results:
            return
        
        os.makedirs(output_path, exist_ok=True)
        for res in self.full_results:
            res.save_to_json(save_path=output_path)
            res.save_to_markdown(save_path=output_path)


class Merge:
    @staticmethod
    def merge_results(text_results=None, vlm_results=None, math_results=None):
        merged = {}
        for result_list in [text_results, vlm_results, math_results]:
            if not result_list:
                continue
            for page_data in result_list:
                page_idx = page_data["page_idx"]
                if page_idx not in merged:
                    merged[page_idx] = {
                        "input_path": page_data["input_path"],
                        "page_idx": page_idx,
                        "image_size": page_data.get("image_size"),
                        "pdf_size": page_data.get("pdf_size"),
                        "boxes": {}
                    }
                for box in page_data.get("boxes", []):
                    order = box["order"]
                    if order not in merged[page_idx]["boxes"] or not merged[page_idx]["boxes"][order].get("result"):
                        merged[page_idx]["boxes"][order] = box
        final_pages = []
        for page_idx in sorted(merged.keys()):
            page = merged[page_idx]
            sorted_boxes = [page["boxes"][o] for o in sorted(page["boxes"].keys())]
            final_pages.append({
                "input_path": page["input_path"],
                "page_idx": page_idx,
                "image_size": page["image_size"],
                "pdf_size": page["pdf_size"],
                "boxes": sorted_boxes
            })
        return final_pages

    @staticmethod
    def markdown_results(merged_pages):
        lines = []
        for page in merged_pages:
            for box in page["boxes"]:
                result = box.get("result", "").strip()
                if result:
                    lines.append(result)
        return "\n\n".join(lines)

    @staticmethod
    def save_results(input_path, output_path, merged_pages, markdown):
        os.makedirs(output_path, exist_ok=True)
        pdf_name = os.path.splitext(os.path.basename(input_path))[0]

        json_path = os.path.join(output_path, f"{pdf_name}.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(merged_pages, f, ensure_ascii=False, indent=4)

        md_path = os.path.join(output_path, f"{pdf_name}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)
