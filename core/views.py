"""Views for the ZIEGERS 2026-27 landing page."""
from django.contrib import messages
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404

# DeCipher Gaming operations — single DB, shared with the results dashboard
from events.models import Tournament, CasualGameSession


def chrome_devtools_probe(request):
    """Respond 204 to Chrome DevTools mobile-emulation probes.

    Chrome's mobile device emulation requests this well-known endpoint
    when network throttling / device inspections are active. A 404 from
    Django causes the debugger to pause on failed connection requests in
    some versions, so we answer with an empty 204 No Content response.
    """
    # HTTP 204 must never carry a body — use HttpResponse, not JsonResponse.
    return HttpResponse(status=204)

# ---------------------------------------------------------------------------
# Event data store — all case details are defined here as data structures.
# This keeps the template clean and makes future edits (e.g. admin-driven
# content) straightforward to introduce.
# ---------------------------------------------------------------------------


def _base_event(key, number, day, name, fee, fee_numeric, tagline, metadata, officers):
    """Return a structured event dictionary used by both grid + modal."""
    return {
        'key': key,
        'number': number,
        'day': day,
        'name': name,
        'fee': fee,
        'fee_numeric': fee_numeric,
        'tagline': tagline,
        'metadata': metadata,
        'officers': officers,
    }


