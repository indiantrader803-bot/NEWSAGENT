import re

with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Enhance overall CSS and Typography
ui_css_inject = """
        /* PRO MAX UI UPGRADES */
        body {
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.15), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.1), transparent 25%);
            background-attachment: fixed;
        }
        
        .sidebar {
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-right: 1px solid var(--card-border);
            background: linear-gradient(180deg, var(--card-bg) 0%, rgba(0,0,0,0.2) 100%);
            box-shadow: 4px 0 24px rgba(0,0,0,0.2);
        }
        
        .nav-item {
            border-radius: 12px;
            margin: 4px 12px;
            transition: all var(--dur-base) var(--ease-spring);
            font-weight: 500;
        }
        
        .nav-item:hover {
            transform: translateX(4px);
            background: rgba(99, 102, 241, 0.15);
        }
        
        .nav-item.active {
            background: linear-gradient(90deg, rgba(99, 102, 241, 0.2) 0%, transparent 100%);
            color: #fff;
            border-left: 3px solid var(--neon-accent);
            box-shadow: inset 2px 0 12px rgba(99, 102, 241, 0.1);
        }

        .page-panel.active {
            animation: slide-up-fade var(--dur-slow) var(--ease-spring) forwards;
        }
        @keyframes slide-up-fade {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Signal Cards Pro */
        .signal-card {
            border-radius: 16px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            background: linear-gradient(145deg, var(--card-bg) 0%, rgba(20, 25, 40, 0.6) 100%);
            border: 1px solid var(--card-border);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
            transition: transform var(--dur-base) var(--ease-spring), box-shadow var(--dur-base) ease;
        }
        
        .signal-card:hover {
            transform: translateY(-6px) scale(1.02);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            border-color: rgba(99, 102, 241, 0.4);
        }
        
        .signal-badge {
            font-weight: 800;
            letter-spacing: 1px;
            text-transform: uppercase;
            border-radius: 8px;
        }
        .buy .signal-badge { background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.4); }
        .sell .signal-badge { background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); }

        /* Confidence Bar Animated */
        .confidence-bg {
            border-radius: 6px;
            background: rgba(255,255,255,0.05);
            overflow: hidden;
        }
        .confidence-bar {
            border-radius: 6px;
            background: linear-gradient(90deg, #4f46e5, #ec4899);
            box-shadow: 0 0 10px rgba(236, 72, 153, 0.5);
        }

        /* Table Pro */
        .analyzer-box {
            border-radius: 16px;
            backdrop-filter: blur(12px);
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            box-shadow: 0 4px 24px rgba(0,0,0,0.1);
        }
        
        th {
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.75rem !important;
            font-weight: 700;
            border-bottom: 1px solid var(--card-border);
        }
        
        tr {
            transition: background 0.2s ease;
        }
        tr:hover td {
            background: rgba(99, 102, 241, 0.08);
        }

        .filter-input {
            border-radius: 10px;
            background: rgba(0,0,0,0.2);
            border: 1px solid var(--card-border);
            transition: all 0.2s ease;
        }
        .filter-input:focus {
            background: rgba(0,0,0,0.3);
            border-color: var(--neon-accent);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
        }

        .btn-analyze {
            border-radius: 10px;
            background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
            box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
            font-weight: 600;
            transition: all var(--dur-base) var(--ease-spring);
        }
        .btn-analyze:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(79, 70, 229, 0.6);
        }
        
        /* Light mode refinements */
        [data-theme="light"] .sidebar {
            background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
            box-shadow: 4px 0 24px rgba(0,0,0,0.05);
        }
        [data-theme="light"] body {
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.08), transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(16, 185, 129, 0.05), transparent 25%);
        }
        [data-theme="light"] .signal-card {
            background: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
        }
"""
html = html.replace('/* === UI/UX IMPROVEMENTS === */', ui_css_inject + '\n/* === UI/UX IMPROVEMENTS === */')

# Make the Header Title a glowing gradient
html = html.replace('<h1 style="font-size: 1.4rem; font-weight: 700; margin: 0; color: var(--text-color); display: flex; align-items: center; gap: 10px;">', 
                    '<h1 style="font-size: 1.5rem; font-weight: 800; margin: 0; background: linear-gradient(90deg, #60a5fa, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; display: flex; align-items: center; gap: 10px; text-shadow: 0 0 20px rgba(167, 139, 250, 0.3);">')


with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("UI updated!")
