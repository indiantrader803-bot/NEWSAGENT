with open("dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Remove Nav Item
import re
nav_regex = re.compile(r'\s*<li class="nav-item" onclick="switchPage\(\'page-btc-lottery\', this\)">.*?</li>', re.DOTALL)
html = nav_regex.sub('', html)

# Remove the BTC Lottery Miner Page Block
# It starts at <!-- BTC LOTTERY MINER PAGE --> and ends at the closing </div> of that panel.
# The panel contains several divs, but we know it's inserted before the closing divs of the workspace.
start_str = "<!-- BTC LOTTERY MINER PAGE -->"
end_str = 'id="miner-terminal"'

start_idx = html.find(start_str)
if start_idx != -1:
    end_terminal = html.find(end_str, start_idx)
    # the terminal div closes with </div>, then the analyzer-box closes with </div>, then the page-panel closes with </div>
    # let's find the third </div> after end_terminal
    current_idx = end_terminal
    for _ in range(3):
        current_idx = html.find("</div>", current_idx) + 6
    
    html = html[:start_idx] + html[current_idx:]

# Remove JS Logic
# Starts at // ==========================
# // BTC LOTTERY MINER LOGIC
js_start = html.find("// ==========================\n        // BTC LOTTERY MINER LOGIC")
if js_start == -1:
    js_start = html.find("// ==========================\n          // BTC LOTTERY MINER LOGIC")

if js_start != -1:
    js_end = html.find("function finishMining()", js_start)
    if js_end != -1:
        # Find the closing bracket of finishMining()
        brace_count = 0
        in_function = False
        final_idx = js_end
        
        for i in range(js_end, len(html)):
            if html[i] == '{':
                brace_count += 1
                in_function = True
            elif html[i] == '}':
                brace_count -= 1
                if in_function and brace_count == 0:
                    final_idx = i + 1
                    break
        
        html = html[:js_start] + html[final_idx:]

with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
print("Removed successfully!")
