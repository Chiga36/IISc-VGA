#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { spawn, execSync } = require('child_process');
const puppeteer = require('puppeteer');
const http = require('http');
const os = require('os');

const PROJECT_ROOT = path.resolve(__dirname, '..');
const OUTPUT_DIR = path.join(PROJECT_ROOT, 'output');

class SimpleBrowserRenderer {
    constructor() {
        this.browser = null;
        this.page = null;
        this.viteProcess = null;
        this.serverUrl = null;
        this.serverPort = 9000;
        this.ensureOutputDir();
    }

    ensureOutputDir() {
        if (!fs.existsSync(OUTPUT_DIR)) {
            fs.mkdirSync(OUTPUT_DIR, { recursive: true });
        }
    }

    async killProcessOnPort(port) {
        try {
            if (process.platform === "win32") {
                // Windows command to kill process on port
                const cmd = `for /f "tokens=5" %a in ('netstat -aon ^| findstr :${port}') do taskkill /F /PID %a 2>nul`;
                execSync(cmd, { stdio: 'ignore', shell: true });
            } else {
                // Unix/Linux command
                execSync(`lsof -ti:${port} | xargs kill -9 2>/dev/null || true`, { stdio: 'ignore' });
            }
            console.log(`🧹 Cleaned up processes on port ${port}`);
            // Give time for port to be released
            await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (e) {
            // Ignore cleanup errors - port might not be in use
        }
    }

    async testServerConnection(url) {
        return new Promise((resolve) => {
            const req = http.get(url, (res) => {
                resolve(true);
            });
            req.on('error', () => resolve(false));
            req.setTimeout(5000, () => {
                req.destroy();
                resolve(false);
            });
        });
    }

    async startMotionCanvasServer() {
        console.log('🚀 Starting Motion Canvas server...');
        
        // Clean up any existing processes first
        await this.killProcessOnPort(9000);
        await this.killProcessOnPort(9001);
        await this.killProcessOnPort(9002);

        return new Promise((resolve, reject) => {
            const npmCmd = process.platform === "win32" ? "npm.cmd" : "npm";
            
            this.viteProcess = spawn(npmCmd, ["start"], {
                cwd: PROJECT_ROOT,
                stdio: "pipe",
                shell: true
            });

            let serverReady = false;

            // Handle stdout - FIXED: Removed async from event handler
            this.viteProcess.stdout.on('data', (data) => {
                const output = data.toString();
                console.log(output.trim());

                // Debug line to confirm detection is running
                console.log(`🔍 DEBUG: Checking for server detection...`);

                // Look for server ready indicators
                // ...existing code...
// Look for server ready indicators
if ((output.includes('Local:') || output.includes('localhost:')) && !serverReady) {
    console.log(`🔍 DEBUG: Found Local/localhost in output`);
    
    // Updated regex pattern to handle the specific Vite output format
    const portMatch = output.match(/(\d{4})/); // Find any 4-digit number (port)

    if (portMatch) {
        console.log(`🔍 DEBUG: Port match found: ${portMatch[1]}`);
        
        this.serverPort = parseInt(portMatch[1]);
        this.serverUrl = `http://localhost:${this.serverPort}`;
        console.log(`✅ Motion Canvas server detected at ${this.serverUrl}`);
        
        serverReady = true;
        
        // Test connection and resolve
        setTimeout(() => {
            console.log('🔍 Testing server connection...');
            this.testServerConnection(this.serverUrl).then(isReady => {
                if (isReady) {
                    console.log('✅ Server is ready and accessible');
                    resolve();
                } else {
                    console.log('⚠️ Server detected but not yet connectable, retrying...');
                    setTimeout(() => {
                        this.testServerConnection(this.serverUrl).then(secondTest => {
                            if (secondTest) {
                                console.log('✅ Server ready (after retry)');
                                resolve();
                            } else {
                                console.log('⚠️ Server still not responding, but continuing...');
                                resolve(); // Continue anyway
                            }
                        });
                    }, 3000);
                }
            });
        }, 2000);
    } else {
        console.log(`🔍 DEBUG: No port match found in: ${output}`);
    }
}
// ...existing code...
                
                // Alternative check for "ready in" message
                if (output.includes('ready in') && this.serverUrl && !serverReady) {
                    console.log('✅ Server ready confirmation received');
                    serverReady = true;
                    setTimeout(() => {
                        resolve();
                    }, 1000);
                }
            });

            // Handle stderr
            this.viteProcess.stderr.on('data', (data) => {
                const error = data.toString();
                if (!error.toLowerCase().includes('deprecated') && 
                    !error.toLowerCase().includes('warning') &&
                    !error.toLowerCase().includes('experimental')) {
                    console.log('Server stderr:', error.trim());
                }
            });

            // Handle process errors
            this.viteProcess.on('error', (error) => {
                if (!serverReady) {
                    reject(new Error(`Server process failed: ${error.message}`));
                }
            });

            this.viteProcess.on('exit', (code, signal) => {
                if (!serverReady && code !== 0) {
                    reject(new Error(`Server exited with code ${code}`));
                }
            });

            // Extended timeout for server startup
            setTimeout(() => {
                if (!serverReady) {
                    reject(new Error('💥 Server startup timeout - server did not become ready'));
                }
            }, 60000); // 60 seconds
        });
    }

    async initializeBrowser() {
        console.log('🌐 Starting browser...');
        
        const launchOptions = {
            headless: true,
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-web-security',
                '--allow-running-insecure-content',
                '--disable-features=VizDisplayCompositor'
            ]
        };

        // For Windows, try to find Chrome executable
        // For Windows, try to find Chrome executable
if (process.platform === "win32") {
    const username = os.userInfo().username;
    const possiblePaths = [
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
        path.join('C:', 'Users', username, 'AppData', 'Local', 'Google', 'Chrome', 'Application', 'chrome.exe'),
        path.join(os.homedir(), 'AppData', 'Local', 'Google', 'Chrome', 'Application', 'chrome.exe'),
        // Alternative locations
        'C:\\Program Files\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files (x86)\\Chrome\\Application\\chrome.exe'
    ];
    
    console.log(`🔍 Looking for Chrome executable for user: ${username}`);
    
    for (const chromePath of possiblePaths) {
        console.log(`🔍 Checking: ${chromePath}`);
        if (fs.existsSync(chromePath)) {
            launchOptions.executablePath = chromePath;
            console.log(`✅ Found Chrome at: ${chromePath}`);
            break;
        } else {
            console.log(`❌ Not found: ${chromePath}`);
        }
    }
    
    // If no Chrome found, try without specifying path (use system default)
    if (!launchOptions.executablePath) {
        console.log('⚠️ Chrome not found in standard locations, using system default');
    }
}


        this.browser = await puppeteer.launch(launchOptions);
        this.page = await this.browser.newPage();
        await this.page.setViewport({ width: 1920, height: 1080 });

        // Enable downloads
        const client = await this.page.target().createCDPSession();
        await client.send('Page.setDownloadBehavior', {
            behavior: 'allow',
            downloadPath: OUTPUT_DIR
        });

        // Add console listeners for debugging
        this.page.on('console', (msg) => {
            if (msg.type() === 'error') {
                console.log('Browser Console Error:', msg.text());
            }
        });

        this.page.on('pageerror', (error) => {
            console.log('Page Error:', error.message);
        });
    }

