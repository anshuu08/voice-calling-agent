import re

with open('styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# 1. Change .hp-bullet background to orange
css = re.sub(
    r'(\.hp-bullet\s*\{[^}]*background-color:\s*)([^;]+)(;)',
    r'\g<1>#FC2415\3',
    css
)

# Also if hp-bullet is missing background-color but has background:
css = re.sub(
    r'(\.hp-bullet\s*\{[^}]*background:\s*)([^;]+)(;)',
    r'\g<1>#FC2415\3',
    css
)

# 2. Change trust checkmarks to orange if they have a specific class. 
# They might use color or stroke. Let's add a rule.
orange_rules = '''
.hp-bullet { background-color: #FC2415 !important; }
.trust-item svg { stroke: #FC2415 !important; color: #FC2415 !important; }
.hero-phone-screen .accent-dot, .hero-phone-screen .active-indicator { background-color: #FC2415 !important; }
'''
if '.hp-bullet { background-color: #FC2415 !important; }' not in css:
    css += orange_rules

# 3. Reduce hero section margin/padding to 80px
css = re.sub(
    r'(\.hero-section\s*\{[^}]*padding-top:\s*)\d+px',
    r'\g<1>80px',
    css
)
css = re.sub(
    r'(\.hero-section\s*\{[^}]*padding-bottom:\s*)\d+px',
    r'\g<1>80px',
    css
)
# Just in case it uses margin
css = re.sub(
    r'(\.hero-section\s*\{[^}]*margin-top:\s*)\d+px',
    r'\g<1>80px',
    css
)

with open('styles.css', 'w', encoding='utf-8') as f:
    f.write(css)
print("Updated styles.css with orange elements and 80px hero padding.")

# Let's also check index.html to apply inline orange to any checkmarks if needed
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# "Appointment Confirmation" checkmarks might have a class we can target directly in html
html = html.replace('<svg class="trust-svg-icon"', '<svg class="trust-svg-icon" style="stroke: #FC2415;"')
# the user mentioned "few details in phone in orange", maybe I'll add inline color to phone elements
html = html.replace('class="live-dot-pulse pulse-blue"', 'class="live-dot-pulse" style="background:#FC2415;"')
html = html.replace('class="v-bar"', 'class="v-bar" style="background:#FC2415;"') # Voice visualizer in hero

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated index.html elements to orange.")
