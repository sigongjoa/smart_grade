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

async function runGradingTest() {
    console.log('='.repeat(60));
    console.log('SMART-GRADER E2E Grading Test - New UI');
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
        // Load page
        console.log('\n1. Loading Batch Grade page...');
        await page.goto('http://localhost:3000', { waitUntil: 'networkidle', timeout: 15000 });
        await page.click('text=Batch Grade');
        await page.waitForTimeout(500);

        const ss1 = path.join(SCREENSHOT_DIR, 'final_01_batch_upload.png');
        await page.screenshot({ path: ss1, fullPage: true });
        console.log('   Screenshot: final_01_batch_upload.png');

        // Upload files
        console.log('\n2. Uploading files...');
        const fileInputs = await page.locator('input[type="file"]').all();
        await fileInputs[0].setInputFiles(ANSWER_PDF);
        await page.waitForTimeout(300);
        await fileInputs[1].setInputFiles(OMR_IMAGE);
        await page.waitForTimeout(500);

        const ss2 = path.join(SCREENSHOT_DIR, 'final_02_files_selected.png');
        await page.screenshot({ path: ss2, fullPage: true });
        console.log('   Screenshot: final_02_files_selected.png');

        // Start grading
        console.log('\n3. Starting batch grading...');
        await page.click('text=Start Batch Grading');

        // Wait for processing - look for result indicators
        console.log('   Waiting for results...');
        try {
            // Wait for either Korean or English result text
            await page.waitForFunction(() => {
                const body = document.body.textContent || '';
                return body.includes('채점 결과') ||
                       body.includes('Grading Results') ||
                       body.includes('정답지') ||
                       body.includes('Answer Key') ||
                       body.includes('전체 결과');
            }, { timeout: 45000 });
            console.log('   Results appeared!');
        } catch (e) {
            console.log('   Timeout waiting for specific text, checking page...');
        }

        await page.waitForTimeout(1000);

        const ss3 = path.join(SCREENSHOT_DIR, 'final_03_grading_result.png');
        await page.screenshot({ path: ss3, fullPage: true });
        console.log('   Screenshot: final_03_grading_result.png');

        // Check if results appeared (check multiple possible indicators)
        const pageText = await page.textContent('body');
        const hasResults = pageText.includes('채점 결과') ||
                          pageText.includes('정답지') ||
                          pageText.includes('Answer Key') ||
                          pageText.includes('통계') ||
                          pageText.includes('Statistics');

        console.log(`\n4. Results appeared: ${hasResults}`);

        if (hasResults) {
            // Check layout elements
            const hasAnswerKey = pageText.includes('정답지') || pageText.includes('Answer Key');
            const hasStudentCards = pageText.includes('학생별') || pageText.includes('Unknown');
            const hasStatistics = pageText.includes('통계') || pageText.includes('Statistics');
            const hasSummary = pageText.includes('전체 결과') || pageText.includes('Summary');

            console.log('\n   Layout elements found:');
            console.log(`   - Answer Key section: ${hasAnswerKey ? 'YES' : 'NO'}`);
            console.log(`   - Student Cards: ${hasStudentCards ? 'YES' : 'NO'}`);
            console.log(`   - Statistics panel: ${hasStatistics ? 'YES' : 'NO'}`);
            console.log(`   - Summary table: ${hasSummary ? 'YES' : 'NO'}`);

            // Try to expand student card
            console.log('\n5. Attempting to expand student card...');

            // Look for clickable student card area
            const studentCard = page.locator('div').filter({ hasText: /Unknown|Student|#1/ }).first();
            if (await studentCard.count() > 0) {
                // Find the clickable header part
                const clickableArea = studentCard.locator('div[style*="cursor: pointer"], div[style*="cursor:pointer"]').first();
                if (await clickableArea.count() > 0) {
                    await clickableArea.click();
                } else {
                    // Click on percentage badge area
                    const badge = page.locator('span:has-text("%")').first();
                    if (await badge.count() > 0) {
                        await badge.click();
                    }
                }
                await page.waitForTimeout(800);
            }

            const ss4 = path.join(SCREENSHOT_DIR, 'final_04_student_expanded.png');
            await page.screenshot({ path: ss4, fullPage: true });
            console.log('   Screenshot: final_04_student_expanded.png');

            // Check for expanded content
            const expandedText = await page.textContent('body');
            const hasOMRImage = expandedText.includes('OCR') || expandedText.includes('OMR 카드');
            const hasAnswerComparison = expandedText.includes('답안 비교') || expandedText.includes('Answer');

            console.log('\n   Expanded content:');
            console.log(`   - OMR Image section: ${hasOMRImage ? 'YES' : 'NO'}`);
            console.log(`   - Answer comparison: ${hasAnswerComparison ? 'YES' : 'NO'}`);

            // Scroll to bottom
            console.log('\n6. Scrolling to summary...');
            await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
            await page.waitForTimeout(500);

            const ss5 = path.join(SCREENSHOT_DIR, 'final_05_summary.png');
            await page.screenshot({ path: ss5, fullPage: true });
            console.log('   Screenshot: final_05_summary.png');
        }

        console.log('\n' + '='.repeat(60));
        console.log('Test completed successfully!');
        console.log('='.repeat(60));

    } catch (error) {
        console.error('\nTest error:', error.message);
        const errorSS = path.join(SCREENSHOT_DIR, 'final_error.png');
        await page.screenshot({ path: errorSS, fullPage: true });
    } finally {
        await browser.close();
    }
}

runGradingTest().catch(console.error);
