/**
 * TakeRemo — ENTERPRISE AI EMPLOYEE PLATFORM
 * Core Interactivity, Preserved Hero 3D Parallax & Telemetry,
 * Live 60-Second Interactive Calling Demo, Sticky Scroll-Driven Storytelling Stack,
 * Industry Switcher, & Modal Handlers
 */

document.addEventListener('DOMContentLoaded', () => {

  // ------------------------------------------------------------------------
  // A. PRESERVED HERO: DYNAMIC PHONE CLOCK & TELEMETRY TIMER
  // ------------------------------------------------------------------------
  const phoneClock = document.getElementById('phone-clock');
  const updatePhoneClock = () => {
    if (!phoneClock) return;
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    phoneClock.textContent = `${hours}:${minutes}`;
  };
  updatePhoneClock();
  setInterval(updatePhoneClock, 60000);

  // Hero Floating Mini Telemetry Timer
  const heroTelemetryTimer = document.getElementById('hero-telemetry-timer');
  let miniSeconds = 268; // 04:28
  if (heroTelemetryTimer) {
    setInterval(() => {
      miniSeconds++;
      const m = String(Math.floor(miniSeconds / 60)).padStart(2, '0');
      const s = String(miniSeconds % 60).padStart(2, '0');
      heroTelemetryTimer.textContent = `${m}:${s}`;
    }, 1000);
  }

  // ------------------------------------------------------------------------
  // B. PRESERVED HERO: LEVEL MOUSE HOVER PARALLAX
  // ------------------------------------------------------------------------
  const heroStage = document.getElementById('hero-phone-stage');
  const phone3d = document.getElementById('phone-3d');

  if (heroStage && phone3d && window.innerWidth > 992) {
    heroStage.addEventListener('mousemove', (e) => {
      const rect = heroStage.getBoundingClientRect();
      const y = e.clientY - rect.top - rect.height / 2;
      const hoverOffset = -(y / (rect.height / 2)) * 8;
      phone3d.style.transform = `translateY(${hoverOffset.toFixed(1)}px)`;
    });

    heroStage.addEventListener('mouseleave', () => {
      phone3d.style.transform = 'translateY(0)';
    });
  }

  // ------------------------------------------------------------------------
  // C. PRESERVED HERO: LIVE AI VOICE CALLING ANIMATION CYCLE
  // ------------------------------------------------------------------------
  const liveCallTimer = document.getElementById('live-call-timer');
  const speakerBadge = document.getElementById('voice-speaker-badge');
  const speakerLabel = document.getElementById('speaker-state-label');
  const trLine2 = document.getElementById('tr-line-2');
  const trText1 = document.getElementById('tr-text-1');
  const trText2 = document.getElementById('tr-text-2');

  const valExp = document.getElementById('val-exp');
  const valSkills = document.getElementById('val-skills');
  const valLoc = document.getElementById('val-loc');
  const valNotice = document.getElementById('val-notice');
  const valCtc = document.getElementById('val-ctc');

  const matchPercent = document.getElementById('match-percent');
  const darkQualCard = document.getElementById('dark-qual-card');

  const chipExp = document.getElementById('chip-exp');
  const chipSkills = document.getElementById('chip-skills');
  const chipLoc = document.getElementById('chip-loc');
  const chipAvail = document.getElementById('chip-avail');

  let callSeconds = 134; // 02:14

  if (liveCallTimer) {
    setInterval(() => {
      callSeconds++;
      const mins = String(Math.floor(callSeconds / 60)).padStart(2, '0');
      const secs = String(callSeconds % 60).padStart(2, '0');
      liveCallTimer.textContent = `${mins}:${secs}`;
    }, 1000);
  }

  // Design 5 Hero Command Center: Live Call Timer (02:38+)
  const callTimerDisplay = document.getElementById('call-timer-display');
  let design5Secs = 158; // 02:38
  if (callTimerDisplay) {
    setInterval(() => {
      design5Secs++;
      const m = String(Math.floor(design5Secs / 60)).padStart(2, '0');
      const s = String(design5Secs % 60).padStart(2, '0');
      callTimerDisplay.textContent = `${m}:${s}`;
    }, 1000);
  }

  // Design 5 Hero Phone Controls
  const liveMuteBtn = document.getElementById('live-mute-btn');
  if (liveMuteBtn) {
    liveMuteBtn.addEventListener('click', () => {
      liveMuteBtn.classList.toggle('active');
    });
  }

  const runLiveCallCycle = () => {
    // Stage 1: Reset to Remo Speaking
    if (speakerLabel) speakerLabel.textContent = '● AI SPEAKING';
    if (speakerBadge) {
      speakerBadge.style.background = 'rgba(37, 99, 235, 0.2)';
      speakerBadge.style.borderColor = 'rgba(96, 165, 250, 0.4)';
    }

    if (trText1) trText1.textContent = '"Hi Rahul, I\'m Remo from the recruitment team. Is this a good time to speak for a few minutes?"';
    if (trText2) trText2.textContent = '"Yes, sure."';

    // Stage 2: Candidate answers & Remo listens
    setTimeout(() => {
      if (speakerLabel) speakerLabel.textContent = '● LISTENING';
      if (speakerBadge) {
        speakerBadge.style.background = 'rgba(56, 189, 248, 0.25)';
        speakerBadge.style.borderColor = 'rgba(147, 197, 253, 0.5)';
      }

      if (trText1) trText1.textContent = '"Great. Could you tell me how many years of relevant development experience you have?"';
      if (trText2) trText2.textContent = '"I have around 3 years in React and Node.js."';
    }, 4200);

    // Stage 3: Extraction
    setTimeout(() => {
      setTimeout(() => {
        if (valExp) { valExp.className = 'ext-val ext-verified'; valExp.textContent = '3 Years ✓'; }
        if (chipExp) chipExp.classList.add('chip-active');
      }, 500);

      setTimeout(() => {
        if (valSkills) { valSkills.className = 'ext-val ext-verified'; valSkills.textContent = 'React • Node.js ✓'; }
        if (chipSkills) chipSkills.classList.add('chip-active');
      }, 1200);

      setTimeout(() => {
        if (valLoc) { valLoc.className = 'ext-val ext-verified'; valLoc.textContent = 'Hyderabad ✓'; }
        if (chipLoc) chipLoc.classList.add('chip-active');
      }, 1900);

      setTimeout(() => {
        if (valNotice) { valNotice.className = 'ext-val ext-verified'; valNotice.textContent = '30 Days ✓'; }
      }, 2600);

      setTimeout(() => {
        if (valCtc) { valCtc.className = 'ext-val ext-verified'; valCtc.textContent = '₹8.5 LPA ✓'; }
        if (chipAvail) chipAvail.classList.add('chip-active');
      }, 3300);
    }, 7800);

    // Stage 4: Qualification
    setTimeout(() => {
      if (matchPercent) {
        let p = 72;
        const rollScore = setInterval(() => {
          p += 4;
          if (p >= 92) {
            p = 92;
            clearInterval(rollScore);
          }
          matchPercent.textContent = `${p}%`;
        }, 60);
      }

      if (darkQualCard) darkQualCard.classList.add('qual-active');
    }, 12500);

    // Stage 5: Loop cycle
    setTimeout(runLiveCallCycle, 17500);
  };

  runLiveCallCycle();

  // ------------------------------------------------------------------------
  // D. PRESERVED HERO PARTICLES (DASHBOARD BLUE)
  // ------------------------------------------------------------------------
  const particlesContainer = document.getElementById('particles-container');
  if (particlesContainer) {
    const particleCount = 14;
    for (let i = 0; i < particleCount; i++) {
      const p = document.createElement('div');
      p.className = 'hero-particle';
      const size = Math.random() * 3 + 2;
      const top = Math.random() * 100;
      const left = Math.random() * 100;
      const delay = Math.random() * 4;
      const duration = Math.random() * 5 + 4;
      const isCyan = Math.random() > 0.5;

      p.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        background: ${isCyan ? '#38BDF8' : '#FC2415'};
        opacity: ${Math.random() * 0.35 + 0.18};
        border-radius: 50%;
        top: ${top}%;
        left: ${left}%;
        pointer-events: none;
        box-shadow: 0 0 10px ${isCyan ? '#38BDF8' : '#FC2415'};
        animation: floatParticle ${duration}s ease-in-out infinite ${delay}s alternate;
      `;
      particlesContainer.appendChild(p);
    }

    const styleEl = document.createElement('style');
    styleEl.textContent = `
      @keyframes floatParticle {
        0% { transform: translateY(0px) scale(0.8); }
        100% { transform: translateY(-16px) scale(1.2); }
      }
    `;
    document.head.appendChild(styleEl);
  }

  // ------------------------------------------------------------------------
  // E. ✨ THE 60-SECOND TEST: INTERACTIVE PHONE CALL (DASHBOARD BLUE)
  // ------------------------------------------------------------------------
  const instantCallForm = document.getElementById('instant-call-form');
  const instantMobileInput = document.getElementById('instant-mobile-input');
  const instantTriggerBtn = document.getElementById('btn-instant-trigger');
  const instantCallStatusPill = document.getElementById('instant-call-status-pill');
  const incomingAcceptBtn = document.getElementById('incoming-demo-accept-btn');
  const declineCallBtn = document.querySelector('.btn-decline-call');
  const btnCancelDialing = document.getElementById('btn-cancel-dialing');

  const incomingDialingScreen = document.getElementById('incoming-dialing-screen');
  const incomingScreen = document.getElementById('incoming-ringing-screen');
  const inCallScreen = document.getElementById('in-call-screen');
  const callFinishedScreen = document.getElementById('call-finished-screen');

  const inCallTimer = document.getElementById('in-call-timer');
  const inCallDialogueText = document.getElementById('in-call-dialogue-text');
  const inCallExtText = document.getElementById('in-call-ext-text');
  const btnEndCall = document.getElementById('btn-end-demo-call');
  const btnRestartCall = document.getElementById('btn-restart-demo-call');
  const callerNumberEl = document.getElementById('incoming-caller-num-display');
  const dialingNumberEl = document.getElementById('dialing-number-display');

  let activeCallTimerInterval = null;
  let dialingTimeout = null;
  let inCallSeconds = 0;

  const showDialingAnimation = (customNumber) => {
    if (incomingScreen) incomingScreen.classList.add('hidden');
    if (inCallScreen) inCallScreen.classList.remove('active');
    if (callFinishedScreen) callFinishedScreen.classList.remove('active');
    if (incomingDialingScreen) incomingDialingScreen.classList.remove('hidden');

    const maskedCallerId = '+91 80 4719 XXXX';
    if (dialingNumberEl) dialingNumberEl.textContent = maskedCallerId;
    if (callerNumberEl) callerNumberEl.textContent = maskedCallerId;

    if (instantCallStatusPill) {
      instantCallStatusPill.innerHTML = `
        <span class="live-dot-pulse pulse-blue"></span>
        <span>Dialing... Connecting via carrier interconnect to your device</span>
      `;
      instantCallStatusPill.style.background = '#EFF6FF';
      instantCallStatusPill.style.borderColor = '#BFDBFE';
      instantCallStatusPill.style.color = '#031740';
    }

    if (dialingTimeout) clearTimeout(dialingTimeout);
    dialingTimeout = setTimeout(() => {
      transitionDialingToRinging();
    }, 1800);
  };

  const transitionDialingToRinging = () => {
    if (incomingDialingScreen) incomingDialingScreen.classList.add('hidden');
    if (incomingScreen) incomingScreen.classList.remove('hidden');

    if (instantCallStatusPill) {
      instantCallStatusPill.innerHTML = `
        <span class="live-dot-pulse pulse-blue"></span>
        <span>Ringing your phone... Tap "Accept" or pick up!</span>
      `;
    }

    const phoneCard = document.querySelector('.incoming-smartphone-card');
    if (phoneCard) {
      phoneCard.style.animation = 'shakePhone 0.6s ease infinite';
    }
  };

  const cancelDialing = () => {
    if (dialingTimeout) clearTimeout(dialingTimeout);
    if (incomingDialingScreen) incomingDialingScreen.classList.add('hidden');
    if (incomingScreen) incomingScreen.classList.remove('hidden');

    const phoneCard = document.querySelector('.incoming-smartphone-card');
    if (phoneCard) phoneCard.style.animation = 'none';

    if (instantCallStatusPill) {
      instantCallStatusPill.innerHTML = `
        <span class="pulse-dot-blue" style="width:6px;height:6px;"></span>
        <span>Dialing cancelled. Enter a number or tap Accept to test again.</span>
      `;
      instantCallStatusPill.style.background = '#F8FAFC';
      instantCallStatusPill.style.borderColor = '#E2E8F0';
      instantCallStatusPill.style.color = '#475569';
    }
  };

  const startActiveCallExperience = (customNumber) => {
    if (dialingTimeout) clearTimeout(dialingTimeout);
    if (incomingDialingScreen) incomingDialingScreen.classList.add('hidden');
    if (incomingScreen) incomingScreen.classList.add('hidden');
    if (callFinishedScreen) callFinishedScreen.classList.remove('active');
    if (inCallScreen) inCallScreen.classList.add('active');

    const phoneCard = document.querySelector('.incoming-smartphone-card');
    if (phoneCard) phoneCard.style.animation = 'none';

    if (instantCallStatusPill) {
      instantCallStatusPill.innerHTML = `
        <span class="pulse-dot-blue" style="width:6px;height:6px;"></span>
        <span>Call Connected: Remo is speaking with you live</span>
      `;
      instantCallStatusPill.style.background = '#EFF6FF';
      instantCallStatusPill.style.borderColor = '#BFDBFE';
      instantCallStatusPill.style.color = '#031740';
    }

    inCallSeconds = 0;
    if (inCallTimer) inCallTimer.textContent = '00:00';
    if (activeCallTimerInterval) clearInterval(activeCallTimerInterval);
    activeCallTimerInterval = setInterval(() => {
      inCallSeconds++;
      const m = String(Math.floor(inCallSeconds / 60)).padStart(2, '0');
      const s = String(inCallSeconds % 60).padStart(2, '0');
      if (inCallTimer) inCallTimer.textContent = `${m}:${s}`;
    }, 1000);

    if (inCallDialogueText) {
      inCallDialogueText.textContent = '"Hello! I\'m Remo, your AI employee. I can screen candidates, call sales leads, or resolve customer tickets. Which workflow would you like to test right now?"';
    }
    if (inCallExtText) {
      inCallExtText.innerHTML = '<span class="pulse-dot-green" style="display:inline-block;vertical-align:middle;margin-right:5px;"></span> Live NER: Call answered in 0.3s · HD Voice interconnected';
    }
  };

  const endActiveCallExperience = () => {
    if (dialingTimeout) clearTimeout(dialingTimeout);
    if (activeCallTimerInterval) clearInterval(activeCallTimerInterval);
    if (inCallScreen) inCallScreen.classList.remove('active');
    if (incomingDialingScreen) incomingDialingScreen.classList.add('hidden');
    if (incomingScreen) incomingScreen.classList.add('hidden');
    if (callFinishedScreen) callFinishedScreen.classList.add('active');

    const durationStr = inCallTimer ? inCallTimer.textContent : '00:38';
    const finishedDuration = document.getElementById('finished-call-duration');
    if (finishedDuration) finishedDuration.textContent = durationStr;

    if (instantCallStatusPill) {
      instantCallStatusPill.innerHTML = `
        <span class="check-emerald" style="color:#FC2415;font-weight:800;">✓</span>
        <span>Call Completed · Notes saved & workflows triggered</span>
      `;
      instantCallStatusPill.style.background = '#FFFFFF';
      instantCallStatusPill.style.borderColor = '#E2E8F0';
      instantCallStatusPill.style.color = '#0F172A';
    }
  };

  const resetCallToIncoming = () => {
    if (dialingTimeout) clearTimeout(dialingTimeout);
    if (activeCallTimerInterval) clearInterval(activeCallTimerInterval);
    if (callFinishedScreen) callFinishedScreen.classList.remove('active');
    if (inCallScreen) inCallScreen.classList.remove('active');
    if (incomingDialingScreen) incomingDialingScreen.classList.add('hidden');
    if (incomingScreen) incomingScreen.classList.remove('hidden');

    if (callerNumberEl) callerNumberEl.textContent = '+91 80 4719 XXXX';
    if (dialingNumberEl) dialingNumberEl.textContent = '+91 80 4719 XXXX';

    if (instantCallStatusPill) {
      instantCallStatusPill.innerHTML = `
        <span class="pulse-dot-blue" style="width:6px;height:6px;"></span>
        <span>Ready to dial — instant call simulation</span>
      `;
      instantCallStatusPill.style.background = '#F8FAFC';
      instantCallStatusPill.style.borderColor = '#E2E8F0';
      instantCallStatusPill.style.color = '#475569';
    }
  };

  if (instantCallForm && instantMobileInput) {
    instantCallForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const phoneNum = instantMobileInput.value.trim();
      if (!phoneNum) return;

      const origBtnContent = instantTriggerBtn.innerHTML;
      instantTriggerBtn.innerHTML = `
        <span class="c-spinner" style="width:14px;height:14px;border:2px solid #ffffff;border-top-color:transparent;border-radius:50%;display:inline-block;margin-right:6px;animation:spin 0.6s linear infinite;"></span>
        <span>Calling +91 ${phoneNum}...</span>
      `;
      instantTriggerBtn.disabled = true;

      // Start outbound dialing animation flow
      showDialingAnimation(phoneNum);

      setTimeout(() => {
        instantTriggerBtn.innerHTML = origBtnContent;
        instantTriggerBtn.disabled = false;
      }, 1800);
    });
  }

  if (btnCancelDialing) {
    btnCancelDialing.addEventListener('click', cancelDialing);
  }

  if (incomingAcceptBtn) {
    incomingAcceptBtn.addEventListener('click', () => {
      playHumanChime('connect');
      startActiveCallExperience('Direct Accept');
    });
  }

  if (declineCallBtn) {
    declineCallBtn.addEventListener('click', () => {
      if (dialingTimeout) clearTimeout(dialingTimeout);
      const phoneCard = document.querySelector('.incoming-smartphone-card');
      if (phoneCard) phoneCard.style.animation = 'none';
      if (instantCallStatusPill) {
        instantCallStatusPill.innerHTML = `<span>Call Declined. Submit a number above to try again.</span>`;
      }
    });
  }

  if (btnEndCall) btnEndCall.addEventListener('click', endActiveCallExperience);
  if (btnRestartCall) btnRestartCall.addEventListener('click', resetCallToIncoming);

  // Interactive Quick Query Chips for Visitor with sound & natural conversational typing
  const quickChips = document.querySelectorAll('.in-call-chip-btn');
  quickChips.forEach(chip => {
    chip.addEventListener('click', () => {
      const topic = chip.getAttribute('data-topic');
      if (!inCallDialogueText) return;
      playHumanChime('click');
      quickChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');

      if (topic === 'recruitment') {
        inCallDialogueText.innerHTML = '<strong>Candidate Screening:</strong> "When a candidate applies, I call them within 30 seconds, introduce our company warmly, ask your exact screening questions, verify their notice period, and shortlist them straight into your ATS."';
        if (inCallExtText) {
          inCallExtText.innerHTML = '<span class="pulse-dot-green" style="display:inline-block;vertical-align:middle;margin-right:5px;"></span> Extracted: 4 Yrs Exp · 30 Days Notice · Candidate Receptive · Shortlisted';
        }
      } else if (topic === 'sales') {
        inCallDialogueText.innerHTML = '<strong>Sales Qualification:</strong> "I call inbound leads the second they submit a form, ask consultative questions about their budget and team size, and book qualified buyers straight onto your calendar."';
        if (inCallExtText) {
          inCallExtText.innerHTML = '<span class="pulse-dot-green" style="display:inline-block;vertical-align:middle;margin-right:5px;"></span> Extracted: 60 Leads/day · Urgent Need · Budget High · Demo Booked for 3 PM';
        }
      } else if (topic === 'support') {
        inCallDialogueText.innerHTML = '<strong>Customer Support:</strong> "I pick up customer calls 24/7 with zero waiting time, reassure anxious buyers, resolve delivery and order questions, and send tracking links directly to WhatsApp."';
        if (inCallExtText) {
          inCallExtText.innerHTML = '<span class="pulse-dot-green" style="display:inline-block;vertical-align:middle;margin-right:5px;"></span> Extracted: Order #8492 Located · Tracking Dispatched · Ticket Closed Successfully';
        }
      }
    });
  });

  // ------------------------------------------------------------------------
  // HUMAN TOUCH AUDIO & SYNTH ENGINE (Web Audio API + SpeechSynthesis)
  // ------------------------------------------------------------------------
  let audioCtx = null;
  let isSoundEnabled = localStorage.getItem('takeremo_sound_fx') !== 'false';

  const getAudioContext = () => {
    if (!audioCtx) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      if (AudioContextClass) {
        audioCtx = new AudioContextClass();
      }
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
    return audioCtx;
  };

  function playHumanChime(type = 'click') {
    if (!isSoundEnabled) return;
    try {
      const ctx = getAudioContext();
      if (!ctx) return;
      const now = ctx.currentTime;

      if (type === 'click') {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(600, now);
        osc.frequency.exponentialRampToValueAtTime(300, now + 0.04);
        gain.gain.setValueAtTime(0.06, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now);
        osc.stop(now + 0.04);
      } else if (type === 'connect') {
        // Warm 3-tone harmonic chime (C5, E5, G5)
        [523.25, 659.25, 783.99].forEach((freq, idx) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, now + idx * 0.07);
          gain.gain.setValueAtTime(0.08, now + idx * 0.07);
          gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.07 + 0.28);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start(now + idx * 0.07);
          osc.stop(now + idx * 0.07 + 0.3);
        });
      } else if (type === 'ring') {
        [0, 0.12].forEach((offset) => {
          const osc1 = ctx.createOscillator();
          const osc2 = ctx.createOscillator();
          const gain = ctx.createGain();
          osc1.frequency.setValueAtTime(440, now + offset);
          osc2.frequency.setValueAtTime(480, now + offset);
          gain.gain.setValueAtTime(0.05, now + offset);
          gain.gain.exponentialRampToValueAtTime(0.001, now + offset + 0.09);
          osc1.connect(gain);
          osc2.connect(gain);
          gain.connect(ctx.destination);
          osc1.start(now + offset);
          osc2.start(now + offset);
          osc1.stop(now + offset + 0.1);
          osc2.stop(now + offset + 0.1);
        });
      }
    } catch (e) {
      // Audio graceful fallback
    }
  };

  // Sound Toggle Handlers
  const btnSoundToggle = document.getElementById('btn-sound-toggle');
  const soundIconOn = document.getElementById('sound-icon-on');
  const soundIconOff = document.getElementById('sound-icon-off');

  const updateSoundUI = () => {
    if (!btnSoundToggle) return;
    if (isSoundEnabled) {
      btnSoundToggle.classList.remove('muted');
      if (soundIconOn) soundIconOn.style.display = 'block';
      if (soundIconOff) soundIconOff.style.display = 'none';
      btnSoundToggle.title = 'Sound FX: On (Click to mute)';
    } else {
      btnSoundToggle.classList.add('muted');
      if (soundIconOn) soundIconOn.style.display = 'none';
      if (soundIconOff) soundIconOff.style.display = 'block';
      btnSoundToggle.title = 'Sound FX: Off (Click to unmute)';
    }
  };
  updateSoundUI();

  if (btnSoundToggle) {
    btnSoundToggle.addEventListener('click', () => {
      isSoundEnabled = !isSoundEnabled;
      localStorage.setItem('takeremo_sound_fx', isSoundEnabled ? 'true' : 'false');
      updateSoundUI();
      if (isSoundEnabled) playHumanChime('connect');
    });
  }

  // Hero Voice Sample Preview Player
  const btnHeroVoiceSample = document.getElementById('btn-hero-voice-sample');
  const heroVoiceVisualizer = document.getElementById('hero-voice-visualizer');
  const heroVoiceBtnText = document.getElementById('hero-voice-btn-text');
  const heroVoicePlayIcon = document.getElementById('hero-voice-play-icon');
  let isVoicePlaying = false;
  let voiceSampleTimer = null;

  const stopHeroVoiceSample = () => {
    if (voiceSampleTimer) clearTimeout(voiceSampleTimer);
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    isVoicePlaying = false;
    if (heroVoiceVisualizer) heroVoiceVisualizer.classList.remove('playing');
    if (heroVoiceBtnText) heroVoiceBtnText.textContent = "Hear Remo's Real Voice";
    if (heroVoicePlayIcon) {
      heroVoicePlayIcon.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>`;
    }
  };

  if (btnHeroVoiceSample) {
    btnHeroVoiceSample.addEventListener('click', () => {
      if (isVoicePlaying) {
        stopHeroVoiceSample();
        return;
      }

      isVoicePlaying = true;
      playHumanChime('connect');
      if (heroVoiceVisualizer) heroVoiceVisualizer.classList.add('playing');
      if (heroVoiceBtnText) heroVoiceBtnText.textContent = "Playing Voice Sample...";
      if (heroVoicePlayIcon) {
        heroVoicePlayIcon.innerHTML = `<svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>`;
      }

      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const text = "Hello! I am Remo, your AI employee. I speak with natural cadence, listen without interrupting, and handle your calls with real human warmth.";
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 0.96;
        utter.pitch = 1.04;
        
        const voices = window.speechSynthesis.getVoices();
        const naturalVoice = voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Samantha') || v.name.includes('Google') || v.name.includes('Daniel') || v.name.includes('Karen')));
        if (naturalVoice) utter.voice = naturalVoice;

        utter.onend = () => stopHeroVoiceSample();
        utter.onerror = () => stopHeroVoiceSample();
        window.speechSynthesis.speak(utter);

        voiceSampleTimer = setTimeout(() => {
          stopHeroVoiceSample();
        }, 6500);
      } else {
        voiceSampleTimer = setTimeout(() => {
          stopHeroVoiceSample();
        }, 5000);
      }
    });
  }

  // ------------------------------------------------------------------------
  // F. TakeRemo — INTERACTIVE WORKFLOW CARDS & LIVE ANALYTICS DASHBOARD
  // Cards: 01 Recruitment -> 02 Sales -> 03 Customer Support
  // Direct Tab Navigation + Smooth Fade/Slide + Animated Charts & Metrics
  // ------------------------------------------------------------------------
  const scrollSection = document.getElementById('capabilities');
  const storyCards = document.querySelectorAll('.story-card');
  const indicatorItems = document.querySelectorAll('.story-indicator-item');
  const compactDashboards = document.querySelectorAll('.compact-dashboard');

  if (storyCards.length > 0) {
    let currentActiveIndex = 0;

    // Fast, responsive metric count-up
    const animateMetricNumber = (el, target, duration = 600) => {
      const startTime = performance.now();
      const tick = (now) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3); // Smooth ease-out cubic
        const val = Math.round(target * ease);
        el.textContent = val;
        if (progress < 1) {
          requestAnimationFrame(tick);
        } else {
          el.textContent = target;
        }
      };
      requestAnimationFrame(tick);
    };

    // Animate Donut progress and Center text
    const animateDonutAndCenter = (maskStroke, centerNumEl, targetVal, isFloat = false, duration = 650) => {
      const startTime = performance.now();
      const tick = (now) => {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const ease = 1 - Math.pow(1 - progress, 3);

        if (maskStroke) {
          const dashLength = (100 * ease).toFixed(1);
          maskStroke.setAttribute('stroke-dasharray', `${dashLength} 100`);
          maskStroke.style.strokeDasharray = `${dashLength} 100`;
        }

        if (centerNumEl) {
          if (isFloat) {
            const val = (targetVal * ease).toFixed(1);
            centerNumEl.textContent = val;
          } else {
            const val = Math.round(targetVal * ease);
            centerNumEl.textContent = `${val}%`;
          }
        }

        if (progress < 1) {
          requestAnimationFrame(tick);
        } else {
          if (maskStroke) {
            maskStroke.setAttribute('stroke-dasharray', '100 0');
            maskStroke.style.strokeDasharray = '100 0';
          }
          if (centerNumEl) {
            centerNumEl.textContent = isFloat ? targetVal.toFixed(1) : `${targetVal}%`;
          }
        }
      };
      requestAnimationFrame(tick);
    };

    // Trigger dashboard charts & metrics animations for a specific card index
    const animateDashboard = (idx) => {
      const dash = compactDashboards[idx];
      if (!dash) return;

      dash.classList.add('dash-active');

      // 1. Metric numbers count-up
      const numbers = dash.querySelectorAll('.dash-stat-number[data-target]');
      numbers.forEach((numEl) => {
        const target = parseInt(numEl.getAttribute('data-target'), 10);
        if (!isNaN(target)) {
          numEl.textContent = '0';
          animateMetricNumber(numEl, target, 600);
        }
      });

      // 2. Bar Chart: Animate heights upward with staggered delays
      const bars = dash.querySelectorAll('.dash-bar-fill');
      bars.forEach((bar, i) => {
        const targetH = bar.getAttribute('data-height') || '60%';
        bar.style.height = '0%';
        bar.style.transition = 'none';
        
        setTimeout(() => {
          bar.style.transition = 'height 650ms cubic-bezier(0.22, 1, 0.36, 1)';
          bar.style.height = targetH;
        }, 50 + i * 40);
      });

      // 3. Donut Chart & Center Stat
      const maskStroke = dash.querySelector('.donut-mask-stroke');
      const centerStat = dash.querySelector('.donut-center-stat');
      if (maskStroke || centerStat) {
        if (maskStroke) {
          maskStroke.setAttribute('stroke-dasharray', '0 100');
          maskStroke.style.strokeDasharray = '0 100';
        }
        const targetVal = centerStat ? parseFloat(centerStat.getAttribute('data-target')) : 0;
        const isFloat = centerStat ? centerStat.getAttribute('data-float') === 'true' : false;
        setTimeout(() => {
          animateDonutAndCenter(maskStroke, centerStat, targetVal, isFloat, 700);
        }, 80);
      }

      // 4. CSAT meter fill for Customer Support
      const csatFill = dash.querySelector('.csat-meter-fill');
      if (csatFill) {
        csatFill.style.width = '0%';
        setTimeout(() => {
          csatFill.style.width = '96%';
        }, 150);
      }
    };

    // Switch visible Story Card
    const switchStoryCard = (targetIndex, triggerSound = true) => {
      if (targetIndex < 0 || targetIndex >= storyCards.length) return;
      currentActiveIndex = targetIndex;

      if (triggerSound) {
        playHumanChime('click');
      }

      // 1. Update Indicator Tab items
      indicatorItems.forEach((item, i) => {
        if (i === targetIndex) {
          item.classList.add('active');
        } else {
          item.classList.remove('active');
        }
      });

      // 2. Update Story Cards visibility & 3D styling
      storyCards.forEach((card, i) => {
        if (i === targetIndex) {
          card.classList.add('active', 'card-in-front');
          card.classList.remove('card-in-back');
          card.style.opacity = '1';
          card.style.visibility = 'visible';
          card.style.pointerEvents = 'auto';
          card.style.zIndex = '10';
          card.style.transform = 'translateY(0) scale(1)';
        } else {
          card.classList.remove('active', 'card-in-front');
          card.classList.add('card-in-back');
          card.style.opacity = '0';
          card.style.visibility = 'hidden';
          card.style.pointerEvents = 'none';
          card.style.zIndex = '1';
          card.style.transform = 'translateY(16px) scale(0.98)';
        }
      });

      // 3. Trigger chart & number animations on the newly active card
      animateDashboard(targetIndex);
    };

    // Attach click handlers to indicators
    indicatorItems.forEach((item, i) => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        switchStoryCard(i, true);
      });
    });

    // Keyboard Arrow navigation when section is in view
    document.addEventListener('keydown', (e) => {
      if (!scrollSection) return;
      const rect = scrollSection.getBoundingClientRect();
      const inView = rect.top < window.innerHeight * 0.8 && rect.bottom > window.innerHeight * 0.2;
      if (!inView) return;

      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
        if (currentActiveIndex < storyCards.length - 1) {
          e.preventDefault();
          switchStoryCard(currentActiveIndex + 1, true);
        }
      } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
        if (currentActiveIndex > 0) {
          e.preventDefault();
          switchStoryCard(currentActiveIndex - 1, true);
        }
      }
    });

    // Nav anchor links (#recruitment, #sales, #support)
    document.querySelectorAll('a[href="#recruitment"], a[href="#sales"], a[href="#support"]').forEach(link => {
      link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        const idx = href === '#recruitment' ? 0 : (href === '#sales' ? 1 : 2);
        switchStoryCard(idx, true);
        if (scrollSection) {
          scrollSection.scrollIntoView({ behavior: 'smooth' });
        }
      });
    });

    // IntersectionObserver to auto-animate when section scrolls into viewport
    let hasInitializedInView = false;
    if (scrollSection && 'IntersectionObserver' in window) {
      const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting && !hasInitializedInView) {
            hasInitializedInView = true;
            switchStoryCard(0, false);
          }
        });
      }, { threshold: 0.2 });
      sectionObserver.observe(scrollSection);
    }

    // Initial activation
    switchStoryCard(0, false);
  }

  // ------------------------------------------------------------------------
  // G. SECTION 5: INDUSTRIES (DASHBOARD BLUE ACCENTS)
  // ------------------------------------------------------------------------
  const industryData = {
    healthcare: {
      title: 'HEALTHCARE & CLINICS',
      text: 'Hi Mrs. Gupta, this is Remo from Apollo Clinic confirming your appointment with Dr. Mehta tomorrow at 4:00 PM. Have you completed the recommended fasting for your lab panel?',
      chips: ['✓ Appointment Confirmation', '✓ Pre-Visit Guidelines', '✓ Rescheduling Support', '✓ EHR Status Synced']
    },
    recruitment: {
      title: 'RECRUITMENT & STAFFING',
      text: 'Hi Pooja, I am Remo from the talent team. I saw your application for Senior Developer. Could you share how many years of React experience you have and your current notice period?',
      chips: ['✓ Candidate Outreach', '✓ Skill Verification', '✓ Notice Period Check', '✓ ATS Auto-Sync']
    },
    sales: {
      title: 'SALES & INBOUND LEADS',
      text: 'Hello Vikram, this is Remo from TakeRemo. I noticed you just requested pricing for automated calling. Is this a good time to discuss your monthly lead volume?',
      chips: ['✓ Sub-30s Speed-to-Lead', '✓ Budget & Need Discovery', '✓ Calendar Demo Booking', '✓ CRM Contact Sync']
    },
    education: {
      title: 'EDUCATION & EDTECH',
      text: 'Hello Rohit, Remo here from Greenfield University. I am following up on your application for the Data Science Master program. Would you like to schedule an advisor consultation?',
      chips: ['✓ Admissions Inquiries', '✓ Course Eligibility Check', '✓ Counselor Walkthroughs', '✓ Fee Deadlines Reminder']
    },
    realestate: {
      title: 'REAL ESTATE & PROPERTY',
      text: 'Hi Priya, this is Remo calling from Prestige Heights regarding the 3-BHK inquiry you submitted. Are you looking to visit the property this Saturday or Sunday?',
      chips: ['✓ Buyer Qualification', '✓ Budget & Locality Discovery', '✓ Site Visit Booking', '✓ Broker Instant Alert']
    },
    support: {
      title: 'CUSTOMER SUPPORT & OPERATIONS',
      text: 'Thank you for calling support. This is Remo. I see your order #8492 is out for delivery with Bluedart and will arrive today by 2:30 PM. I have also texted you the live tracking link.',
      chips: ['✓ Zero Queue Wait Time', '✓ Order & Delivery Lookup', '✓ WhatsApp Auto-Dispatch', '✓ First-Call Resolution']
    },
    finance: {
      title: 'FINANCIAL SERVICES & BFSI',
      text: 'Hello Suresh, this is Remo from FinServe. I am following up regarding your KYC verification document upload for your business account. May I guide you through the remaining steps?',
      chips: ['✓ KYC Document Follow-up', '✓ Loan Pre-Screening', '✓ Payment Reminders', '✓ Compliance-Logged Audio']
    },
    automotive: {
      title: 'AUTOMOTIVE DEALERSHIPS',
      text: 'Hi Ananya, Remo calling from Hyundai Motors. You requested a test drive for the new Creta. We have a test vehicle available tomorrow at 11:00 AM at the Indiranagar showroom.',
      chips: ['✓ Test Drive Booking', '✓ Service Maintenance Alerts', '✓ Finance Eligibility Check', '✓ Trade-In Valuation Intake']
    }
  };

  const industryTabs = document.querySelectorAll('.ind-pill-btn, .ind-tab');
  const indDisplayTitle = document.getElementById('ind-display-title');
  const indDisplayText = document.getElementById('ind-display-text');
  const indDisplayChips = document.getElementById('ind-display-chips');
  const indDisplayCard = document.getElementById('industry-display-card');

  industryTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      industryTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const indKey = tab.getAttribute('data-industry');
      const data = industryData[indKey];
      if (!data) return;

      if (indDisplayCard) {
        indDisplayCard.style.opacity = '0.5';
        indDisplayCard.style.transform = 'translateY(3px)';
        setTimeout(() => {
          if (indDisplayTitle) indDisplayTitle.textContent = data.title;
          if (indDisplayText) indDisplayText.textContent = `"${data.text}"`;
          if (indDisplayChips) {
            indDisplayChips.innerHTML = data.chips.map(chip => {
              const cleanText = chip.replace(/^[^a-zA-Z0-9]+/, '').trim();
              return `<span class="ind-chip"><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" style="display:inline-block;vertical-align:middle;margin-right:4px;"><polyline points="20 6 9 17 4 12"/></svg> ${cleanText}</span>`;
            }).join('');
          }
          indDisplayCard.style.opacity = '1';
          indDisplayCard.style.transform = 'translateY(0)';
        }, 120);
      }
    });
  });

  // ------------------------------------------------------------------------
  // SERVICE CARDS: Non-routing tactile buttons
  // ------------------------------------------------------------------------
  const serviceCardButtons = document.querySelectorAll('.btn-service-card');
  serviceCardButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      playHumanChime('click');
      btn.style.transform = 'scale(0.96)';
      setTimeout(() => {
        btn.style.transform = '';
      }, 140);
    });
  });

  // ------------------------------------------------------------------------
  // H. BOOK A DEMO MODAL HANDLERS
  // ------------------------------------------------------------------------
  const demoModal = document.getElementById('demo-modal');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const modalResetBtn = document.getElementById('modal-reset-btn');
  const demoForm = document.getElementById('demo-form');
  const modalSuccess = document.getElementById('modal-success');
  const demoUseCaseSelect = document.getElementById('demo-usecase');

  function attachModalListeners() {
    const openDemoBtns = document.querySelectorAll('.open-demo-btn');
    openDemoBtns.forEach(btn => {
      btn.removeEventListener('click', handleOpenModalClick);
      btn.addEventListener('click', handleOpenModalClick);
    });
  }

  function handleOpenModalClick(e) {
    e.preventDefault();
    const useCase = this.getAttribute('data-usecase') || '';
    openModal(useCase);
  }

  const openModal = (useCase) => {
    if (demoModal) {
      demoModal.classList.add('active');
      document.body.style.overflow = 'hidden';
      if (useCase && demoUseCaseSelect) {
        const option = Array.from(demoUseCaseSelect.options).find(opt => 
          opt.value.toLowerCase().includes(useCase.toLowerCase()) || 
          useCase.toLowerCase().includes(opt.value.toLowerCase())
        );
        if (option) {
          demoUseCaseSelect.value = option.value;
        }
      }
    }
  };

  const closeModal = () => {
    if (demoModal) {
      demoModal.classList.remove('active');
      document.body.style.overflow = '';
      setTimeout(() => {
        if (demoForm) demoForm.style.display = 'flex';
        if (modalSuccess) modalSuccess.classList.remove('visible');
      }, 300);
    }
  };

  attachModalListeners();

  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeModal);
  if (modalResetBtn) modalResetBtn.addEventListener('click', closeModal);

  if (demoModal) {
    demoModal.addEventListener('click', (e) => {
      if (e.target === demoModal) closeModal();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && demoModal && demoModal.classList.contains('active')) {
      closeModal();
    }
  });

  if (demoForm) {
    demoForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const submitBtn = demoForm.querySelector('button[type="submit"]');
      const originalText = submitBtn.innerHTML;

      submitBtn.innerHTML = `
        <span class="c-spinner" style="width:14px;height:14px;border:2px solid #ffffff;border-top-color:transparent;border-radius:50%;display:inline-block;margin-right:6px;animation:spin 0.6s linear infinite;"></span>
        <span>Connecting with TakeRemo...</span>
      `;
      submitBtn.disabled = true;

      setTimeout(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
        demoForm.style.display = 'none';
        if (modalSuccess) modalSuccess.classList.add('visible');
      }, 800);
    });
  }

  // ------------------------------------------------------------------------
  // I. GLOBAL HUMAN TOUCH: SMOOTH SECTION REVEALS & TACTILE CLICKS
  // ------------------------------------------------------------------------
  const interactiveBtns = document.querySelectorAll('.btn, .nav-link, .ind-pill-btn, .hiw-step-card');
  interactiveBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      playHumanChime('click');
    });
  });

  if ('IntersectionObserver' in window) {
    const revealObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });

    const revealElements = document.querySelectorAll('.human-pillar-card, .caller-quote-card, .hiw-step-card, .ind-preview-card');
    revealElements.forEach(el => {
      el.classList.add('fade-in-up');
      revealObserver.observe(el);
    });
  }

});
