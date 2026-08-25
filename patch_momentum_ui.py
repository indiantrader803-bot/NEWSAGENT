with open("dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add Navigation Item
nav_target = """            <li class="nav-item" onclick="switchPage('page-tools', this)">
                ??? Trading Toolkit
            </li>"""

nav_replacement = """            <li class="nav-item" onclick="switchPage('page-momentum', this); initMomentumEngine();">
                ?? Option Momentum AI
            </li>
            <li class="nav-item" onclick="switchPage('page-tools', this)">
                ??? Trading Toolkit
            </li>"""

# 2. Add Page Panel
panel_target = """            <div class="page-panel" id="page-tools">"""

panel_replacement = """            <div class="page-panel" id="page-momentum">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h2 style="font-size: 1.5rem; font-weight: 800; letter-spacing: -0.03em;">?? AI Option Momentum Engine</h2>
                    <div style="display: flex; gap: 10px;">
                        <button class="btn-analyze" id="btn-momentum-start" onclick="startMomentumEngine()">Start Engine</button>
                        <button class="btn-analyze" id="btn-momentum-stop" style="background: rgba(239, 68, 68, 0.1); color: #ef4444;" onclick="stopMomentumEngine()">Stop Engine</button>
                    </div>
                </div>
                <p style="color: var(--text-muted); margin-bottom: 1.5rem; font-size: 0.9rem;">
                    Fully automated tick-by-tick option charting, swing detection, and trailing stop-loss execution with Indian broker APIs.
                </p>

                <!-- Status Banner -->
                <div id="momentum-status" style="background: rgba(99, 102, 241, 0.1); border: 1px solid var(--neon-accent); border-radius: 12px; padding: 12px; margin-bottom: 1.5rem; text-align: center; font-weight: bold; color: var(--neon-accent);">
                    Engine is currently OFFLINE
                </div>

                <div class="main-grid" style="grid-template-columns: 2fr 1fr; gap: 1.5rem;">
                    <!-- Active Trades -->
                    <div class="signal-card" style="padding: 1.5rem;">
                        <h3 style="font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; margin-bottom: 1rem;">? Active Option Trades</h3>
                        <div id="momentum-trades" style="display: flex; flex-direction: column; gap: 10px;">
                            <div style="color: var(--text-muted); font-size: 0.9rem;">No active trades running.</div>
                        </div>
                    </div>

                    <!-- Strategy Logs -->
                    <div class="signal-card" style="padding: 1.5rem;">
                        <h3 style="font-size: 1.1rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; margin-bottom: 1rem;">?? Event Log</h3>
                        <div id="momentum-logs" style="font-family: monospace; font-size: 0.8rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 6px; max-height: 400px; overflow-y: auto;">
                            No logs yet.
                        </div>
                    </div>
                </div>
            </div>

            <div class="page-panel" id="page-tools">"""

# 3. Add JS Functions
js_target = """        // Fetch Market Schedule"""

js_replacement = """
        // --- Option Momentum Engine ---
        let momentumInterval = null;

        async function initMomentumEngine() {
            if (!momentumInterval) {
                fetchMomentumData();
                momentumInterval = setInterval(fetchMomentumData, 2000); // Poll every 2 seconds
            }
        }

        async function startMomentumEngine() {
            try {
                const res = await fetch('/api/momentum/start');
                const data = await res.json();
                fetchMomentumData();
            } catch (e) { console.error(e); }
        }

        async function stopMomentumEngine() {
            try {
                const res = await fetch('/api/momentum/stop');
                const data = await res.json();
                fetchMomentumData();
            } catch (e) { console.error(e); }
        }

        async function fetchMomentumData() {
            try {
                const res = await fetch('/api/momentum/live');
                const data = await res.json();
                
                const statusEl = document.getElementById("momentum-status");
                if (data.engine_active) {
                    statusEl.textContent = "Engine is currently RUNNING and tracking Option Ticks";
                    statusEl.style.background = "rgba(16, 185, 129, 0.1)";
                    statusEl.style.color = "#10b981";
                    statusEl.style.borderColor = "#10b981";
                } else {
                    statusEl.textContent = "Engine is currently OFFLINE";
                    statusEl.style.background = "rgba(239, 68, 68, 0.1)";
                    statusEl.style.color = "#ef4444";
                    statusEl.style.borderColor = "#ef4444";
                }

                const tradesEl = document.getElementById("momentum-trades");
                if (data.active_trades && data.active_trades.length > 0) {
                    tradesEl.innerHTML = data.active_trades.map(t => {
                        return `
                        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; font-size: 0.9rem;">
                            <div><div style="color: var(--text-muted); font-size: 0.75rem;">Symbol</div><div style="font-weight: 700; color: #10b981;">${t.symbol}</div></div>
                            <div><div style="color: var(--text-muted); font-size: 0.75rem;">Side</div><div style="font-weight: 700;">${t.side}</div></div>
                            <div><div style="color: var(--text-muted); font-size: 0.75rem;">Entry</div><div style="font-weight: 700;">?${t.entry.toFixed(2)}</div></div>
                            <div><div style="color: var(--text-muted); font-size: 0.75rem;">Trail SL</div><div style="font-weight: 700; color: #f59e0b;">?${t.sl.toFixed(2)}</div></div>
                        </div>`;
                    }).join('');
                } else {
                    tradesEl.innerHTML = '<div style="color: var(--text-muted); font-size: 0.9rem;">No active trades running.</div>';
                }

                const logsEl = document.getElementById("momentum-logs");
                if (data.recent_logs && data.recent_logs.length > 0) {
                    logsEl.innerHTML = data.recent_logs.map(l => {
                        let color = "var(--text-muted)";
                        if(l.event === "SIGNAL" || l.event === "EXECUTE") color = "#10b981";
                        if(l.event === "EXIT") color = "#ef4444";
                        if(l.event === "TRAIL") color = "#f59e0b";
                        return `<div style="border-bottom: 1px solid rgba(255,255,255,0.05); padding: 4px 0;">
                            <span style="color: #6b7280;">[${l.timestamp.substring(11, 19)}]</span> 
                            <span style="color: ${color}; font-weight: bold;">${l.event}</span>: 
                            ${l.message}
                        </div>`;
                    }).join('');
                }
            } catch (e) { console.error("Error fetching momentum data", e); }
        }

        // Fetch Market Schedule"""


if nav_target in content:
    content = content.replace(nav_target, nav_replacement)
if panel_target in content:
    content = content.replace(panel_target, panel_replacement)
if js_target in content:
    content = content.replace(js_target, js_replacement)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Patched UI")
