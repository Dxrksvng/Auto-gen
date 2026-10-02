#!/bin/sh
# Chromium print-to-PDF of the same HTML (Chrome path is macOS-specific).
here="$(cd "$(dirname "$0")" && pwd)"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$here/out_chrome.pdf" "file://$here/thai_test_sheet.html" 2>/dev/null
echo "chrome done"
