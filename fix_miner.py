import re

with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Update wallet address and remove duration input
wallet = "bc1qzc7ulxegew507z9ssnq9a6nz2d55wknd80l7lk"

html = re.sub(
    r'<input type="text" id="btc-wallet-address" class="filter-input" placeholder="[^"]+" value="[^"]+">',
    f'<input type="text" id="btc-wallet-address" class="filter-input" placeholder="{wallet}" value="{wallet}">',
    html
)

# Remove the duration input block
duration_html_pattern = r'<div>\s*<label style="display:block; margin-bottom:5px; color:var\(--text-muted\); font-size:0\.85rem;">Duration \(Seconds\)</label>\s*<input type="number" id="btc-duration".*?</div>'
html = re.sub(duration_html_pattern, '', html, flags=re.DOTALL)

# Change "Time Remaining" to "Uptime"
html = html.replace('id="miner-time">0s</div>', 'id="miner-time">0s</div>')
html = html.replace('Time Remaining</div>', 'Uptime (24/7)</div>')

# 2. Update JavaScript
js_old = """            const wallet = document.getElementById('btc-wallet-address').value;
            const difficulty = parseInt(document.getElementById('btc-difficulty').value);
            const duration = parseInt(document.getElementById('btc-duration').value);
            const terminal = document.getElementById('miner-terminal');
            const btn = document.getElementById('btn-start-miner');
            
            isMining = true;
            btn.innerHTML = '<span>?? Stop Mining</span>';
            btn.style.background = 'var(--loss)';
            
            terminal.innerHTML = `> Starting Bitcoin Solo Miner Simulator...<br>> Wallet: ${wallet}<br>> Target Difficulty: ${difficulty} leading zeros<br>> Duration: ${duration} seconds<br>> Initiating hash sequence...<br><br>`;
            
            let nonce = 0;
            let totalHashes = 0;
            let startTime = Date.now();
            let lastUiUpdate = startTime;
            let targetPrefix = "0".repeat(difficulty);
            let winnerFound = false;
            
            const blockTemplate = {
                version: 1,
                previous_block_hash: "0000000000000000000000000000000000000000000000000000000000000000",
                merkle_root: "dummy_merkle_root_for_lottery_simulation",
                timestamp: Math.floor(Date.now() / 1000)
            };

            // Non-blocking hash loop
            async function mineLoop() {
                if (!isMining || (Date.now() - startTime) / 1000 >= duration) {
                    finishMining(winnerFound, difficulty);
                    return;
                }

                // Batch hash to prevent UI freeze
                let batchSize = 100;
                for (let i = 0; i < batchSize; i++) {
                    nonce++;
                    totalHashes++;
                    let blockString = `${blockTemplate.version}${blockTemplate.previous_block_hash}${blockTemplate.merkle_root}${blockTemplate.timestamp}${nonce}`;
                    let hash = await sha256(blockString);
                    
                    if (hash.startsWith(targetPrefix)) {
                        winnerFound = true;
                        terminal.innerHTML += `<br><span style="color: #ffaa00; font-weight: bold; font-size: 1.1rem;">?? BLOCK FOUND! ??</span><br>`;
                        terminal.innerHTML += `<span style="color: #fff;">Hash: ${hash}</span><br>`;
                        terminal.innerHTML += `Nonce: ${nonce}<br>`;
                        terminal.innerHTML += `Time taken: ${((Date.now() - startTime)/1000).toFixed(2)}s<br>`;
                        terminal.innerHTML += `<span style="color: #ffaa00;">Simulated Block Reward (3.125 BTC) directed to ${wallet}</span><br>`;
                        isMining = false;
                        finishMining(true, difficulty);
                        return;
                    }
                }
                
                let now = Date.now();
                if (now - lastUiUpdate > 250) {
                    let elapsed = (now - startTime) / 1000;
                    let remaining = Math.max(0, duration - elapsed).toFixed(1);
                    let hashrate = Math.floor(totalHashes / elapsed);
                    
                    document.getElementById('miner-hashrate').innerText = hashrate.toLocaleString() + ' H/s';
                    document.getElementById('miner-hashes').innerText = totalHashes.toLocaleString();
                    document.getElementById('miner-time').innerText = remaining + 's';
                    
                    // Show random hash in terminal
                    let dummyHash = await sha256("dummy" + nonce);
                    terminal.innerHTML += `> Hashing... ${dummyHash.substring(0, 32)}...<br>`;
                    terminal.scrollTop = terminal.scrollHeight;
                    
                    lastUiUpdate = now;
                }
                
                // Yield to event loop
                requestAnimationFrame(mineLoop);
            }
            
            requestAnimationFrame(mineLoop);
        }
        
        function finishMining(winnerFound, difficulty) {
            const terminal = document.getElementById('miner-terminal');
            const btn = document.getElementById('btn-start-miner');
            isMining = false;
            btn.innerHTML = '<span>?? Start Solo Mining</span>';
            btn.style.background = '';
            
            if (!winnerFound) {
                terminal.innerHTML += `<br><span style="color: #ff5555;">? Time's up! No block found matching difficulty ${difficulty}.</span><br>`;
                terminal.innerHTML += `> Try lowering the difficulty or increasing the duration.<br>`;
            }
            terminal.scrollTop = terminal.scrollHeight;
        }"""

