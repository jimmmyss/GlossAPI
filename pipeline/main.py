from Analyzer import Analyze
from LayoutDetector import LayoutDetect
from SectionExtractor import TextExtract, TableExtract, MathExtract, VLMExtract, Merge

def main():
    input_path = "pdfs/stress_test_no_text_layer.pdf"

    text_extractor = TextExtract()
    # table_extractor = TableExtract()
    math_extractor = MathExtract()
    vlm_extractor = VLMExtract()

    if Analyze.is_scanned(input_path):
        print("Scanned PDF")
        vlm_extractor.full_extract(input_path)
        vlm_extractor.save_full_results("output") # For visual debugging

    else:
        text_results, vlm_results, math_results = [], [], []

        detector = LayoutDetect()
        layout_coordinates = detector.detect(input_path)
        text_coordinates, table_coordinates, math_coordinates = detector.filter(layout_coordinates)
        detector.save_results("output") # For visual debugging

        if text_coordinates:
            text_results, text_results_empty = text_extractor.extract(text_coordinates)
            text_extractor.save_results("output") # For visual debugging

            if text_results_empty:
                vlm_results = vlm_extractor.partial_extract(text_results_empty)
                vlm_extractor.save_partial_results("output") # For visual debugging

        # if table_coordinates:
        #     table_extractor.extract(table_coordinates)
        #     table_extractor.save_results("output") # For visual debugging

        if math_coordinates:
            math_results = math_extractor.extract(math_coordinates)
            math_extractor.save_results("output") # For visual debugging

        merged = Merge.merge_results(text_results=text_results, vlm_results=vlm_results, math_results=math_results)
        markdown = Merge.markdown_results(merged)
        Merge.save_results(input_path, "output", merged, markdown)

if __name__ == "__main__":
    main()