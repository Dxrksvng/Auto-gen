"""Rasterize page 1 of every letter PDF in a run directory to PNG for visual review.

Text extraction cannot see where tone marks and vowels are drawn, so a person must
look at the pictures. Usage:  python scripts/rasterize_letters.py <run_dir> <out_dir> [dpi]
"""

import sys
from pathlib import Path

import pymupdf


def main() -> int:
    run_dir, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
    dpi = int(sys.argv[3]) if len(sys.argv) > 3 else 110
    out_dir.mkdir(parents=True, exist_ok=True)
    for pdf in sorted((run_dir / "letters").glob("*.pdf")):
        with pymupdf.open(pdf) as doc:
            target = out_dir / f"{pdf.stem}.png"
            doc[0].get_pixmap(dpi=dpi).save(target)
            print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
