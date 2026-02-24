from Analyzer import Analyze
from LayoutDetector import LayoutDetect
from SectionExtractor import TextExtract, TableExtract, MathExtract, VLMExtract

def main():
    input_path = "pdfs/stress_test_no_text_layer.pdf"

    analyzer = Analyze()
    detector = LayoutDetect()
    text_extractor = TextExtract()
    table_extractor = TableExtract()
    math_extractor = MathExtract()
    vlm_extractor = VLMExtract()

    if analyzer.has_text_layer(input_path):
        layout_coordinates = detector.detect(input_path)
        text_coordinates, table_coordinates, math_coordinates = detector.filter(layout_coordinates)
        detector.save_results("output") # For visual debugging

        # <section>_coordinates are never truly empty so create functions that check them
        if text_coordinates:
            text_results, text_results_empty = text_extractor.extract(text_coordinates)
            text_extractor.save_results("output") # For visual debugging

            # If there are empty regions detected, send them to the VLM to extract
            if text_results_empty:
                vlm_extractor.partial_extract(text_results_empty)
                vlm_extractor.save_results("output") # For visual debugging

        if table_coordinates:
            table_extractor.extract(table_coordinates)
            table_extractor.save_results("output") # For visual debugging

        # if math_coordinates:
        #     math_extractor.extract(math_coordinates)
        #     math_extractor.save_results("output") # For visual debugging

    else:
        # vlm_extractor.full_extract(input_path)
        # vlm_extractor.save_results("output") # For visual debugging

if __name__ == "__main__":
    main()