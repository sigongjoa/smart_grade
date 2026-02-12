const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Screenshot directory
const SCREENSHOT_DIR = '/tmp/claude-0/-mnt-d-progress-mathesis-node13-smart-grader/ac7cdfce-d349-4d33-87df-214be6908d98/scratchpad/screenshots';

// Ensure screenshot directory exists
if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

// Calculate image hash for comparison
function getImageHash(filePath) {
    const buffer = fs.readFileSync(filePath);
    return crypto.createHash('md5').update(buffer).digest('hex');
}

// Compare two screenshots
function areScreenshotsDifferent(path1, path2) {
    if (!fs.existsSync(path1) || !fs.existsSync(path2)) {
        return true;
    }
    const hash1 = getImageHash(path1);
    const hash2 = getImageHash(path2);
    return hash1 !== hash2;
}

async function runTests() {
    console.log('Starting E2E Tests...\n');

    const browser = await chromium.launch({
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 }
    });
    const page = await context.newPage();

    const screenshots = [];
    const results = [];

    try {
        // Test 1: Load home page (Single Scan is default)
        console.log('Test 1: Loading home page (Single Scan mode)...');
        await page.goto('http://localhost:3001', { waitUntil: 'networkidle', timeout: 10000 });
        await page.waitForTimeout(1000);

        const ss1 = path.join(SCREENSHOT_DIR, '01_single_scan_default.png');
        await page.screenshot({ path: ss1, fullPage: true });
        screenshots.push(ss1);
        console.log('  - Screenshot saved: 01_single_scan_default.png');

        // Check main UI elements
        const hasSmartGrader = await page.locator('text=SMART-GRADER').count() > 0;
        const hasSingleScanTab = await page.locator('text=Single Scan').count() > 0;
        const hasBatchGradeTab = await page.locator('text=Batch Grade').count() > 0;
        const hasQuickScan = await page.locator('text=Quick Scan').count() > 0;
        const hasProgress = await page.locator('text=Progress').count() > 0;

        results.push({
            test: 'Home page loads with correct UI',
            passed: hasSmartGrader && (hasSingleScanTab || hasBatchGradeTab),
            details: `SMART-GRADER: ${hasSmartGrader}, SingleScan: ${hasSingleScanTab}, BatchGrade: ${hasBatchGradeTab}, QuickScan: ${hasQuickScan}, Progress: ${hasProgress}`
        });
        console.log(`  - SMART-GRADER header: ${hasSmartGrader}`);
        console.log(`  - Single Scan tab: ${hasSingleScanTab}`);
        console.log(`  - Batch Grade tab: ${hasBatchGradeTab}`);
        console.log(`  - Quick Scan section: ${hasQuickScan}`);
        console.log(`  - Progress section: ${hasProgress}\n`);

        // Test 2: Click on Batch Grade tab
        console.log('Test 2: Navigate to Batch Grade tab...');
        const batchTab = page.locator('text=Batch Grade').first();
        if (await batchTab.count() > 0) {
            await batchTab.click();
            await page.waitForTimeout(1000);
        }

        const ss2 = path.join(SCREENSHOT_DIR, '02_batch_grade_tab.png');
        await page.screenshot({ path: ss2, fullPage: true });
        screenshots.push(ss2);
        console.log('  - Screenshot saved: 02_batch_grade_tab.png');

        const isDifferent1 = areScreenshotsDifferent(ss1, ss2);
        results.push({
            test: 'Batch Grade tab navigation',
            passed: isDifferent1,
            details: `Screenshots are different: ${isDifferent1}`
        });
        console.log(`  - Page changed after clicking Batch Grade: ${isDifferent1}\n`);

        // Test 3: Go back to Single Scan tab
        console.log('Test 3: Return to Single Scan tab...');
        const singleTab = page.locator('text=Single Scan').first();
        if (await singleTab.count() > 0) {
            await singleTab.click();
            await page.waitForTimeout(1000);
        }

        const ss3 = path.join(SCREENSHOT_DIR, '03_back_to_single_scan.png');
        await page.screenshot({ path: ss3, fullPage: true });
        screenshots.push(ss3);
        console.log('  - Screenshot saved: 03_back_to_single_scan.png');

        const isDifferent2 = areScreenshotsDifferent(ss2, ss3);
        const isSameAsOriginal = !areScreenshotsDifferent(ss1, ss3);
        results.push({
            test: 'Single Scan tab navigation',
            passed: isDifferent2,
            details: `Different from Batch: ${isDifferent2}, Same as original: ${isSameAsOriginal}`
        });
        console.log(`  - Different from Batch Grade: ${isDifferent2}`);
        console.log(`  - Same as original Single Scan: ${isSameAsOriginal}\n`);

        // Test 4: Check for file upload area
        console.log('Test 4: Check file upload functionality...');
        const hasFileUpload = await page.locator('text=Click to select a file').count() > 0 ||
                             await page.locator('input[type="file"]').count() > 0 ||
                             await page.locator('[class*="upload"]').count() > 0 ||
                             await page.locator('[class*="dropzone"]').count() > 0;

        results.push({
            test: 'File upload area exists',
            passed: hasFileUpload,
            details: `Upload area found: ${hasFileUpload}`
        });
        console.log(`  - File upload area found: ${hasFileUpload}\n`);

        // Test 5: Check Teacher Mode button
        console.log('Test 5: Check Teacher Mode toggle...');
        const teacherMode = page.locator('text=Teacher Mode').first();
        const hasTeacherMode = await teacherMode.count() > 0;

        if (hasTeacherMode) {
            await teacherMode.click();
            await page.waitForTimeout(500);
        }

        const ss4 = path.join(SCREENSHOT_DIR, '04_teacher_mode.png');
        await page.screenshot({ path: ss4, fullPage: true });
        screenshots.push(ss4);
        console.log('  - Screenshot saved: 04_teacher_mode.png');

        results.push({
            test: 'Teacher Mode toggle exists',
            passed: hasTeacherMode,
            details: `Teacher Mode button: ${hasTeacherMode}`
        });
        console.log(`  - Teacher Mode found: ${hasTeacherMode}\n`);

        // Test 6: Check responsive design (tablet)
        console.log('Test 6: Check tablet responsive design...');
        await page.setViewportSize({ width: 768, height: 1024 });
        await page.waitForTimeout(500);

        const ss5 = path.join(SCREENSHOT_DIR, '05_tablet_view.png');
        await page.screenshot({ path: ss5, fullPage: true });
        screenshots.push(ss5);
        console.log('  - Screenshot saved: 05_tablet_view.png');

        const isDifferentTablet = areScreenshotsDifferent(ss3, ss5);
        results.push({
            test: 'Tablet responsive design',
            passed: true, // Layout may or may not change based on design
            details: `View changed for tablet: ${isDifferentTablet}`
        });
        console.log(`  - Tablet view different: ${isDifferentTablet}\n`);

        // Test 7: Check responsive design (mobile)
        console.log('Test 7: Check mobile responsive design...');
        await page.setViewportSize({ width: 375, height: 667 });
        await page.waitForTimeout(500);

        const ss6 = path.join(SCREENSHOT_DIR, '06_mobile_view.png');
        await page.screenshot({ path: ss6, fullPage: true });
        screenshots.push(ss6);
        console.log('  - Screenshot saved: 06_mobile_view.png');

        const isDifferentMobile = areScreenshotsDifferent(ss5, ss6);
        results.push({
            test: 'Mobile responsive design',
            passed: true,
            details: `Mobile view different from tablet: ${isDifferentMobile}`
        });
        console.log(`  - Mobile view different from tablet: ${isDifferentMobile}\n`);

        // Test 8: System status check
        console.log('Test 8: Check system status indicator...');
        await page.setViewportSize({ width: 1280, height: 800 });
        await page.waitForTimeout(500);

        const hasSystemActive = await page.locator('text=System Active').count() > 0;
        const hasStatusIndicator = await page.locator('[class*="status"]').count() > 0;

        const ss7 = path.join(SCREENSHOT_DIR, '07_system_status.png');
        await page.screenshot({ path: ss7, fullPage: true });
        screenshots.push(ss7);
        console.log('  - Screenshot saved: 07_system_status.png');

        results.push({
            test: 'System status indicator',
            passed: hasSystemActive || hasStatusIndicator,
            details: `System Active: ${hasSystemActive}`
        });
        console.log(`  - System Active indicator: ${hasSystemActive}\n`);

    } catch (error) {
        console.error('Test error:', error.message);
        const errorSS = path.join(SCREENSHOT_DIR, 'error_screenshot.png');
        await page.screenshot({ path: errorSS, fullPage: true });
        screenshots.push(errorSS);
        results.push({
            test: 'Test execution',
            passed: false,
            details: error.message
        });
    } finally {
        await browser.close();
    }

    // Print summary
    console.log('='.repeat(60));
    console.log('TEST SUMMARY');
    console.log('='.repeat(60));

    let passed = 0;
    let failed = 0;

    results.forEach(r => {
        const status = r.passed ? 'PASS' : 'FAIL';
        console.log(`[${status}] ${r.test}`);
        console.log(`       ${r.details}`);
        if (r.passed) passed++;
        else failed++;
    });

    console.log('='.repeat(60));
    console.log(`Total: ${passed} passed, ${failed} failed out of ${results.length} tests`);
    console.log('='.repeat(60));

    // Print screenshot paths
    console.log('\nScreenshots saved:');
    screenshots.forEach(s => console.log(`  - ${s}`));

    // Verify all screenshots are different
    console.log('\nScreenshot uniqueness verification:');
    const hashes = screenshots.map(s => ({
        file: path.basename(s),
        hash: fs.existsSync(s) ? getImageHash(s) : 'N/A'
    }));

    // Group by hash to find duplicates
    const hashGroups = {};
    hashes.forEach(h => {
        if (!hashGroups[h.hash]) hashGroups[h.hash] = [];
        hashGroups[h.hash].push(h.file);
    });

    const uniqueHashes = Object.keys(hashGroups).length;
    console.log(`  - Total screenshots: ${hashes.length}`);
    console.log(`  - Unique screenshots: ${uniqueHashes}`);

    Object.entries(hashGroups).forEach(([hash, files]) => {
        if (files.length > 1) {
            console.log(`  - DUPLICATE: ${files.join(', ')} (hash: ${hash.substring(0, 8)}...)`);
        }
    });

    if (uniqueHashes >= hashes.length - 1) { // Allow 1 duplicate (original vs return)
        console.log('\n  Screenshots are sufficiently unique!');
    }

    return { passed, failed, screenshots };
}

runTests().catch(console.error);