# Events rendered as cards in the "Open Cases" grid.
EVENTS = [
    _base_event(
        key='bgmi', number='01', day='day1', name='BGMI SQUAD',
        fee='₹149 / TEAM', fee_numeric=149,
        tagline=(
            'Team-based battle royale tournament using Advanced Custom Rooms. '
            'Online knockout rounds shortlist teams for campus finals across multiple maps.'
        ),
        metadata=[
            ('users', 'Full Squad (Minimum Level 35)'),
            ('crosshair', 'Erangel & Miramar Custom Rooms'),
            ('phone', 'Officers: Ethan / Aayush'),
        ],
        officers=[{'name': 'Ethan', 'phone': '9930698777'},
                  {'name': 'Aayush', 'phone': '9833773577'}],
    ),
    _base_event(
        key='freefire', number='02', day='day1', name='FREE FIRE',
        fee='₹149 / TEAM', fee_numeric=149,
        tagline=(
            'Fast-paced battle royale showdown with Custom Rooms. '
            'Online knockouts to shortlist top squads for live campus final matches.'
        ),
        metadata=[
            ('users', 'Full Squad (Min Lvl 35)'),
            ('tv', 'Selected Matches Live Streamed'),
            ('phone', 'Officers: Ethan / Aayush'),
        ],
        officers=[{'name': 'Ethan', 'phone': '9930698777'},
                  {'name': 'Aayush', 'phone': '9833773577'}],
    ),
    _base_event(
        key='techmania', number='03', day='day1', name='TECHMANIA',
        fee='₹49 / PERSON', fee_numeric=49,
        tagline=(
            'Think. React. Outsmart. Test your instincts across 4-5 thrilling '
            'mini-games filled with quick tech challenges. No coding experience needed!'
        ),
        metadata=[
            ('zap', '4-5 Reaction Mini Games'),
            ('brain', 'Open to All Specializations'),
            ('phone', 'Officers: Karan / Siddhi'),
        ],
        officers=[{'name': 'Karan Singh', 'phone': '9699265426'},
                  {'name': 'Siddhi More', 'phone': '9137505014'}],
    ),
    _base_event(
        key='fc25', number='04', day='day1', name='FC 25 FOOTBALL',
        fee='₹49 / PERSON', fee_numeric=49,
        tagline=(
            '1v1 competitive football tournament on PlayStation (EA SPORTS FC 25). '
            'Direct knockout format featuring 10-minute intense matches.'
        ),
        metadata=[
            ('gamepad-2', 'PS5 / Tele Broadcast View'),
            ('timer', '10 Mins • Sudden Penalties'),
            ('phone', 'Officers: Ethan / Aayush'),
        ],
        officers=[{'name': 'Ethan', 'phone': '9930698777'},
                  {'name': 'Aayush', 'phone': '9833773577'}],
    ),
    _base_event(
        key='wwe', number='05', day='day1', name='WWE 2K SHOWDOWN',
        fee='₹49 / PERSON', fee_numeric=49,
        tagline=(
            'Head-to-head 1v1 wrestling gaming experience. '
            'Fast 5-minute competitive matches under standard tournament settings.'
        ),
        metadata=[
            ('swords', '1v1 Bracket Matchups'),
            ('clock', '5 Mins Rapid Knockouts'),
            ('phone', 'Officers: Ethan / Aayush'),
        ],
        officers=[{'name': 'Ethan', 'phone': '9930698777'},
                  {'name': 'Aayush', 'phone': '9833773577'}],
    ),
    _base_event(
        key='vr', number='06', day='day1', name='VR EXPERIENCE',
        fee='₹69 / PERSON', fee_numeric=69,
        tagline=(
            'Step inside virtual reality with state-of-the-art headsets, '
            'supervised play area, and high-octane immersive simulations.'
        ),
        metadata=[
            ('glasses', 'Virtual Reality Setup'),
            ('shield', 'Supervised Arena'),
            ('phone', 'Officers: Ethan / Aayush'),
        ],
        officers=[{'name': 'Ethan', 'phone': '9930698777'},
                  {'name': 'Aayush', 'phone': '9833773577'}],
    ),
    _base_event(
        key='codesprint', number='07', day='day2', name='CODESPRINT 2026 HACKATHON',
        fee='₹449 / TEAM', fee_numeric=449,
        tagline=(
            'Step into the future of software creation with our intensive '
            '<strong>5-hour solo or duo hackathon</strong>. Experience AI-assisted '
            'development (vibe coding), master Git/GitHub practically, innovate, '
            'make meaningful commits, and ship portfolio-worthy projects!'
        ),
        metadata=[
            ('cpu', 'AI & Vibe Tools Permitted'),
            ('git-commit', 'Git Commits Mandatory'),
            ('phone', 'Officers: Vedhas / Karthik'),
        ],
        officers=[{'name': 'Vedhas Mayekar', 'phone': '8451097792'},
                  {'name': 'Karthik Vinod', 'phone': '9820489099'}],
    ),
    _base_event(
        key='decipher', number='08', day='day2', name='DECIPHER HUNT',
        fee='₹49 / PERSON', fee_numeric=49,
        tagline=(
            'Decode clues, follow the digital trail, collect QR fragments, '
            'and race across campus to unlock the final treasure vault!'
        ),
        metadata=[
            ('map-pin', 'Campus-Wide QR Search'),
            ('key', '3 Tech-Based Envelopes'),
            ('phone', 'Officers: Karan / Siddhi'),
        ],
        officers=[{'name': 'Karan Singh', 'phone': '9699265426'},
                  {'name': 'Siddhi More', 'phone': '9137505014'}],
    ),
]

