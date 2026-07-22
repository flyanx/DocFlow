"""
DocFlow — Flask web application
Desktop document conversion tool with bilingual UI.
Replaces the Gradio-based UI for full layout control.
"""
import os
import sys
import threading
import uuid
import subprocess
import logging
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.converter import DocumentConverter
from utils.helpers import check_cuda_available, check_gpu_memory, is_enhance_mode_available
from utils.i18n import TEXTS

app = Flask(__name__, static_folder=None)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "temp_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global state for conversion jobs (thread-safe)
_jobs = {}
_jobs_lock = threading.Lock()


# ── Routes ──────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory(os.path.join(BASE_DIR, 'web'), 'index.html')


@app.route('/icon')
def icon():
    icon_path = os.path.join(BASE_DIR, "assets", "icon(1).jpg")
    if os.path.exists(icon_path):
        return send_file(icon_path, mimetype='image/jpeg')
    return '', 404


@app.route('/api/system')
def system_info():
    has_cuda, gpu_name = check_cuda_available()
    enhanced = is_enhance_mode_available()
    default_output = os.path.join(BASE_DIR, "output")
    return jsonify({
        'cuda': has_cuda,
        'gpu_name': gpu_name,
        'enhanced_available': enhanced,
        'default_output': default_output,
    })


@app.route('/api/browse', methods=['POST'])
def browse_folder():
    """Open a native folder picker via tkinter subprocess."""
    data = request.get_json(silent=True) or {}
    current = data.get('path', '')

    script = (
        'import tkinter as tk\n'
        'from tkinter import filedialog\n'
        'import sys\n'
        'root = tk.Tk()\n'
        'root.withdraw()\n'
        'root.attributes("-topmost", True)\n'
        'init = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else "."\n'
        'folder = filedialog.askdirectory(initialdir=init)\n'
        'if folder:\n'
        '    print(folder)\n'
        'root.destroy()\n'
    )
    try:
        result = subprocess.run(
            [sys.executable, '-c', script, current or ''],
            capture_output=True, text=True, timeout=120
        )
        folder = result.stdout.strip()
        return jsonify({'path': folder if folder else current})
    except subprocess.TimeoutExpired:
        return jsonify({'path': current})
    except Exception as e:
        logger.error(f"Browse error: {e}")
        return jsonify({'path': current, 'error': str(e)}), 500


@app.route('/api/open_folder', methods=['POST'])
def open_folder():
    data = request.get_json(silent=True) or {}
    path = data.get('path', '')
    if path and os.path.exists(path):
        try:
            os.startfile(path)
        except Exception:
            subprocess.Popen(['explorer', os.path.normpath(path)])
    return jsonify({'ok': True})


@app.route('/api/convert', methods=['POST'])
def convert():
    files = request.files.getlist('files')
    mode = request.form.get('mode', 'standard')
    output_dir = request.form.get('output_dir', '')
    lang = request.form.get('lang', 'zh')

    if not files:
        texts = TEXTS.get(lang, TEXTS['zh'])
        return jsonify({'error': texts.get('status_no_files', 'No files')}), 400

    # Save uploaded files to temp dir (keep original name for output)
    saved = []
    for f in files:
        safe_name = os.path.basename(f.filename)
        save_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex[:8]}_{safe_name}")
        f.save(save_path)
        saved.append((save_path, safe_name))  # (temp_path, original_name)

    # Create job
    job_id = uuid.uuid4().hex[:12]
    with _jobs_lock:
        _jobs[job_id] = {
            'status': 'processing',
            'progress': 0,
            'message': '',
            'results': [],
            'skipped_doc': [],
            'output_dir': '',
            'error': None,
            'files': [],  # per-file status: [{name, status, message, error}, ...]
        }

    # Start conversion in background thread
    t = threading.Thread(
        target=_run_conversion,
        args=(job_id, saved, mode, output_dir, lang),
        daemon=True
    )
    t.start()

    return jsonify({'job_id': job_id})


@app.route('/api/progress/<job_id>')
def get_progress(job_id):
    with _jobs_lock:
        job = _jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)


# ── Background conversion ───────────────────────────────

