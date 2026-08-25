with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

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
"""

html = html.replace("    <script>\n        let currentTab = 'ALL';", page_panel + "\n    <script>\n        let currentTab = 'ALL';")

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
