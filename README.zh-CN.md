<div align="center">

<img src="assets/icon.jpg" alt="DocFlow" width="200">

# DocFlow

**纯本地运行的文档智能转换工具 — 将 PDF、图片、Office 文档批量转为 DOCX**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](#)
[![Flask](https://img.shields.io/badge/Framework-Flask-000000.svg)](https://flask.palletsprojects.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](#-贡献)

**100% 本地运行 · 隐私优先 · 文档不上传服务器**

[English](README.md) · [简体中文](README.zh-CN.md)

</div>

---

DocFlow 是一个**零配置、纯本地运行**的文档智能转换工具，可将 PDF、图片、Office 文档批量转换为可编辑的 DOCX 格式。核心能力包括 **OCR 文字识别**（RapidOCR）、**AI 图片语义描述**（Qwen-VL）以及**表格还原**，所有处理均在本地完成，文档**不会上传到任何服务器**。

## ✨ 功能特性

| 特性 | 说明 |
|------|------|
| **多格式支持** | PDF、DOCX、XLS、XLSX、JPG、PNG、GIF、BMP、WebP、TIFF |
| **批量处理** | 一次拖拽多个文件，逐个跟踪转换进度 |
| **OCR 文字识别** | 基于 RapidOCR，自动提取图片、扫描件、PPT 截图中的文字内容，支持中英文混排 |
| **AI 图片描述** | 增强模式使用 Qwen-VL 本地多模态模型，为图片生成语义描述 |
| **表格还原** | 将图片表格识别为可编辑的 DOCX 表格 |
| **双语界面** | 支持中文 / 英文一键切换 |
| **完全本地** | 无需联网，文档不上传任何服务器，隐私有保障 |

## 🆚 为什么选择 DocFlow？

| | DocFlow | 在线转换器 | Adobe Acrobat |
|---|---------|------------|---------------|
| **隐私保护** | ✅ 100% 本地，不上传 | ❌ 文件上传到服务器 | ⚠️ 部分本地 |
| **OCR 识别** | ✅ 内置 RapidOCR | ⚠️ 部分支持 | ✅ 支持 |
| **AI 图片描述** | ✅ Qwen-VL | ❌ 无 | ❌ 无 |
| **批量转换** | ✅ 免费 | ⚠️ 常需付费 | ✅ 付费 |
| **价格** | ✅ 免费开源 | ⚠️ 免费增值 | ❌ 昂贵 |
| **无需注册** | ✅ | ❌ 需注册账号 | ❌ 需订阅 |

## 🚀 快速开始

### 环境要求

- **操作系统**：Windows 10 或更高版本
- **Python**：3.10 – 3.13（[下载地址](https://www.python.org/downloads/)，安装时勾选 "Add Python to PATH"）
- **增强模式**（可选）：NVIDIA 显卡，显存 >= 10GB

### 安装

**方式一：一键安装（推荐）**

双击运行 `install.bat`，等待依赖安装完成。

**方式二：手动安装**

```bash
# 创建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 启动

双击 `run.bat`（或在 PowerShell 中运行 `run.ps1`），浏览器将自动打开 http://localhost:7860

## 📖 使用指南

### 两种转换模式

| 模式 | 功能 | 硬件要求 |
|------|------|---------|
| **标准模式** | 保留原图 + OCR 文字识别 | 任何电脑 |
| **增强模式** | 额外增加 AI 图片描述 | NVIDIA 显卡，10GB+ 显存 |

### 转换步骤

1. **添加文件** — 点击或拖拽文件到上传区
2. **选择模式** — 标准模式（任何电脑）或增强模式（需 NVIDIA 显卡）
3. **设置输出路径** — 点击"浏览"选择输出文件夹
4. **开始转换** — 点击"开始转换"，实时查看每个文件的处理进度
5. **查看结果** — 转换完成后，点击"打开"直接定位到输出文件夹

## 🏗️ 项目结构

```
DocFlow/
├── app.py                  # Flask 后端主程序
├── run.bat                 # Windows 启动脚本
├── run.ps1                 # PowerShell 启动脚本
├── install.bat             # 一键安装脚本
├── requirements.txt        # Python 依赖
├── LICENSE                 # MIT 许可证
├── README.md               # 英文文档
├── README.zh-CN.md         # 中文文档（当前页面）
├── assets/                 # 图标和图片
├── core/                   # 核心转换模块
│   ├── converter.py        # 主转换器（批量/单文件）
│   ├── parser.py           # 文档解析（PDF/DOCX/XLSX）
│   ├── ocr_engine.py       # OCR 引擎（RapidOCR）
│   ├── image_describer.py  # AI 图片描述（Qwen-VL）
│   └── docx_builder.py     # DOCX 生成器
├── utils/                  # 工具模块
│   ├── helpers.py          # 辅助函数
│   └── i18n.py             # 多语言文本
└── web/
    └── index.html          # 前端界面
```

## 🔧 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Flask 3.x |
| 前端 | 原生 HTML / CSS / JS |
| PDF 解析 | PyMuPDF (fitz) |
| OCR | RapidOCR (ONNX Runtime) |
| AI 描述 | Qwen-VL-Chat-Int4 (via ModelScope) |
| DOCX 生成 | python-docx |
| XLSX 解析 | openpyxl |

## ❓ 常见问题

**Q：为什么 .doc 文件无法转换？**  
A：python-docx 不支持 .doc 格式。请先在 Word 中另存为 .docx 格式。

**Q：增强模式提示不可用怎么办？**  
A：增强模式需要 NVIDIA 显卡且显存 >= 10GB。请切换到标准模式，标准模式在任何电脑上都能正常运行。

**Q：转换后的文件在哪里？**  
A：默认保存在项目目录下的 `output/` 文件夹中。可以在界面中点击"浏览"修改输出路径，点击"打开"直接打开文件夹。

**Q：支持 macOS / Linux 吗？**  
A：当前仅支持 Windows。核心代码是跨平台的，但启动脚本（.bat/.ps1）和系统调用需要适配。欢迎提交 PR！

**Q：真的是 100% 离线吗？**  
A：是的。标准模式完全不需要联网。增强模式首次运行时会下载 Qwen-VL 模型，下载后即可完全离线运行。

## 🤝 贡献

欢迎贡献代码！你可以：

- 🐛 [报告 Bug](https://github.com/flyanx/DocFlow/issues/new?labels=bug&template=bug.md) 或建议新功能
- 🔀 提交 Pull Request
- ⭐ 如果觉得有用，给项目点个 Star
- 📢 分享给可能需要的人

## 📄 许可证

[MIT License](LICENSE) — 个人和商业使用均免费。

---

<div align="center">

**如果 DocFlow 帮到了你，点个 ⭐ 吧 — 也能让更多人发现它！**

</div>

<!-- 关键词：PDF转DOCX, 文档转换器, OCR文字识别, RapidOCR, Qwen-VL, 批量转换PDF, 图片转Word, OCR中英文, 本地文档转换, 离线PDF转换, Python文档转换, Flask应用, python-docx, 表格识别, 图片文字提取, document converter, PDF to Word, image to DOCX -->
