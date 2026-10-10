import re

with open('styles.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Replace color variables for the new theme
css = re.sub(r'--brand-blue: #[0-9A-Fa-f]+;', '--brand-blue: #031740;', css)
css = re.sub(r'--brand-blue-hover: #[0-9A-Fa-f]+;', '--brand-blue-hover: #031740;', css)
css = re.sub(r'--primary-blue: #[0-9A-Fa-f]+;', '--primary-blue: #FC2415;', css)
css = re.sub(r'--primary-blue-hover: #[0-9A-Fa-f]+;', '--primary-blue-hover: #FC2415;', css)
css = re.sub(r'--deep-blue: #[0-9A-Fa-f]+;', '--deep-blue: #031740;', css)
css = re.sub(r'--navy-dark: #[0-9A-Fa-f]+;', '--navy-dark: #031740;', css)
css = re.sub(r'--cyan-accent: #[0-9A-Fa-f]+;', '--cyan-accent: #FC2415;', css)

stack_css = '''
/* SCROLL STACK DECK ANIMATION */
.scroll-stack-section {
  padding: 100px 20px;
  background: var(--bg-primary);
}
.scroll-stack-header {
  text-align: center;
  margin-bottom: 60px;
}
.scroll-stack-header h2 {
  font-size: 3rem;
  color: var(--deep-blue);
  font-family: var(--font-display);
}
.scroll-stack-deck {
  position: relative;
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
  padding-bottom: 100px;
}
.scroll-stack-card {
  position: sticky;
  top: 15vh;
  width: 100%;
  height: 65vh;
  background: var(--bg-card);
  border-radius: 32px;
  box-shadow: 0 20px 40px rgba(3, 23, 64, 0.08);
  border: 1px solid var(--border-light);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  margin-bottom: 60px;
}
@media (max-width: 768px) {
  .scroll-stack-card { height: 75vh; }
}
.stack-card-header {
  padding: 30px 40px;
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  gap: 20px;
}
.stack-card-number {
  font-family: var(--font-mono);
  color: var(--primary-blue);
  font-weight: 600;
  font-size: 1.2rem;
}
.stack-card-title {
  font-size: 1.8rem;
  color: var(--deep-blue);
  font-weight: 700;
}
.stack-card-content {
  padding: 40px;
  flex: 1;
  background: var(--bg-secondary);
  display: flex;
  justify-content: center;
  align-items: center;
}
.ai-mock-ui {
  width: 100%;
  max-width: 500px;
  background: white;
  border-radius: 24px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.05);
}
.ai-mock-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  font-weight: 600;
  color: var(--deep-blue);
}
.ai-mock-dot {
  width: 12px;
  height: 12px;
  background: var(--primary-blue);
  border-radius: 50%;
  animation: pulse 2s infinite;
}
.ai-mock-row {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}
.ai-mock-row:last-child { border: none; }
'''

if 'SCROLL STACK DECK' not in css:
    css += stack_css

with open('styles.css', 'w', encoding='utf-8') as f:
    f.write(css)
    
print("Updated styles.css successfully.")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

stack_html = '''
    <!-- ==========================================
         SCROLL STACK DECK SECTION
         ========================================== -->
    <section class="scroll-stack-section" id="services">
      <div class="scroll-stack-header">
        <div class="hero-eyebrow"><span class="live-dot-pulse" style="background:#FC2415;"></span><span>AI EMPLOYEES</span></div>
        <h2>Our AI Voice Agents</h2>
      </div>
      <div class="scroll-stack-deck">
        <!-- Card 1 -->
        <div class="scroll-stack-card">
          <div class="stack-card-header">
            <span class="stack-card-number">01</span>
            <h3 class="stack-card-title">AI Recruitment Agent</h3>
          </div>
          <div class="stack-card-content">
            <div class="ai-mock-ui">
              <div class="ai-mock-header">
                <div class="ai-mock-dot"></div> Active Conversation
              </div>
              <div class="ai-mock-row"><span>Candidate:</span> <strong>Alex Johnson</strong></div>
              <div class="ai-mock-row"><span>Status:</span> <strong style="color: #16A34A;">✓ Qualified</strong></div>
              <div class="ai-mock-row"><span>Experience:</span> <strong>5 Years</strong></div>
              <div class="ai-mock-row"><span>Availability:</span> <strong>Immediate</strong></div>
            </div>
          </div>
        </div>
        <!-- Card 2 -->
        <div class="scroll-stack-card">
          <div class="stack-card-header">
            <span class="stack-card-number">02</span>
            <h3 class="stack-card-title">AI Sales Agent</h3>
          </div>
          <div class="stack-card-content">
            <div class="ai-mock-ui">
              <div class="ai-mock-header">
                <div class="ai-mock-dot"></div> Live Outbound Call
              </div>
              <div class="ai-mock-row"><span>Lead:</span> <strong>Sarah Connor</strong></div>
              <div class="ai-mock-row"><span>Interest Level:</span> <strong style="color: #FC2415;">High</strong></div>
              <div class="ai-mock-row"><span>Next Step:</span> <strong>Booked Demo</strong></div>
            </div>
          </div>
        </div>
        <!-- Card 3 -->
        <div class="scroll-stack-card">
          <div class="stack-card-header">
            <span class="stack-card-number">03</span>
            <h3 class="stack-card-title">Customer Support</h3>
          </div>
          <div class="stack-card-content">
            <div class="ai-mock-ui">
              <div class="ai-mock-header">
                <div class="ai-mock-dot"></div> Resolving Issue
              </div>
              <div class="ai-mock-row"><span>Issue:</span> <strong>Billing Inquiry</strong></div>
              <div class="ai-mock-row"><span>Resolution:</span> <strong style="color: #16A34A;">Resolved</strong></div>
              <div class="ai-mock-row"><span>Satisfaction:</span> <strong>5/5</strong></div>
            </div>
          </div>
        </div>
      </div>
    </section>
'''

# Check if we already inserted it
if 'SCROLL STACK DECK SECTION' not in html:
    # Insert right after hero section
    html = html.replace('</section>\\n\\n    <!-- ==========================================\\n         SECTION 2', '</section>\\n' + stack_html + '\\n    <!-- ==========================================\\n         SECTION 2')
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated index.html successfully.")
else:
    print("Stack deck already exists in index.html.")

