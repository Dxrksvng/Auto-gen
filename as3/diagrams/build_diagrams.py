"""Render diagrams/*.mmd to PNG with the vendored Mermaid + headless Chrome, then trim whitespace."""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

here = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # macOS path; change on other systems
PAGE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:SarabunT;src:url('../assets/fonts/Sarabun-Regular.ttf');font-weight:400}}
@font-face{{font-family:SarabunT;src:url('../assets/fonts/Sarabun-Bold.ttf');font-weight:700}}
body{{margin:0;padding:16px;background:#fff;font-family:SarabunT}}
.mermaid{{display:inline-block}}
</style></head><body><pre class="mermaid">
{src}
</pre><script src="../assets/vendor/mermaid.min.js"></script><script>
mermaid.initialize({{startOnLoad:true,theme:'base',securityLevel:'strict',
 themeVariables:{{fontFamily:'SarabunT',fontSize:'19px',primaryColor:'#eaf0ff',primaryBorderColor:'#1a56db',
 primaryTextColor:'#1d2433',lineColor:'#41507a',tertiaryColor:'#fff'}},
 flowchart:{{htmlLabels:true,useMaxWidth:false,curve:'basis',nodeSpacing:24,rankSpacing:30,padding:10,wrappingWidth:520}}}});
</script></body></html>"""

for mmd in sorted(here.glob("*.mmd")):
    html_path = here / f"_{mmd.stem}.html"
    html_path.write_text(PAGE.format(src=mmd.read_text(encoding="utf-8")), encoding="utf-8")
    png = here / f"{mmd.stem}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    "--window-size=1400,4200", "--virtual-time-budget=10000", f"--screenshot={png}", f"file://{html_path}"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    img = Image.open(png).convert("RGB")
    box = ImageChops.difference(img, Image.new("RGB", img.size, (255, 255, 255))).getbbox()
    pad = 24
    img.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, img.width), min(box[3] + pad, img.height))).save(png)
    html_path.unlink()
    print(mmd.stem, Image.open(png).size)
