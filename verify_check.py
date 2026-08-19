"""Verification helper — checks noir-theme markers + live data on rendered pages."""
import os

PAGES = {
    'results.html':      ('/results/',             ['police-tape', 'stamp-mark', 'typewriter-text', 'title-cinzel',
                                                     'bg-noir-950', 'shadow-2xl', 'bg-dossier', 'border-noir-700']),
    'events_index.html': ('/events/',              ['police-tape', 'typewriter-text', 'title-cinzel',
                                                     'ACTIVE CASE FILES', 'CASE #']),
    'tournament1.html':  ('/events/tournament/1/', ['police-tape', 'typewriter-text', 'STAGE 1', 'STAGE 2', 'VICTOR']),
    'tournament2.html':  ('/events/tournament/2/', ['police-tape', 'typewriter-text', 'LEADERBOARD',
                                                     'Squad One', 'Squad Three', 'PTS']),
}
DATA = {
    'results.html':      ['WWE 2K SHOWDOWN', 'Alpha', 'VS', 'VICTOR: Alpha',
                          'BGMI SQUAD CLASH', 'Squad One', 'Squad Three',
                          'Agent Vega', 'Walk-in', 'Completed'],
}

out = []
host = 'http://127.0.0.1:8000'
import urllib.request

def fetch(path):
    try:
        with urllib.request.urlopen(host + path, timeout=10) as r:
            return r.read().decode('utf-8')
    except Exception as e:
        return None

all_html = {}
for fname, (path, _) in PAGES.items():
    html = fetch(path)
    all_html[fname] = html
    if html is None:
        out.append('FAIL fetch {} ({} bytes)'.format(path, 'n/a'))
    else:
        out.append('OK fetch {} ({} bytes)'.format(path, len(html)))

out.append('=== THEME MARKERS ===')
for fname, (_, markers) in PAGES.items():
    html = all_html.get(fname) or ''
    out.append('[' + fname + ']')
    for m in markers:
        out.append(('  OK   ' if m in html else '  MISS ') + m)

out.append('=== LIVE DATA ===')
for fname, items in DATA.items():
    html = all_html.get(fname) or ''
    out.append('[' + fname + ']')
    for d in items:
        out.append(('  OK   ' if d in html else '  MISS ') + d)

open('verify_output.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('verify_output.txt written')
