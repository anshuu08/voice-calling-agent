import re
import os

print("Applying TakeRemo UI Fixes...")

# ========================================================
# 1. UPDATE index.html
# ========================================================
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Update favicon links
html = re.sub(
    r'<link rel=["\']icon["\'][^>]*>',
    '<link rel="icon" type="image/png" href="/assets/tabIcon.png">\n  <link rel="shortcut icon" href="/favicon.ico">',
    html
)

# Update nav brand to use Takeremo AI Calling Logo.png
nav_brand_pattern = r'<a href="#hero" class="nav-brand">[\s\S]*?</a>'
new_nav_brand = '''<a href="#hero" class="nav-brand">
        <img src="/assets/Takeremo%20AI%20Calling%20Logo.png" alt="TakeRemo AI Calling" class="nav-brand-logo-img">
      </a>'''
html = re.sub(nav_brand_pattern, new_nav_brand, html, count=1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Updated index.html: nav brand logo and favicon.")


# ========================================================
# 2. UPDATE script.js (Smooth animations & cards containment)
# ========================================================
with open('script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Smooth out bar graph animations (900ms smooth cubic-bezier)
js = js.replace(
    "bar.style.transition = 'height 420ms cubic-bezier(0.16, 1, 0.3, 1)';",
    "bar.style.transition = 'height 900ms cubic-bezier(0.22, 1, 0.36, 1)';"
)
js = js.replace(
    "bar.style.transitionDelay = `${i * 25}ms`;",
    "bar.style.transitionDelay = `${i * 45}ms`;"
)

# Smooth out donut chart duration to 850ms
js = js.replace(
    "animateDonutAndCenter(d.maskStroke, d.centerStat, targetVal, isFloat, 480);",
    "animateDonutAndCenter(d.maskStroke, d.centerStat, targetVal, isFloat, 850);"
)

# In 3D deck rendering: ensure inactive cards do NOT translate above top (no negative transY that sticks out)
# When scene 0 is inactive, keep transY0 = 0 or positive, and hide it with opacity = 0
js = js.replace(
    "scale0 = 0.90; transY0 = -40; transZ0 = -50; opacity0 = 0.30; brightness0 = 0.40; pointer0 = 'none';",
    "scale0 = 0.92; transY0 = 0; transZ0 = -40; opacity0 = 0.0; brightness0 = 0.40; pointer0 = 'none';"
)
js = js.replace(
    "scale1 = 0.95; transY1 = -22; transZ1 = -25; opacity1 = 0.65; brightness1 = 0.65; pointer1 = 'none';",
    "scale1 = 0.95; transY1 = 0; transZ1 = -20; opacity1 = 0.0; brightness1 = 0.65; pointer1 = 'none';"
)
js = js.replace(
    "transY0 = -22 * e;",
    "transY0 = 0;"
)
js = js.replace(
    "transY0 = -22 - 18 * e2;",
    "transY0 = 0;"
)
js = js.replace(
    "transY1 = -22 * e2;",
    "transY1 = 0;"
)

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(js)
print("Updated script.js: smooth bar/chart animation and deck containment.")


# ========================================================
# 3. UPDATE styles.css (Contrast, Cards Sizing, Spacing)
# ========================================================
with open('styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Append targeted, authoritative CSS overrides at the bottom
overrides = """
/* ==========================================================================
   TAKEREMO BRANDING, VISIBILITY & LAYOUT REFINEMENTS
   ========================================================================== */

/* 1. Nav Brand Logo */
.nav-brand-logo-img {
  height: 42px;
  width: auto;
  max-width: 220px;
  object-fit: contain;
  display: block;
  transition: opacity 0.2s ease;
}
.nav-brand-logo-img:hover {
  opacity: 0.92;
}

/* 2. Reduced Section Spacing After Nav and Hero */
.hero-section {
  padding-top: 36px !important;
  padding-bottom: 28px !important;
}
.section-spacing {
  padding-top: 50px !important;
  padding-bottom: 50px !important;
}
.human-stories-wrap {
  margin-bottom: 24px !important;
  padding: 24px 28px !important;
}

/* 3. Cards Deck & Container Containment (01 Recruitment, 02 Sales, 03 Support) */
.cards-stack-stage {
  min-height: 640px !important;
  height: 640px !important;
  position: relative !important;
  width: 100% !important;
  max-width: 100% !important;
  overflow: hidden !important;
  border-radius: var(--radius-card) !important;
}

.story-card {
  position: absolute !important;
  inset: 0 !important;
  width: 100% !important;
  height: 100% !important;
  background: #0B111E !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: var(--radius-card) !important;
  padding: 20px 28px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  overflow: hidden !important;
  box-sizing: border-box !important;
}

.story-card .feature-split-grid,
.feature-split-grid.domain-card-grid {
  width: 100% !important;
  display: grid !important;
  grid-template-columns: 250px 1fr 375px !important;
  gap: 20px !important;
  align-items: center !important;
}

/* 4. Realistic Call Card: Compact & Contained inside Box */
.realistic-call-card {
  background: #0F172A !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  border-radius: 18px !important;
  box-shadow: 0 12px 35px rgba(0, 0, 0, 0.45) !important;
  overflow: hidden !important;
  width: 100% !important;
  max-width: 375px !important;
  margin: 0 auto !important;
}

.call-card-top {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding: 8px 14px !important;
  background: #0B111E !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
}
.call-status-tag {
  color: #F8FAFC !important;
  font-size: 0.68rem !important;
  font-weight: 700 !important;
}
.voice-state-text {
  font-size: 0.7rem !important;
  font-weight: 600 !important;
  color: #93C5FD !important;
}

.call-parties-strip {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  padding: 8px 14px !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08) !important;
  background: #0F172A !important;
}
.party-name {
  color: #F8FAFC !important;
  font-weight: 700 !important;
  font-size: 0.78rem !important;
}
.party-role {
  color: #94A3B8 !important;
  font-size: 0.68rem !important;
}

.call-dialogue-stream {
  padding: 10px 14px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
  background: #090E17 !important;
  min-height: auto !important;
}

/* 5. Remo & Contact Speech Bubbles Visibility */
.realistic-call-card .entry-agent,
.dialogue-entry.entry-agent {
  align-self: flex-start !important;
  background: #192742 !important;
  border: 1px solid rgba(96, 165, 250, 0.38) !important;
  color: #FFFFFF !important;
  padding: 7px 11px !important;
  border-radius: 12px !important;
  max-width: 90% !important;
}
.realistic-call-card .entry-agent .dialogue-speaker,
.dialogue-entry.entry-agent .dialogue-speaker {
  color: #93C5FD !important;
  font-weight: 700 !important;
  font-size: 0.7rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  margin-bottom: 2px !important;
  display: block !important;
}
.realistic-call-card .entry-agent .dialogue-quote,
.dialogue-entry.entry-agent .dialogue-quote {
  color: #F1F5F9 !important;
  font-size: 0.8rem !important;
  line-height: 1.42 !important;
}

.realistic-call-card .entry-contact,
.dialogue-entry.entry-contact {
  align-self: flex-end !important;
  background: #FFFFFF !important;
  border: 1px solid #E2E8F0 !important;
  color: #0F172A !important;
  padding: 7px 11px !important;
  border-radius: 12px !important;
  max-width: 90% !important;
}
.realistic-call-card .entry-contact .dialogue-speaker,
.dialogue-entry.entry-contact .dialogue-speaker {
  color: #0F172A !important;
  font-weight: 700 !important;
  font-size: 0.7rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
  margin-bottom: 2px !important;
  display: block !important;
}
.realistic-call-card .entry-contact .dialogue-quote,
.dialogue-entry.entry-contact .dialogue-quote {
  color: #1E293B !important;
  font-size: 0.8rem !important;
  line-height: 1.42 !important;
}

/* 6. Extracted Information Card */
.extraction-card {
  padding: 8px 14px !important;
  background: #0B111E !important;
  border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
}
.ext-badge {
  color: #38BDF8 !important;
  font-weight: 700 !important;
  font-size: 0.72rem !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 5px !important;
}
.ext-target {
  color: #94A3B8 !important;
  font-size: 0.65rem !important;
}
.extraction-items-row {
  display: flex !important;
  gap: 6px !important;
  margin: 6px 0 !important;
}
.ext-item {
  flex: 1 !important;
  background: #162032 !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  border-radius: 8px !important;
  padding: 4px 6px !important;
}
.ext-label {
  color: #94A3B8 !important;
  font-size: 0.58rem !important;
  display: block !important;
}
.ext-value {
  color: #F8FAFC !important;
  font-size: 0.72rem !important;
  font-weight: 700 !important;
}
.ext-human-note {
  color: #94A3B8 !important;
  font-size: 0.65rem !important;
}

/* 7. Bar Graphs, Charts & Table Contrast Inside Story Cards */
.story-card .dash-bar-fill {
  background: linear-gradient(180deg, #60A5FA 0%, #2563EB 100%) !important;
  box-shadow: 0 0 10px rgba(96, 165, 250, 0.5) !important;
}
.story-card .dash-bar-track {
  background: rgba(255, 255, 255, 0.12) !important;
}
.story-card .dash-bar-day {
  color: #CBD5E1 !important;
  font-weight: 600 !important;
  font-size: 0.64rem !important;
}
.story-card .dash-chart-title {
  color: #FFFFFF !important;
  font-weight: 700 !important;
}
.story-card .dash-chart-sub {
  color: #94A3B8 !important;
}
.story-card .dash-stat-number {
  color: #FFFFFF !important;
}
.story-card .dash-stat-label {
  color: #94A3B8 !important;
}

/* Recent Inbound Calls & Candidate Pipeline Tables */
.story-card .dash-act-title {
  color: #FFFFFF !important;
  font-weight: 700 !important;
  font-size: 0.74rem !important;
}
.story-card .dash-act-meta {
  color: #94A3B8 !important;
  font-size: 0.64rem !important;
}
.story-card .dash-act-th,
.story-card .dash-act-th span,
.story-card .dash-act-th .col-cand,
.story-card .dash-act-th .col-status {
  color: #94A3B8 !important;
  font-size: 0.62rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.05em !important;
}
.story-card .dash-act-tr {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
}
.story-card .dash-act-tr .cand-name,
.story-card .dash-act-tr .col-cand,
.story-card .cand-name {
  color: #F8FAFC !important;
  font-weight: 600 !important;
  font-size: 0.74rem !important;
}

/* 8. Bottom-Left Highlight Box (Empathetic Experience) */
.story-card .human-touch-highlight {
  background: rgba(255, 255, 255, 0.06) !important;
  border: 1px solid rgba(255, 255, 255, 0.14) !important;
  padding: 10px 14px !important;
  border-radius: 12px !important;
  margin-top: 14px !important;
  margin-bottom: 16px !important;
}
.story-card .human-touch-highlight .ht-icon-wrap {
  background: rgba(255, 68, 51, 0.18) !important;
  color: #FF4433 !important;
  border-radius: 8px !important;
  width: 32px !important;
  height: 32px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  flex-shrink: 0 !important;
}
.story-card .human-touch-highlight .ht-text {
  color: #E2E8F0 !important;
  font-size: 0.8rem !important;
  line-height: 1.4 !important;
}
.story-card .human-touch-highlight .ht-text strong {
  color: #FFFFFF !important;
  font-weight: 700 !important;
  display: block !important;
  margin-bottom: 2px !important;
}
.story-card .human-touch-highlight .ht-text span {
  color: #CBD5E1 !important;
  display: block !important;
}
"""

with open('styles.css', 'a', encoding='utf-8') as f:
    f.write(overrides)
print("Appended authoritative UI styling to styles.css.")
print("All fixes applied successfully!")
