import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]

# We want to replace the auth-brand-orb and sidebar-brand-orb SVGs and text with the logo image.

auth_pattern = re.compile(r'<div class="auth-brand-orb">.*?</div>\s*<span class="auth-brand-text">TakeRemo</span>', re.DOTALL)
sidebar_pattern = re.compile(r'<div class="sidebar-brand-orb">.*?</div>\s*<span class="sidebar-brand-text">TakeRemo</span>', re.DOTALL)

auth_replacement = '<img src="/assets/Takeremo%20AI%20Calling%20Logo.png" alt="TakeRemo AI Calling" style="height: 36px; width: auto; object-fit: contain;">'
sidebar_replacement = '<img src="/assets/Takeremo%20AI%20Calling%20Logo.png" alt="TakeRemo AI Calling" style="height: 32px; width: auto; object-fit: contain;">'

for file in html_files:
    if file == 'index.html':
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = auth_pattern.sub(auth_replacement, content)
    new_content = sidebar_pattern.sub(sidebar_replacement, new_content)
    
    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file}")
