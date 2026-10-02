"""Rasterize every page of a PDF to PNG (for visual inspection) and build contact sheets.
Usage: python3 tools/rasterize_pdf.py in.pdf out_dir [dpi]   (needs PyMuPDF + Pillow)"""
import sys
from pathlib import Path

import fitz
from PIL import Image

pdf, out = Path(sys.argv[1]), Path(sys.argv[2])
dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 80
out.mkdir(parents=True, exist_ok=True)
doc = fitz.open(pdf)
paths = []
for i, page in enumerate(doc, 1):
    p = out / f"p{i:02d}.png"
    page.get_pixmap(dpi=dpi).save(p)
    paths.append(p)
# contact sheets: 6 pages each (3 x 2)
for s in range(0, len(paths), 6):
    imgs = [Image.open(p) for p in paths[s:s + 6]]
    w, h = imgs[0].size
    sheet = Image.new("RGB", (w * 3, h * 2), "white")
    for k, im in enumerate(imgs):
        sheet.paste(im, ((k % 3) * w, (k // 3) * h))
    sheet.save(out / f"sheet_{s // 6 + 1:02d}.png")
print("pages:", len(paths), "->", out)
