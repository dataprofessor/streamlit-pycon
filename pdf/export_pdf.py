import os
import time
from playwright.sync_api import sync_playwright
from PyPDF2 import PdfMerger

PDF_DIR = os.path.dirname(os.path.abspath(__file__))
TALK_DIR = os.path.dirname(PDF_DIR)
OUTPUT = os.path.join(PDF_DIR, "streamlit_pycon_talk.pdf")

SLIDE_PLAN = [
    ("index.html", [0, 1, 2]),
    ("slides1.html", None),
    ("slides2.html", None),
    ("index.html", [3]),
]

def export_slides():
    merger = PdfMerger()
    tmp_files = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})

        for file_name, slide_indices in SLIDE_PLAN:
            file_path = os.path.join(TALK_DIR, file_name)
            url = f"file://{file_path}"
            page.goto(url)
            page.wait_for_timeout(2000)

            total = page.evaluate("Reveal.getTotalSlides()")

            if slide_indices is None:
                slide_indices = list(range(total))

            for idx in slide_indices:
                page.evaluate(f"Reveal.slide({idx})")
                page.wait_for_timeout(500)

                tmp_path = os.path.join(PDF_DIR, f"_tmp_slide_{file_name}_{idx}.pdf")
                page.pdf(
                    path=tmp_path,
                    width="1280px",
                    height="720px",
                    print_background=True,
                    margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
                )
                tmp_files.append(tmp_path)
                merger.append(tmp_path)

        browser.close()

    merger.write(OUTPUT)
    merger.close()

    for f in tmp_files:
        os.remove(f)

    print(f"PDF exported: {OUTPUT}")
    print(f"Total pages: {len(tmp_files)}")

if __name__ == "__main__":
    export_slides()
