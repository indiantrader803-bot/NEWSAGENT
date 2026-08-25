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

# 2. Add Page Panel before the script closing body
page_panel = """
        <!-- BTC LOTTERY MINER PAGE -->
        <div id="page-btc-lottery" class="page-panel">
            <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem;">?? Bitcoin Lottery Miner (Solo Mining Simulator)</h2>

            <div class="analyzer-box">
                <p style="color: var(--text-muted); margin-bottom: 20px; font-size: 0.9rem; line-height: 1.5;">
                    Test your luck in the Bitcoin Lottery! This tool simulates Solo Mining by generating block candidates and hashing them using your browser's CPU. If you find a hash with enough leading zeros, you win the simulated block!
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
                    <div>
                        <label style="display:block; margin-bottom:5px; color:var(--text-muted); font-size:0.85rem;">BTC Wallet Address</label>
                        <input type="text" id="btc-wallet-address" class="filter-input" placeholder="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa" value="1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa">
                    </div>
                    <div>
                        <label style="display:block; margin-bottom:5px; color:var(--text-muted); font-size:0.85rem;">Difficulty (Leading Zeros)</label>
                        <input type="number" id="btc-difficulty" class="filter-input" value="4" min="1" max="64">
                    </div>
                    <div>
                        <label style="display:block; margin-bottom:5px; color:var(--text-muted); font-size:0.85rem;">Duration (Seconds)</label>
                        <input type="number" id="btc-duration" class="filter-input" value="30" min="5" max="3600">
                    </div>
                </div>
                <button class="btn-analyze" id="btn-start-miner" onclick="startBTCMiner()" style="width: 100%; display: flex; justify-content: center; align-items: center; gap: 10px; font-size:1rem; padding: 12px;">
                    <span>?? Start Solo Mining</span>
                </button>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-top: 20px; margin-bottom: 20px;">
                <div class="stat-card" style="padding: 15px; border-radius: 12px; background: rgba(99, 102, 241, 0.05); border: 1px solid rgba(99, 102, 241, 0.2);">
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--neon-accent);" id="miner-hashrate">0 H/s</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">Hashrate</div>
                </div>
                <div class="stat-card" style="padding: 15px; border-radius: 12px; background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.2);">
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--gain);" id="miner-hashes">0</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">Hashes Checked</div>
                </div>
                <div class="stat-card" style="padding: 15px; border-radius: 12px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.2);">
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--loss);" id="miner-time">0s</div>
                    <div style="font-size: 0.8rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px;">Time Remaining</div>
                </div>
            </div>

            <div class="analyzer-box" style="margin-top: 20px; background: #0a0a0a; border: 1px solid #333; overflow: hidden; padding: 0;">
                <div style="background: #1a1a1a; padding: 8px 15px; font-size: 0.8rem; color: #888; border-bottom: 1px solid #333; display:flex; gap:6px; align-items:center;">
                    <div style="width:10px; height:10px; border-radius:50%; background:#ef4444;"></div>
                    <div style="width:10px; height:10px; border-radius:50%; background:#eab308;"></div>
                    <div style="width:10px; height:10px; border-radius:50%; background:#22c55e;"></div>
                    <span style="margin-left: 10px; font-family: monospace;">miner-terminal</span>
                </div>
                <div id="miner-terminal" style="font-family: 'Consolas', 'Courier New', monospace; color: #0f0; height: 350px; overflow-y: auto; padding: 15px; font-size: 0.85rem; line-height: 1.4;">
                    > BTC Solo Miner Ready...<br>> Awaiting start command...
                </div>
            </div>
        </div>

        <!-- END OF PAGES -->
    </div>
"""
html = html.replace("    </div>\n    \n    <!-- Chat Bot Integration -->", page_panel + "    <!-- Chat Bot Integration -->")


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
            if (isMining) {
                isMining = false; // Stop if already mining
                return;
            }
            
            const wallet = document.getElementById('btc-wallet-address').value;
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
        }
    </script>
</body>"""

html = html.replace("    </script>\n\n</body>", js_code)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
