"""Comprehensive end-to-end verification for the integrated events app + footer credit.

Checks: (1) footer credit bytes in base.html, (2) font-decipher resolved,
(3) all pages serve 200 + carry the footer credit, (4) staff login + /events/walkins
render under noir theme, (5) the /results/ toggle POST flips session status.
Writes a plain-text report to final_report.txt.
"""
import urllib.request, urllib.parse, http.cookiejar, re

BASE = 'http://127.0.0.1:8000'
R = []
def log(s=''):
    R.append(s)

# ------------------------------------------------------------------
# 1) FILE-BYTE CHECKS (always work, no server needed)
# ------------------------------------------------------------------
b = open('templates/core/base.html', encoding='utf-8').read()
c = open('events/templates/events/casual_log.html', encoding='utf-8').read()
log('=== FILE-BYTE CHECKS ===')
log('footer credit (Designed by Karthik Vinod) in base.html: '
    + ('PRESENT' if 'Designed by Karthik Vinod' in b else 'MISSING'))
log('font-decipher still in casual_log.html: '
    + ('YES (BAD)' if 'font-decipher' in c else 'NO (good)'))
log('typewriter-text in casual_log.html: '
    + ('YES (good)' if 'typewriter-text' in c else 'NO (BAD)'))
# show the real footer lines
i = b.find('<!-- FOOTER')
log('--- base.html footer (real bytes) ---')
R.extend(b[i:b.find('<!-- MODAL: CASE DOSSIER DETAIL')].split('\n'))
log('')

# ------------------------------------------------------------------
# 2) HTTP CHECKS (server should be running)
# ------------------------------------------------------------------
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [('User-Agent', 'zieggers-verify/1.0')]

def get(path):
    try:
        r = op.open(BASE + path, timeout=12)
        return r.getcode(), r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return -1, str(e)

def post(path, data):
    try:
        r = op.open(BASE + path, urllib.parse.urlencode(data).encode(), timeout=12)
        return r.getcode(), r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except Exception as e:
        return -1, str(e)

log('=== HTTP STATUS (expect 200, except walkins=302 anonymous) ===')
pages = ['/results/', '/events/', '/events/tournament/1/', '/events/tournament/2/',
         '/events/walkins/', '/']
for p in pages:
    code, body = get(p)
    credit = 'footer-credit' if (p in ['/results/'] and 'Designed by Karthik Vinod' in (body or '')) else ''
    log('  {:24s} -> {:>4} {}'.format(p, code, credit))

# anonymous walkins -> 302
if True:
    class NR(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opnr = urllib.request.build_opener(NR, urllib.request.HTTPCookieProcessor(cj))
    try:
        opnr.open(BASE + '/events/walkins/', timeout=12)
        code = 200
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception as e:
        code = -1
    log('  anonymous /events/walkins/ (no-redirect) -> {} (expect 302)'.format(code))
log('')

# footer credit on each content page
log('=== FOOTER CREDIT ON PAGES ===')
for p in ['/results/', '/events/', '/events/tournament/1/', '/events/tournament/2/', '/']:
    code, body = get(p)
    ok = 'Designed by Karthik Vinod' in (body or '')
    log('  {} footer credit: {}'.format(p, 'OK' if ok else 'MISSING'))
log('')

# ------------------------------------------------------------------
# 3) STAFF LOGIN + /events/walkins/ render under noir theme
# ------------------------------------------------------------------
log('=== STAFF LOGIN + /events/walkins/ ===')
_, lp = get('/admin/login/')
tok = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', lp) if lp else None
_, _ = post('/admin/login/', {'username': 'admin', 'password': 'admin123',
                              'csrfmiddlewaretoken': tok.group(1) if tok else ''})
logged_in = any(c.name == 'sessionid' for c in cj)
log('login as admin: ' + ('OK' if logged_in else 'FAILED'))
code, walkins = get('/events/walkins/')
log('staff /events/walkins/ -> HTTP {} (expect 200)'.format(code))
for m in ['police-tape', 'typewriter-text', 'title-cinzel',
          'PRE-REGISTERED AGENTS', 'REGISTER NEW WALK-IN OPERATOR',
          'Agent Vega', 'Agent Reeves', 'VR Gaming',
          'Walk-in', 'Completed', 'Active (Click to Complete)']:
    log('  marker {}: {}'.format(m, 'OK' if m in (walkins or '') else 'MISSING'))
log('')

# ------------------------------------------------------------------
# 4) TOGGLE POST on /results/
# ------------------------------------------------------------------
log('=== TOGGLE POST (results) ===')
_, res = get('/results/')
csrf = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', res) if res else None
vega = re.search(r'Agent Vega.*?name="session_id" value="(\d+)"', res, re.S) if res else None
log('csrf token: {}; Vega session_id: {}'.format(
    'found' if csrf else 'NOT FOUND', vega.group(1) if vega else 'NOT FOUND'))
ab = (res or '').count('Active (Click to Complete)')
cb = (res or '').count('✓ Completed')
log('before: Active=%d, Completed=%d' % (ab, cb))
if csrf and vega:
    post('/results/', {'action': 'toggle_status', 'session_id': vega.group(1),
                       'csrfmiddlewaretoken': csrf.group(1)})
    _, res2 = get('/results/')
    aa = (res2 or '').count('Active (Click to Complete)')
    ca = (res2 or '').count('✓ Completed')
    log('after toggle: Active=%d, Completed=%d (expect 0, 2)' % (aa, ca))
    log('toggle result: ' + ('OK (Vega Active->Completed)' if aa == 0 and ca == 2 else 'CHECK'))
    # restore
    s2 = re.search(r'Agent Vega.*?name="session_id" value="(\d+)"', res2, re.S)
    if s2:
        post('/results/', {'action': 'toggle_status', 'session_id': s2.group(1),
                           'csrfmiddlewaretoken': csrf.group(1)})
        _, res3 = get('/results/')
        log('restore: Active=%d, Completed=%d (expect 1, 1)' % (
            (res3 or '').count('Active (Click to Complete)'),
            (res3 or '').count('✓ Completed')))
else:
    log('toggle: skipped (csrf or vega sid missing)')
log('')

log('=== FINAL: server started cleanly? ===')
try:
    log('  runserver.log tail: ' + (open('runserver.log').read()[-400:]))
except Exception as e:
    log('  runserver.log unavailable: ' + str(e))

open('final_report.txt', 'w', encoding='utf-8').write('\n'.join(R) + '\n')
