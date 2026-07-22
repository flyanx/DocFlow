"""
OCR Engine - based on RapidOCR (lightweight, no PaddlePaddle needed)
Falls back to EasyOCR if RapidOCR unavailable.
"""
import os
import numpy as np
from PIL import Image
from typing import List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class OCREngine:
    """OCR Engine wrapper"""

    def __init__(self, use_gpu: bool = False):
        self.use_gpu = use_gpu
        self.ocr = None
        self._engine_type = None  # 'rapidocr' or 'easyocr'
        self._init_ocr()

    def _init_ocr(self):
        """Initialize OCR engine, try RapidOCR first, then EasyOCR"""
        # Try RapidOCR (lightweight, fast, good Chinese support)
        try:
            from rapidocr_onnxruntime import RapidOCR
            logger.info("Initializing RapidOCR...")
            self.ocr = RapidOCR()
            self._engine_type = 'rapidocr'
            logger.info("RapidOCR initialized")
            return
        except ImportError:
            logger.info("RapidOCR not available, trying EasyOCR...")

        # Fallback to EasyOCR
        try:
            import easyocr
            logger.info("Initializing EasyOCR...")
            self.ocr = easyocr.Reader(['ch_sim', 'en'], gpu=self.use_gpu)
            self._engine_type = 'easyocr'
            logger.info("EasyOCR initialized")
            return
        except ImportError:
            logger.error("No OCR engine available. Please install rapidocr_onnxruntime or easyocr")
            raise RuntimeError(
                "No OCR engine found. Run: pip install rapidocr_onnxruntime"
            )

    def recognize_text(self, image_path: str) -> str:
        """Recognize text in image"""
        if self.ocr is None:
            return ""

        try:
            if self._engine_type == 'rapidocr':
                raw = self._recognize_rapidocr(image_path)
            elif self._engine_type == 'easyocr':
                raw = self._recognize_easyocr(image_path)
            else:
                return ""
            return self._clean_ocr_text(raw)
        except Exception as e:
            logger.error(f"OCR failed for {image_path}: {e}")
            return ""

    @staticmethod
    def _clean_ocr_text(text: str) -> str:
        """
        Clean OCR text for knowledge base compatibility:
        - Merge consecutive blank lines into one
        - Merge very short lines (< 10 chars) into previous line if no punctuation ending
        """
        if not text:
            return ""

        lines = text.split('\n')
        cleaned = []

        for line in lines:
            stripped = line.strip()

            # Skip empty lines (will add paragraph break only between real content)
            if not stripped:
                if cleaned and cleaned[-1] != '':
                    cleaned.append('')  # Single blank line as paragraph break
                continue

            # Merge short lines into previous line
            # (e.g., PPT slides often have fragmented text)
            if (len(stripped) < 10
                    and cleaned
                    and cleaned[-1] != ''
                    and not cleaned[-1].endswith(('。', '，', '；', '：', '！', '？', '.', ',', ';', ':', '!', '?'))
                    and not stripped.startswith(('•', '-', '–', '·', '1', '2', '3', '4', '5', '6', '7', '8', '9'))):
                cleaned[-1] = cleaned[-1] + stripped
            else:
                cleaned.append(stripped)

        # Remove trailing empty line
        while cleaned and cleaned[-1] == '':
            cleaned.pop()

        return '\n'.join(cleaned)

    def _recognize_rapidocr(self, image_path: str) -> str:
        """RapidOCR recognition"""
        result, _ = self.ocr(image_path)
        if not result:
            return ""
        texts = [line[1] for line in result]
        return "\n".join(texts)

    def _recognize_easyocr(self, image_path: str) -> str:
        """EasyOCR recognition"""
        results = self.ocr.readtext(image_path)
        if not results:
            return ""
        texts = [item[1] for item in results]
        return "\n".join(texts)

    def recognize_table(self, image_path: str) -> Optional[List[List[str]]]:
        """
        Recognize table in image.
        Uses text recognition + simple grid detection.
        Returns 2D list of cell texts, or None if no table detected.
        """
        try:
            # Get all text with positions
            img = Image.open(image_path).convert('RGB')
            img_array = np.array(img)

            if self._engine_type == 'rapidocr':
                result, _ = self.ocr(image_path)
                if not result:
                    return None
                # Group text lines into rows by Y-coordinate
                lines_with_pos = []
                for line in result:
                    box = line[0]  # [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                    text = line[1]
                    y_center = (box[0][1] + box[2][1]) / 2
                    x_start = box[0][0]
                    lines_with_pos.append((y_center, x_start, text))

                if not lines_with_pos:
                    return None

                # Cluster into rows (lines within 15px Y distance)
                lines_with_pos.sort(key=lambda x: (x[0], x[1]))
                rows = []
                current_row = [lines_with_pos[0]]
                for item in lines_with_pos[1:]:
                    if abs(item[0] - current_row[-1][0]) < 15:
                        current_row.append(item)
                    else:
                        rows.append(current_row)
                        current_row = [item]
                rows.append(current_row)

                # Sort each row by X position
                table_data = []
                for row in rows:
                    row.sort(key=lambda x: x[1])
                    table_data.append([item[2] for item in row])

                # Only return if looks like a table (multiple rows with similar col count)
                if len(table_data) >= 2:
                    return table_data
                return None

            elif self._engine_type == 'easyocr':
                results = self.ocr.readtext(image_path)
                if not results:
                    return None

                lines_with_pos = []
                for item in results:
                    bbox = item[0]
                    text = item[1]
                    y_center = (bbox[0][1] + bbox[2][1]) / 2
                    x_start = bbox[0][0]
                    lines_with_pos.append((y_center, x_start, text))

                if not lines_with_pos:
                    return None

                lines_with_pos.sort(key=lambda x: (x[0], x[1]))
                rows = []
                current_row = [lines_with_pos[0]]
                for item in lines_with_pos[1:]:
                    if abs(item[0] - current_row[-1][0]) < 15:
                        current_row.append(item)
                    else:
                        rows.append(current_row)
                        current_row = [item]
                rows.append(current_row)

                table_data = []
                for row in rows:
                    row.sort(key=lambda x: x[1])
                    table_data.append([item[2] for item in row])

                if len(table_data) >= 2:
                    return table_data
                return None

        except Exception as e:
            logger.error(f"Table recognition failed for {image_path}: {e}")
            return None
        return None
