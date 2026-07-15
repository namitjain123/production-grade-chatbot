import asyncio
import base64
import sys
from pathlib import Path
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = Path(__file__).parent / "DATA" / "true_data_new"
BASENAME = "epping-footballer-critical-head-injury-during-game-afl"

async def main():
    config = CrawlerRunConfig(pdf=True, screenshot=True)
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.abc.net.au/news/2026-07-05/epping-footballer-critical-head-injury-during-game-afl/106881856",
            config=config,
        )

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        saved = []

        md_file = OUTPUT_DIR / f"{BASENAME}.md"
        md_file.write_text(result.markdown, encoding="utf-8")
        saved.append(md_file)

        txt_file = OUTPUT_DIR / f"{BASENAME}.txt"
        txt_file.write_text(result.markdown, encoding="utf-8")
        saved.append(txt_file)

        html_file = OUTPUT_DIR / f"{BASENAME}.html"
        html_file.write_text(result.cleaned_html or result.html, encoding="utf-8")
        saved.append(html_file)

        if result.pdf:
            pdf_file = OUTPUT_DIR / f"{BASENAME}.pdf"
            pdf_file.write_bytes(result.pdf)
            saved.append(pdf_file)

        if result.screenshot:
            png_file = OUTPUT_DIR / f"{BASENAME}.png"
            png_file.write_bytes(base64.b64decode(result.screenshot))
            saved.append(png_file)

        for f in saved:
            print(f"Saved {f}")

if __name__ == "__main__":
    asyncio.run(main())