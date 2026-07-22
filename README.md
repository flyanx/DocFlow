<div align="center">

# DocFlow

**Convert PDF, Images & Office Documents to DOCX with OCR — Local, Private, No Upload**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](#)
[![Flask](https://img.shields.io/badge/Framework-Flask-000000.svg)](https://flask.palletsprojects.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](#contributing)

**100% Local · Privacy-First · No Document Uploads**

[English](README.md) · [简体中文](README.zh-CN.md)

</div>

---

DocFlow is a **zero-code, fully local** document conversion tool that batch-converts **PDF, images, and Office documents** into editable **DOCX** files. It features **OCR text recognition** (RapidOCR), **AI image description** (Qwen-VL), and **table restoration** — all running locally with **no document ever leaving your machine**.

![DocFlow](assets/icon.jpg)

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Multi-format Input** | PDF, DOCX, XLS, XLSX, JPG, PNG, GIF, BMP, WebP, TIFF |
| **Batch Processing** | Drag & drop multiple files, track progress per file |
| **OCR Text Recognition** | Powered by RapidOCR — extracts text from images, scans, and PPT screenshots; supports Chinese-English mixed text |
| **AI Image Description** | Enhanced mode uses Qwen-VL local multimodal model to generate semantic descriptions for images |
| **Table Restoration** | Converts image-based tables into editable DOCX tables |
| **Bilingual UI** | Chinese / English one-click switch |
| **100% Local & Private** | No internet required, no document uploads — your data stays on your machine |

## 🆚 Why DocFlow?

| | DocFlow | Online Converters | Adobe Acrobat |
|---|---------|-------------------|---------------|
| **Privacy** | ✅ 100% local, no upload | ❌ Files uploaded to server | ⚠️ Partial |
| **OCR** | ✅ Built-in (RapidOCR) | ⚠️ Some have it | ✅ Yes |
| **AI Image Description** | ✅ Qwen-VL | ❌ No | ❌ No |
| **Batch Conversion** | ✅ Free | ⚠️ Often paid | ✅ Paid |
| **Cost** | ✅ Free & Open Source | ⚠️ Freemium | ❌ Expensive |
| **No Account Needed** | ✅ | ❌ Sign-up required | ❌ Subscription |

## 🚀 Quick Start

### Prerequisites

- **OS**: Windows 10 or later
- **Python**: 3.10 – 3.13 ([Download](https://www.python.org/downloads/), check "Add Python to PATH")
- **Enhanced mode** (optional): NVIDIA GPU with 10GB+ VRAM

### Installation

**Option A — One-click install (recommended):**

Double-click `install.bat` and wait for dependencies to finish.

**Option B — Manual install:**

```bash
# Create virtual environment (recommended)
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run

Double-click `run.bat` (or run `run.ps1` in PowerShell). Your browser will open at http://localhost:7860 automatically.

## 📖 Usage

### Two Conversion Modes

| Mode | Features | Hardware |
|------|----------|----------|
| **Standard Mode** | Preserve original images + OCR text recognition | Any computer |
| **Enhanced Mode** | Adds AI image description (Qwen-VL) | NVIDIA GPU, 10GB+ VRAM |

### Steps

1. **Add files** — Click or drag files into the upload area
2. **Select mode** — Standard (any PC) or Enhanced (requires NVIDIA GPU)
3. **Set output path** — Click "Browse" to choose output folder
4. **Start conversion** — Click "Convert" and watch real-time progress
5. **View results** — Click "Open" to jump to the output folder

## 🏗️ Project Structure

```
DocFlow/
├── app.py                  # Flask backend main application
├── run.bat                 # Windows launcher
├── run.ps1                 # PowerShell launcher
├── install.bat             # One-click installer
├── requirements.txt        # Python dependencies
├── LICENSE                 # MIT License
├── README.md               # English docs
├── README.zh-CN.md         # Chinese docs
├── assets/                 # Icons & images
├── core/                   # Core conversion modules
│   ├── converter.py        # Main converter (batch & single)
│   ├── parser.py           # Document parsing (PDF/DOCX/XLSX)
│   ├── ocr_engine.py       # OCR engine (RapidOCR)
│   ├── image_describer.py  # AI image description (Qwen-VL)
│   └── docx_builder.py     # DOCX generator
├── utils/                  # Utilities
│   ├── helpers.py          # Helper functions
│   └── i18n.py             # Internationalization
└── web/
    └── index.html          # Frontend UI
```

## 🔧 Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Flask 3.x |
| Frontend | Vanilla HTML / CSS / JS |
| PDF Parsing | PyMuPDF (fitz) |
| OCR | RapidOCR (ONNX Runtime) |
| AI Description | Qwen-VL-Chat-Int4 (via ModelScope) |
| DOCX Generation | python-docx |
| XLSX Parsing | openpyxl |

## ❓ FAQ

**Q: Why can't `.doc` files be converted?**  
A: python-docx does not support the legacy `.doc` format. Please save as `.docx` in Word first.

**Q: Enhanced mode says unavailable — what should I do?**  
A: Enhanced mode requires an NVIDIA GPU with 10GB+ VRAM. Switch to Standard mode, which works on any computer.

**Q: Where are the converted files?**  
A: By default in the `output/` folder. You can change the output path in the UI and click "Open" to access it directly.

**Q: Does it support macOS / Linux?**  
A: Currently Windows only. The core code is cross-platform, but the launcher scripts (.bat/.ps1) and system calls need adaptation. PRs welcome!

**Q: Is it really 100% offline?**  
A: Yes. Standard mode needs no internet at all. Enhanced mode downloads the Qwen-VL model once (on first run), after which it runs fully offline.

## 🤝 Contributing

Contributions are welcome! Feel free to:

- 🐛 [Report bugs](https://github.com/flyanx/DocFlow/issues/new?labels=bug&template=bug.md) or suggest features
- 🔀 Submit a Pull Request
- ⭐ Star the project if you find it useful
- 📢 Share it with others who might benefit

## 📄 License

[MIT License](LICENSE) — free for personal and commercial use.

---

<div align="center">

**If DocFlow helps you, consider giving it a ⭐ — it helps others discover it too!**

</div>

<!-- Keywords: PDF to DOCX converter, document conversion, OCR, RapidOCR, Qwen-VL, batch convert PDF, image to DOCX, OCR Chinese, local document converter, offline PDF converter, python document conversion, Flask web app, python-docx, table recognition, image text extraction, PDF转Word, 图片转Word, OCR文字识别, 文档转换器 -->