# Detailed modal dossier data — rules + extended descriptions per case.
CASE_DETAILS = {
    'bgmi': {
        'title': 'BGMI SQUAD TOURNAMENT',
        'case_no': 'CASE 01 • DAY 1',
        'fee': '₹149 / TEAM',
        'fee_num': 149,
        'desc': (
            'Team-based battle royale tournament using Advanced Custom Rooms. '
            'Online knockout rounds shortlist teams for on-campus finals across '
            'multiple maps ranked by total points.'
        ),
        'rules': [
            'Only full squad registrations are allowed; minimum Level 35 in-game account.',
            'Cheating, unauthorized software, exploiting bugs, or teaming is strictly prohibited.',
            'Players must join assigned custom rooms on time.',
            'Organizers verify match results; screenshots proof required if requested.',
            'Organizers hold final decision on all disputes and tournament adjustments.',
        ],
        'officers': [{'name': 'Ethan', 'phone': '9930698777'},
                     {'name': 'Aayush', 'phone': '9833773577'}],
    },
    'freefire': {
        'title': 'FREE FIRE BATTLE ROYALE',
        'case_no': 'CASE 02 • DAY 1',
        'fee': '₹149 / TEAM',
        'fee_num': 149,
        'desc': (
            'Fast-paced battle royale tournament featuring Custom Rooms. '
            'Online knockouts select top squads for live campus final matches.'
        ),
        'rules': [
            'Full squad registrations only with minimum Level 35 accounts.',
            'Strict anti-cheating policy & bug exploitation ban.',
            'Room credentials issued on scheduled timing; punctuality required.',
            'Selected matches streamed live by ZIEGERS media team.',
            'Organizer decisions are final in all circumstances.',
        ],
        'officers': [{'name': 'Ethan', 'phone': '9930698777'},
                     {'name': 'Aayush', 'phone': '9833773577'}],
    },
    'techmania': {
        'title': 'TECHMANIA MINI-GAMES',
        'case_no': 'CASE 03 • DAY 1',
        'fee': '₹49 / PERSON',
        'fee_num': 49,
        'desc': (
            'Think. React. Outsmart. Test your instincts in 4-5 thrilling '
            'games packed with challenges and surprises! No tech expertise needed.'
        ),
        'rules': [
            'Participants must follow instructions given by coordinators.',
            'Non-refundable and non-transferable registration.',
            'Report to venue prior to scheduled event start time.',
            'Unfair means result in instant disqualification.',
        ],
        'officers': [{'name': 'Karan Singh', 'phone': '9699265426'},
                     {'name': 'Siddhi More', 'phone': '9137505014'}],
    },
    'fc25': {
        'title': 'EA SPORTS FC 25 (PS5)',
        'case_no': 'CASE 04 • DAY 1',
        'fee': '₹49 / PERSON',
        'fee_num': 49,
        'desc': (
            '1v1 competitive football tournament on PlayStation. '
            'Knockout format for fast-paced football gaming enthusiasts.'
        ),
        'rules': [
            'Camera Preset: Tele Broadcast.',
            'Match length: 10 Minutes total.',
            'No extra time — direct penalty shootouts.',
            'Soccer Aid and All-Star teams strictly banned.',
            'Legacy Defending is not permitted.',
        ],
        'officers': [{'name': 'Ethan', 'phone': '9930698777'},
                     {'name': 'Aayush', 'phone': '9833773577'}],
    },
    'wwe': {
        'title': 'WWE 2K SHOWDOWN',
        'case_no': 'CASE 05 • DAY 1',
        'fee': '₹49 / PERSON',
        'fee_num': 49,
        'desc': (
            'Head-to-head 1v1 wrestling matches under standardized '
            'competitive tournament settings.'
        ),
        'rules': [
            '1v1 matches, 5-minute round limit.',
            'Random pairings or standard bracket setup.',
            'Respectful sportsmanlike conduct required at all times.',
            'Glitch or bug exploitation causes instant loss.',
        ],
        'officers': [{'name': 'Ethan', 'phone': '9930698777'},
                     {'name': 'Aayush', 'phone': '9833773577'}],
    },
    'vr': {
        'title': 'VR GAMING EXPERIENCE',
        'case_no': 'CASE 06 • DAY 1',
        'fee': '₹69 / PERSON',
        'fee_num': 69,
        'desc': (
            'Immersive virtual-reality gaming in a controlled '
            'safety-monitored campus environment.'
        ),
        'rules': [
            'Follow safety distance guidelines within VR play bounds.',
            'Handle expensive VR headsets with extreme care.',
            'Game titles announced based on hardware availability.',
            'Staff decisions final regarding operational safety.',
        ],
        'officers': [{'name': 'Ethan', 'phone': '9930698777'},
                     {'name': 'Aayush', 'phone': '9833773577'}],
    },
    'codesprint': {
        'title': 'CODESPRINT 2026 HACKATHON',
        'case_no': 'CASE 07 • DAY 2',
        'fee': '₹449 / TEAM',
        'fee_num': 449,
        'desc': (
            '5-Hour solo or duo hackathon focusing on AI-assisted development '
            '(vibe coding), practical Git workflow, and shipping working software.'
        ),
        'rules': [
            'Solo or duo teams (1-2 members). Any programming stack or AI tools allowed.',
            '100% original work; copying existing projects prohibited.',
            'Must strictly adhere to problem statement requirements.',
            'GitHub repository with meaningful commits and README mandatory.',
            'Evaluation based strictly on fully working features.',
        ],
        'officers': [{'name': 'Vedhas Mayekar', 'phone': '8451097792'},
                     {'name': 'Karthik Vinod', 'phone': '9820489099'}],
    },
    'decipher': {
        'title': 'DECIPHER TREASURE HUNT',
        'case_no': 'CASE 08 • DAY 2',
        'fee': '₹49 / PERSON',
        'fee_num': 49,
        'desc': (
            'Decode clues, follow digital trails, collect QR fragments, '
            'and race across campus to unlock the final treasure vault.'
        ),
        'rules': [
            'Participants divided into groups.',
            'Solve 3 technology-based clues to progress.',
            'Collect ONLY your team\'s assigned envelope.',
            'Tampering with other teams\' envelopes = instant DQ.',
        ],
        'officers': [{'name': 'Karan Singh', 'phone': '9699265426'},
                     {'name': 'Siddhi More', 'phone': '9137505014'}],
    },
}

