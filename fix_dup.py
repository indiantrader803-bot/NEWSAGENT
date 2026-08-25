import re
with open('dashboard.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Also fix multiple ASSET headers just in case
c = re.sub(r'(<th>ASSET</th>\s*)+', r'<th>ASSET</th>\n', c)
c = re.sub(r'(\s*<td style="font-weight:700; color:var\(--text-color\);"></td>)+', '', c)

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(c)
