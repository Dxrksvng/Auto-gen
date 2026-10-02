from weasyprint import HTML
import pathlib
here = pathlib.Path(__file__).parent
HTML(filename=str(here / "thai_test_sheet.html")).write_pdf(str(here / "out_weasyprint.pdf"))
print("weasyprint ok")