# Evidence board items
EVIDENCE_ITEMS = [
    {
        'number': 'EVIDENCE #01',
        'color': 'stamp-red',
        'icon_color': 'text-stamp-red',
        'title': 'Esports Sector',
        'text': 'Custom room credentials dispatched 30 mins prior to match time.',
    },
    {
        'number': 'EVIDENCE #02',
        'color': 'stamp-gold',
        'icon_color': 'text-stamp-gold',
        'title': 'Decipher QR Clues',
        'text': '3 Technology-based envelopes hidden strictly within college parameters.',
    },
    {
        'number': 'EVIDENCE #03',
        'color': 'green-600',
        'icon_color': 'text-green-500',
        'title': 'PS5 Arena',
        'text': 'Tele-broadcast preset enabled. Zero tolerance for Legacy Defending.',
    },
    {
        'number': 'EVIDENCE #04',
        'color': 'purple-600',
        'icon_color': 'text-purple-400',
        'title': 'Verification Lab',
        'text': 'Physical College ID verification mandatory at Entry Bureau.',
    },
]

# Security / protocol instructions
PROTOCOLS = [
    ('Mandatory Identity Check:',
     'Bringing your physical college ID on event days is strictly mandatory. Entry will be denied without it.'),
    ('Prohibited Items:',
     'Sharp objects, drugs, alcohol, or any harmful materials are strictly forbidden and cause immediate disqualification.'),
    ('Final Authority:',
     'Event coordinators\' rulings are absolute in all disputes and investigations.'),
    ('Dress Code:',
     'Standard college dress code rules must be maintained throughout campus.'),
    ('Volunteer Cooperation:',
     'Cooperate with Ziegers student volunteers & faculty staff at all times.'),
    ('No Refund Policy:',
     'Registration fees are non-refundable and non-transferable under any circumstances.'),
    ('Have Fun:',
     'Maintain a respectful, friendly environment and enjoy the event!'),
]

# Leadership / Command Crew
LEADERSHIP = [
    {
        'role': 'CHAIRPERSON',
        'name': 'Harsh Pitkekar',
        'phone': '8652687593',
    },
    {
        'role': 'VICE CHAIRPERSON',
        'name': 'Shivam Bhilare',
        'phone': '8356048667',
    },
    {
        'role': 'VICE CHAIRPERSON',
        'name': 'Supriya Gupta',
        'phone': '7700927008',
    },
]

