import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Talk to Remo button
html = re.sub(
    r'<button([^>]+)class="btn btn-secondary([^"]*)"([^>]*)>\s*<span>Talk to Remo</span>',
    r'<button\1class="btn btn-primary\2"\3 style="background-color: #FC2415 !important; border-color: #FC2415 !important; color: white !important;">\n              <span>Talk to Remo</span>',
    html
)

# Replace Get instant call button
html = re.sub(
    r'<button([^>]+)id="btn-instant-trigger"([^>]*)>\s*<span>Get instant call</span>',
    r'<button\1id="btn-instant-trigger"\2 style="background-color: #FC2415 !important; border-color: #FC2415 !important; color: white !important;">\n                  <span>Get instant call</span>',
    html
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Buttons updated successfully.")
