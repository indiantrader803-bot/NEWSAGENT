import re
with open('dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'<th>DATE</th>', r'<th>DATE</th>\n                                      <th>ASSET</th>', content)
content = re.sub(r'(<td[^>]*>\s*\$\{t\.date\}\s*</td>)', r'\1\n                          <td style="font-weight:700; color:var(--text-color);">${t.asset || "NIFTY"}</td>', content)

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(content)
