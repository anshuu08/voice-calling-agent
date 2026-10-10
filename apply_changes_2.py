import re
import sys

# 1. Update dashboard.css
try:
    with open('dashboard.css', 'r', encoding='utf-8') as f:
        dash_css = f.read()

    dash_css = re.sub(r'--dash-primary-blue: #[0-9A-Fa-f]+;', '--dash-primary-blue: #FC2415;', dash_css)
    dash_css = re.sub(r'--dash-primary-hover: #[0-9A-Fa-f]+;', '--dash-primary-hover: #D11F11;', dash_css)
    dash_css = re.sub(r'--dash-deep-blue: #[0-9A-Fa-f]+;', '--dash-deep-blue: #031740;', dash_css)

    with open('dashboard.css', 'w', encoding='utf-8') as f:
        f.write(dash_css)
    print("Updated dashboard.css colors.")
except Exception as e:
    print("Error updating dashboard.css:", e)


# 2. Update index.html
try:
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Remove the paragraph
    pattern_p = r'<p class="section-subtitle-clean">\s*Callers shouldn\'t feel like they\'re trapped in an automated phone maze\. TakeRemo brings genuine\s*conversational warmth, emotional intelligence, and natural cadence to every phone call\.\s*</p>'
    html = re.sub(pattern_p, '', html)

    # Reduce card 1
    html = html.replace(
        'Zero monotone robot drone. Remo speaks with subtle vocal dynamics, warm phrasing, and\n              human breathing pauses that make callers feel valued and heard.',
        'Speaks with subtle vocal dynamics and human breathing pauses.'
    )
    # in case it is on one line:
    html = html.replace(
        'Zero monotone robot drone. Remo speaks with subtle vocal dynamics, warm phrasing, and human breathing pauses that make callers feel valued and heard.',
        'Speaks with subtle vocal dynamics and human breathing pauses.'
    )

    # Reduce card 2
    html = html.replace(
        'Ever tried talking to an IVR that talks over you? Remo stops talking within 120ms when the caller interjects,\n              listens carefully, and adapts on the fly.',
        'Stops talking within 120ms when you interject, listens carefully, and adapts.'
    )
    html = html.replace(
        'Ever tried talking to an IVR that talks over you? Remo stops talking within 120ms when the caller interjects, listens carefully, and adapts on the fly.',
        'Stops talking within 120ms when you interject, listens carefully, and adapts.'
    )

    # Reduce card 3
    html = html.replace(
        'Senses frustration, hesitation, or urgency from vocal acoustics and word choice. Remo softens tone,\n              validates concerns, and offers genuine reassurance.',
        'Senses frustration or urgency, softening tone to offer genuine reassurance.'
    )
    html = html.replace(
        'Senses frustration, hesitation, or urgency from vocal acoustics and word choice. Remo softens tone, validates concerns, and offers genuine reassurance.',
        'Senses frustration or urgency, softening tone to offer genuine reassurance.'
    )

    # Reduce card 4
    html = html.replace(
        'Never forgets a detail. Remo sends instant, polite WhatsApp summaries, confirms calendar invites, and\n              updates your team with structured notes immediately.',
        'Sends instant WhatsApp summaries, confirms invites, and updates structured notes.'
    )
    html = html.replace(
        'Never forgets a detail. Remo sends instant, polite WhatsApp summaries, confirms calendar invites, and updates your team with structured notes immediately.',
        'Sends instant WhatsApp summaries, confirms invites, and updates structured notes.'
    )

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated index.html successfully.")
except Exception as e:
    print("Error updating index.html:", e)