# ───────────────────────────────────────────────────────────────
# Command Crew — Full Portfolio Dossier Directory
# Each PNG dossier image maps to a designation + unique
# gender-neutral case description (DeCipher investigation theme).
# tier: command | heads | coheads | committee
# ───────────────────────────────────────────────────────────────
COMMAND_CREW = [
    # ── TIER 1 · COMMAND CORE ─────────────────────────────────
    {
        'image': 'images/cp.png',
        'role': 'CHAIRPERSON',
        'code': 'CASE COMMANDER',
        'tier': 'command',
        'description': (
            'The apex authority of the ZIEGERS investigation bureau. '
            'Every operation, dossier, and negotiation passes through '
            'this commanding vision — setting the mission, aligning '
            'every department, and carrying the final word on all '
            'strategic decisions.'
        ),
    },
    {
        'image': 'images/vcp1.png',
        'role': 'VICE CHAIRPERSON',
        'code': 'DEPUTY COMMAND',
        'tier': 'command',
        'description': (
            'Right hand of the command core, bridging every portfolio '
            'and keeping cross-bureau operations in perfect sync. '
            'Handles high-stakes coordination, unblocks critical paths, '
            'and ensures the mission advances without a single '
            'loose thread.'
        ),
    },
    {
        'image': 'images/vcp2.png',
        'role': 'VICE CHAIRPERSON',
        'code': 'DEPUTY COMMAND',
        'tier': 'command',
        'description': (
            'Co-deputy of the bureau, wired into ground execution and '
            'operational continuity. Moves between departments to '
            'strengthen collaboration, resolve friction points, and '
            'keep momentum steady through every phase of the event.'
        ),
    },

    # ── TIER 2 · PORTFOLIO HEADS ──────────────────────────────
    {
        'image': 'images/creativeshead.png',
        'role': 'CREATIVE HEAD',
        'code': 'DIRECTOR OF NARRATIVES',
        'tier': 'heads',
        'description': (
            'Warden of visual storytelling — shaping raw case concepts '
            'into immersive, cinematic experiences that pull every '
            'investigator deeper into the mystery.'
        ),
    },
    {
        'image': 'images/designhead.png',
        'role': 'DESIGN HEAD',
        'code': 'KEEPER OF IDENTITY',
        'tier': 'heads',
        'description': (
            'Architect of the bureau\u2019s visual identity. Every poster, '
            'banner, and case file carries the signature polish of this '
            'meticulous craftsperson\u2019s eye for detail.'
        ),
    },
    {
        'image': 'images/editinghead.png',
        'role': 'EDITING HEAD',
        'code': 'PRECISION CLERK',
        'tier': 'heads',
        'description': (
            'The precision editor behind the bureau\u2019s polished output — '
            'refining every frame, line, and asset until it clears the '
            'highest quality standards of the dossier.'
        ),
    },
    {
        'image': 'images/financehead1.png',
        'role': 'FINANCE HEAD',
        'code': 'KEEPER OF THE VAULT',
        'tier': 'heads',
        'description': (
            'Guardian of the bureau\u2019s treasury. Balances every ledger, '
            'tracks every rupee, and guarantees every operation runs with '
            'full financial integrity and accountability.'
        ),
    },
    {
        'image': 'images/financehead2.png',
        'role': 'FINANCE HEAD',
        'code': 'LEDGER WARDEN',
        'tier': 'heads',
        'description': (
            'Second key of the vault — steering resource allocation, '
            'expense flow, and budget forecasting to keep the entire '
            'mission funded, stable, and transparent.'
        ),
    },
    {
        'image': 'images/gaminghead.png',
        'role': 'GAMING HEAD',
        'code': 'ARENA STRATEGIST',
        'tier': 'heads',
        'description': (
            'Tournament commander of the esports arena. Designs match '
            'formats, enforces fair-play protocol, and keeps the '
            'competitive intensity at full throttle.'
        ),
    },
    {
        'image': 'images/techmainahead.png',
        'role': 'TECHMANIA HEAD',
        'code': 'MINIGAME WARDEN',
        'tier': 'heads',
        'description': (
            'Warden of the quick-reaction game lab. Engineer of rapid-fire '
            'challenges that test reflexes, logic, and composure — '
            'no coding experience required, only instincts.'
        ),
    },
    {
        'image': 'images/hackathonhead1.png',
        'role': 'HACKATHON HEAD',
        'code': 'CODESPRINT ARCHITECT',
        'tier': 'heads',
        'description': (
            'Master architect of the CodeSprint mission — designing the '
            '5-hour challenge, setting the problem statement, and '
            'crafting the battlefield where innovation meets execution.'
        ),
    },
    {
        'image': 'images/hackathonhead2.png',
        'role': 'HACKATHON HEAD',
        'code': 'TALENT SCOUT',
        'tier': 'heads',
        'description': (
            'Lead evaluator of the hackarena — shaping judging rubrics, '
            'reviewing commits, and scouting the sharpest builders '
            'emerging from the hacking floor.'
        ),
    },
    {
        'image': 'images/managementhead1.png',
        'role': 'MANAGEMENT HEAD',
        'code': 'CHIEF OF OPERATIONS',
        'tier': 'heads',
        'description': (
            'Chief of on-ground operations. Coordinates the volunteer '
            'corps, allocates resources, and commands the logistical '
            'machine that keeps every venue running on schedule.'
        ),
    },
    {
        'image': 'images/prhead1.png',
        'role': 'PR HEAD',
        'code': 'VOICE OF THE BUREAU',
        'tier': 'heads',
        'description': (
            'The public voice of ZIEGERS. Crafts every announcement, '
            'manages outreach, and keeps the world informed with sharp, '
            'accurate, and compelling communication.'
        ),
    },
    {
        'image': 'images/prhead2.png',
        'role': 'PR HEAD',
        'code': 'AMPLIFICATION AGENT',
        'tier': 'heads',
        'description': (
            'Strategist of outreach and media presence — amplifying every '
            'case update across platforms and keeping the bureau\u2019s '
            'reputation at its strongest.'
        ),
    },
    {
        'image': 'images/sponsorshiphead.png',
        'role': 'SPONSORSHIP HEAD',
        'code': 'ALLIANCE NEGOTIATOR',
        'tier': 'heads',
        'description': (
            'Master negotiator forging strategic alliances. Secures '
            'partners, resources, and backing that fuel the entire '
            'bureau\u2019s operation from start to close.'
        ),
    },
    {
        'image': 'images/videohead1.png',
        'role': 'VIDEO HEAD',
        'code': 'CINEMATIC EYES',
        'tier': 'heads',
        'description': (
            'The cinematic eyes of the case files. Captures every key '
            'moment, every clue, and every victory in high-caliber '
            'footage that preserves the mission for history.'
        ),
    },
    {
        'image': 'images/committeehead1.png',
        'role': 'COMMITTEE HEAD',
        'code': 'FIELD COMMANDER',
        'tier': 'heads',
        'description': (
            'Lead commander of the support battalion — aligning the full '
            'committee, driving collaborative execution, and ensuring '
            'every portfolio works as a single coordinated unit.'
        ),
    },

    # ── TIER 3 · CO-HEADS ─────────────────────────────────────
    {
        'image': 'images/creativescohead.png',
        'role': 'CREATIVE CO-HEAD',
        'code': 'NARRATIVE DEPUTY',
        'tier': 'coheads',
        'description': (
            'Deputy creative unit — assisting the visual direction, '
            'crafting auxiliary assets, and bringing the bureau\u2019s '
            'artistic vision to life.'
        ),
    },
    {
        'image': 'images/creativescohead2.png',
        'role': 'CREATIVE CO-HEAD',
        'code': 'DESIGN SUPPORT',
        'tier': 'coheads',
        'description': (
            'Support arm of the creative cell — helping shape concepts, '
            'executing theme-driven details, and keeping the visual '
            'language consistent across every touchpoint.'
        ),
    },
    {
        'image': 'images/gamaingcohead.png',
        'role': 'GAMING CO-HEAD',
        'code': 'ARENA DEPUTY',
        'tier': 'coheads',
        'description': (
            'Deputy of the esports arena — coordinating squads, managing '
            'custom rooms, and ensuring every match drops into action '
            'without a hitch.'
        ),
    },
    {
        'image': 'images/techmaniacohead.png',
        'role': 'TECHMANIA CO-HEAD',
        'code': 'GAMELAB SUPPORT',
        'tier': 'coheads',
        'description': (
            'Deputy warden of the game lab — fine-tuning mini-game '
            'mechanics, managing station flow, and keeping the '
            'challenge queue moving.'
        ),
    },
    {
        'image': 'images/hackathoncohead.png',
        'role': 'HACKATHON CO-HEAD',
        'code': 'HACKARENA DEPUTY',
        'tier': 'coheads',
        'description': (
            'Deputy handler of the CodeSprint operation — tracking '
            'submissions, supporting teams, and keeping the innovation '
            'pipeline flowing smoothly.'
        ),
    },
    {
        'image': 'images/managementcohead.png',
        'role': 'MANAGEMENT CO-HEAD',
        'code': 'GROUND DEPUTY',
        'tier': 'coheads',
        'description': (
            'Ground operations deputy — handling crowd flow, on-site '
            'logistics, and resource deployment with precision under '
            'pressure.'
        ),
    },

    # ── TIER 4 · COMMITTEE ────────────────────────────────────
    {
        'image': 'images/committeemember1.png',
        'role': 'COMMITTEE MEMBER',
        'code': 'FIELD OPERATIVE',
        'tier': 'committee',
        'description': (
            'Frontline operative of the bureau — executing ground duties '
            'across departments and ensuring no detail slips past '
            'event day.'
        ),
    },
    {
        'image': 'images/committteemember2.png',
        'role': 'COMMITTEE MEMBER',
        'code': 'LOGISTICS SCOUT',
        'tier': 'committee',
        'description': (
            'Logistics scout keeping the operational gear ready — from '
            'venue setup to material movement, this operative covers '
            'every corner of the mission.'
        ),
    },
    {
        'image': 'images/committeemember3.png',
        'role': 'COMMITTEE MEMBER',
        'code': 'PARTICIPANT LIAISON',
        'tier': 'committee',
        'description': (
            'Liaison of the bureau — guiding participants, answering '
            'field questions, and keeping every interaction smooth '
            'from check-in to finish.'
        ),
    },
    {
        'image': 'images/committeemember4.png',
        'role': 'COMMITTEE MEMBER',
        'code': 'EXECUTION SUPPORT',
        'tier': 'committee',
        'description': (
            'Execution support unit — reinforcing events on the ground, '
            'assisting coordinators, and keeping the energy high '
            'through closing ceremonies.'
        ),
    },
]

