with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add Nav Item
nav_item_new = """            <li class="nav-item" onclick="switchPage('page-tools', this)">
                ??? Trading Toolkit
            </li>
            <li class="nav-item" onclick="switchPage('page-smc', this); loadSMCMatrix();">
                ?? Smart Money (SMC)
            </li>"""

html = html.replace("""            <li class="nav-item" onclick="switchPage('page-tools', this)">
                ??? Trading Toolkit
            </li>""", nav_item_new)


page_panel = """
        <!-- SMC PAGE -->
        <div class="page-panel" id="page-smc">
            <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 0.5rem;">?? Institutional Smart Money Scanner</h2>
            <p style="color: var(--text-muted); margin-bottom: 1.5rem; font-size: 0.9rem;">Multi-timeframe confluence and Smart Money Concepts (FVG, Order Blocks, Liquidity Sweeps) for advanced professional trading.</p>

            <div style="display: flex; gap: 10px; margin-bottom: 20px; align-items: center; flex-wrap: wrap;">
                <input type="text" id="smc-symbol-input" class="filter-input" placeholder="e.g. XAUUSD=X, ^NSEI, EURUSD=X" value="^NSEI, XAUUSD=X, EURUSD=X" style="width: 300px; margin-bottom: 0;">
                <button class="btn-analyze" onclick="loadSMCMatrix()">Scan Confluence Matrix</button>
            </div>

            <div id="smc-loading" style="display: none; padding: 2rem; text-align: center;">
                <div class="spinner" style="margin: 0 auto 1rem;"></div>
                <div style="color: var(--neon-accent);">Scanning multiple timeframes for institutional flow...</div>
            </div>

            <div id="smc-error" style="display: none; padding: 1.5rem; background: rgba(239, 68, 68, 0.1); border: 1px solid var(--loss-border); color: var(--loss); border-radius: 8px; margin-bottom: 1.5rem;"></div>

            <div id="smc-results" style="display: none; gap: 1.5rem; flex-direction: column;">
                <!-- Matrix Table -->
                <div class="analyzer-box" style="padding: 0; overflow: hidden; border: 1px solid var(--card-border);">
                    <div style="padding: 15px; border-bottom: 1px solid var(--card-border); background: rgba(0,0,0,0.2);">
                        <h3 style="font-size: 1.1rem; font-weight: 600;">Multi-Timeframe Trend Matrix</h3>
                    </div>
                    <div class="table-container" style="overflow-x: auto;">
                        <table style="width: 100%; text-align: left; border-collapse: collapse;">
                            <thead>
                                <tr style="background: rgba(99, 102, 241, 0.1); font-size: 0.85rem; color: var(--text-muted);">
                                    <th style="padding: 12px 15px;">Asset</th>
                                    <th style="padding: 12px 15px;">15M Trend</th>
                                    <th style="padding: 12px 15px;">1H Trend</th>
                                    <th style="padding: 12px 15px;">4H Trend</th>
                                    <th style="padding: 12px 15px;">1D Trend</th>
                                    <th style="padding: 12px 15px;">Confluence Score</th>
                                </tr>
                            </thead>
                            <tbody id="smc-matrix-body">
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- SMC Setups -->
                <h3 style="font-size: 1.1rem; font-weight: 600; margin-top: 1rem;">Active SMC Setups (Order Blocks & FVGs)</h3>
                <div id="smc-setups-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem;">
                </div>
            </div>
        </div>
"""
# Insert before `<div class="page-panel" id="page-tools">`
html = html.replace('            <div class="page-panel" id="page-tools">', page_panel + '\n            <div class="page-panel" id="page-tools">')


