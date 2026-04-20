# Append the rest of the HTML generation to gen_map.py

remaining = """
    '    <button class="popup-close" onclick="closePopup()">×</button>\\n'
    '    </div>\\n'
    '    <div class="popup-body" id="popupBody"></div>\\n'
    '  </div>\\n'
    '</div>\\n'
    + (JS % popup_json) + '\\n'
    '</body>\\n</html>'
)

with open('/root/.openclaw/workspace/etf-map-site/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"done")
"""
with open('/root/.openclaw/workspace/gen_map.py', 'a') as f:
    f.write(remaining)

import subprocess
result = subprocess.run(['python3', '/root/.openclaw/workspace/gen_map.py'], capture_output=True, text=True)
print(result.stdout)
print(result.stderr[:500] if result.stderr else '')
