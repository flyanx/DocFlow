@echo off
title Research Document Converter - Installation
echo ==========================================
echo    Research Document Converter - Setup
echo ==========================================
echo.
echo All files will be installed to F drive to save C drive space.
echo.

REM Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not detected. Please install Python 3.8 or higher first.
    echo Download: https://www.python.org/downloads/
    echo IMPORTANT: During installation, choose "Customize installation" and set path to F:\Python39
    pause
    exit /b 1
)

python --version 2>&1
echo [OK] Python detected

REM Check pip
echo.
echo [2/5] Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not installed
    pause
    exit /b 1
)
echo [OK] pip detected

REM Create virtual environment on F drive
echo.
echo [3/5] Creating virtual environment on F drive...
set VENV_PATH=F:\doc_converter_env
if not exist %VENV_PATH% (
    python -m venv %VENV_PATH%
    echo [OK] Virtual environment created at %VENV_PATH%
) else (
    echo [OK] Virtual environment already exists at %VENV_PATH%
)

REM Activate virtual environment
call %VENV_PATH%\Scripts\activate.bat

REM Upgrade pip
echo.
echo [4/5] Upgrading pip in virtual environment...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

REM Install dependencies
echo.
echo [5/5] Installing dependencies (may take 10-20 minutes)...
echo All packages will be installed on F drive.
echo.

REM Use Tsinghua mirror for faster download in China
set PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

REM Install basic dependencies
echo Installing basic dependencies...
python -m pip install --only-binary :all: flask python-docx openpyxl Pillow numpy -i %PIP_INDEX_URL%
python -m pip install PyMuPDF -i %PIP_INDEX_URL%
if errorlevel 1 (
    echo [WARNING] Some basic dependencies may have failed, continuing...
)

REM Install RapidOCR (lightweight OCR engine, no PaddlePaddle needed)
echo.
echo Installing RapidOCR (for text recognition)...
python -m pip install rapidocr_onnxruntime -i %PIP_INDEX_URL%
if errorlevel 1 (
    echo [WARNING] RapidOCR install failed, trying EasyOCR as fallback...
    python -m pip install easyocr -i %PIP_INDEX_URL%
)

REM Check for NVIDIA GPU to decide PyTorch version
echo.
echo Detecting graphics card...
nvidia-smi >nul 2>&1
if errorlevel 1 (
    echo [INFO] No NVIDIA GPU detected. Installing CPU version of PyTorch (normal mode available).
    python -m pip install torch torchvision torchaudio -i %PIP_INDEX_URL%
) else (
    echo [INFO] NVIDIA GPU detected. Installing CUDA version of PyTorch (enhanced mode supported).
    python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
)

REM Install transformers and modelscope (for enhanced mode)
echo.
echo Installing AI model dependencies...
python -m pip install transformers accelerate modelscope -i %PIP_INDEX_URL%
if errorlevel 1 (
    echo [WARNING] AI model dependencies may have issues.
)

REM Deactivate virtual environment
call deactivate

echo.
echo ==========================================
echo    Installation Complete!
echo ==========================================
echo.
echo All packages installed on F drive at: %VENV_PATH%
echo.
echo You can now run run.bat to start the tool.
echo.
pause
