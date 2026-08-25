with open("dashboard.html", "r", encoding="utf-8") as f:
    content = f.read()

target = """                const topSigContainer = document.getElementById('intel-top-signals-list');
                topSigContainer.innerHTML = '';
                (data.top_graded_signals || []).forEach(sig => {"""

replacement = """                const topSigContainer = document.getElementById('intel-top-signals-list');
                topSigContainer.innerHTML = '';
                
                if (!data.top_graded_signals || data.top_graded_signals.length === 0) {
                    topSigContainer.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-muted); font-size: 0.9rem; background: rgba(0,0,0,0.1); border-radius: 12px; border: 1px dashed var(--card-border);">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">??????</div>
                        <b>No High-Probability Setups Found</b><br/>
                        The engine requires a 70%+ confidence score and strong institutional flow to generate a graded signal. Scanning market...
                    </div>`;
                }

                (data.top_graded_signals || []).forEach(sig => {"""

content = content.replace(target, replacement)

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Empty UI state added")
