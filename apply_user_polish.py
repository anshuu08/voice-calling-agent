import re

print("Applying User UI Polish...")

# ========================================================
# 1. UPDATE script.js:
# Fix card deck scrolling: NO MERGING, NO AWKWARD VISIBLE PREVIOUS CARDS
# Only ONE card visible at a time with clean, smooth crossfade
# ========================================================
with open('script.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Replace renderDeckFrame function with clean, non-merging discrete transitions
deck_pattern = r'const renderDeckFrame = \(progress\) => \{[\s\S]*?cardData\.forEach\(\(scene, i\) => \{[\s\S]*?\}\);[\s\S]*?if \(progress >= 0\.28\)'

new_deck_frame = """const renderDeckFrame = (progress) => {
      if (window.innerWidth <= 900) {
        cardData.forEach(scene => {
          scene.card.style.transform = '';
          scene.card.style.opacity = '';
          scene.card.style.filter = '';
          scene.card.style.pointerEvents = '';
          scene.card.style.zIndex = '';
          scene.card.style.visibility = '';
          scene.card.classList.remove('card-in-front', 'card-in-back');
        });
        dashData.forEach((_, i) => triggerDashboardAnimation(i));
        return;
      }

      const rect = scrollTrack.getBoundingClientRect();
      const viewportHeight = window.innerHeight;
      if (rect.top <= viewportHeight * 0.85 && rect.bottom >= 0) {
        triggerDashboardAnimation(0);
      }

      // Discrete Card Activation (Zero merging, zero awkward overlapping)
      let activeIndex = 0;
      if (progress < 0.35) {
        activeIndex = 0;
      } else if (progress < 0.70) {
        activeIndex = 1;
      } else {
        activeIndex = 2;
      }

      // Smooth, clean single-card visibility
      cardData.forEach((scene, i) => {
        if (i === activeIndex) {
          scene.card.style.transform = 'translate3d(0, 0, 0) scale(1)';
          scene.card.style.opacity = '1';
          scene.card.style.filter = 'none';
          scene.card.style.zIndex = '10';
          scene.card.style.pointerEvents = 'auto';
          scene.card.style.visibility = 'visible';
          scene.card.classList.add('card-in-front');
          scene.card.classList.remove('card-in-back');
        } else {
          scene.card.style.transform = 'translate3d(0, 0, 0) scale(0.98)';
          scene.card.style.opacity = '0';
          scene.card.style.filter = 'none';
          scene.card.style.zIndex = '1';
          scene.card.style.pointerEvents = 'none';
          scene.card.style.visibility = 'hidden';
          scene.card.classList.remove('card-in-front');
          scene.card.classList.add('card-in-back');
        }
      });

      // Chart activations
      if (progress >= 0.28)"""

if "const renderDeckFrame = (progress) => {" in js:
    # Use regex substitution
    js = re.sub(deck_pattern, new_deck_frame, js, count=1)
    print("Updated script.js with clean single-card display (no overlapping/merging).")
else:
    print("Notice: renderDeckFrame not matched exactly, checking script.")

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(js)


# ========================================================
# 2. UPDATE styles.css:
# 1. Reduce gap between nav and hero section
# 2. Reduce size of mic icon in phone
# 3. Remove banner box styling in the 60-second test section
# 4. Clean card deck styling (no merging, cards fit in box)
# ========================================================
with open('styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

polish_overrides = """
/* ==========================================================================
   USER REQUESTED POLISH: SPACING, MIC ICON, BANNERS, AND DECK CLEANUP
   ========================================================================== */

/* 1. Reduce gap between nav and hero section */
.top-nav {
  padding-top: 10px !important;
  padding-bottom: 10px !important;
}

.hero-section {
  padding-top: 16px !important;
  padding-bottom: 24px !important;
}

.hero-grid {
  margin-top: 0 !important;
  padding-top: 4px !important;
}

/* 2. Reduce size of mic icon in phone */
.Remo-voice-orb,
.remo-voice-orb,
.brand-group-left .Remo-voice-orb {
  width: 32px !important;
  height: 32px !important;
  min-width: 32px !important;
  min-height: 32px !important;
  margin: 0 10px 0 0 !important;
  border-radius: 50% !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3) !important;
}

.Remo-voice-orb svg,
.remo-voice-orb svg,
.brand-group-left .Remo-voice-orb svg {
  width: 15px !important;
  height: 15px !important;
}

.command-header-card {
  padding: 10px 14px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
}

.brand-group-left {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
}

#live-mute-btn svg {
  width: 16px !important;
  height: 16px !important;
}

/* 3. The 60-Second Test: Remove banner styling (no giant full-width empty boxes) */
.instant-test-section .test-copy-col {
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-start !important;
}

.instant-test-section .section-eyebrow {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  width: auto !important;
  max-width: fit-content !important;
  align-self: flex-start !important;
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  margin-bottom: 12px !important;
  color: #FF4433 !important;
  font-size: 0.78rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}

.instant-test-section .section-eyebrow svg {
  color: #FF4433 !important;
}

.instant-test-section .callout-capability-pill {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  width: auto !important;
  max-width: 100% !important;
  align-self: flex-start !important;
  background: transparent !important;
  border: none !important;
  padding: 0 !important;
  margin: 12px 0 22px 0 !important;
  color: #475569 !important;
  font-size: 0.88rem !important;
}

.instant-test-section .callout-capability-pill .pill-pen-icon {
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  color: var(--brand-blue, #0A192F) !important;
}

/* 4. While scrolling cards: cards cleanly stay in container and NEVER merge */
.cards-stack-stage {
  position: relative !important;
  overflow: hidden !important;
  height: 640px !important;
  min-height: 640px !important;
  border-radius: var(--radius-card) !important;
}

.story-card {
  transition: opacity 0.35s ease, transform 0.35s ease !important;
  will-change: opacity, transform !important;
}

.story-card.card-in-back {
  opacity: 0 !important;
  pointer-events: none !important;
  visibility: hidden !important;
  transform: scale(0.98) !important;
}

.story-card.card-in-front {
  opacity: 1 !important;
  pointer-events: auto !important;
  visibility: visible !important;
  transform: translate3d(0, 0, 0) scale(1) !important;
}
"""

with open('styles.css', 'a', encoding='utf-8') as f:
    f.write(polish_overrides)
print("Appended polish overrides to styles.css.")
print("Done!")