# Hero stats
HERO_STATS = [
    {'label': 'Active Dossiers', 'value': '08 Cases', 'icon': 'folder-kanban', 'color': 'text-stamp-red'},
    {'label': 'Operations Duration', 'value': '2 Days', 'icon': 'calendar', 'color': 'text-stamp-gold'},
    {'label': 'Entry Fee Starts', 'value': '₹49 / Head', 'icon': 'indian-rupee', 'color': 'text-green-500'},
    {'label': 'Case Closing Date', 'value': 'Aug 28', 'icon': 'clock', 'color': 'text-stamp-red'},
]


def landing_page(request):
    """Render the ZIEGERS 2026-27 landing page."""
    context = {
        'page_title': 'ZIEGERS 2026-27 | DeCipher - Solve the Unsolved',
        'events': EVENTS,
        'case_details': CASE_DETAILS,
        'case_details_json': CASE_DETAILS,
        'evidence_items': EVIDENCE_ITEMS,
        'protocols': PROTOCOLS,
        'leadership': LEADERSHIP,
        'hero_stats': HERO_STATS,
        'codesprint_event': next(e for e in EVENTS if e['number'] == '07'),
    }
    return render(request, 'core/index.html', context)


def results_page(request):
    """Render the ZIEGERS 2026-27 results dashboard.

    Live DeCipher Gaming operations are merged into the noir case-file
    theme: tournament brackets (1v1), battle-royale points tables, and the
    casual walk-in log with inline status toggling — all drawn from the
    shared events database.
    """
    # Results remain public, but changing an operational status is a staff-only
    # action.  Previously any visitor could submit this form (or a malformed
    # session id) and either alter a record or receive a 404 error page.
    if request.method == 'POST':
        if request.POST.get('action') != 'toggle_status':
            return HttpResponseBadRequest('Unsupported results action.')

        if not request.user.is_staff:
            messages.error(request, 'Sign in as a staff member to update a session.')
            return redirect('core:results')

        session_id = request.POST.get('session_id')
        try:
            session = CasualGameSession.objects.get(pk=session_id)
        except (CasualGameSession.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'That session could not be found. Please refresh and try again.')
        else:
            session.status = 'Completed' if session.status == 'Playing' else 'Playing'
            session.save(update_fields=['status'])
            messages.success(request, f'{session.player_name}\'s session is now {session.status.lower()}.')
        return redirect('core:results')

    # Build tournament dossiers with prefetched relations for the board
    tournaments_data = []
    for tournament in Tournament.objects.prefetch_related(
        'teams', 'teams__scores', 'teams__players', 'matches'
    ):
        matches_by_round = {}
        if tournament.game_type == '1v1':
            for match in tournament.matches.all().order_by('round_number', 'match_number'):
                matches_by_round.setdefault(match.round_number, []).append(match)
        tournaments_data.append({
            'tournament': tournament,
            'teams': tournament.teams.all(),
            'matches_by_round': matches_by_round,
        })

    casual_sessions = CasualGameSession.objects.select_related('game').order_by('-check_in_time')

    context = {
        'page_title': 'Results | ZIEGERS 2026-27',
        'tournaments_data': tournaments_data,
        'casual_sessions': casual_sessions,
    }
    return render(request, 'core/results.html', context)