js_new = """            const wallet = document.getElementById('btc-wallet-address').value;
            const difficulty = parseInt(document.getElementById('btc-difficulty').value);
            const terminal = document.getElementById('miner-terminal');
            const btn = document.getElementById('btn-start-miner');
            
            isMining = true;
            btn.innerHTML = '<span>?? Stop Mining</span>';
            btn.style.background = 'var(--loss)';
            
            terminal.innerHTML = `> Starting 24/7 Bitcoin Solo Miner Simulator...<br>> Wallet: ${wallet}<br>> Target Difficulty: ${difficulty} leading zeros<br>> Initiating hash sequence...<br><br>`;
            
            let nonce = 0;
            let totalHashes = 0;
            let blocksFound = 0;
            let startTime = Date.now();
            let lastUiUpdate = startTime;
            let targetPrefix = "0".repeat(difficulty);
            
            let blockTemplate = {
                version: 1,
                previous_block_hash: "0000000000000000000000000000000000000000000000000000000000000000",
                merkle_root: "dummy_merkle_root_for_lottery_simulation",
                timestamp: Math.floor(Date.now() / 1000)
            };

            // Non-blocking hash loop
            async function mineLoop() {
                if (!isMining) {
                    finishMining();
                    return;
                }

                // Batch hash to prevent UI freeze
                let batchSize = 100;
                for (let i = 0; i < batchSize; i++) {
                    nonce++;
                    totalHashes++;
                    let blockString = `${blockTemplate.version}${blockTemplate.previous_block_hash}${blockTemplate.merkle_root}${blockTemplate.timestamp}${nonce}`;
                    let hash = await sha256(blockString);
                    
                    if (hash.startsWith(targetPrefix)) {
                        blocksFound++;
                        terminal.innerHTML += `<br><span style="color: #ffaa00; font-weight: bold; font-size: 1.1rem;">?? BLOCK FOUND! ??</span><br>`;
                        terminal.innerHTML += `<span style="color: #fff;">Hash: ${hash}</span><br>`;
                        terminal.innerHTML += `Nonce: ${nonce}<br>`;
                        terminal.innerHTML += `<span style="color: #ffaa00;">Simulated Block Reward (3.125 BTC) directed to ${wallet}</span><br>`;
                        terminal.innerHTML += `> Total Blocks Found: ${blocksFound}<br>`;
                        terminal.innerHTML += `> Continuing to mine next block (24/7 mode active)...<br><br>`;
                        
                        // Reset for next block
                        blockTemplate.timestamp = Math.floor(Date.now() / 1000);
                        nonce = 0;
                        break; // Exit for loop to update UI, then continue mining
                    }
                }
                
                let now = Date.now();
                if (now - lastUiUpdate > 250) {
                    let elapsed = (now - startTime) / 1000;
                    let hashrate = Math.floor(totalHashes / elapsed);
                    
                    // Format uptime (HH:MM:SS)
                    let hrs = Math.floor(elapsed / 3600);
                    let mins = Math.floor((elapsed % 3600) / 60);
                    let secs = Math.floor(elapsed % 60);
                    let uptimeStr = `${hrs > 0 ? hrs + 'h ' : ''}${mins > 0 ? mins + 'm ' : ''}${secs}s`;
                    
                    document.getElementById('miner-hashrate').innerText = hashrate.toLocaleString() + ' H/s';
                    document.getElementById('miner-hashes').innerText = totalHashes.toLocaleString();
                    document.getElementById('miner-time').innerText = uptimeStr;
                    
                    // Show random hash in terminal
                    let dummyHash = await sha256("dummy" + nonce);
                    terminal.innerHTML += `> Hashing... ${dummyHash.substring(0, 32)}...<br>`;
                    terminal.scrollTop = terminal.scrollHeight;
                    
                    lastUiUpdate = now;
                }
                
                // Yield to event loop
                requestAnimationFrame(mineLoop);
            }
            
            requestAnimationFrame(mineLoop);
        }
        
        function finishMining() {
            const terminal = document.getElementById('miner-terminal');
            const btn = document.getElementById('btn-start-miner');
            isMining = false;
            btn.innerHTML = '<span>?? Start Solo Mining</span>';
            btn.style.background = '';
            
            terminal.innerHTML += `<br><span style="color: #ff5555;">?? Mining stopped by user.</span><br>`;
            terminal.scrollTop = terminal.scrollHeight;
        }"""

# A bit risky with simple replace if there are mismatched quotes/emojis, 
# let's write a targeted function to swap the JS block.
html = html.replace(js_old, js_new)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Mining updated to 24/7 and wallet address updated.")