    async renderSingleScene(sceneName) {
        console.log(`🎬 Processing scene: ${sceneName}`);
        
        try {
            console.log('🌐 Loading Motion Canvas interface...');
            
            let navigationSuccess = false;
            for (let attempt = 0; attempt < 3; attempt++) {
                try {
                    await this.page.goto(this.serverUrl, { 
                        waitUntil: 'networkidle2', 
                        timeout: 60000 
                    });
                    navigationSuccess = true;
                    console.log(`✅ Successfully navigated to ${this.serverUrl}`);
                    break;
                } catch (e) {
                    console.log(`⚠️ Navigation attempt ${attempt + 1} failed: ${e.message}`);
                    if (attempt < 2) {
                        await new Promise(resolve => setTimeout(resolve, 3000));
                    }
                }
            }

            if (!navigationSuccess) {
                throw new Error('Failed to navigate to Motion Canvas interface after 3 attempts');
            }

            // Wait for interface to load
            await new Promise(resolve => setTimeout(resolve, 5000));

            // Take screenshot for debugging
            const debugPath = path.join(OUTPUT_DIR, `debug_${sceneName.toLowerCase()}.png`);
            await this.page.screenshot({ path: debugPath, fullPage: true });
            console.log(`📸 Debug screenshot: ${debugPath}`);

            // Look for interface elements
            console.log('⏳ Looking for Motion Canvas interface...');
            const interfaceInfo = await this.page.evaluate(() => {
                const buttons = document.querySelectorAll('button, [role="button"]');
                const selects = document.querySelectorAll('select');
                const canvas = document.querySelectorAll('canvas');
                const inputs = document.querySelectorAll('input');
                
                return {
                    buttons: buttons.length,
                    selects: selects.length,
                    canvas: canvas.length,
                    inputs: inputs.length,
                    hasInterface: buttons.length > 0 || canvas.length > 0 || selects.length > 0
                };
            });

            console.log(`Found: ${interfaceInfo.buttons} buttons, ${interfaceInfo.selects} selects, ${interfaceInfo.canvas} canvas, ${interfaceInfo.inputs} inputs`);

            if (!interfaceInfo.hasInterface) {
                console.log('⚠️ No interface elements detected, but continuing...');
            }

            // Try to find and set video export format
            console.log('📹 Setting export format...');
            const formatResult = await this.page.evaluate(() => {
                const selects = document.querySelectorAll('select');
                console.log(`Found ${selects.length} select elements`);
                
                for (let i = 0; i < selects.length; i++) {
                    const select = selects[i];
                    const options = Array.from(select.options);
                    console.log(`Select ${i}: ${options.map(o => o.text || o.value).join(', ')}`);
                    
                    const videoOption = options.find(opt => 
                        (opt.text && opt.text.toLowerCase().includes('video')) || 
                        (opt.text && opt.text.toLowerCase().includes('mp4')) ||
                        (opt.value && opt.value.toLowerCase().includes('video')) ||
                        (opt.value && opt.value.toLowerCase().includes('mp4'))
                    );
                    
                    if (videoOption) {
                        console.log(`Setting video format: ${videoOption.text || videoOption.value}`);
                        select.value = videoOption.value;
                        select.dispatchEvent(new Event('change', { bubbles: true }));
                        return { success: true, option: videoOption.text || videoOption.value };
                    }
                }
                return { success: false, reason: 'No video format option found' };
            });

            if (formatResult.success) {
                console.log(`✅ Export format set to: ${formatResult.option}`);
                await new Promise(resolve => setTimeout(resolve, 2000));
            } else {
                console.log(`⚠️ ${formatResult.reason}, will proceed with default format`);
            }

            // Look for render button
            console.log('🔍 Looking for render button...');
            const renderResult = await this.page.evaluate(() => {
                const buttons = Array.from(document.querySelectorAll('button, [role="button"], input[type="button"]'));
                console.log(`Found ${buttons.length} clickable elements`);

                // Log available buttons for debugging
                buttons.forEach((btn, i) => {
                    const text = (btn.textContent || btn.innerText || btn.value || '').trim();
                    const className = btn.className || '';
                    const id = btn.id || '';
                    console.log(`Button ${i}: "${text}" class="${className}" id="${id}"`);
                });

                // Try to find render button with various keywords
                const renderKeywords = ['render', 'export', 'download', 'generate', 'create', 'produce', 'save'];
                
                for (const keyword of renderKeywords) {
                    const button = buttons.find(btn => {
                        const text = (btn.textContent || btn.innerText || btn.value || '').toLowerCase();
                        return text.includes(keyword);
                    });
                    
                    if (button) {
                        console.log(`Found button with "${keyword}": ${button.textContent || button.innerText || button.value}`);
                        button.click();
                        return { success: true, keyword, buttonText: button.textContent || button.innerText || button.value };
                    }
                }

                // If no specific render button found, try the first button
                if (buttons.length > 0) {
                    console.log('No render button found, clicking first available button');
                    buttons[0].click();
                    return { success: true, keyword: 'first-available', buttonText: buttons[0].textContent || buttons[0].innerText || 'First button' };
                }

                return { success: false, reason: 'No buttons found on page' };
            });

            if (renderResult.success) {
                console.log(`✅ Clicked button: ${renderResult.buttonText} (keyword: ${renderResult.keyword})`);
                
                // Wait for rendering process
                console.log('⏳ Waiting for video generation...');
                
                // Take screenshot after clicking
                const afterClickPath = path.join(OUTPUT_DIR, `debug_${sceneName.toLowerCase()}_after_click.png`);
                await this.page.screenshot({ path: afterClickPath, fullPage: true });
                console.log(`📸 After click screenshot: ${afterClickPath}`);
                
                // Wait for video file
                const videoCreated = await this.waitForVideoFile(sceneName, 180000); // 3 minutes
                
                if (videoCreated) {
                    console.log(`✅ Scene ${sceneName} completed successfully`);
                    return true;
                } else {
                    console.log(`⚠️ No video file generated for ${sceneName}`);
                }
            } else {
                console.log(`❌ Could not interact with render controls: ${renderResult.reason}`);
            }

            // Try keyboard shortcuts as fallback
            console.log('🔄 Trying keyboard shortcuts...');
            const shortcuts = [
                ['Control', 'Enter'],
                ['Control', 'R'],
                ['F5'],
                ['Enter']
            ];

            for (const shortcut of shortcuts) {
                console.log(`Trying shortcut: ${shortcut.join('+')}`);
                
                // Press keys down
                for (const key of shortcut) {
                    if (key.length > 1) {
                        await this.page.keyboard.down(key);
                    } else {
                        await this.page.keyboard.press(key);
                    }
                }
                
                // Release keys up (in reverse order)
                for (let i = shortcut.length - 1; i >= 0; i--) {
                    const key = shortcut[i];
                    if (key.length > 1) {
                        await this.page.keyboard.up(key);
                    }
                }
                
                await new Promise(resolve => setTimeout(resolve, 2000));
                
                // Quick check if video appeared
                const quickCheck = await this.checkForVideoFile(sceneName);
                if (quickCheck) {
                    console.log(`✅ Shortcut ${shortcut.join('+')} worked!`);
                    return true;
                }
            }

            console.log(`⚠️ All rendering attempts completed for ${sceneName}`);
            return false;

        } catch (error) {
            console.error(`❌ Error processing ${sceneName}:`, error.message);
            
            // Take error screenshot
            try {
                const errorPath = path.join(OUTPUT_DIR, `error_${sceneName.toLowerCase()}.png`);
                await this.page.screenshot({ path: errorPath, fullPage: true });
                console.log(`📸 Error screenshot: ${errorPath}`);
            } catch (e) {
                console.log('Could not take error screenshot');
            }
            
            return false;
        }
    }