def command_crew_page(request):
    """Render the ZIEGERS 2026-27 command crew leadership page."""
    # Tier metadata + grouped crew, bundled per section.
    tier_sections = [
        {
            'key': 'command',
            'label': 'COMMAND CORE',
            'icon': 'shield',
            'desc': 'The apex directory — final authority over every operation.',
            'members': [m for m in COMMAND_CREW if m['tier'] == 'command'],
        },
        {
            'key': 'heads',
            'label': 'PORTFOLIO HEADS',
            'icon': 'briefcase',
            'desc': 'Senior custodians of each investigation portfolio.',
            'members': [m for m in COMMAND_CREW if m['tier'] == 'heads'],
        },
        {
            'key': 'coheads',
            'label': 'DEPUTY UNIT — CO-HEADS',
            'icon': 'users',
            'desc': 'Support commanders bridging strategy and execution.',
            'members': [m for m in COMMAND_CREW if m['tier'] == 'coheads'],
        },
        {
            'key': 'committee',
            'label': 'FIELD COMMITTEE',
            'icon': 'shield-check',
            'desc': 'Frontline operatives holding the event together.',
            'members': [m for m in COMMAND_CREW if m['tier'] == 'committee'],
        },
    ]

    context = {
        'page_title': 'Command Crew | ZIEGERS 2026-27',
        'tier_sections': tier_sections,
    }
    return render(request, 'core/command_crew.html', context)
