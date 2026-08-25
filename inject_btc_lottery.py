import re

with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add Nav Item
nav_item = """            <li class="nav-item" onclick="switchPage('page-tools', this)">
                ??? Trading Toolkit
            </li>
            <li class="nav-item" onclick="switchPage('page-btc-lottery', this)">
                ?? BTC Lottery Miner
            </li>"""

html = html.replace("""            <li class="nav-item" onclick="switchPage('page-tools', this)">
                ??? Trading Toolkit
            </li>""", nav_item)

# 2. Add Page Panel
page_panel = """
        <!-- BTC LOTTERY MINER PAGE -->
        <div id="page-btc-lottery" class="page-panel">
            <div class="header">
                <h2>?? Bitcoin Lottery Miner (Solo Mining Simulator)</h2>
                <div class="theme-toggle" onclick="toggleTheme()">??</div>
            </div>

            <div class="settings-panel">
                <p style="color: var(--text-muted); margin-bottom: 20px;">
                    Test your luck in the Bitcoin Lottery! This tool simulates Solo Mining by generating block candidates and hashing them using your browser's CPU. If you find a hash with enough leading zeros, you win the simulated block!
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                    <div>
                        <label style="display:block; margin-bottom:5px; color:var(--text-muted);">BTC Wallet Address</label>
                        <input type="text" id="btc-wallet-address" class="filter-input" placeholder="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" value="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa">
                    </div>
                    <div>
                        <label style="display:block; margin-bottom:5px; color:var(--text-muted);">Difficulty (Leading Zeros)</label>
                        <input type="number" id="btc-difficulty" class="filter-input" value="4" min="1" max="64">
                    </div>
                    <div>
                        <label style="display:block; margin-bottom:5px; color:var(--text-muted);">Duration (Seconds)</label>
                        <input type="number" id="btc-duration" class="filter-input" value="30" min="5" max="3600">
                    </div>
                </div>
                <button class="btn-analyze" id="btn-start-miner" onclick="startBTCMiner()" style="width: 100%; display: flex; justify-content: center; align-items: center; gap: 10px;">
                    <span>?? Start Mining</span>
                </button>
            </div>

            <div class="metrics-grid" style="margin-top: 20px;">
                <div class="metric-card">
                    <div class="metric-value" id="miner-hashrate">0 H/s</div>
                    <div class="metric-label">Hashrate</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="miner-hashes">0</div>
                    <div class="metric-label">Total Hashes Checked</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value" id="miner-time">0s</div>
                    <div class="metric-label">Time Remaining</div>
                </div>
            </div>

            <div class="signal-card" style="margin-top: 20px; background: #000; color: #0f0; font-family: monospace; height: 300px; overflow-y: auto; padding: 15px;" id="miner-terminal">
                > BTC Solo Miner Ready...
                > Awaiting start command...
            </div>
        </div>

        <!-- END OF PAGES -->"""

html = html.replace("        <!-- END OF PAGES -->", page_panel + "\n        <!-- END OF PAGES -->")

# 3. Add JavaScript
js_code = """
        // ==========================
        // BTC LOTTERY MINER LOGIC
        // ==========================
        let isMining = false;
        
        async function sha256(message) {
            const msgBuffer = new TextEncoder().encode(message);
            const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
            const hashArray = Array.from(new Uint8Array(hashBuffer));
            return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        }

        async function startBTCMiner() {
            if (isMining) return;
            
            const wallet = document.getElementById('btc-wallet-address').value;
            const difficulty = parseInt(document.getElementById('btc-difficulty').value);
            const duration = parseInt(document.getElementById('btc-duration').value);
            const terminal = document.getElementById('miner-terminal');
            const btn = document.getElementById('btn-start-miner');
            
            isMining = true;
            btn.innerHTML = '<span>?? Stop Mining</span>';
            btn.onclick = stopBTCMiner;
            
            terminal.innerHTML = `> Starting Bitcoin Solo Miner Simulator...<br>> Wallet: ${wallet}<br>> Difficulty Target: ${difficulty} leading zeros<br>> Duration: ${duration} seconds<br>> Initiating hash sequence...<br><br>`;
            
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

            while (isMining && (Date.now() - startTime) / 1000 < duration) {
                // To keep UI responsive, process in small batches
                for(let i=0; i<100; i++) {
                    nonce++;
                    totalHashes++;
                    let blockString = `${blockTemplate.version}${blockTemplate.previous_block_hash}${blockTemplate.merkle_root}${blockTemplate.timestamp}${nonce}`;
                    let hash = await sha256(blockString);
                    
                    if (hash.startsWith(targetPrefix)) {
                        winnerFound = true;
                        terminal.innerHTML += `<br><span style="color: #ffaa00;">?? BLOCK FOUND! ??</span><br>`;
                        terminal.innerHTML += `<span style="color: #fff;">Hash: ${hash}</span><br>`;
                        terminal.innerHTML += `Nonce: ${nonce}<br>`;
                        terminal.innerHTML += `Time taken: ${((Date.now() - startTime)/1000).toFixed(2)}s<br>`;
                        terminal.innerHTML += `<span style="color: #ffaa00;">Simulated Block Reward (3.125 BTC) directed to ${wallet}</span><br>`;
                        isMining = false;
                        break;
                    }
                }
                
                let now = Date.now();
                if (now - lastUiUpdate > 100) {
                    let elapsed = (now - startTime) / 1000;
                    let remaining = Math.max(0, duration - elapsed).toFixed(1);
                    let hashrate = Math.floor(totalHashes / elapsed);
                    
                    document.getElementById('miner-hashrate').innerText = hashrate.toLocaleString() + ' H/s';
                    document.getElementById('miner-hashes').innerText = totalHashes.toLocaleString();
                    document.getElementById('miner-time').innerText = remaining + 's';
                    
                    if (totalHashes % 1000 < 100) {
                        let dummyHash = await sha256("dummy" + nonce);
                        terminal.innerHTML += `> Hashing... ${dummyHash.substring(0, 32)}...<br>`;
                        terminal.scrollTop = terminal.scrollHeight;
                    }
                    
                    lastUiUpdate = now;
                }
            }
            
            if (!winnerFound && !isMining && (Date.now() - startTime) / 1000 >= duration) {
                terminal.innerHTML += `<br><span style="color: #ff5555;">? Time's up! No block found matching difficulty ${difficulty}.</span><br>`;
                terminal.innerHTML += `> Try lowering the difficulty or increasing the duration.<br>`;
            } else if (!winnerFound && !isMining) {
                terminal.innerHTML += `<br>> Mining stopped by user.<br>`;
            }
            
            terminal.scrollTop = terminal.scrollHeight;
            stopBTCMiner();
        }
        
        function stopBTCMiner() {
            isMining = false;
            const btn = document.getElementById('btn-start-miner');
            btn.innerHTML = '<span>?? Start Mining</span>';
            btn.onclick = startBTCMiner;
        }
    </script>
</body>"""

html = html.replace("    </script>\n</body>", js_code)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
