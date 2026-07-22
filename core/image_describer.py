"""
Image Describer - Local Qwen-VL model (Enhanced Mode)
Only loaded when enhanced mode is enabled.
"""
import os
from PIL import Image
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class ImageDescriber:
    """Image Describer - uses local Qwen-VL model"""

    def __init__(self, model_dir: str = "models/Qwen-VL-Chat-Int4"):
        self.model_dir = model_dir
        self.model = None
        self.tokenizer = None
        self.device = None
        self._initialized = False
        self._torch = None

    def initialize(self) -> bool:
        """Initialize model (lazy import torch)"""
        try:
            import torch
            self._torch = torch

            from transformers import AutoModelForCausalLM, AutoTokenizer
            from modelscope import snapshot_download

            logger.info("Initializing Qwen-VL model...")

            if not torch.cuda.is_available():
                logger.warning("CUDA not detected, enhanced mode unavailable")
                return False

            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            if gpu_memory < 10.0:
                logger.warning(f"GPU memory insufficient: {gpu_memory:.1f}GB < 10GB")
                return False

            model_id = "qwen/Qwen-VL-Chat-Int4"
            if not os.path.exists(self.model_dir) or len(os.listdir(self.model_dir)) == 0:
                logger.info(f"Downloading model from ModelScope: {model_id}")
                logger.info("First download takes ~5-10 min, please wait...")
                self.model_dir = snapshot_download(model_id, cache_dir="models")
                logger.info(f"Model downloaded: {self.model_dir}")

            self.device = "cuda"
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_dir, trust_remote_code=True
            )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_dir, device_map="cuda", trust_remote_code=True
            ).eval()

            self._initialized = True
            logger.info("Qwen-VL model ready")
            return True

        except Exception as e:
            logger.error(f"Qwen-VL init failed: {e}")
            return False

    def describe_for_knowledge_base(self, image_path: str, ocr_text: str = "") -> str:
        """Generate structured description for knowledge base"""
        if not self._initialized or self.model is None:
            if ocr_text:
                return f"[Image Content - OCR]\n{ocr_text}"
            return ""

        try:
            prompt = """Analyze this scientific image and output in this format:

[Image Type]: (e.g., bar chart, line graph, Western Blot, microscopy photo, flow chart, PPT screenshot)
[Main Content]: (2-3 sentences summarizing the key information)
[Key Data/Findings]: (important data, trends, comparison results)
[Text Labels]: (title, caption, axis labels, etc.)

If unclear, state "Image content cannot be clearly identified".
Answer in Chinese."""

            if ocr_text:
                prompt += f"\n\nRecognized text in image: {ocr_text}"

            query = self.tokenizer.from_list_format([
                {'image': image_path},
                {'text': prompt}
            ])

            with self._torch.no_grad():
                response, _ = self.model.chat(
                    self.tokenizer, query=query, history=None
                )

            return response.strip()

        except Exception as e:
            logger.error(f"Description failed: {e}")
            if ocr_text:
                return f"[Image Content - OCR]\n{ocr_text}"
            return ""

    def is_available(self) -> bool:
        return self._initialized and self.model is not None

    def unload(self):
        """Unload model to free VRAM"""
        if self.model is not None:
            del self.model
            self.model = None
        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None
        if self._torch is not None:
            self._torch.cuda.empty_cache()
        self._initialized = False
        logger.info("Qwen-VL model unloaded")
