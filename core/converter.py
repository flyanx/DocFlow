"""
Core Converter - integrates all modules for document conversion
"""
import os
import shutil
from typing import List, Dict, Callable, Optional
from pathlib import Path
import logging

from core.parser import DocumentParser, PageContent
from core.ocr_engine import OCREngine
from core.image_describer import ImageDescriber
from core.docx_builder import DocxBuilder
from utils.helpers import get_output_path, create_temp_dir, clean_temp_dir, ensure_dir

logger = logging.getLogger(__name__)


class DocumentConverter:
    """Document Converter"""

    def __init__(self, output_dir: str = "output",
                 use_enhance_mode: bool = False,
                 progress_callback: Optional[Callable] = None):
        self.output_dir = output_dir
        self.use_enhance_mode = use_enhance_mode
        self.progress_callback = progress_callback
        self._batch_offset = 0.0
        self._batch_scale = 1.0

        ensure_dir(output_dir)

        # Initialize components
        self.ocr_engine = OCREngine(use_gpu=False)
        self.image_describer = ImageDescriber() if use_enhance_mode else None

        if use_enhance_mode and self.image_describer:
            success = self.image_describer.initialize()
            if not success:
                logger.warning("Enhanced mode init failed, falling back to normal mode")
                self.use_enhance_mode = False
                self.image_describer = None

    def _update_progress(self, progress: float, message: str):
        # Map 0-1 internal progress to global batch progress
        global_progress = self._batch_offset + progress * self._batch_scale
        if self.progress_callback:
            self.progress_callback(min(global_progress, 1.0), message)
        logger.info(f"[{global_progress:.0%}] {message}")

    def convert(self, input_path: str, base_name: str = None) -> str:
        input_name = base_name or Path(input_path).name
        output_path = get_output_path(input_path, self.output_dir, base_name=base_name)

        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except PermissionError:
                logger.warning(f"Output file is locked, using alternate name: {input_name}")
                stem = (base_name or Path(input_path).stem)
                output_path = os.path.join(self.output_dir, f"{stem}_{hash(input_path) % 10000:04d}.docx")

        temp_dir = create_temp_dir()

        try:
            self._update_progress(0.05, f"Processing: {input_name}")

            # 1. Parse document
            self._update_progress(0.10, "Parsing document structure...")
            parser = DocumentParser(temp_dir)
            pages = parser.parse(input_path)

            # 2. Collect all images
            all_images = []
            for page in pages:
                all_images.extend(page.image_blocks)

            # 3. OCR
            ocr_results = {}
            if all_images:
                self._update_progress(0.30, f"OCR on {len(all_images)} image(s)...")
                for i, img_block in enumerate(all_images):
                    progress = 0.30 + (0.30 * i / len(all_images))
                    self._update_progress(progress, f"OCR image {i+1}/{len(all_images)}...")

                    ocr_text = self.ocr_engine.recognize_text(img_block.image_path)
                    if ocr_text:
                        ocr_results[img_block.image_path] = ocr_text

            # 4. AI image description (enhanced mode)
            descriptions = {}
            if self.use_enhance_mode and self.image_describer and self.image_describer.is_available():
                self._update_progress(0.60, f"AI description for {len(all_images)} image(s)...")
                for i, img_block in enumerate(all_images):
                    progress = 0.60 + (0.25 * i / len(all_images))
                    self._update_progress(progress, f"AI describe {i+1}/{len(all_images)}...")

                    ocr_text = ocr_results.get(img_block.image_path, "")
                    desc = self.image_describer.describe_for_knowledge_base(
                        img_block.image_path,
                        ocr_text
                    )
                    if desc:
                        descriptions[img_block.image_path] = desc

            # 5. Process image tables
            for page in pages:
                for table_block in page.table_blocks:
                    if table_block.is_image and os.path.exists(table_block.image_path):
                        table_data = self.ocr_engine.recognize_table(table_block.image_path)
                        if table_data:
                            table_block.data = table_data

            # 6. Build DOCX
            self._update_progress(0.90, "Generating DOCX...")
            builder = DocxBuilder(output_path)
            builder.add_metadata(
                title=Path(input_path).stem,
                description=f"Converted by Doc Converter | Mode: {'Enhanced' if self.use_enhance_mode else 'Normal'}"
            )
            builder.build(pages, ocr_results, descriptions)

            self._update_progress(1.0, f"Done: {input_name}")
            return output_path

        except Exception as e:
            logger.error(f"Conversion failed {input_name}: {e}")
            raise
        finally:
            clean_temp_dir(temp_dir)

    def convert_image(self, input_path: str, base_name: str = None) -> str:
        """Convert a bare image file (JPG, PNG, etc.) into a DOCX with OCR."""
        input_name = base_name or Path(input_path).name
        stem = base_name or Path(input_path).stem
        output_path = os.path.join(self.output_dir, f"{stem}.docx")

        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except PermissionError:
                output_path = os.path.join(self.output_dir, f"{stem}_{hash(input_path) % 10000:04d}.docx")

        self._update_progress(0.05, f"Processing image: {input_name}")

        # OCR the image
        ocr_text = ""
        self._update_progress(0.30, "OCR on image...")
        ocr_text = self.ocr_engine.recognize_text(input_path)

        # AI description (enhanced mode)
        description = ""
        if self.use_enhance_mode and self.image_describer and self.image_describer.is_available():
            self._update_progress(0.60, "AI image description...")
            description = self.image_describer.describe_for_knowledge_base(input_path, ocr_text)

        # Build DOCX
        self._update_progress(0.85, "Generating DOCX...")
        from core.docx_builder import DocxBuilder
        builder = DocxBuilder(output_path)
        builder.add_metadata(
            title=stem,
            description=f"Converted from image by DocFlow"
        )

        # Create a minimal page-like structure
        from core.parser import ImageBlock, PageContent
        img_block = ImageBlock(
            image_path=input_path,
            x=0, y=0, width=400, height=300,
            page_num=0
        )
        page = PageContent(
            page_num=0,
            text_blocks=[],
            image_blocks=[img_block],
            table_blocks=[],
            width=612, height=792
        )
        builder.build(
            [page],
            ocr_results={input_path: ocr_text} if ocr_text else {},
            descriptions={input_path: description} if description else {}
        )

        self._update_progress(1.0, f"Done: {input_name}")
        return output_path

    def convert_batch(self, input_paths: List[str]) -> List[str]:
        results = []
        total = len(input_paths)

        for i, input_path in enumerate(input_paths):
            try:
                self._batch_offset = i / total
                self._batch_scale = 1.0 / total
                output_path = self.convert(input_path)
                results.append(output_path)
            except Exception as e:
                logger.error(f"Skipping failed file {input_path}: {e}")
                results.append(None)

        return results

    def close(self):
        if self.image_describer:
            self.image_describer.unload()