def _run_conversion(job_id, file_items, mode, output_dir, lang):
    texts = TEXTS.get(lang, TEXTS['zh'])

    def update(progress, message):
        with _jobs_lock:
            if job_id in _jobs:
                _jobs[job_id]['progress'] = min(progress, 1.0)
                _jobs[job_id]['message'] = message

    try:
        valid_exts = ['.pdf', '.docx', '.xls', '.xlsx']
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif']

        input_items, image_items, skipped_doc = [], [], []
        for save_path, orig_name in file_items:
            ext = Path(orig_name).suffix.lower()
            if ext == '.doc':
                skipped_doc.append(orig_name)
            elif ext in image_exts:
                image_items.append((save_path, orig_name))
            elif ext in valid_exts:
                input_items.append((save_path, orig_name))

        # Initialize per-file status
        all_items = input_items + image_items
        file_states = []
        for _, orig_name in all_items:
            file_states.append({
                'name': orig_name,
                'status': 'waiting',
                'message': '',
                'error': ''
            })

        with _jobs_lock:
            _jobs[job_id]['files'] = file_states
            _jobs[job_id]['skipped_doc'] = skipped_doc

        if not input_items and not image_items:
            with _jobs_lock:
                _jobs[job_id]['status'] = 'done'
                msg = texts.get('status_no_valid', '')
                if skipped_doc:
                    msg += ' ' + texts.get('skip_doc_hint', '')
                _jobs[job_id]['message'] = msg
            _cleanup([p for p, _ in file_items])
            return

        use_enhance = (mode == 'enhanced')
        if use_enhance and not is_enhance_mode_available():
            with _jobs_lock:
                _jobs[job_id]['status'] = 'done'
                _jobs[job_id]['message'] = texts.get('status_enhanced_unavailable', '')
            _cleanup([p for p, _ in file_items])
            return

        if not output_dir:
            output_dir = os.path.join(BASE_DIR, "output")
        os.makedirs(output_dir, exist_ok=True)

        converter = DocumentConverter(
            output_dir=output_dir,
            use_enhance_mode=use_enhance,
            progress_callback=update
        )

        total = len(all_items)
        results = []

        for idx, (save_path, orig_name) in enumerate(all_items):
            # Mark as processing
            file_states[idx]['status'] = 'processing'
            file_states[idx]['message'] = texts.get('status_processing', 'Processing...')
            with _jobs_lock:
                _jobs[job_id]['files'] = file_states
                _jobs[job_id]['message'] = f"Processing {orig_name}..."

            # Map converter's 0-1 progress to global batch progress
            converter._batch_offset = idx / total
            converter._batch_scale = 1.0 / total

            try:
                stem = Path(orig_name).stem
                if idx < len(input_items):
                    result = converter.convert(save_path, base_name=stem)
                else:
                    result = converter.convert_image(save_path, base_name=stem)
                results.append(result)
                file_states[idx]['status'] = 'success'
                file_states[idx]['message'] = texts.get('status_done', 'Done')
            except Exception as e:
                logger.error(f"File conversion failed {orig_name}: {e}")
                results.append(None)
                file_states[idx]['status'] = 'fail'
                file_states[idx]['message'] = texts.get('status_failed', 'Failed')
                file_states[idx]['error'] = str(e)

            with _jobs_lock:
                _jobs[job_id]['files'] = file_states

        converter.close()

        # Build simplified result list for final state
        result_list = []
        for i, r in enumerate(results):
            stem = Path(all_items[i][1]).stem
            if r and os.path.exists(r):
                result_list.append({
                    'name': f"{stem}.docx",
                    'status': 'success',
                    'label': texts.get('result_success', 'OK'),
                })
            else:
                result_list.append({
                    'name': stem,
                    'status': 'fail',
                    'label': texts.get('result_fail', 'FAIL'),
                })

        with _jobs_lock:
            _jobs[job_id]['status'] = 'done'
            _jobs[job_id]['progress'] = 1.0
            _jobs[job_id]['message'] = texts.get('status_done', 'Done')
            _jobs[job_id]['results'] = result_list
            _jobs[job_id]['output_dir'] = output_dir

        _cleanup([p for p, _ in file_items])

    except Exception as e:
        logger.error(f"Conversion error: {e}", exc_info=True)
        with _jobs_lock:
            _jobs[job_id]['status'] = 'error'
            _jobs[job_id]['error'] = str(e)
            _jobs[job_id]['message'] = f"{texts.get('status_failed', 'Failed')}: {e}"
        _cleanup([p for p, _ in file_items])


def _cleanup(file_paths):
    for p in file_paths:
        try:
            os.remove(p)
        except Exception:
            pass


# ── Entry point ─────────────────────────────────────────

def main():
    import webbrowser
    print("=" * 50)
    print("  DocFlow")
    print("  Opening http://localhost:7860 ...")
    print("=" * 50)

    def _open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open('http://localhost:7860')

    threading.Thread(target=_open_browser, daemon=True).start()
    app.run(host='0.0.0.0', port=7860, debug=False, threaded=True)


if __name__ == '__main__':
    main()
