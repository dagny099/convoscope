#!/usr/bin/env python3
"""
Capture Compare and Results screenshots from a running Streamlit app.
Requires Playwright (and browsers installed):
  pip install playwright && python -m playwright install chromium
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = "http://localhost:8501"
OUT_DIR = Path("docs/assets/screenshots")
OUT_DIR.mkdir(parents=True, exist_ok=True)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()
        await page.goto(BASE_URL)
        # Give Streamlit time to render
        await page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=30000)
        await asyncio.sleep(1.5)

        # Compare view (default)
        await page.screenshot(path=OUT_DIR / "07-compare-view.png", full_page=True)

        # Click Results tab button if visible
        try:
            await page.get_by_role("button", name=lambda n: n and "Results" in n).click()
        except Exception:
            # Try contains text selector fallback
            try:
                await page.click("button:has-text('Results')")
            except Exception:
                pass
        await asyncio.sleep(1.0)
        await page.screenshot(path=OUT_DIR / "08-results-view.png", full_page=True)

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())

