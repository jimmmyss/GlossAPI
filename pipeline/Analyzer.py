import fitz

class Analyze:
    @staticmethod
    def is_scanned(input_path):
        with fitz.open(input_path) as pdf:
            img_area, text_area = 0, 0
            for page in pdf:
                for img in page.get_image_info():
                    r = fitz.Rect(img["bbox"])
                    img_area += abs(r.width * r.height)
                for blk in page.get_text("blocks"):
                    if blk[6] == 0:  # Text block
                        r = fitz.Rect(blk[:4])
                        text_area += abs(r.width * r.height)
            return text_area < img_area
