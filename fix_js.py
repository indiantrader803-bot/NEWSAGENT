import re

with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace startBTCMiner entirely
js_pattern = r'async function startBTCMiner\(\).*?function finishMining[^{]*\{[^}]*\}'

js_new = """async function startBTCMiner() {
            if (isMining) {
                isMining = false;
                return;
            }
            
            const wallet = document.getElementById('btc-wallet-address').value;
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
                    
                    let hrs = Math.floor(elapsed / 3600);
                    let mins = Math.floor((elapsed % 3600) / 60);
                    let secs = Math.floor(elapsed % 60);
                    let uptimeStr = `${hrs > 0 ? hrs + 'h ' : ''}${mins > 0 ? mins + 'm ' : ''}${secs}s`;
                    
                    document.getElementById('miner-hashrate').innerText = hashrate.toLocaleString() + ' H/s';
                    document.getElementById('miner-hashes').innerText = totalHashes.toLocaleString();
                    document.getElementById('miner-time').innerText = uptimeStr;
                    
                    let dummyHash = await sha256("dummy" + nonce);
                    terminal.innerHTML += `> Hashing... ${dummyHash.substring(0, 32)}...<br>`;
                    terminal.scrollTop = terminal.scrollHeight;
                    
                    lastUiUpdate = now;
                }
                
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
            
            terminal.innerHTML += `<br><span style="color: #ff5555;">?? Mining stopped.</span><br>`;
            terminal.scrollTop = terminal.scrollHeight;
        }"""

html = re.sub(js_pattern, js_new, html, flags=re.DOTALL)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("JS updated successfully.")
