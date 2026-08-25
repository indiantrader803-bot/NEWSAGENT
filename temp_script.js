
        let currentTab = 'ALL';
        let allSignals = [];
        let allEvents = [];
        let intelLoaded = false;
        let currentLanguage = 'en';

        function onLanguageChange() {
            currentLanguage = document.getElementById("dashboard-lang").value;
            loadNews();
        }

        // Deep Analysis step styles
        const styleEl = document.createElement('style');
        styleEl.textContent = `
          .deep-step {
            padding: 0.3rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            border: 1px solid var(--card-border);
            background: var(--card-bg);
            color: var(--text-muted);
            transition: all 200ms var(--ease-out);
          }
          .deep-step.active {
            background: var(--neon-accent);
            color: white;
            border-color: var(--neon-accent);
          }
          .deep-step.done {
            background: rgba(16,185,129,0.15);
            color: #10b981;
            border-color: #10b981;
          }
          .bull-card { background: rgba(0,200,83,0.07); border: 1px solid rgba(0,200,83,0.2); border-radius:14px; padding:1.2rem; }
          .bear-card { background: rgba(255,61,61,0.07); border: 1px solid rgba(255,61,61,0.2); border-radius:14px; padding:1.2rem; }
          .synth-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius:14px; padding:1.2rem; }
          .trade-verdict-card { border-radius:16px; padding:1.5rem 2rem; text-align:center; }
          .trade-verdict-card.buy { background: rgba(0,200,83,0.1); border: 2px solid var(--gain); }
          .trade-verdict-card.sell { background: rgba(255,61,61,0.1); border: 2px solid var(--loss); }
          .trade-verdict-card.neutral { background: rgba(99,102,241,0.1); border: 2px solid var(--neon-accent); }
          .intel-card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius:14px; padding:1.2rem 1.5rem; backdrop-filter: var(--glass-blur); }
        `;
        document.head.appendChild(styleEl);

        const API_BASE = window.location.protocol === 'file:' ? 'http://127.0.0.1:8080' : '';

        function toggleSidebar(open) {
            const sidebar = document.querySelector(".sidebar");
            const backdrop = document.getElementById("sidebar-backdrop");
            if (open) {
                sidebar.classList.add("open");
                backdrop.classList.add("active");
            } else {
                sidebar.classList.remove("open");
                backdrop.classList.remove("active");
            }
        }

        // Navigation
        function switchPage(pageId, element) {
            document.querySelectorAll(".page-panel").forEach(p => p.classList.remove("active"));
            document.querySelectorAll(".nav-item").forEach(i => i.classList.remove("active"));
            document.getElementById(pageId).classList.add("active");
            element.classList.add("active");
            
            // Close mobile sidebar if open
            toggleSidebar(false);

            // Native Window scrolling reset
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // Theme Toggle
        const themeBtn = document.getElementById("theme-btn");
        themeBtn.addEventListener("click", () => {
            const currentTheme = document.documentElement.getAttribute("data-theme");
            const newTheme = currentTheme === "dark" ? "light" : "dark";
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("theme", newTheme);
            themeBtn.innerText = newTheme === "dark" ? "🌙 Dark Mode" : "☀️ Light Mode";
        });
        themeBtn.innerText = theme === "dark" ? "🌙 Dark Mode" : "☀️ Light Mode";

        // Signal Classification Helper
        function classifySignal(sig) {
            if (!sig) return 'ALL';
            const sym = String(sig.pair || "").toUpperCase();
            const src = String(sig.source || "").toLowerCase();
            if (src === 'india' || src === 'intraday' || sym.includes(".NS") || sym.includes(".BO") || sym.includes("NIFTY") || sym.includes("SENSEX") || sym.includes("BSE") || sym.includes("NSE") || sym.includes("TCS") || sym.includes("RELIANCE") || sym.includes("HDFCBANK")) {
                return 'INDIAN';
            }
            if (sym.includes("XAU") || sym.includes("GOLD") || sym.includes("XAG") || sym.includes("SILVER") || sym.includes("OIL") || sym.includes("WTI") || sym.includes("BRENT") || src === 'commodities') {
                return 'COMMODITIES';
            }
            if (sym.includes("/") || sym.includes("USD") || sym.includes("EUR") || sym.includes("GBP") || sym.includes("JPY") || sym.includes("AUD") || sym.includes("CAD") || src === 'forex') {
                return 'FOREX';
            }
            return 'US';
        }

        // Load & Filter Signals
        async function loadSignals() {
            try {
                const res = await fetch(`${API_BASE}/api/signals`);
                allSignals = await res.json();
                renderSignals();
            } catch (e) {
                console.error("Failed to load signals:", e);
            }
        }

        function filterCategory(cat, element) {
            document.querySelectorAll(".cat-tab").forEach(t => t.classList.remove("active"));
            element.classList.add("active");
            currentTab = cat;
            renderSignals();
        }

        function renderSignals() {
            const container = document.getElementById("signals-container");
            if (!container) return;
            container.innerHTML = "";
            
            const uniqueSignals = [];
            const seen = new Set();
            
            if (Array.isArray(allSignals)) {
                allSignals.forEach(s => {
                    if (!s) return;
                    const key = `${s.pair || ''}_${s.direction || ''}_${s.entry || ''}_${s.tp1 || ''}_${s.sl || ''}`;
                    if (!seen.has(key)) {
                        seen.add(key);
                        uniqueSignals.push(s);
                    }
                });
            } else if (allSignals && allSignals.error) {
                container.innerHTML = `<div style="color: #ef4444; padding: 2rem;">Error: ${allSignals.error}</div>`;
                return;
            }
            
            const filtered = uniqueSignals.filter(s => {
                if (currentTab === 'ALL') return true;
                return classifySignal(s) === currentTab;
            });

            if (filtered.length === 0) {
                container.innerHTML = `
                    <div class="signal-card buy" style="grid-column: 1/-1; text-align: center; padding: 3rem; background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px;">
                        <div class="asset-name" style="font-size: 1.1rem; color: var(--text-main); font-weight: 700;">No active ${currentTab} signals currently available.</div>
                        <div style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.5rem;">Select another category tab like 'All', 'Forex', or 'Indian Market' to view active live signals.</div>
                    </div>
                `;
                return;
            }

            filtered.forEach((sig, idx) => {
                const dir = String(sig.direction || 'BUY').toUpperCase();
                const isBuy = dir.includes("BUY") || dir.includes("LONG") || dir.includes("BULLISH");
                const cardClass = isBuy ? "buy" : "sell";
                const badgeText = isBuy ? "BUY / LONG" : "SELL / SHORT";
                
                const card = document.createElement("div");
                card.className = `signal-card ${cardClass}`;
                card.innerHTML = `
                    <div class="signal-top">
                        <div class="signal-badge">${badgeText}</div>
                        <div class="signal-timestamp">${sig.timestamp || sig.time || 'Live'}</div>
                    </div>
                    <div class="asset-name">${sig.pair || 'ASSET'}</div>
                    <div class="signal-parameters">
                        <div class="param-group">
                            <span class="param-label">Entry</span>
                            <span class="param-value">${sig.entry || '—'}</span>
                        </div>
                        <div class="param-group">
                            <span class="param-label">Stop Loss</span>
                            <span class="param-value">${sig.sl || '—'}</span>
                        </div>
                        <div class="param-group" style="margin-top: 0.5rem;">
                            <span class="param-label">TP 1</span>
                            <span class="param-value" style="color: var(--secondary-accent);">${sig.tp1 || '—'}</span>
                        </div>
                        <div class="param-group" style="margin-top: 0.5rem;">
                            <span class="param-label">TP 2</span>
                            <span class="param-value" style="color: var(--secondary-accent);">${sig.tp2 || '—'}</span>
                        </div>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 0.25rem;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; font-weight: 600; color: var(--text-muted);">
                            <span>CONFIDENCE LEVEL</span>
                            <span>${sig.confidence || 80}%</span>
                        </div>
                        <div style="height: 6px; background: rgba(255, 255, 255, 0.05); border-radius: 3px; overflow: hidden;">
                            <div style="height: 100%; background: linear-gradient(90deg, var(--neon-accent), #a855f7); width: ${sig.confidence || 80}%;"></div>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
        }

        // AI Analyzer Action
        async function runAnalysis() {
            const symbol = document.getElementById("symbol-input").value.trim();
            const spinner = document.getElementById("analyzer-spinner");
            const resultBox = document.getElementById("analyzer-result");
            
            if (!symbol) {
                alert("Please enter a ticker symbol!");
                return;
            }

            spinner.style.display = "block";
            resultBox.style.display = "none";
            resultBox.innerHTML = "";

            try {
                let cleanSym = symbol.toUpperCase().replace("/", "").trim();
                let yfSymbol = cleanSym;
                if (cleanSym === "XAUUSD" || cleanSym === "GOLD" || cleanSym === "XAU") yfSymbol = "GC=F";
                else if (cleanSym === "XAGUSD" || cleanSym === "SILVER" || cleanSym === "XAG") yfSymbol = "SI=F";
                else if (cleanSym.length === 6) {
                    yfSymbol = cleanSym + "=X";
                }

                const response = await fetch(`${API_BASE}/api/analyze?symbol=${encodeURIComponent(yfSymbol)}`);
                const data = await response.json();
                
                spinner.style.display = "none";
                resultBox.style.display = "block";

                if (data.error) {
                    resultBox.innerHTML = `
                        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 12px; padding: 1.5rem; text-align: center; color: #ef4444; font-weight: 600;">
                            ⚠️ Analysis Failed: ${data.error}
                        </div>
                    `;
                    return;
                }

                const isBuy = data.direction.toUpperCase().includes("BUY") || data.direction.toUpperCase().includes("LONG") || data.direction.toUpperCase().includes("BULLISH");
                const cardClass = isBuy ? "buy" : "sell";
                const badgeText = isBuy ? "BUY / LONG" : "SELL / SHORT";

                resultBox.innerHTML = `
                    <div class="signal-card ${cardClass}" style="width: 100%;">
                        <div class="signal-top">
                            <div class="signal-badge">${badgeText}</div>
                            <div style="font-weight: 700; color: var(--secondary-accent); font-size: 1.05rem;">
                                ${data.current_price} <span style="font-size: 0.85rem; font-weight: 500;">(${data.change_pct})</span>
                            </div>
                        </div>
                        <div class="asset-name">AI Setup for ${data.symbol}</div>
                        <div class="signal-parameters">
                            <div class="param-group">
                                <span class="param-label">Entry Price</span>
                                <span class="param-value">${data.entry}</span>
                            </div>
                            <div class="param-group">
                                <span class="param-label">Stop Loss</span>
                                <span class="param-value">${data.sl}</span>
                            </div>
                            <div class="param-group" style="margin-top: 0.5rem;">
                                <span class="param-label">Target 1</span>
                                <span class="param-value" style="color: var(--secondary-accent);">${data.tp1}</span>
                            </div>
                            <div class="param-group" style="margin-top: 0.5rem;">
                                <span class="param-label">Target 2</span>
                                <span class="param-value" style="color: var(--secondary-accent);">${data.tp2}</span>
                            </div>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 0.5rem; background: rgba(0,0,0,0.03); padding: 1rem; border-radius: 10px; border: 1px solid var(--card-border);">
                            <span class="param-label">AI Analysis Logic</span>
                            <p style="font-size: 0.9rem; line-height: 1.4; color: var(--text-color); font-weight: 500;">${data.reason}</p>
                        </div>
                    </div>
                `;
            } catch (err) {
                spinner.style.display = "none";
                resultBox.style.display = "block";
                resultBox.innerHTML = `
                    <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 12px; padding: 1.5rem; text-align: center; color: #ef4444; font-weight: 600;">
                        ⚠️ Network Error connecting to analyzer.
                    </div>
                `;
            }
        }

        // Load & Filter Economic Calendar Events (matching Forex Factory layout)
        function onRangeChange() {
            const range = document.getElementById("cal-range").value;
            const customDiv = document.getElementById("custom-date-inputs");
            if (range === "custom") {
                customDiv.style.display = "flex";
            } else {
                customDiv.style.display = "none";
                loadCalendar();
            }
        }

        async function loadCalendar() {
            const container = document.getElementById("calendar-container");
            try {
                container.innerHTML = `<tr><td colspan="7" style="text-align:center; color: var(--text-muted); padding: 2rem;">⏳ Loading economic calendar...</td></tr>`;
                
                const range = document.getElementById("cal-range").value;
                const rangeLabel = range === "this_week" ? "This Week" :
                                   range === "next_week" ? "Next Week" :
                                   range === "next_month" ? "Next Month" :
                                   range === "full_year" ? "Full Year" : "Custom Range";
                document.getElementById("calendar-title").innerText = `Economic Calendar (${rangeLabel})`;

                let url = `${API_BASE}/api/calendar?range=${range}`;
                if (range === "custom") {
                    const from = document.getElementById("cal-from-date").value;
                    const to = document.getElementById("cal-to-date").value;
                    if (from) url += `&from=${from}`;
                    if (to) url += `&to=${to}`;
                }
                
                const res = await fetch(url);
                const data = await res.json();
                if (data && data.error) {
                    container.innerHTML = `<tr><td colspan="7" style="text-align:center; color: #ef4444; padding: 2rem;">⚠️ ${data.error}</td></tr>`;
                    return;
                }
                allEvents = Array.isArray(data) ? data : [];
                filterCalendar();
            } catch (e) {
                console.error("Failed to load calendar:", e);
                container.innerHTML = `<tr><td colspan="7" style="text-align:center; color: #ef4444; padding: 2rem;">⚠️ Failed to load calendar. Please try again.</td></tr>`;
            }
        }

        function formatCalDate(dateStr, timeStr) {
            try {
                // dateStr: "08-07-2026", timeStr: "9:15am"
                const [m, d, y] = dateStr.split("-");
                const dateObj = new Date(`${y}-${m}-${d}`);
                const dayNames = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
                const monNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
                return `${dayNames[dateObj.getDay()]} ${monNames[dateObj.getMonth()]} ${d}, ${timeStr}`;
            } catch(e) {
                return `${dateStr} ${timeStr}`;
            }
        }

        function exportCalendarToCSV() {
            if (!allEvents || allEvents.length === 0) return;
            let csv = "Time,Currency,Indicator,Impact,Forecast,Previous,Actual\n";
            allEvents.forEach(ev => {
                const row = [
                    `"${ev.date} ${ev.time}"`,
                    `"${ev.country}"`,
                    `"${(ev.title || '').replace(/"/g, '""')}"`,
                    `"${ev.impact}"`,
                    `"${ev.forecast}"`,
                    `"${ev.previous}"`,
                    `"${ev.actual}"`
                ];
                csv += row.join(",") + "\n";
            });
            const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.setAttribute("download", `economic_calendar_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function exportSignalsToCSV() {
            if (!allSignals || allSignals.length === 0) return;
            let csv = "Date,Time,Asset,Direction,Entry,Stop Loss,Take Profit 1,Take Profit 2,Source\n";
            allSignals.forEach(sig => {
                const row = [
                    `"${sig.date}"`,
                    `"${sig.time}"`,
                    `"${sig.pair}"`,
                    `"${sig.direction}"`,
                    `"${sig.entry}"`,
                    `"${sig.sl}"`,
                    `"${sig.tp1}"`,
                    `"${sig.tp2}"`,
                    `"${sig.source}"`
                ];
                csv += row.join(",") + "\n";
            });
            const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.setAttribute("download", `trading_signals_${new Date().toISOString().split('T')[0]}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function calculatePositionSize() {
            const balance = parseFloat(document.getElementById("calc-balance").value) || 0;
            const riskPct = parseFloat(document.getElementById("calc-risk").value) || 0;
            const sl = parseFloat(document.getElementById("calc-sl").value) || 0;
            const assetType = document.getElementById("calc-asset-type").value;
            
            if (balance <= 0 || riskPct <= 0 || sl <= 0) return;
            
            const riskAmt = (balance * riskPct) / 100;
            let lots = 0;
            
            if (assetType === "forex") {
                lots = riskAmt / (sl * 10);
            } else if (assetType === "gold") {
                lots = riskAmt / (sl * 10);
            } else {
                lots = riskAmt / sl;
            }
            
            document.getElementById("calc-res-risk").innerText = `$${riskAmt.toFixed(2)}`;
            document.getElementById("calc-res-lots").innerText = `${lots.toFixed(2)} Lots / Units`;
            document.getElementById("calc-results").style.display = "block";
        }

        async function triggerTelegramTest() {
            const btn = document.getElementById("btn-test-telegram");
            const resultDiv = document.getElementById("telegram-test-result");
            
            btn.disabled = true;
            btn.innerText = "Sending test message...";
            resultDiv.style.display = "none";
            
            try {
                const res = await fetch(`${API_BASE}/api/test-telegram`);
                const data = await res.json();
                
                if (data.success) {
                    resultDiv.style.background = "rgba(16,185,129,0.15)";
                    resultDiv.style.border = "1px solid var(--gain)";
                    resultDiv.style.color = "var(--gain)";
                    resultDiv.innerText = `Success! Test message sent successfully.`;
                } else {
                    resultDiv.style.background = "rgba(239,68,68,0.15)";
                    resultDiv.style.border = "1px solid #ef4444";
                    resultDiv.style.color = "#ef4444";
                    resultDiv.innerText = `Error: ${data.error}`;
                }
                resultDiv.style.display = "block";
            } catch(e) {
                resultDiv.style.background = "rgba(239,68,68,0.15)";
                resultDiv.style.border = "1px solid #ef4444";
                resultDiv.style.color = "#ef4444";
                resultDiv.innerText = `Failed to contact API. Make sure local server is running.`;
                resultDiv.style.display = "block";
            } finally {
                btn.disabled = false;
                btn.innerText = "⚡ Send Test Telegram Message";
            }
        }

        function filterCalendar() {
            const query = (document.getElementById("cal-search").value || "").trim().toUpperCase();
            const impactFilter = document.getElementById("cal-impact").value;
            const container = document.getElementById("calendar-container");
            container.innerHTML = "";

            if (!allEvents || allEvents.length === 0) {
                container.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 2rem;">No calendar events available this week.</td></tr>`;
                return;
            }

            const filtered = allEvents.filter(ev => {
                if (!ev || !ev.country) return false;
                const matchQuery = !query || (ev.country || "").includes(query) || (ev.title || "").toUpperCase().includes(query);
                const matchImpact = impactFilter === 'ALL' || (ev.impact || "").toUpperCase() === impactFilter;
                return matchQuery && matchImpact;
            });

            if (filtered.length === 0) {
                container.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted); padding: 2rem;">No events matching your filters.</td></tr>`;
                return;
            }

            // Group by India Time date
            const byDate = {};
            filtered.forEach(ev => {
                let dKey = "Unknown";
                if (ev.datetime) {
                    const localDate = new Date(ev.datetime);
                    const options = { timeZone: "Asia/Kolkata", year: "numeric", month: "2-digit", day: "2-digit" };
                    const parts = localDate.toLocaleDateString("en-US", options).split("/");
                    dKey = `${parts[0]}-${parts[1]}-${parts[2]}`; // MM-DD-YYYY
                }
                if (!byDate[dKey]) byDate[dKey] = [];
                byDate[dKey].push(ev);
            });

            Object.keys(byDate).sort().forEach(dateKey => {
                const [m, d, y] = (dateKey || "--").split("-");
                const dateObj = new Date(`${y}-${m}-${d}`);
                const dayNames = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
                const monNames = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
                const dateLabel = isNaN(dateObj) ? dateKey : `${dayNames[dateObj.getDay()]}, ${monNames[dateObj.getMonth()]} ${d}, ${y}`;

                const sepRow = document.createElement("tr");
                sepRow.innerHTML = `<td colspan="8" style="background: rgba(99,102,241,0.15); color: var(--neon-accent); font-weight: 700; font-size: 0.85rem; padding: 0.6rem 1rem; letter-spacing: 0.05em;">📅 ${dateLabel} (India Time)</td>`;
                container.appendChild(sepRow);

                byDate[dateKey].forEach(ev => {
                    const imp = (ev.impact || "low").toLowerCase();
                    let badgeClass = "impact-none";
                    let impIcon = "⚪";
                    if (imp === "high") { badgeClass = "impact-high"; impIcon = "🔴"; }
                    else if (imp === "medium") { badgeClass = "impact-medium"; impIcon = "🟡"; }
                    else if (imp === "low") { badgeClass = "impact-low"; impIcon = "🟢"; }
                    else if (imp === "holiday") { badgeClass = "impact-none"; impIcon = "📆"; }

                    const forecast = ev.forecast && ev.forecast !== "N/A" ? ev.forecast : "—";
                    const previous = ev.previous && ev.previous !== "N/A" ? ev.previous : "—";
                    const actual = ev.actual && ev.actual !== "N/A" ? `<span style="color:#10b981;font-weight:700;">${ev.actual}</span>` : `<span style="color:var(--text-muted);">Pending</span>`;

                    // Format Time in Asia/Kolkata
                    let localTimeStr = "All Day";
                    if (ev.datetime) {
                        const localDate = new Date(ev.datetime);
                        localTimeStr = localDate.toLocaleTimeString("en-US", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit", hour12: true });
                    }

                    const row = document.createElement("tr");
                    row.innerHTML = `
                        <td style="font-size:0.82rem; color: var(--text-muted); font-weight: 600;">${localTimeStr}</td>
                        <td style="font-weight: 700; color: var(--neon-accent);">${ev.country || "—"}</td>
                        <td style="font-weight: 600;">${ev.title || "—"}</td>
                        <td><span class="impact-badge ${badgeClass}">${impIcon} ${imp}</span></td>
                        <td style="font-weight: 600; color: var(--secondary-accent);">${forecast}</td>
                        <td style="font-weight: 600; color: var(--text-muted);">${previous}</td>
                        <td>${actual}</td>
                        <td class="cal-countdown" data-datetime="${ev.datetime || ''}" data-title="${encodeURIComponent(ev.title || '')}" data-country="${encodeURIComponent(ev.country || '')}" data-forecast="${encodeURIComponent(ev.forecast || '')}" data-previous="${encodeURIComponent(ev.previous || '')}" data-actual="${encodeURIComponent(ev.actual || '')}" data-impact="${ev.impact || ''}">
                            <span style="color:var(--text-muted); font-size:0.75rem;">Scheduled</span>
                        </td>
                    `;
                    container.appendChild(row);
                });
            });
            tickCalendarCountdowns();
        }

        function tickCalendarCountdowns() {
            document.querySelectorAll(".cal-countdown").forEach(el => {
                const dtStr = el.getAttribute("data-datetime");
                if (!dtStr) return;
                const eventTime = new Date(dtStr);
                const now = new Date();
                const diffSec = Math.floor((eventTime - now) / 1000);
                
                const title = el.getAttribute("data-title");
                const country = el.getAttribute("data-country");
                const forecast = el.getAttribute("data-forecast");
                const previous = el.getAttribute("data-previous");
                const actual = el.getAttribute("data-actual");
                const impact = el.getAttribute("data-impact");

                if (diffSec > 0 && diffSec <= 10) {
                    el.innerHTML = `<span style="color:#ef4444; font-weight:700; animation: pulse 1s infinite; display:inline-block;">🚨 Release: ${diffSec}s</span>`;
                } else if (diffSec <= 0) {
                    if (actual === "N/A" || !actual || actual === "%25" || actual === "null") {
                        el.innerHTML = `<button class="btn-analyze" style="padding:0.25rem 0.5rem; font-size:0.75rem;" onclick="analyzeEventImpact('${title}', '${country}', '${forecast}', '${previous}')">⏳ Analyze Impact</button>`;
                    } else {
                        el.innerHTML = `<button class="btn-analyze" style="padding:0.25rem 0.5rem; font-size:0.75rem; background:rgba(16,185,129,0.2); color:#10b981; border-color:#10b981;" onclick="analyzeEventImpact('${title}', '${country}', '${forecast}', '${previous}', '${actual}')">📊 View Analysis</button>`;
                    }
                } else {
                    el.innerHTML = `<span style="color:var(--text-muted); font-size:0.75rem;">Scheduled</span>`;
                }
            });
        }
        
        setInterval(tickCalendarCountdowns, 1000);

        async function analyzeEventImpact(title, country, forecast, previous, actual) {
            title = decodeURIComponent(title);
            country = decodeURIComponent(country);
            forecast = decodeURIComponent(forecast);
            previous = decodeURIComponent(previous);
            actual = actual ? decodeURIComponent(actual) : "Pending";
            
            const overlayId = "calendar-analysis-overlay";
            let overlay = document.getElementById(overlayId);
            if (!overlay) {
                overlay = document.createElement("div");
                overlay.id = overlayId;
                overlay.style = "position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); backdrop-filter:blur(8px); z-index:9999; display:flex; justify-content:center; align-items:center; opacity:0; transition:opacity 200ms ease;";
                document.body.appendChild(overlay);
            }
            
            overlay.innerHTML = `
                <div style="background:var(--card-bg); border:1px solid var(--card-border); border-radius:16px; padding:2rem; max-width:550px; width:90%; box-shadow:0 20px 40px rgba(0,0,0,0.5); text-align:left; position:relative;">
                    <button onclick="document.getElementById('${overlayId}').style.opacity='0'; setTimeout(()=>document.getElementById('${overlayId}').remove(), 200);" style="position:absolute; top:1.2rem; right:1.2rem; background:none; border:none; color:var(--text-muted); font-size:1.5rem; cursor:pointer;">&times;</button>
                    <h3 style="color:var(--neon-accent); font-weight:800; font-size:1.2rem; margin-bottom:1rem;">📊 Live Macro Impact Analysis</h3>
                    <div style="font-size:0.95rem; font-weight:700; margin-bottom:0.5rem; color:#e2e8f0;">${title} (${country})</div>
                    <div style="display:flex; gap:1.5rem; font-size:0.8rem; color:var(--text-muted); margin-bottom:1.5rem;">
                        <div>Forecast: <b>${forecast}</b></div>
                        <div>Previous: <b>${previous}</b></div>
                        <div>Actual: <b style="color:#10b981;">${actual}</b></div>
                    </div>
                    <div id="calendar-analysis-body" style="font-size:0.88rem; line-height:1.6; color:var(--text-muted);">
                        ⏳ Running FinRobot real-time position analysis...
                    </div>
                </div>
            `;
            
            overlay.style.display = "flex";
            setTimeout(() => overlay.style.opacity = "1", 10);
            
            try {
                const res = await fetch(`${API_BASE}/api/calendar-analyze?title=${encodeURIComponent(title)}&country=${encodeURIComponent(country)}&actual=${encodeURIComponent(actual)}&forecast=${encodeURIComponent(forecast)}&previous=${encodeURIComponent(previous)}`);
                const data = await res.json();
                const body = document.getElementById("calendar-analysis-body");
                if (data.error) {
                    body.innerHTML = `<span style="color:#ef4444;">⚠️ Analysis failed: ${data.error}</span>`;
                } else {
                    body.innerHTML = data.analysis.replace(/\n/g, "<br/>");
                }
            } catch(e) {
                document.getElementById("calendar-analysis-body").innerHTML = `<span style="color:#ef4444;">⚠️ Connection failed.</span>`;
            }
        }

        // Load Sentiment News
        async function loadNews() {
            try {
                const container = document.getElementById("news-container");
                container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 2rem;">⏳ Loading & translating news feed...</div>`;
                
                const res = await fetch(`${API_BASE}/api/news?lang=${currentLanguage}`);
                const data = await res.json();
                container.innerHTML = "";
                
                if (data.length === 0) {
                    container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 2rem;">No recent news articles found.</div>`;
                    return;
                }

                data.forEach(a => {
                    const card = document.createElement("div");
                    card.className = "news-card";
                    card.innerHTML = `
                        <div class="news-top">
                            <span>📰 ${a.link ? `<a href="${a.link}" target="_blank" style="color: var(--primary); text-decoration: none; font-weight: 600;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">${a.source} ↗</a>` : a.source}</span>
                            <span>${a.publishedAt}</span>
                        </div>
                        <div class="news-title">${a.title}</div>
                        <div class="news-desc">${a.description || ''}</div>
                        <div style="display: flex; gap: 0.5rem; align-items: center; margin-top: 0.5rem; flex-wrap: wrap;">
                            <span class="sentiment-badge sentiment-${a.direction}">${a.direction}</span>
                            <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Confidence: ${a.confidence}</span>
                            <span style="background: rgba(99, 102, 241, 0.15); color: #818cf8; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; margin-left: auto;">🎯 ${a.asset || 'MARKET'}</span>
                        </div>
                    `;
                    container.appendChild(card);
                });
            } catch (e) {
                console.error("Failed to load news:", e);
            }
        }

        // ── Indian Market Intelligence ──────────────────────────────────────
        let scannedStocks = [];

                // 1. Top Signals (Graded Live)
                const topSigContainer = document.getElementById('intel-top-signals-list');
                topSigContainer.innerHTML = '';
                (data.top_graded_signals || []).forEach(sig => {
                    const dirColor = sig.direction === 'BULLISH' ? 'var(--gain)' : 'var(--loss)';
                    const dirBg = sig.direction === 'BULLISH' ? 'rgba(0,200,83,0.12)' : 'rgba(255,61,61,0.12)';
                    
                    let evHtml = (sig.evidence || []).map(ev => `
                        <div style="display:flex; align-items:center; gap:0.5rem; margin-top:0.35rem; font-size:0.8rem; color:${ev.pass ? 'var(--text-main)' : 'var(--text-muted)'};">
                            <span>${ev.pass ? '✓' : '✕'}</span>
                            <span style="${ev.pass ? '' : 'text-decoration:line-through; opacity:0.7;'}">${ev.text}</span>
                        </div>
                    `).join('');

                    const card = document.createElement('div');
                    card.style.cssText = `background:var(--card-bg); border:1px solid var(--card-border); border-radius:16px; padding:1.25rem 1.5rem; backdrop-filter:var(--glass-blur);`;
                    card.innerHTML = `
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                            <div style="font-size:1.15rem; font-weight:800;">${sig.strike}</div>
                            <span style="padding:0.25rem 0.75rem; border-radius:20px; font-weight:800; font-size:0.75rem; background:${dirBg}; color:${dirColor};">${sig.direction}</span>
                        </div>
                        <div style="font-size:0.92rem; font-weight:600; margin-bottom:0.75rem;">${sig.headline}</div>
                        <div style="display:flex; gap:0.5rem; align-items:center; flex-wrap:wrap; margin-bottom:0.75rem;">
                            <span style="background:rgba(255,255,255,0.06); border:1px solid var(--card-border); padding:0.2rem 0.6rem; border-radius:8px; font-size:0.78rem; font-weight:700;">${sig.flow_cr}</span>
                            <span style="background:rgba(255,255,255,0.06); border:1px solid var(--card-border); padding:0.2rem 0.6rem; border-radius:8px; font-size:0.78rem;">${sig.time}</span>
                            <span style="background:rgba(255,255,255,0.06); border:1px solid var(--card-border); padding:0.2rem 0.6rem; border-radius:8px; font-size:0.78rem; font-weight:700; color:var(--secondary-accent);">Score ${sig.score}</span>
                        </div>
                        <details style="border-top:1px solid var(--card-border); padding-top:0.6rem; margin-top:0.4rem;">
                            <summary style="font-size:0.78rem; font-weight:800; letter-spacing:0.06em; color:var(--text-muted); cursor:pointer; text-transform:uppercase;">WHAT THE EVIDENCE SHOWS</summary>
                            <div style="margin-top:0.4rem;">${evHtml}</div>
                        </details>
                    `;
                    topSigContainer.appendChild(card);
                });

                // 2. Institutional Campaigns (Stock Flow Cards)
                const campContainer = document.getElementById('intel-campaigns-list');
                campContainer.innerHTML = '';
                (data.campaigns || []).forEach(c => {
                    const isBull = c.direction === 'BULLISH';
                    const mainColor = isBull ? 'var(--gain)' : 'var(--loss)';
                    const flagColor = c.flag_color === 'green' ? 'var(--gain)' : (c.flag_color === 'red' ? 'var(--loss)' : '#f59e0b');

                    let legsHtml = (c.legs || []).map(l => `<span style="background:rgba(255,255,255,0.06); border:1px solid var(--card-border); padding:0.2rem 0.6rem; border-radius:8px; font-size:0.78rem; font-weight:600;">${l.name} ${l.amount}</span>`).join(' ');
                    let warnHtml = c.warning ? `<div style="font-size:0.78rem; color:#f59e0b; margin-top:0.5rem;">⚠️ ${c.warning}</div>` : '';

                    const cCard = document.createElement('div');
                    cCard.style.cssText = `background:var(--card-bg); border:1px solid ${isBull ? 'rgba(0,200,83,0.3)' : 'rgba(255,61,61,0.3)'}; border-radius:16px; padding:1.25rem 1.5rem; backdrop-filter:var(--glass-blur);`;
                    cCard.innerHTML = `
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                            <div style="font-size:1.1rem; font-weight:800;">${c.ticker}</div>
                            <div style="display:flex; gap:0.5rem; align-items:center;">
                                <span style="font-size:0.75rem; font-weight:800; padding:0.2rem 0.6rem; border-radius:12px; background:rgba(255,255,255,0.08); color:${flagColor};">${c.status_flag}</span>
                                <span style="font-size:0.8rem; font-weight:800; color:${mainColor};">${isBull ? '↑' : '↓'} ${c.direction}</span>
                            </div>
                        </div>
                        <div style="font-size:0.82rem; color:var(--text-muted); margin-bottom:0.6rem;">
                            ${c.gross_flow} · <span style="color:var(--secondary-accent); font-weight:700;">${c.net_flow}</span> · ${c.legs_count} · first ${c.first_time} · last ${c.last_time}
                        </div>
                        <div style="display:flex; gap:0.4rem; align-items:center; flex-wrap:wrap; margin-bottom:0.5rem;">${legsHtml}</div>
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="color:#f59e0b; font-size:0.85rem;">${c.stars} <span style="color:var(--text-muted); font-size:0.78rem;">${c.confirmation}</span></span>
                            <span style="font-size:0.75rem; color:var(--text-muted);">${c.oi_build}</span>
                        </div>
                        ${warnHtml}
                    `;
                    campContainer.appendChild(cCard);
                });

                // 3. Top OI Buildup
                const oiContainer = document.getElementById('intel-top-oi-list');
                oiContainer.innerHTML = '';
                (data.top_oi || []).forEach(item => {
                    const isBull = item.sentiment === 'BULLISH';
                    const color = isBull ? 'var(--gain)' : 'var(--loss)';
                    const row = document.createElement('div');
                    row.style.cssText = `display:flex; justify-content:space-between; align-items:center; padding:0.4rem 0; border-bottom:1px solid var(--card-border);`;
                    row.innerHTML = `
                        <div>
                            <div style="font-weight:700; font-size:0.88rem;">${item.strike}</div>
                            <div style="font-size:0.7rem; color:var(--text-muted);">${item.expiry}</div>
                        </div>
                        <div style="font-weight:800; font-size:0.9rem; color:${color};">${item.oi_change}</div>
                    `;
                    oiContainer.appendChild(row);
                });

                // 4. PCR Watch Bar Gauges
                const pcrContainer = document.getElementById('intel-pcr-watch-list');
                pcrContainer.innerHTML = '';
                (data.pcr_watch || []).forEach(p => {
                    const val = parseFloat(p.pcr);
                    const color = val > 1.15 ? 'var(--gain)' : (val < 0.85 ? 'var(--loss)' : '#f59e0b');
                    const barWidth = Math.min(100, Math.max(10, val * 50));
                    
                    const row = document.createElement('div');
                    row.innerHTML = `
                        <div style="display:flex; justify-content:space-between; font-size:0.8rem; font-weight:700; margin-bottom:0.25rem;">
                            <span>${p.index}</span>
                            <span style="color:${color};">${val}</span>
                        </div>
                        <div style="width:100%; height:6px; background:rgba(255,255,255,0.08); border-radius:4px; overflow:hidden;">
                            <div style="width:${barWidth}%; height:100%; background:${color}; border-radius:4px;"></div>
                        </div>
                    `;
                    pcrContainer.appendChild(row);
                });

                // 5. Kasandra Execution Trade Log
                const logData = data.trade_log || {};
                document.getElementById('intel-log-summary').textContent = logData.summary || '';
                document.getElementById('intel-log-time').textContent = logData.updated_at ? 'updated ' + logData.updated_at : '';
                const logTable = document.getElementById('intel-trade-log-body');
                logTable.innerHTML = '';
                (logData.trades || []).forEach(t => {
                    const isWin = t.result === 'WIN';
                    const resColor = isWin ? 'var(--gain)' : 'var(--loss)';
                    const resBg = isWin ? 'rgba(0,200,83,0.15)' : 'rgba(255,61,61,0.15)';
                    const pipsColor = t.pips.startsWith('+') ? 'var(--gain)' : 'var(--loss)';
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td style="font-size:0.8rem; color:var(--text-muted);">${t.date}</td>
                        <td style="font-weight:700; color:var(--loss);">${t.side}</td>
                        <td class="num" style="font-weight:600;">${t.entry}</td>
                        <td class="num" style="font-weight:700; color:${pipsColor};">${t.pips}</td>
                        <td><span style="padding:0.2rem 0.5rem; border-radius:6px; font-weight:800; font-size:0.75rem; background:${resBg}; color:${resColor};">${t.result}</span></td>
                    `;
                    logTable.appendChild(tr);
                });

                // F&O days
                document.getElementById('intel-fno-days').textContent = data.fno_days ?? '—';

                // NIFTY Scanner Table
                scannedStocks = data.scan || [];
                renderScannerTable();

                // Sector Summary
                const sectorEl = document.getElementById('intel-sectors');
                sectorEl.innerHTML = '';
                const sectors = data.sector_summary || {};
                Object.entries(sectors).sort((a,b) => b[1]-a[1]).forEach(([sec, score]) => {
                    const chip = document.createElement('div');
                    chip.style.cssText = `padding:0.4rem 0.9rem; border-radius:20px; font-size:0.8rem; font-weight:600;
                        border:1px solid ${score >= 1 ? 'rgba(0,200,83,0.3)' : score <= -1 ? 'rgba(255,61,61,0.3)' : 'var(--card-border)'};
                        background:${score >= 1 ? 'rgba(0,200,83,0.08)' : score <= -1 ? 'rgba(255,61,61,0.08)' : 'var(--card-bg)'};
                        color:${score >= 1 ? 'var(--gain)' : score <= -1 ? 'var(--loss)' : 'var(--text-muted)'};`;
                    chip.textContent = sec + ' ' + (score >= 0 ? '+' : '') + score;
                    sectorEl.appendChild(chip);
                });

                intelLoaded = true;
            } catch(e) {
                console.error('Failed to load Indian Intel:', e);
            }
        }

        function renderScannerTable() {
            const scanTable = document.getElementById('intel-scan-table');
            scanTable.innerHTML = '';
            
            const sectorFilter = document.getElementById("intel-sector-select").value || "ALL";
            const filtered = scannedStocks.filter(s => {
                return sectorFilter === "ALL" || (s.sector || "").toLowerCase() === sectorFilter.toLowerCase();
            });

            if (filtered.length === 0) {
                scanTable.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:2rem;color:var(--text-muted);">No matching signals found.</td></tr>';
                return;
            }

            filtered.forEach((s, i) => {
                const changeColor = s.change_pct >= 0 ? 'var(--gain)' : 'var(--loss)';
                const scoreColor = s.score >= 2 ? 'var(--gain)' : s.score <= -2 ? 'var(--loss)' : 'var(--text-muted)';
                const rsiColor = s.rsi < 35 ? 'var(--gain)' : s.rsi > 65 ? 'var(--loss)' : 'inherit';
                const row = document.createElement('tr');
                row.className = 'card-animate';
                row.style.animationDelay = (i * 40) + 'ms';
                row.innerHTML = `
                    <td style="font-weight:700; color:var(--neon-accent);">${s.ticker}</td>
                    <td style="font-size:0.8rem; color:var(--text-muted);">${s.sector || '—'}</td>
                    <td class="num" style="font-weight:600;">₹${(s.price || 0).toLocaleString('en-IN')}</td>
                    <td class="num" style="font-weight:600; color:${changeColor};">${s.change_pct >= 0 ? '+' : ''}${s.change_pct}%</td>
                    <td class="num" style="color:${rsiColor}; font-weight:600;">${s.rsi}</td>
                    <td class="num" style="font-weight:700; color:${scoreColor};">${s.score >= 0 ? '+' : ''}${s.score}</td>
                    <td><span style="padding:0.2rem 0.6rem; border-radius:8px; font-size:0.78rem; font-weight:700;
                        background:${s.score >= 2 ? 'rgba(0,200,83,0.15)' : s.score <= -2 ? 'rgba(255,61,61,0.15)' : 'rgba(99,102,241,0.12)'};
                        color:${s.score >= 2 ? 'var(--gain)' : s.score <= -2 ? 'var(--loss)' : 'var(--neon-accent)'};">${s.badge || ''} ${s.rating}</span></td>
                    <td style="font-size:0.78rem; color:var(--text-muted); max-width:180px;">${(s.signals || []).slice(0,2).join(', ')}</td>
                `;
                scanTable.appendChild(row);
            });
        }

        function changeExchange() {
            intelLoaded = false;
            loadIndianIntel();
        }

        function filterSector() {
            renderScannerTable();
        }

        async function broadcastIndianIntel() {
            const btn = document.getElementById("intel-broadcast-btn");
            const exchange = document.getElementById("intel-exchange-select").value || "NSE";
            
            btn.disabled = true;
            btn.innerText = "⏳ Broadcasting...";
            
            try {
                const res = await fetch(`${API_BASE}/api/broadcast-indian-intel?exchange=${exchange}`);
                const data = await res.json();
                if (data.success) {
                    alert("📢 " + data.message);
                } else {
                    alert("⚠️ " + (data.error || "Failed to broadcast."));
                }
            } catch(e) {
                console.error("Broadcast failed:", e);
                alert("⚠️ Connection failed.");
            } finally {
                btn.disabled = false;
                btn.innerText = "📢 Broadcast to Telegram";
            }
        }

        // ── Deep Analysis (Multi-Agent) ─────────────────────────────────────
        async function runDeepAnalysis() {
            const symbol = document.getElementById('deep-symbol-input').value.trim();
            if (!symbol) { alert('Enter a symbol first.'); return; }

            const btn = document.getElementById('deep-analyze-btn');
            const stepper = document.getElementById('deep-stepper');
            const result = document.getElementById('deep-result');
            const steps = ['step-technical','step-bull','step-bear','step-judge','step-trader'];

            btn.disabled = true;
            btn.textContent = '⏳ Running 5-agent pipeline…';
            stepper.style.display = 'block';
            result.innerHTML = '<div style="text-align:center; color:var(--text-muted); padding:2rem;">⏳ AI agents are analysing — this takes ~30 seconds…</div>';
            steps.forEach(s => { const el = document.getElementById(s); el.className = 'deep-step'; });

            // Animate steps forward while waiting
            let stepIdx = 0;
            const stepInterval = setInterval(() => {
                if (stepIdx > 0) document.getElementById(steps[stepIdx-1]).className = 'deep-step done';
                if (stepIdx < steps.length) document.getElementById(steps[stepIdx]).className = 'deep-step active';
                stepIdx++;
                if (stepIdx > steps.length) clearInterval(stepInterval);
            }, 5000);

            try {
                const res = await fetch(`${API_BASE}/api/deep-analyze?symbol=${encodeURIComponent(symbol)}`);
                const data = await res.json();
                clearInterval(stepInterval);
                steps.forEach(s => document.getElementById(s).className = 'deep-step done');
                btn.disabled = false;
                btn.textContent = 'Run Deep Analysis';

                if (data.error) {
                    result.innerHTML = `<div style="background:rgba(239,68,68,0.1);border:1px solid #ef4444;border-radius:12px;padding:1.5rem;color:#ef4444;font-weight:600;">⚠️ ${data.error}</div>`;
                    return;
                }

                const dir = (data.direction || 'NEUTRAL').toUpperCase();
                const isBuy = dir === 'BUY';
                const isSell = dir === 'SELL';
                const verdictClass = isBuy ? 'buy' : isSell ? 'sell' : 'neutral';
                const verdictColor = isBuy ? 'var(--gain)' : isSell ? 'var(--loss)' : 'var(--neon-accent)';

                result.innerHTML = `
                    <div style="display:flex;flex-direction:column;gap:1rem;" class="card-animate">
                        <!-- Price Summary -->
                        <div style="font-size:0.82rem;color:var(--text-muted);padding:0.75rem 1rem;background:var(--card-bg);border-radius:10px;border:1px solid var(--card-border);white-space:pre-line;">${data.price_data}</div>

                        <!-- Technical Report -->
                        <div class="synth-card">
                            <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.07em;color:var(--text-muted);margin-bottom:8px;">📊 Technical Analyst</div>
                            <p style="font-size:0.88rem;line-height:1.6;">${data.technical_report}</p>
                        </div>

                        <!-- Bull & Bear side by side -->
                        <div class="deep-cases-grid" style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">
                            <div class="bull-card">
                                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.07em;color:var(--gain);margin-bottom:8px;">🐂 Bull Case</div>
                                <p style="font-size:0.86rem;line-height:1.6;">${data.bull_thesis}</p>
                            </div>
                            <div class="bear-card">
                                <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.07em;color:var(--loss);margin-bottom:8px;">🐻 Bear Case</div>
                                <p style="font-size:0.86rem;line-height:1.6;">${data.bear_thesis}</p>
                            </div>
                        </div>

                        <!-- Synthesis -->
                        <div class="synth-card">
                            <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.07em;color:var(--neon-accent);margin-bottom:8px;">⚖️ Research Synthesis</div>
                            <p style="font-size:0.88rem;line-height:1.6;">${data.research_summary}</p>
                        </div>

                        <!-- Trade Verdict -->
                        <div class="trade-verdict-card ${verdictClass}">
                            <div style="font-size:2rem;font-weight:800;color:${verdictColor};">${dir}</div>
                            <div style="font-size:0.9rem;color:var(--text-muted);margin:0.5rem 0;">${data.reason}</div>
                            <div style="display:flex;justify-content:center;gap:2rem;margin-top:1rem;flex-wrap:wrap;">
                                <div><div style="font-size:0.7rem;color:var(--text-muted);">CONFIDENCE</div><div class="num" style="font-weight:700;font-size:1.2rem;">${data.confidence}</div></div>
                                <div><div style="font-size:0.7rem;color:var(--text-muted);">ENTRY</div><div class="num" style="font-weight:700;font-size:1.2rem;">${data.entry}</div></div>
                                <div><div style="font-size:0.7rem;color:var(--text-muted);">STOP LOSS</div><div class="num" style="font-weight:700;font-size:1.2rem;color:var(--loss);">${data.sl}</div></div>
                                <div><div style="font-size:0.7rem;color:var(--text-muted);">TP 1</div><div class="num" style="font-weight:700;font-size:1.2rem;color:var(--gain);">${data.tp1}</div></div>
                                <div><div style="font-size:0.7rem;color:var(--text-muted);">TP 2</div><div class="num" style="font-weight:700;font-size:1.2rem;color:var(--gain);">${data.tp2}</div></div>
                            </div>
                        </div>
                        <div style="font-size:0.72rem;color:var(--text-muted);text-align:right;">Generated: ${data.generated_at}</div>
                    </div>
                `;
            } catch(e) {
                clearInterval(stepInterval);
                btn.disabled = false;
                btn.textContent = 'Run Deep Analysis';
                result.innerHTML = `<div style="background:rgba(239,68,68,0.1);border:1px solid #ef4444;border-radius:12px;padding:1.5rem;color:#ef4444;font-weight:600;">⚠️ Network error. Try again.</div>`;
            }
        }

        async function runFinRobotAnalysis() {
            const symbol = document.getElementById('finrobot-symbol-input').value.trim();
            if (!symbol) { alert('Enter a symbol first.'); return; }

            const btn = document.getElementById('finrobot-analyze-btn');
            const stepper = document.getElementById('finrobot-stepper');
            const result = document.getElementById('finrobot-result');
            const steps = ['step-fr-fetch','step-fr-chart','step-fr-analyze','step-fr-pdf'];

            btn.disabled = true;
            btn.textContent = '⏳ Running FinRobot pipeline…';
            stepper.style.display = 'block';
            result.innerHTML = '<div style="text-align:center; color:var(--text-muted); padding:2rem;">⏳ FinRobot AI agents are compiling report — this takes ~30 seconds…</div>';
            steps.forEach(s => { const el = document.getElementById(s); el.className = 'deep-step'; });

            let stepIdx = 0;
            const stepInterval = setInterval(() => {
                if (stepIdx > 0) document.getElementById(steps[stepIdx-1]).className = 'deep-step done';
                if (stepIdx < steps.length) document.getElementById(steps[stepIdx]).className = 'deep-step active';
                stepIdx++;
                if (stepIdx > steps.length) clearInterval(stepInterval);
            }, 6000);

            try {
                const res = await fetch(`${API_BASE}/api/finrobot-report?symbol=${encodeURIComponent(symbol)}`);
                const data = await res.json();
                clearInterval(stepInterval);
                steps.forEach(s => document.getElementById(s).className = 'deep-step done');
                btn.disabled = false;
                btn.textContent = 'Generate Report';

                if (data.error) {
                    result.innerHTML = `<div style="background:rgba(239,68,68,0.1);border:1px solid #ef4444;border-radius:12px;padding:1.5rem;color:#ef4444;font-weight:600;">⚠️ ${data.error}</div>`;
                    return;
                }

                let formattedReport = data.report_content
                    .replace(/\n\n/g, '<br/><br/>')
                    .replace(/### (.*)/g, '<h4 style="font-size:1.1rem;font-weight:700;color:var(--neon-accent);margin:1.5rem 0 0.5rem 0;">$1</h4>')
                    .replace(/## (.*)/g, '<h3 style="font-size:1.3rem;font-weight:800;color:var(--neon-accent);margin:1.8rem 0 0.8rem 0;">$1</h3>')
                    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

                result.innerHTML = `
                    <div style="display:flex;flex-direction:column;gap:1.5rem;" class="card-animate">
                        <!-- Chart Display -->
                        <div class="synth-card" style="text-align:center;padding:1.5rem;">
                            <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.07em;color:var(--text-muted);margin-bottom:12px;text-align:left;">📈 Performance Chart</div>
                            <img src="${API_BASE}${data.chart_url}" style="max-width:100%;border-radius:8px;border:1px solid var(--card-border);" alt="Stock Chart" />
                        </div>

                        <!-- Statement Summaries side-by-side -->
                        <div style="display:grid;grid-template-columns:1fr;gap:1rem;font-size:0.8rem;">
                            <div class="synth-card">
                                <div style="font-weight:700;margin-bottom:0.5rem;color:var(--neon-accent);">📑 Income Statement Summary</div>
                                <pre style="font-family:monospace;white-space:pre-wrap;color:var(--text-muted);margin:0;">${data.income_statement}</pre>
                            </div>
                            <div class="synth-card">
                                <div style="font-weight:700;margin-bottom:0.5rem;color:var(--neon-accent);">⚖️ Balance Sheet Summary</div>
                                <pre style="font-family:monospace;white-space:pre-wrap;color:var(--text-muted);margin:0;">${data.balance_sheet}</pre>
                            </div>
                            <div class="synth-card">
                                <div style="font-weight:700;margin-bottom:0.5rem;color:var(--neon-accent);">💸 Cash Flow Summary</div>
                                <pre style="font-family:monospace;white-space:pre-wrap;color:var(--text-muted);margin:0;">${data.cash_flow}</pre>
                            </div>
                        </div>

                        <!-- AI Report Text -->
                        <div class="synth-card" style="padding:1.8rem;">
                            <div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.07em;color:var(--text-muted);margin-bottom:12px;">🤖 FinRobot Agent Analysis</div>
                            <div style="font-size:0.92rem;line-height:1.6;color:var(--text-muted);">${formattedReport}</div>
                        </div>

                        <!-- PDF Download Button -->
                        <div style="text-align:center;margin-top:1rem;">
                            <a href="${API_BASE}${data.pdf_url}" target="_blank" class="btn-analyze" style="text-decoration:none;display:inline-block;padding:0.75rem 2rem;border-radius:8px;font-weight:700;background:var(--neon-accent);color:white;">📥 Download PDF Report</a>
                        </div>
                    </div>
                `;
            } catch(e) {
                clearInterval(stepInterval);
                btn.disabled = false;
                btn.textContent = 'Generate Report';
                result.innerHTML = `<div style="background:rgba(239,68,68,0.1);border:1px solid #ef4444;border-radius:12px;padding:1.5rem;color:#ef4444;font-weight:600;">⚠️ Connection Failed: ${e}</div>`;
            }
        }

        // ── Intraday Breakout & Options Agent ───────────────────────────────
        let breakoutScanDone = false;
        
        async function initOptionsAgent() {
            if (!breakoutScanDone) {
                scanBreakoutStocks();
            }
        }
        
        async function scanBreakoutStocks() {
            const exchange = document.getElementById("opt-exchange-select").value || "NSE";
            const btn = document.getElementById("opt-scan-btn");
            const stepper = document.getElementById("opt-stepper");
            
            btn.disabled = true;
            btn.innerText = "⏳ Scanning F&O Universe...";
            stepper.style.display = "block";
            document.getElementById("step-opt-scan").className = "deep-step active";
            document.getElementById("step-opt-liquidity").className = "deep-step";
            document.getElementById("step-opt-agent").className = "deep-step";
            
            try {
                const res = await fetch(`${API_BASE}/api/breakout-scanner?exchange=${exchange}`);
                const data = await res.json();
                
                btn.disabled = false;
                btn.innerText = "⚡ Scan Breakout Candidates";
                
                if (data.error) {
                    alert("⚠️ " + data.error);
                    stepper.style.display = "none";
                    return;
                }
                
                document.getElementById("step-opt-scan").className = "deep-step done";
                document.getElementById("step-opt-liquidity").className = "deep-step active";
                
                const tbody = document.getElementById("opt-scanner-body");
                tbody.innerHTML = "";
                
                if (data.candidates && data.candidates.length > 0) {
                    data.candidates.forEach(c => {
                        const tr = document.createElement("tr");
                        
                        // Status badge colors
                        let statusColor = "var(--text-muted)";
                        let statusBg = "rgba(255,255,255,0.05)";
                        if (c.status.includes("PUMP")) {
                            statusColor = "var(--gain)";
                            statusBg = "rgba(0,200,83,0.12)";
                        } else if (c.status.includes("DUMP")) {
                            statusColor = "var(--loss)";
                            statusBg = "rgba(255,61,61,0.12)";
                        }
                        
                        // Option Details
                        const optText = c.option_contract !== "—" 
                            ? `<b>${c.option_contract.split(' ').slice(2).join(' ')}</b><br/><span style='font-size:0.72rem;color:var(--text-muted);'>Premium: ₹${c.option_premium} | Vol: ${c.option_vol.toLocaleString()}</span>`
                            : "—";
                        
                        // Action button only if status has breakout
                        const hasBreakout = c.status.includes("BREAKOUT") && c.option_contract !== "—";
                        const actionHtml = hasBreakout 
                            ? `<button class="btn-analyze" onclick="analyzeBreakoutStock('${c.ticker}', '${c.status}', '${c.option_contract}', ${c.option_premium})" style="padding:0.4rem 0.8rem; font-size:0.75rem; border-radius:8px;">🧠 Options AI</button>`
                            : `<span style='color:var(--text-muted); font-size:0.75rem;'>No Breakout</span>`;
                        
                        tr.innerHTML = `
                            <td><b>${c.ticker}</b><br/><span style='font-size:0.72rem;color:var(--text-muted);'>${c.sector}</span></td>
                            <td class="num">₹${c.price}</td>
                            <td class="num">${c.range_pct}%</td>
                            <td class="num" style="color: ${c.volume_ratio >= 1.5 ? 'var(--secondary-accent)' : 'var(--text-muted)'}">${c.volume_ratio}x</td>
                            <td><span style="padding:0.25rem 0.6rem; border-radius:12px; font-weight:800; font-size:0.7rem; background:${statusBg}; color:${statusColor}; text-transform:uppercase;">${c.status.replace(" BREAKOUT", "")}</span></td>
                            <td>${optText}</td>
                            <td>${actionHtml}</td>
                        `;
                        tbody.appendChild(tr);
                    });
                    
                    document.getElementById("opt-scanner-container").style.display = "block";
                    document.getElementById("step-opt-liquidity").className = "deep-step done";
                    breakoutScanDone = true;
                } else {
                    tbody.innerHTML = "<tr><td colspan='7' style='text-align:center;'>No candidates matched scanning criteria</td></tr>";
                    stepper.style.display = "none";
                }
            } catch(e) {
                console.error("Scanner failed:", e);
                alert("Failed to scan breakout candidates.");
                stepper.style.display = "none";
                btn.disabled = false;
                btn.innerText = "⚡ Scan Breakout Candidates";
            }
        }
        
        async function analyzeBreakoutStock(ticker, status, optContract, optPremium) {
            const exchange = document.getElementById("opt-exchange-select").value || "NSE";
            const stepper = document.getElementById("opt-stepper");
            
            stepper.style.display = "block";
            document.getElementById("step-opt-liquidity").className = "deep-step done";
            document.getElementById("step-opt-agent").className = "deep-step active";
            
            try {
                const res = await fetch(`${API_BASE}/api/breakout-analyze?ticker=${ticker}&exchange=${exchange}&status=${encodeURIComponent(status)}&option_contract=${encodeURIComponent(optContract)}&option_premium=${optPremium}`);
                const data = await res.json();
                
                if (data.error) {
                    alert("⚠️ " + data.error);
                    document.getElementById("step-opt-agent").className = "deep-step";
                    return;
                }
                
                document.getElementById("step-opt-agent").className = "deep-step done";
                
                // Update Recommendation Card
                const action = data.trade.action || "HOLD";
                const actBadge = document.getElementById("opt-trade-action");
                actBadge.innerText = action;
                
                if (action.includes("BUY CALL") || action.includes("BULL")) {
                    actBadge.style.background = "rgba(0,200,83,0.15)";
                    actBadge.style.color = "var(--gain)";
                } else if (action.includes("BUY PUT") || action.includes("BEAR")) {
                    actBadge.style.background = "rgba(255,61,61,0.15)";
                    actBadge.style.color = "var(--loss)";
                } else {
                    actBadge.style.background = "rgba(99,102,241,0.12)";
                    actBadge.style.color = "var(--neon-accent)";
                }
                
                // Parse option strike description for readability
                const strikeParts = data.option_contract.split(" ");
                const expiryText = strikeParts[1] || "";
                const strikeVal = strikeParts[2] || "";
                const typeText = strikeParts[3] || "";
                
                document.getElementById("opt-trade-target").innerHTML = `<b>${ticker}</b> ${expiryText}<br/><b>${strikeVal} ${typeText}</b>`;
                document.getElementById("opt-trade-entry").innerText = "₹" + (data.trade.premium_entry || "—");
                document.getElementById("opt-trade-sl").innerText = "₹" + (data.trade.sl || "—");
                document.getElementById("opt-trade-tp1").innerText = "₹" + (data.trade.tp1 || "—");
                document.getElementById("opt-trade-tp2").innerText = "₹" + (data.trade.tp2 || "—");
                document.getElementById("opt-trade-rationale").innerText = data.trade.rationale || "—";
                
                document.getElementById("opt-result-container").style.display = "block";
                
                // Scroll to result view
                document.getElementById("opt-result-container").scrollIntoView({ behavior: 'smooth' });
            } catch(e) {
                console.error("AI Breakout analysis failed:", e);
                alert("Failed to analyze breakout options.");
                document.getElementById("step-opt-agent").className = "deep-step";
            }
        }

        // Initialize date inputs
        try {
            const today = new Date().toISOString().split('T')[0];
            document.getElementById("cal-from-date").value = today;
            const nextWeek = new Date();
            nextWeek.setDate(nextWeek.getDate() + 7);
            document.getElementById("cal-to-date").value = nextWeek.toISOString().split('T')[0];
        } catch(e) {}

        // Initial Data Fetch & Page Polls
        loadSignals();
        loadCalendar();
        loadNews();

        setInterval(loadSignals, 10000);
        setInterval(loadCalendar, 60000);
        setInterval(loadNews, 30000);

        async function updateUptimeLive() {
            try {
                const res = await fetch(`${API_BASE}/api/uptime`);
                const data = await res.json();
                if (data && data.uptime) {
                    document.getElementById("uptime-status-text").innerText = `Live: 24/7 (Uptime: ${data.uptime})`;
                    const dot = document.querySelector("#uptime-container .status-dot");
                    if (dot) {
                        dot.style.background = "#10b981";
                        dot.style.boxShadow = "0 0 10px #10b981";
                    }
                    document.getElementById("uptime-container").style.color = "#10b981";
                    document.getElementById("uptime-container").style.background = "rgba(16, 185, 129, 0.1)";
                    document.getElementById("uptime-container").style.borderColor = "rgba(16, 185, 129, 0.2)";
                    
                    // Update Health fields
                    if (data.health) {
                        const dbVal = document.getElementById("health-db-val");
                        const tgVal = document.getElementById("health-tg-val");
                        if (dbVal) {
                            dbVal.innerText = data.health.database === "Healthy" ? "🟢 Healthy" : "🔴 Degraded";
                            dbVal.style.color = data.health.database === "Healthy" ? "#10b981" : "#ef4444";
                        }
                        if (tgVal) {
                            tgVal.innerText = data.health.telegram === "Active" ? "🟢 Active" : "⚪ Disabled";
                            tgVal.style.color = data.health.telegram === "Active" ? "#10b981" : "var(--text-muted)";
                        }
                    }
                }
            } catch(e) {
                console.warn("Uptime fetch failed:", e);
                document.getElementById("uptime-status-text").innerText = `Offline`;
                const dot = document.querySelector("#uptime-container .status-dot");
                if (dot) {
                    dot.style.background = "#ef4444";
                    dot.style.boxShadow = "0 0 10px #ef4444";
                }
                document.getElementById("uptime-container").style.color = "#ef4444";
                document.getElementById("uptime-container").style.background = "rgba(239, 68, 68, 0.1)";
                document.getElementById("uptime-container").style.borderColor = "rgba(239, 68, 68, 0.2)";
            }
        }
        
        function toggleHealthDropdown(event) {
            event.stopPropagation();
            const el = document.getElementById("health-status-tooltip");
            if (!el) return;
            el.style.display = el.style.display === "block" ? "none" : "block";
        }
        
        // Close dropdown when clicking elsewhere
        document.addEventListener("click", () => {
            const el = document.getElementById("health-status-tooltip");
            if (el) el.style.display = "none";
        });
        
        updateUptimeLive();
        setInterval(updateUptimeLive, 5000);

        // ── AI Chatbot Widget ───────────────────────────────────────────────
        (function() {
            // Append CSS
            const style = document.createElement("style");
            style.textContent = `
                .chat-widget-btn {
                    position: fixed;
                    bottom: 24px;
                    right: 24px;
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, var(--neon-accent), #a855f7);
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 8px 32px rgba(168, 85, 247, 0.4);
                    cursor: pointer;
                    z-index: 1000;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }
                .chat-widget-btn:hover {
                    transform: scale(1.08) rotate(5deg);
                    box-shadow: 0 12px 40px rgba(168, 85, 247, 0.6);
                }
                .chat-widget-btn svg {
                    width: 28px;
                    height: 28px;
                }
                .chat-widget-btn::after {
                    content: '';
                    position: absolute;
                    top: 2px;
                    right: 2px;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    background: #22c55e;
                    border: 2px solid var(--dashboard-bg);
                }

                .chat-drawer {
                    position: fixed;
                    bottom: 96px;
                    right: 24px;
                    width: 380px;
                    height: 520px;
                    border-radius: 20px;
                    background: rgba(18, 18, 29, 0.85);
                    backdrop-filter: blur(20px);
                    -webkit-backdrop-filter: blur(20px);
                    border: 1px solid var(--card-border);
                    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
                    z-index: 1000;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    transform: translateY(30px) scale(0.95);
                    opacity: 0;
                    visibility: hidden;
                    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                }
                .chat-drawer.open {
                    transform: translateY(0) scale(1);
                    opacity: 1;
                    visibility: visible;
                }

                .chat-header {
                    padding: 1rem 1.25rem;
                    background: linear-gradient(90deg, rgba(168, 85, 247, 0.15), rgba(6, 182, 212, 0.15));
                    border-bottom: 1px solid var(--card-border);
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                .chat-header-title {
                    font-weight: 700;
                    font-size: 0.95rem;
                    color: var(--text-primary);
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                .chat-header-status {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #22c55e;
                    display: inline-block;
                }
                .chat-close-btn {
                    background: none;
                    border: none;
                    color: var(--text-muted);
                    cursor: pointer;
                    font-size: 1.25rem;
                    transition: color 0.2s;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .chat-close-btn:hover {
                    color: var(--loss);
                }

                .chat-messages {
                    flex: 1;
                    padding: 1.25rem;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }
                .chat-messages::-webkit-scrollbar {
                    width: 4px;
                }
                .chat-messages::-webkit-scrollbar-thumb {
                    background: var(--card-border);
                    border-radius: 10px;
                }

                .chat-bubble {
                    max-width: 80%;
                    padding: 0.75rem 1rem;
                    border-radius: 16px;
                    font-size: 0.85rem;
                    line-height: 1.4;
                    word-wrap: break-word;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
                .chat-bubble.bot {
                    align-self: flex-start;
                    background: var(--card-bg);
                    color: var(--text-primary);
                    border-bottom-left-radius: 4px;
                    border: 1px solid var(--card-border);
                }
                .chat-bubble.user {
                    align-self: flex-end;
                    background: linear-gradient(135deg, var(--neon-accent), #a855f7);
                    color: white;
                    border-bottom-right-radius: 4px;
                }

                .chat-input-area {
                    padding: 1rem;
                    border-top: 1px solid var(--card-border);
                    display: flex;
                    gap: 8px;
                    background: rgba(18, 18, 29, 0.5);
                }
                .chat-input {
                    flex: 1;
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid var(--card-border);
                    border-radius: 12px;
                    padding: 0.75rem 1rem;
                    color: var(--text-primary);
                    font-size: 0.85rem;
                    outline: none;
                    transition: border-color 0.2s;
                }
                .chat-input:focus {
                    border-color: var(--neon-accent);
                }
                .chat-send-btn {
                    background: linear-gradient(135deg, var(--neon-accent), #a855f7);
                    border: none;
                    border-radius: 12px;
                    width: 44px;
                    height: 44px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    cursor: pointer;
                    transition: transform 0.2s;
                }
                .chat-send-btn:hover {
                    transform: scale(1.05);
                }

                .typing-indicator {
                    display: flex;
                    gap: 4px;
                    align-items: center;
                    padding: 4px 8px;
                }
                .typing-dot {
                    width: 6px;
                    height: 6px;
                    background: var(--text-muted);
                    border-radius: 50%;
                    animation: typingBounce 1.4s infinite ease-in-out both;
                }
                .typing-dot:nth-child(1) { animation-delay: -0.32s; }
                .typing-dot:nth-child(2) { animation-delay: -0.16s; }

                @keyframes typingBounce {
                    0%, 80%, 100% { transform: scale(0); }
                    40% { transform: scale(1); }
                }

                @media (max-width: 480px) {
                    .chat-drawer {
                        width: calc(100vw - 32px);
                        height: 460px;
                        right: 16px;
                        bottom: 88px;
                    }
                }
            `;
            document.head.appendChild(style);

            // Append HTML elements
            const btn = document.createElement("div");
            btn.className = "chat-widget-btn";
            btn.onclick = toggleChat;
            btn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
            `;
            document.body.appendChild(btn);

            const drawer = document.createElement("div");
            drawer.id = "chat-drawer";
            drawer.className = "chat-drawer";
            drawer.innerHTML = `
                <div class="chat-header">
                    <div class="chat-header-title">
                        <span class="chat-header-status"></span>
                        <span>AI Market Copilot 🤖</span>
                    </div>
                    <button class="chat-close-btn" onclick="toggleChat()">&times;</button>
                </div>
                <div class="chat-messages" id="chat-messages">
                    <div class="chat-bubble bot">
                        Hello! I am your AI Market Assistant. Ask me anything about tickers (e.g. "analyze Gold" or "Price of BTCUSD") or general trading strategies! I ground my answers in live market data. 📈
                    </div>
                </div>
                <div class="chat-input-area">
                    <input type="text" id="chat-input" class="chat-input" placeholder="Ask a question..." />
                    <button class="chat-send-btn" onclick="sendChatMessage()">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="22" y1="2" x2="11" y2="13"></line>
                            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                        </svg>
                    </button>
                </div>
            `;
            document.body.appendChild(drawer);

            // Setup input listener
            setTimeout(() => {
                const input = document.getElementById("chat-input");
                if (input) {
                    input.addEventListener("keypress", function(e) {
                        if (e.key === "Enter") {
                            sendChatMessage();
                        }
                    });
                }
            }, 100);
        })();

        function toggleChat() {
            const drawer = document.getElementById("chat-drawer");
            drawer.classList.toggle("open");
            if (drawer.classList.contains("open")) {
                document.getElementById("chat-input").focus();
            }
        }

        function appendChatMessage(sender, text) {
            const container = document.getElementById("chat-messages");
            const bubble = document.createElement("div");
            bubble.className = `chat-bubble ${sender}`;
            
            let formatted = text
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n/g, '<br>');
            
            bubble.innerHTML = formatted;
            container.appendChild(bubble);
            container.scrollTop = container.scrollHeight;
        }

        async function sendChatMessage() {
            const input = document.getElementById("chat-input");
            const query = input.value.trim();
            if (!query) return;

            input.value = "";
            appendChatMessage("user", query);

            const container = document.getElementById("chat-messages");
            const indicator = document.createElement("div");
            indicator.id = "chat-typing-indicator";
            indicator.className = "chat-bubble bot";
            indicator.innerHTML = `
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            `;
            container.appendChild(indicator);
            container.scrollTop = container.scrollHeight;

            try {
                const response = await fetch(`${API_BASE}/api/chat`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ message: query })
                });
                const data = await response.json();
                
                const oldIndicator = document.getElementById("chat-typing-indicator");
                if (oldIndicator) oldIndicator.remove();

                if (data.error) {
                    appendChatMessage("bot", `⚠️ Error: ${data.error}`);
                } else {
                    appendChatMessage("bot", data.response);
                }
            } catch(e) {
                const oldIndicator = document.getElementById("chat-typing-indicator");
                if (oldIndicator) oldIndicator.remove();
                appendChatMessage("bot", "⚠️ Network error. Please try again.");
            }
        }
    