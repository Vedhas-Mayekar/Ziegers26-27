"""End-to-end verification: staff login, walkins render, toggle POST, font check."""
import urllib.request, urllib.parse, http.cookiejar, re

BASE = 'http://127.0.0.1:8000'
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
op.addheaders = [('User-Agent', 'zieggers-verify/1.0')]

def get(path):
    r = op.open(BASE + path, timeout=15)
    return r.getcode(), r.read().decode('utf-8')

def post(path, data):
    r = op.open(BASE + path, urllib.parse.urlencode(data).encode(), timeout=15)
    return r.getcode(), r.read().decode('utf-8')

R = []
def log(s):
    R.append(s)

try:
    # 0. real-bytes check for the old undefined class
    raw = open('events/templates/events/casual_log.html', encoding='utf-8').read()
    log('font-decipher in casual_log.html bytes: ' +
        ('STILL PRESENT (fix failed)' if 'font-decipher' in raw else 'absent (good)'))
    log('typewriter-text in casual_log.html bytes: ' +
        ('present (good)' if 'typewriter-text' in raw else 'absent (BAD)'))

    # 1. anonymous walkins -> expect 302 redirect to admin login
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            return None
    opnr = urllib.request.build_opener(NoRedirect, urllib.request.HTTPCookieProcessor(cj))
    try:
        opnr.open(BASE + '/events/walkins/', timeout=15)
        acode = 200
    except urllib.error.HTTPError as e:
        acode = e.code
    log('anonymous /events/walkins/ -> HTTP ' + str(acode) + ' (expect 302)')

    # 2. login as admin: GET login page for csrf, then POST credentials
    _, login_page = get('/admin/login/')
    tok = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', login_page)
    _, _ = post('/admin/login/', {'username': 'admin', 'password': 'admin123',
                                  'csrfmiddlewaretoken': tok.group(1) if tok else ''})
    logged_in = any(c.name == 'sessionid' for c in cj)
    log('login as admin: ' + ('OK (sessionid set)' if logged_in else 'FAILED'))

    # 3. staff GET /events/walkins/ -> 200 under noir theme with live data
    code, walkins = get('/events/walkins/')
    log('staff /events/walkins/ -> HTTP ' + str(code) + ' (expect 200)')
    markers = ['police-tape', 'typewriter-text', 'title-cinzel',
               'PRE-REGISTERED AGENTS', 'REGISTER NEW WALK-IN OPERATOR',
               'Agent Vega', 'Agent Reeves', 'VR Gaming',
               'Walk-in', 'Completed', 'Active (Click to Complete)']
    for m in markers:
        log('  marker ' + m + ': ' + ('OK' if m in walkins else 'MISSING'))

    # 4. toggle test on /results/: Vega is 'Playing' -> button 'Active'; toggle -> 'Completed'
    _, res = get('/results/')
    csrf = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', res)
    active_before = res.count('Active (Click to Complete)')
    completed_before = res.count('✓ Completed')
    vega_sid = re.search(r'Agent Vega.*?name="session_id" value="(\d+)"', res, re.S)
    log('toggle pre-state: Active buttons=%d, Completed buttons=%d, Vega sid=%s'
        % (active_before, completed_before, vega_sid.group(1) if vega_sid else 'NOTFOUND'))
    if csrf and vega_sid:
        post('/results/', {'action': 'toggle_status', 'session_id': vega_sid.group(1),
                           'csrfmiddlewaretoken': csrf.group(1)})
        _, res2 = get('/results/')
        active_after = res2.count('Active (Click to Complete)')
        completed_after = res2.count('✓ Completed')
        log('toggle post-state: Active=%d, Completed=%d  (expect Active 0, Completed 2)'
            % (active_after, completed_after))
        log('toggle result: ' + ('OK (Vega flipped Active->Completed)'
                                 if active_after == 0 and completed_after == 2 else 'CHECK!'))
        # restore: toggle Vega back to Playing
        sid2 = re.search(r'Agent Vega.*?name="session_id" value="(\d+)"', res2, re.S)
        if csrf and sid2:
            post('/results/', {'action': 'toggle_status', 'session_id': sid2.group(1),
                               'csrfmiddlewaretoken': csrf.group(1)})
            _, res3 = get('/results/')
            log('restore: Active=%d, Completed=%d (expect Active 1, Completed 1)'
                % (res3.count('Active (Click to Complete)'), res3.count('✓ Completed')))
    else:
        log('toggle: skipped (csrf/session_id missing)')

    log('VERIFY DONE')
except Exception as e:
    import traceback
    log('EXCEPTION: ' + str(e))
    log(traceback.format_exc())

open('verify_output2.txt', 'w', encoding='utf-8').write('\n'.join(R) + '\n')
print('written verify_output2.txt')
