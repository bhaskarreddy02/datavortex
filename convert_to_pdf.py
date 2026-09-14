import os
import sys
import subprocess
import markdown
import base64
import re

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not os.path.exists(EDGE_PATH):
    EDGE_PATH = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

CSS_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

@page {
    size: A4;
    margin: 18mm 18mm 18mm 18mm;
    @bottom-center {
        content: counter(page);
    }
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #1f2328;
    line-height: 1.6;
    font-size: 13.5px;
    max-width: 100%;
    margin: 0;
    padding: 0;
}

h1, h2, h3, h4, h5, h6 {
    color: #0f172a;
    font-weight: 700;
    line-height: 1.3;
    page-break-after: avoid;
}

h1 {
    font-size: 26px;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px;
    margin-top: 0;
}

h2 {
    font-size: 20px;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 6px;
    margin-top: 24px;
}

h3 {
    font-size: 16px;
    margin-top: 18px;
}

h4 {
    font-size: 14px;
    margin-top: 14px;
}

p, ul, ol {
    margin-top: 0;
    margin-bottom: 12px;
}

li {
    margin-bottom: 4px;
}

hr {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 20px 0;
}

blockquote {
    margin: 12px 0;
    padding: 8px 16px;
    color: #475569;
    background-color: #f8fafc;
    border-left: 4px solid #3b82f6;
    border-radius: 0 6px 6px 0;
    page-break-inside: avoid;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 16px 0;
    font-size: 12.5px;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid #cbd5e1;
    padding: 7px 10px;
    text-align: left;
}

th {
    background-color: #f1f5f9;
    font-weight: 600;
    color: #0f172a;
}

tr:nth-child(even) {
    background-color: #f8fafc;
}

code {
    font-family: 'JetBrains Mono', Consolas, Monaco, monospace;
    font-size: 12px;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 2px 5px;
    border-radius: 4px;
}

pre {
    background-color: #0f172a;
    color: #f8fafc;
    padding: 14px;
    border-radius: 8px;
    overflow-x: auto;
    page-break-inside: avoid;
}

pre code {
    background-color: transparent;
    color: inherit;
    padding: 0;
    font-size: 12px;
}

img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 14px auto;
    border-radius: 6px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    page-break-inside: avoid;
}

.figure-caption {
    text-align: center;
    font-size: 11.5px;
    color: #64748b;
    font-style: italic;
    margin-top: -6px;
    margin-bottom: 16px;
    page-break-before: avoid;
}
</style>
"""

def embed_images_as_base64(html_content, base_dir):
    def replace_img(match):
        src = match.group(1)
        # Skip if already data URI or web link
        if src.startswith('data:') or src.startswith('http://') or src.startswith('https://'):
            return match.group(0)
        
        img_path = os.path.normpath(os.path.join(base_dir, src))
        if os.path.exists(img_path):
            ext = os.path.splitext(img_path)[1].lower().replace('.', '')
            if ext == 'jpg':
                ext = 'jpeg'
            try:
                with open(img_path, 'rb') as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                return f'<img src="data:image/{ext};base64,{b64}"'
            except Exception as e:
                print(f"Warning: Could not read image {img_path}: {e}")
        else:
            print(f"Warning: Image path not found: {img_path}")
        return match.group(0)

    return re.sub(r'<img\s+[^>]*src="([^"]+)"', replace_img, html_content)

def convert_md_to_pdf(md_filename, pdf_filename=None):
    if not os.path.exists(md_filename):
        print(f"File not found: {md_filename}")
        return False

    if pdf_filename is None:
        pdf_filename = os.path.splitext(md_filename)[0] + ".pdf"

    base_dir = os.path.abspath(os.path.dirname(md_filename))
    
    with open(md_filename, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Convert Markdown to HTML with tables, code fences, etc.
    html_body = markdown.markdown(
        md_text,
        extensions=[
            'extra',
            'tables',
            'fenced_code',
            'codehilite',
            'toc',
            'nl2br',
            'sane_lists'
        ]
    )

    # Embed images as Base64 to ensure 100% self-contained PDF rendering
    html_body = embed_images_as_base64(html_body, base_dir)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{os.path.basename(md_filename)}</title>
    {CSS_STYLE}
</head>
<body>
{html_body}
</body>
</html>
"""

    temp_html_path = os.path.abspath(os.path.splitext(md_filename)[0] + "_temp_render.html")
    pdf_abs_path = os.path.abspath(pdf_filename)

    with open(temp_html_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"Generating PDF for {md_filename} via Headless Engine...")
    cmd = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_abs_path}",
        f"file:///{temp_html_path.replace(os.sep, '/')}"
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if os.path.exists(temp_html_path):
            os.remove(temp_html_path)
        if os.path.exists(pdf_abs_path):
            file_size_kb = os.path.getsize(pdf_abs_path) / 1024.0
            print(f"SUCCESS: Created '{pdf_filename}' ({file_size_kb:.1f} KB) with all images preserved!")
            return True
        else:
            print(f"Error: PDF was not generated.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e}")
        return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "EDA_Report.md"
    convert_md_to_pdf(target)