# Add the JS logic right before the end of the script block
js_code = """
        // ==========================
        // SMART MONEY CONCEPTS LOGIC
        // ==========================
        async function loadSMCMatrix() {
            const symbols = document.getElementById('smc-symbol-input').value;
            if(!symbols) return;

            const loader = document.getElementById('smc-loading');
            const errorDiv = document.getElementById('smc-error');
            const results = document.getElementById('smc-results');
            
            loader.style.display = 'block';
            errorDiv.style.display = 'none';
            results.style.display = 'none';

            try {
                const response = await fetch(`${API_BASE}/api/smc-matrix?symbols=${encodeURIComponent(symbols)}`);
                const data = await response.json();

                if (data.error) {
                    errorDiv.innerText = data.error;
                    errorDiv.style.display = 'block';
                    return;
                }

                renderSMCMatrix(data.matrix);
                renderSMCSetups(data.setups);
                results.style.display = 'flex';
            } catch (err) {
                errorDiv.innerText = "Failed to connect to the SMC Scanner engine. " + err.message;
                errorDiv.style.display = 'block';
            } finally {
                loader.style.display = 'none';
            }
        }

        function formatTrend(trendData) {
            if (!trendData) return `<span style="color:var(--text-muted);">N/A</span>`;
            const dir = trendData.trend === 'BULLISH' ? 'var(--gain)' : (trendData.trend === 'BEARISH' ? 'var(--loss)' : 'var(--text-muted)');
            const icon = trendData.trend === 'BULLISH' ? '??' : (trendData.trend === 'BEARISH' ? '??' : '?');
            return `<div style="display: flex; flex-direction: column;">
                <span style="color: ${dir}; font-weight: 600;">${icon} ${trendData.trend}</span>
                <span style="font-size: 0.75rem; color: var(--text-muted);">${trendData.bias}</span>
            </div>`;
        }

        function renderSMCMatrix(matrixList) {
            const tbody = document.getElementById('smc-matrix-body');
            tbody.innerHTML = '';
            
            matrixList.forEach(m => {
                let scoreColor = 'var(--text-muted)';
                if (m.score >= 80) scoreColor = 'var(--gain)';
                else if (m.score <= 20) scoreColor = 'var(--loss)';
                else if (m.score > 50) scoreColor = 'rgba(16, 185, 129, 0.7)';
                else scoreColor = 'rgba(239, 68, 68, 0.7)';

                tbody.innerHTML += `
                    <tr style="border-bottom: 1px solid var(--card-border);">
                        <td style="padding: 12px 15px; font-weight: 700; color: #fff;">${m.symbol}</td>
                        <td style="padding: 12px 15px;">${formatTrend(m.t15m)}</td>
                        <td style="padding: 12px 15px;">${formatTrend(m.t1h)}</td>
                        <td style="padding: 12px 15px;">${formatTrend(m.t4h)}</td>
                        <td style="padding: 12px 15px;">${formatTrend(m.t1d)}</td>
                        <td style="padding: 12px 15px;">
                            <div style="font-weight: 800; color: ${scoreColor}; font-size: 1.1rem;">${m.score}%</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted);">${m.verdict}</div>
                        </td>
                    </tr>
                `;
            });
        }

        function renderSMCSetups(setups) {
            const grid = document.getElementById('smc-setups-grid');
            grid.innerHTML = '';

            if(!setups || setups.length === 0) {
                grid.innerHTML = `<div style="color: var(--text-muted);">No prominent FVGs or Order Blocks found.</div>`;
                return;
            }

            setups.forEach(s => {
                const color = s.type === 'BULLISH' ? 'var(--gain)' : 'var(--loss)';
                const border = s.type === 'BULLISH' ? 'var(--gain-border)' : 'var(--loss-border)';
                const bg = s.type === 'BULLISH' ? 'rgba(16, 185, 129, 0.05)' : 'rgba(239, 68, 68, 0.05)';
                
                grid.innerHTML += `
                    <div class="stat-card" style="border: 1px solid ${border}; background: ${bg}; padding: 1.2rem; display: flex; flex-direction: column; gap: 0.8rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: 800; font-size: 1.1rem; color: #fff;">${s.symbol}</span>
                            <span style="color: ${color}; font-weight: 700; font-size: 0.8rem; border: 1px solid ${color}; padding: 2px 8px; border-radius: 12px;">${s.setup_type}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: var(--text-muted);">Timeframe: <b>${s.timeframe}</b></div>
                        <div style="font-size: 0.95rem; color: var(--text-primary); line-height: 1.4;">${s.description}</div>
                        <div style="margin-top: 0.5rem; font-size: 0.8rem; display: flex; justify-content: space-between;">
                            <span style="color: var(--text-muted);">Key Level:</span>
                            <span style="font-weight: 600; font-family: monospace;">${s.level}</span>
                        </div>
                    </div>
                `;
            });
        }
"""
html = html.replace("        function filterCalendar() {", js_code + "\n        function filterCalendar() {")

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
