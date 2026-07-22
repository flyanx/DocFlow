"""
Helper utility functions
"""
import os
import re
from pathlib import Path
from typing import List, Tuple, Optional
import tempfile


def get_file_type(file_path: str) -> str:
    """Detect file type by extension"""
    ext = Path(file_path).suffix.lower()
    if ext == '.pdf':
        return 'pdf'
    elif ext in ['.doc', '.docx']:
        return 'docx'
    elif ext in ['.xls', '.xlsx']:
        return 'xlsx'
    else:
        return 'unknown'


def ensure_dir(dir_path: str):
    """Ensure directory exists"""
    os.makedirs(dir_path, exist_ok=True)


def get_safe_filename(filename: str) -> str:
    """Generate safe filename"""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename


def get_output_path(input_path: str, output_dir: str, base_name: str = None) -> str:
    """Generate output file path from input"""
    input_name = base_name or Path(input_path).stem
    safe_name = get_safe_filename(input_name)
    return os.path.join(output_dir, f"{safe_name}.docx")


def check_cuda_available() -> Tuple[bool, Optional[str]]:
    """Check CUDA availability (lazy import torch)"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            return True, f"{gpu_name} ({gpu_memory:.1f}GB)"
        return False, None
    except Exception:
        return False, None


def check_gpu_memory() -> float:
    """Check GPU VRAM in GB (lazy import torch)"""
    try:
        import torch
        if torch.cuda.is_available():
            return torch.cuda.get_device_properties(0).total_memory / (1024**3)
        return 0.0
    except Exception:
        return 0.0


def is_enhance_mode_available() -> bool:
    """Check if enhanced mode is available (needs >=10GB VRAM)"""
    has_cuda, _ = check_cuda_available()
    if not has_cuda:
        return False
    memory = check_gpu_memory()
    return memory >= 10.0


def create_temp_dir() -> str:
    """Create temp directory"""
    return tempfile.mkdtemp()


def clean_temp_dir(temp_dir: str):
    """Clean up temp directory"""
    import shutil
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)