    async checkForVideoFile(sceneName) {
        const expectedFile = path.join(OUTPUT_DIR, `${sceneName.toLowerCase()}.mp4`);
        if (fs.existsSync(expectedFile)) {
            const stats = fs.statSync(expectedFile);
            return stats.size > 1000; // At least 1KB
        }
        return false;
    }

    async waitForVideoFile(sceneName, maxWait = 180000) {
        const expectedFile = path.join(OUTPUT_DIR, `${sceneName.toLowerCase()}.mp4`);
        const startTime = Date.now();
        
        console.log(`⏳ Waiting for video file: ${expectedFile}`);
        
        while (Date.now() - startTime < maxWait) {
            // Check expected location
            if (await this.checkForVideoFile(sceneName)) {
                const stats = fs.statSync(expectedFile);
                console.log(`✅ Video file found: ${expectedFile} (${(stats.size / 1024).toFixed(1)}KB)`);
                return true;
            }

            // Check output directory for any new MP4 files
            try {
                const files = fs.readdirSync(OUTPUT_DIR);
                const recentMp4s = files.filter(f => f.endsWith('.mp4')).filter(f => {
                    const filePath = path.join(OUTPUT_DIR, f);
                    const stats = fs.statSync(filePath);
                    return Date.now() - stats.mtime.getTime() < 120000 && stats.size > 1000; // Modified in last 2 minutes
                });

                if (recentMp4s.length > 0) {
                    const recentFile = recentMp4s[0];
                    const sourcePath = path.join(OUTPUT_DIR, recentFile);
                    
                    if (recentFile !== `${sceneName.toLowerCase()}.mp4`) {
    // Check if target file already exists
    if (fs.existsSync(expectedFile)) {
        const backupFile = expectedFile.replace('.mp4', '_backup.mp4');
        console.log(`⚠️ Target file exists, backing up to: ${backupFile}`);
        fs.renameSync(expectedFile, backupFile);
    }
    
    fs.renameSync(sourcePath, expectedFile);
    console.log(`✅ Renamed video file: ${expectedFile}`);
}

                    return true;
                }
            } catch (e) {
                // Ignore directory errors
            }

            // Check Windows Downloads folder
            try {
                const downloadsDir = path.join(os.homedir(), 'Downloads');
                if (fs.existsSync(downloadsDir)) {
                    const files = fs.readdirSync(downloadsDir);
                    const recentMp4 = files.filter(f => f.endsWith('.mp4')).find(f => {
                        const filePath = path.join(downloadsDir, f);
                        const stats = fs.statSync(filePath);
                        return Date.now() - stats.mtime.getTime() < 120000 && stats.size > 1000; // Last 2 minutes
                    });

                    if (recentMp4) {
                        const sourcePath = path.join(downloadsDir, recentMp4);
                        fs.renameSync(sourcePath, expectedFile);
                        console.log(`✅ Moved video from Downloads: ${expectedFile}`);
                        return true;
                    }
                }
            } catch (e) {
                // Ignore downloads folder errors
            }

            // Progress indicator
            const elapsed = Math.floor((Date.now() - startTime) / 1000);
            if (elapsed % 30 === 0 && elapsed > 0) { // Every 30 seconds
                console.log(`⏳ Still waiting for video... (${elapsed}s elapsed)`);
            }

            await new Promise(resolve => setTimeout(resolve, 5000)); // Check every 5 seconds
        }
        
        console.log(`⚠️ Video file not found after ${Math.floor(maxWait/1000)}s timeout`);
        return false;
    }

