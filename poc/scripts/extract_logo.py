"""Rebuild assets/logo.png from the brief's template (data/template_test.pdf).

The logo is stored in the PDF as an RGB image plus a separate soft mask (alpha).
Extracting only the image gives a black box, so the mask is merged back in.
"""

from pathlib import Path

import pymupdf

POC = Path(__file__).resolve().parents[1]
SOURCE = POC.parent / "data" / "template_test.pdf"
TARGET = POC / "assets" / "logo.png"


def main() -> None:
    with pymupdf.open(SOURCE) as doc:
        image = doc[0].get_images(full=True)[0]
        xref, smask = image[0], image[1]
        color = pymupdf.Pixmap(doc, xref)
        if color.alpha:
            color = pymupdf.Pixmap(color, 0)  # drop any embedded alpha before merging the mask
        merged = pymupdf.Pixmap(color, pymupdf.Pixmap(doc, smask)) if smask else color
        merged.save(TARGET)
        print(f"saved {TARGET} {merged.width}x{merged.height} alpha={merged.alpha}")


if __name__ == "__main__":
    main()
