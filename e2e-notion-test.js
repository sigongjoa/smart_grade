const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// Screenshot directory
const SCREENSHOT_DIR = '/tmp/claude-0/-mnt-d-progress-mathesis-node13-smart-grader/ac7cdfce-d349-4d33-87df-214be6908d98/scratchpad/screenshots';

// Test files
const TEST_DATA_DIR = '/mnt/d/progress/mathesis/node13_smart_grader/test_data';
const ANSWER_PDF = path.join(TEST_DATA_DIR, 'suneung_answers.pdf');
const OMR_IMAGE = path.join(TEST_DATA_DIR, 'ss03_omr_marked.jpg');

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function runNotionTest() {
    console.log('='.repeat(60));
    console.log('SMART-GRADER E2E Test with Notion Integration');
    console.log('='.repeat(60));

    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 }
    });
    const page = await context.newPage();

    try {
        // Load page and go to Batch Grade
        console.log('\n1. Loading Batch Grade page...');
        await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 15000 });
        await page.click('text=Batch Grade');
        await page.waitForTimeout(500);

        // Upload files
        console.log('2. Uploading files...');
        const fileInputs = await page.locator('input[type="file"]').all();
        await fileInputs[0].setInputFiles(ANSWER_PDF);
        await page.waitForTimeout(300);
        await fileInputs[1].setInputFiles(OMR_IMAGE);
        await page.waitForTimeout(500);

        // Start grading
        console.log('3. Starting batch grading...');
        await page.click('text=Start Batch Grading');

        // Wait for results
        console.log('   Waiting for results...');
        await page.waitForFunction(() => {
            const body = document.body.textContent || '';
            return body.includes('채점 결과') || body.includes('정답지');
        }, { timeout: 45000 });
        await page.waitForTimeout(1000);

        const ss1 = path.join(SCREENSHOT_DIR, 'notion_01_grading_result.png');
        await page.screenshot({ path: ss1, fullPage: true });
        console.log('   Screenshot: notion_01_grading_result.png');

        // Check for Notion upload section
        console.log('\n4. Checking Notion integration UI...');
        const hasNotionSection = await page.locator('text=Notion DB 연동').count() > 0;
        console.log(`   - Notion section found: ${hasNotionSection}`);

        if (hasNotionSection) {
            // Scroll to Notion section
            await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
            await page.waitForTimeout(500);

            const ss2 = path.join(SCREENSHOT_DIR, 'notion_02_upload_section.png');
            await page.screenshot({ path: ss2, fullPage: true });
            console.log('   Screenshot: notion_02_upload_section.png');

            // Fill in Notion form
            console.log('\n5. Filling Notion form...');
            const subjectInput = await page.locator('input[placeholder*="수학"]').first();
            if (await subjectInput.count() > 0) {
                await subjectInput.fill('E2E테스트');
            }

            const dateInput = await page.locator('input[placeholder*="2026"]').first();
            if (await dateInput.count() > 0) {
                await dateInput.fill('2026-02');
            }

            const ss3 = path.join(SCREENSHOT_DIR, 'notion_03_form_filled.png');
            await page.screenshot({ path: ss3, fullPage: true });
            console.log('   Screenshot: notion_03_form_filled.png');

            // Click Notion upload button
            console.log('\n6. Uploading to Notion...');
            const uploadButton = page.locator('button:has-text("Notion 업로드")');
            if (await uploadButton.count() > 0) {
                await uploadButton.click();

                // Wait for upload to complete
                console.log('   Waiting for upload...');
                try {
                    await page.waitForFunction(() => {
                        const body = document.body.textContent || '';
                        return body.includes('업로드 완료') || body.includes('성적이 Notion에');
                    }, { timeout: 15000 });
                    console.log('   Upload completed!');
                } catch (e) {
                    console.log('   Upload timeout or error');
                }

                await page.waitForTimeout(1000);

                const ss4 = path.join(SCREENSHOT_DIR, 'notion_04_upload_result.png');
                await page.screenshot({ path: ss4, fullPage: true });
                console.log('   Screenshot: notion_04_upload_result.png');

                // Check upload result
                const uploadSuccess = await page.locator('text=Notion에 저장되었습니다').count() > 0 ||
                                     await page.locator('text=업로드 완료').count() > 0;
                console.log(`   - Upload successful: ${uploadSuccess}`);
            }
        }

        console.log('\n' + '='.repeat(60));
        console.log('Test completed!');
        console.log('='.repeat(60));

    } catch (error) {
        console.error('\nTest error:', error.message);
        const errorSS = path.join(SCREENSHOT_DIR, 'notion_error.png');
        await page.screenshot({ path: errorSS, fullPage: true });
    } finally {
        await browser.close();
    }
}

runNotionTest().catch(console.error);