    async renderAllScenes(sceneNames) {
        console.log('🎬 Starting video rendering...');
        console.log('📋 Scenes:', sceneNames.join(', '));

        try {
            console.log('🔧 Initializing Motion Canvas server...');
            await this.startMotionCanvasServer();
            
            console.log('🔧 Initializing browser...');
            await this.initializeBrowser();

            const results = [];
            for (const sceneName of sceneNames) {
                console.log(`\n🎬 Processing scene: ${sceneName}`);
                const success = await this.renderSingleScene(sceneName);
                results.push({ scene: sceneName, success });
                
                // Brief pause between scenes
                if (sceneNames.length > 1) {
                    console.log('⏳ Pausing between scenes...');
                    await new Promise(resolve => setTimeout(resolve, 3000));
                }
            }

            console.log('\n🎉 Rendering process complete!');
            console.log('📊 Results:');
            results.forEach(({ scene, success }) => {
                console.log(`   ${success ? '✅' : '❌'} ${scene}`);
            });
            
            return results;

        } catch (error) {
            console.error('💥 Critical error in rendering process:', error.message);
            throw error;
        } finally {
            await this.cleanup();
        }
    }

    async cleanup() {
        console.log('🧹 Cleaning up resources...');
        
        if (this.page) {
            try {
                await this.page.close();
                console.log('✅ Browser page closed');
            } catch (e) {
                console.log('⚠️ Error closing page:', e.message);
            }
        }
        
        if (this.browser) {
            try {
                await this.browser.close();
                console.log('✅ Browser closed');
            } catch (e) {
                console.log('⚠️ Error closing browser:', e.message);
            }
        }
        
        if (this.viteProcess && !this.viteProcess.killed) {
            console.log('🛑 Stopping Motion Canvas server...');
            
            try {
                this.viteProcess.kill('SIGTERM');
                
                // Wait for graceful shutdown
                await new Promise(resolve => setTimeout(resolve, 3000));
                
                if (!this.viteProcess.killed) {
                    this.viteProcess.kill('SIGKILL');
                    console.log('🔪 Force-killed server process');
                }
                
                console.log('✅ Server stopped');
            } catch (e) {
                console.log('⚠️ Error stopping server:', e.message);
            }
        }
        
        // Final port cleanup
        await this.killProcessOnPort(9000);
        await this.killProcessOnPort(9001);
        await this.killProcessOnPort(9002);
    }
}

