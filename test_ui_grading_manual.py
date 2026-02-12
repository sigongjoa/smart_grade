
import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to frontend
        print("Navigating to http://localhost:3001...")
        try:
            await page.goto("http://localhost:3001", timeout=60000)
        except Exception as e:
            print(f"Failed to load page: {e}")
            await browser.close()
            return

        # Upload the OMR image
        # Assuming there is an input[type="file"] or similar
        print("Uploading OMR image...")
        file_input = page.locator('input[type="file"]')
        if await file_input.count() > 0:
            await file_input.set_input_files("/mnt/d/progress/mathesis/node13_smart_grader/scan_20260212_160120.jpg")
        else:
            print("File input not found. Searching for buttons...")
            # Fallback: look for buttons that might trigger upload
            await page.click("text=Upload") # Adjust based on actual UI
            
        # Wait for results
        print("Waiting for processing...")
        await page.wait_for_timeout(10000) # Give it some time to process
        
        # Take screenshot
        screenshot_path = "/root/.gemini/antigravity/brain/1af698b7-336e-4a30-ae87-d1d2b612d8c0/ui_verification.png"
        await page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to {screenshot_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
