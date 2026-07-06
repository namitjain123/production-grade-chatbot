import asyncio
import sys
from crawl4ai import *

sys.stdout.reconfigure(encoding="utf-8")

async def main():
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            url="https://www.abc.net.au/news/2026-07-05/epping-footballer-critical-head-injury-during-game-afl/106881856",
        )
        print(result.markdown)

if __name__ == "__main__":
    asyncio.run(main())