// CLI Interface
if (require.main === module) {
    const args = process.argv.slice(2);
    
    if (args.length === 0) {
        console.log('Usage: node simple_browser_renderer.js <scene1> [scene2] [scene3] ...');
        console.log('');
        console.log('Examples:');
        console.log('  node simple_browser_renderer.js Scene1');
        console.log('  node simple_browser_renderer.js Scene1 Scene2');
        process.exit(1);
    }

    const renderer = new SimpleBrowserRenderer();
    
    // Handle interruption signals
    process.on('SIGINT', async () => {
        console.log('\n🛑 Received interrupt signal, cleaning up...');
        await renderer.cleanup();
        process.exit(0);
    });

    process.on('SIGTERM', async () => {
        console.log('\n🛑 Received termination signal, cleaning up...');
        await renderer.cleanup();
        process.exit(0);
    });

    async function main() {
        try {
            const results = await renderer.renderAllScenes(args);
            
            const successCount = results.filter(r => r.success).length;
            console.log(`\n🎊 Completed! ${successCount}/${results.length} scenes rendered successfully.`);
            
            if (successCount < results.length) {
                console.log('⚠️ Some scenes failed to render. Check the debug screenshots in the output folder.');
                process.exit(1);
            }
            
        } catch (error) {
            console.error('💥 Fatal error:', error.message);
            process.exit(1);
        }
    }

    main().catch(console.error);
}

module.exports = SimpleBrowserRenderer;
