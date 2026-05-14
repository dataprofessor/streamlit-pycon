import os
from playwright.sync_api import sync_playwright
from PIL import Image

PDF_DIR = os.path.dirname(os.path.abspath(__file__))
TALK_DIR = os.path.dirname(PDF_DIR)
OUTPUT = os.path.join(PDF_DIR, "streamlit_pycon_talk.pdf")

SLIDE_PLAN = [
    ("index.html", [0, 1, 2]),
    ("slides1.html", None),
    ("slides2.html", None),
    ("index.html", [3]),
]

VIEWPORT_W = 1600
VIEWPORT_H = 900

def export_slides():
    images = []
    tmp_files = []

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": VIEWPORT_W, "height": VIEWPORT_H},
            device_scale_factor=2,
        )
        page = context.new_page()

        for file_name, slide_indices in SLIDE_PLAN:
            file_path = os.path.join(TALK_DIR, file_name)
            url = f"file://{file_path}"
            page.goto(url)
            page.wait_for_timeout(2000)

            page.evaluate("""() => {
                Reveal.configure({ margin: 0, width: 1280, height: 720, minScale: 1, maxScale: 1, controls: false });
                Reveal.layout();
            }""")
            page.wait_for_timeout(600)

            total = page.evaluate("Reveal.getTotalSlides()")

            if slide_indices is None:
                slide_indices = list(range(total))

            for idx in slide_indices:
                page.evaluate(f"Reveal.slide({idx})")
                page.wait_for_timeout(400)

                tmp_path = os.path.join(PDF_DIR, f"_tmp_{file_name}_{idx}.png")
                page.screenshot(path=tmp_path, full_page=False)
                tmp_files.append(tmp_path)

        browser.close()

    for f in tmp_files:
        img = Image.open(f).convert("RGB")
        images.append(img)

    if images:
        images[0].save(OUTPUT, save_all=True, append_images=images[1:], resolution=300)

    for f in tmp_files:
        os.remove(f)

    print(f"PDF exported: {OUTPUT}")
    print(f"Total pages: {len(images)}")

if __name__ == "__main__":
    export_slides()
