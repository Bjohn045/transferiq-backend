from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ─── D1 ESPN TEAM IDs ─────────────────────────────────────────────────────────
ESPN_IDS = {
    "Duke": "150", "Kansas": "2305", "Kentucky": "96", "Iowa": "2294",
    "Ohio State": "194", "Michigan": "130", "Indiana": "84", "Purdue": "2509",
    "Wisconsin": "275", "Michigan State": "127", "Illinois": "356",
    "Minnesota": "135", "Northwestern": "77", "Nebraska": "158",
    "Penn State": "213", "Maryland": "97", "Rutgers": "164",
    "Gonzaga": "2250", "Arizona": "12", "UCLA": "26", "USC": "30",
    "Oregon": "2483", "Washington": "264", "Colorado": "38", "Utah": "254",
    "Stanford": "24", "Florida": "57", "Florida State": "52",
    "North Carolina": "153", "Virginia": "258", "Virginia Tech": "259",
    "Syracuse": "183", "Pittsburgh": "221", "Louisville": "97",
    "Notre Dame": "87", "Connecticut": "41", "Villanova": "222",
    "Creighton": "156", "Marquette": "269", "Xavier": "2752",
    "Butler": "2086", "Houston": "248", "Baylor": "239", "Texas": "251",
    "Texas Tech": "2641", "Kansas State": "2306", "Iowa State": "66",
    "West Virginia": "277", "Tennessee": "2633", "Alabama": "333",
    "Auburn": "2", "LSU": "99", "Georgia": "61", "Mississippi State": "344",
    "Ole Miss": "145", "Arkansas": "8", "Missouri": "142",
    "Vanderbilt": "238", "Texas A&M": "245", "BYU": "252",
    "Dayton": "2065", "VCU": "2670", "Murray State": "93",
}

# ─── D2/D3 School domains ──────────────────────────────────────────────────────
NCAA_DOMAINS = {
    "Baldwin Wallace": "bwyellowjackets.com",
    "Wisconsin-Platteville": "letsgopioneers.com",
    "Mount Union": "athletics.mountunion.edu",
    "Otterbein": "otterbeinathletics.com",
    "Ohio Northern": "athletics.onu.edu",
    "Muskingum": "athletics.muskingum.edu",
    "Marietta": "gomarietta.com",
    "Heidelberg": "heidelbergstudentathletics.com",
    "John Carroll": "jcusports.com",
    "Capital": "capitalcrusaders.com",
    "Wilmington (OH)": "wilmingtonathletics.com",
    "Kenyon": "kenyonlords.com",
    "Ohio Wesleyan": "owuathletics.com",
    "Emory": "emoryeagles.com",
    "Wheaton (IL)": "wheatoncollegeathletics.com",
    "Calvin": "calvinknight.com",
    "Illinois Wesleyan": "iwuathletics.com",
    "Virginia Wesleyan": "vwcmarlins.com",
    "Hood": "hoodathletics.com",
    "Wisconsin-La Crosse": "uwlathletics.com",
    "Washburn": "washburnichabods.com",
    "Northwest Missouri State": "nwmobearcat.com",
    "Ferris State": "ferrissports.com",
    "Grand Valley State": "gvsulakers.com",
    "Nova Southeastern": "nsusharks.com",
    "Augustana (SD)": "goaugie.com",
    "Michigan Tech": "michigantechathletics.com",
    "Gannon": "gannonknight.com",
    "Black Hills State": "yellowjacketathletics.com",
    "Bluffton": "blufftonbeavers.com",
    "Chatham": "chathamathletics.com",
    "Hiram": "hiramsportes.com",
    "Trine": "trineathletics.com",
    "Wittenberg": "wittenbergathletics.com",
    "Pitt.-Greensburg": "pittgreensburgathletics.com",
    "Dordt": "godordt.com",
    "Duke": "goduke.com",
    "Arkansas": "arkansasrazorbacks.com",
    "BYU": "byucougars.com",
    "Michigan": "mgoblue.com",
    "Purdue": "purduesports.com",
}

# ─── NAIA slugs ───────────────────────────────────────────────────────────────
NAIA_SLUGS = {
    "Benedictine (KS)": "benedictineks", "College of Idaho": "collegeofidaho",
    "Cornerstone": "cornerstonemi", "Doane": "doanene", "Friends": "friendsks",
    "Georgetown (KY)": "georgetownky", "Grand View": "grandviewia",
    "Indiana Wesleyan": "indianawesleyan", "Keiser": "keiserfl",
    "Lewis-Clark State": "lewisclarkstate", "Life": "life",
    "Lindsey Wilson": "lindseywilson", "LSU-Alexandria": "lsua",
    "Marian (IN)": "marianian", "McKendree": "mckendree",
    "MidAmerica Nazarene": "midamericanazarene", "Mobile": "mobileal",
    "Morningside": "morningsideia", "Mount Mercy": "mountmercyia",
    "Northwestern (IA)": "northwesternia", "Oklahoma Wesleyan": "oklahomawesleyan",
    "Oregon Tech": "oregontech", "Our Lady of the Lake": "ollu",
    "Peru State": "perustate", "Rocky Mountain": "rockymountainmt",
    "Saint Ambrose": "saintambrose", "Science & Arts (OK)": "scienceartsok",
    "Siena Heights": "sienaheights", "Southern Oregon": "southernoregon",
    "Southwestern (KS)": "southwesternks", "Tabor": "taborks",
    "Taylor": "taylorin", "Thomas More (KY)": "thomasmorekentucky",
    "Trevecca Nazarene": "treveccanazarene", "Union (TN)": "uniontn",
    "Valley City State": "valleycitystate", "Viterbo": "viterbowi",
    "Wayland Baptist": "waylandbaptist", "William Penn": "williampenn",
}

# ─── NJCAA slugs ──────────────────────────────────────────────────────────────
NJCAA_SLUGS = {
    "Allen County CC": "allencountycc", "Barton County CC": "bartoncommunitycollege",
    "Blinn College": "blinncollege", "Butler CC": "butlercommunitycollegeks",
    "Casper College": "caspercollege", "Central Arizona": "centralarizonacollege",
    "Chipola College": "chipolacollege", "Cloud County CC": "cloudcountycommunitycollege",
    "Cochise College": "cochisecollege", "Coffeyville CC": "coffeyvillecommunitycollege",
    "College of Southern Idaho": "collegeofsouthernidaho",
    "Connors State": "connorsstatecollege",
    "Copiah-Lincoln CC": "copiahlincolncommunitycollege",
    "Cowley College": "cowleycountycommunitycollege",
    "Dodge City CC": "dodgecitycommunitycollege",
    "Eastern Arizona": "easternarizonacollege",
    "Garden City CC": "gardencitycommunitycollege",
    "Gulf Coast State": "gulfcoaststatecollege",
    "Hillsborough CC": "hillsboroughcommunitycollege",
    "Holmes CC": "holmescommunitycollege", "Howard College": "howardcollege",
    "Hutchinson CC": "hutchinsoncommunitycollege",
    "Independence CC": "independencecommunitycollege",
    "Indian Hills CC": "indianhillscommunitycollege",
    "John A. Logan College": "johnalogancollege", "Kilgore College": "kilgorecollege",
    "Lake Land College": "lakelandcollege",
    "Laramie County CC": "laramiecountycommunitycollege",
    "Meridian CC": "meridiancommunitycollege",
    "Moberly Area CC": "moberlyareacommunitycollege",
    "Murray State College": "murraystatecollege", "Navarro College": "navarrocollege",
    "New Mexico JC": "newmexicojuniorcollege", "North Idaho College": "northidahocollege",
    "Northeast Mississippi CC": "northeastmississippicommunitycollege",
    "Northeastern Oklahoma A&M": "northeasternoklahomaamcollege",
    "Northwest Mississippi CC": "northwestmississippicommunitycollege",
    "Odessa College": "odessacollege", "Panola College": "panolacollege",
    "Paris Junior College": "parisjuniorcollege",
    "Pensacola State": "pensacolastatecollege", "Pratt CC": "prattcommunitycollege",
    "Ranger College": "rangercollege", "Salt Lake CC": "saltlakecommunitycollege",
    "Seward County CC": "sewardcountycommunitycollege",
    "South Plains College": "southplainscollege", "Temple College": "templecollege",
    "Three Rivers College": "threeriverscommunitycollegemo",
    "Trinity Valley CC": "trinityvalleycommunitycollege",
    "Tyler Junior College": "tylerjuniorcollege", "Vincennes": "vincennesuniversity",
    "Wallace State CC": "wallacestatecommunitycollegehancevil",
    "Weatherford College": "weatherfordcollege",
    "Western Nebraska CC": "westernnebraskacommunitycollege",
    "Western Texas College": "westerntexascollege", "Yavapai College": "yavapaicollege",
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def name_matches(text, player_name):
    parts = player_name.lower().split()
    return all(p in text.lower() for p in parts if len(p) > 1)

def safe_float(cells, idx, default=0.0):
    try:
        if idx >= len(cells): return default
        val = cells[idx].get_text(strip=True).replace('%','').strip()
        if val in ['-','','--','N/A']: return default
        return float(val)
    except:
        return default

def pct(val):
    return round(val * 100, 1) if 0 < val <= 1.0 else round(val, 1)

def parse_height(text):
    """Convert any height format to inches."""
    if not text: return None
    text = str(text).strip().replace('"','').replace('\u2019',"'").replace('\u2018',"'")
    m = re.search(r"(\d)['\u2019](\d{1,2})", text)
    if m:
        h = int(m.group(1)) * 12 + int(m.group(2))
        if 60 <= h <= 96: return h
    m = re.search(r'\b([5-7])-(\d{1,2})\b', text)
    if m:
        h = int(m.group(1)) * 12 + int(m.group(2))
        if 60 <= h <= 96: return h
    return None

def detect_platform(html):
    """Detect Sidearm vs PrestoSports from page footer."""
    lower = html.lower()
    if 'sidearmsports.com' in lower or '"sidearm"' in lower or 'sidearm sports' in lower:
        return 'sidearm'
    if 'prestosports.com' in lower or 'presto sports' in lower:
        return 'presto'
    return 'unknown'

def dedup(seq):
    seen = set()
    return [x for x in seq if not (x in seen or seen.add(x))]

# ─── ESPN D1 FETCHER ──────────────────────────────────────────────────────────
def fetch_espn_stats(player_name, school_name, season):
    """Fetch D1 player stats via ESPN hidden API."""
    espn_id = ESPN_IDS.get(school_name)
    if not espn_id:
        for k, v in ESPN_IDS.items():
            if school_name.lower() in k.lower() or k.lower() in school_name.lower():
                espn_id = v; break
    if not espn_id:
        return None, None, f"School not in ESPN database"

    try:
        # Get team roster with player IDs and heights
        roster_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/teams/{espn_id}/roster"
        resp = requests.get(roster_url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return None, None, f"ESPN roster unavailable (status {resp.status_code})"

        data = resp.json()
        # Roster response has 'athletes' array
        athletes = data.get('athletes', [])
        # Sometimes nested under position groups
        if not athletes:
            for group in data.get('coach', []):
                athletes.extend(group.get('athletes', []))

        player_id = None
        height_inches = None

        for athlete in athletes:
            full_name = athlete.get('fullName', '')
            if name_matches(full_name, player_name) or name_matches(player_name, full_name):
                player_id = str(athlete.get('id', ''))
                # ESPN height comes as display string like "6'5\""
                ht_display = athlete.get('displayHeight', '')
                if ht_display:
                    height_inches = parse_height(ht_display)
                # Also try numeric height in inches
                if not height_inches:
                    ht = athlete.get('height')
                    if ht:
                        try: height_inches = int(round(float(ht)))
                        except: pass
                break

        if not player_id:
            return None, None, f"Player '{player_name}' not found on ESPN roster"

        # Get player season statistics
        stats_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/athletes/{player_id}/statistics/0"
        sresp = requests.get(stats_url, headers=HEADERS, timeout=10)
        if sresp.status_code != 200:
            # Try without the /0
            stats_url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/athletes/{player_id}/statistics"
            sresp = requests.get(stats_url, headers=HEADERS, timeout=10)
        if sresp.status_code != 200:
            return None, height_inches, "ESPN stats unavailable"

        sdata = sresp.json()
        cats = sdata.get('splits', {}).get('categories', [])
        raw = {}
        for cat in cats:
            for stat in cat.get('stats', []):
                raw[stat.get('name', '')] = stat.get('value', 0)

        gp = max(int(raw.get('gamesPlayed', 1)), 1)

        result = {
            'games': gp,
            'fgp':  round(raw.get('fieldGoalPct', 0) * 100, 1),
            'tpa':  round(raw.get('threePointFieldGoalsAttempted', 0) / gp, 1),
            'tpp':  round(raw.get('threePointFieldGoalPct', 0) * 100, 1),
            'ftp':  round(raw.get('freeThrowPct', 0) * 100, 1),
            'pts':  round(raw.get('points', 0) / gp, 1),
            'reb':  round(raw.get('totalRebounds', 0) / gp, 1),
            'ast':  round(raw.get('assists', 0) / gp, 1),
            'stl':  round(raw.get('steals', 0) / gp, 1),
            'blk':  round(raw.get('blocks', 0) / gp, 1),
            'tov':  round(raw.get('turnovers', 0) / gp, 1),
            'min':  round(raw.get('minutesPerGame', 0), 1),
        }
        print(f"ESPN: {player_name} GP={gp} PTS={result['pts']} REB={result['reb']} TO/G={result['tov']}")
        return result, height_inches, None

    except Exception as e:
        return None, None, f"ESPN error: {e}"

# ─── HEIGHT FETCHER (Sidearm roster page) ─────────────────────────────────────
def fetch_height_from_roster(domain, player_name):
    """
    Fetch player height from school roster page.
    Works for both Sidearm and most other platforms.
    Tries multiple URL patterns.
    """
    urls = [
        f"https://{domain}/sports/mens-basketball/roster",
        f"https://{domain}/sports/mbkb/roster",
        f"https://{domain}/sports/mens-basketball/roster.aspx",
    ]
    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200: continue
            soup = BeautifulSoup(resp.text, 'html.parser')

            # Try structured blocks first (Sidearm uses li/article per player)
            for block in soup.find_all(['li','article','div'], class_=re.compile(r'roster|player|athlete', re.I)):
                block_text = block.get_text(' ', strip=True)
                if not name_matches(block_text, player_name): continue
                h = parse_height(block_text)
                if h:
                    print(f"Height found (block): {h} for {player_name}")
                    return h

            # Fallback: scan all rows/cells
            for tag in soup.find_all(['tr','td','span','div','p','li']):
                tag_text = tag.get_text(' ', strip=True)
                if not name_matches(tag_text, player_name): continue
                h = parse_height(tag_text)
                if h:
                    print(f"Height found (fallback): {h} for {player_name}")
                    return h

        except Exception as e:
            print(f"Height fetch error ({url}): {e}")
    return None

# ─── SIDEARM PARSER ───────────────────────────────────────────────────────────
def parse_sidearm(html, player_name):
    """
    Parse a Sidearm Sports stats page.
    Sidearm is consistent: averages table + overall totals table.
    We get per-game stats from averages, and 3PA/TO from overall totals.
    """
    soup = BeautifulSoup(html, 'html.parser')
    averages_stats = None
    overall_tpa = 0.0
    overall_tov = 0.0

    for table in soup.find_all('table'):
        headers = [th.get_text(strip=True).upper() for th in table.find_all('th')]
        h_str = ' '.join(headers)

        is_avg = 'FG%' in h_str and 'REB' in h_str and 'FGM' not in h_str and 'PTS' in h_str
        is_overall = 'FGM' in h_str and ('3PTA' in h_str or '3PA' in h_str)

        tpa_col = next((i for i, h in enumerate(headers) if h in ['3PTA', '3PA']), None)
        to_col  = next((i for i, h in enumerate(headers) if h in ['TO', 'TOV', 'TURNOVERS', 'T/O', 'TURN']), None)

        for row in table.find_all('tr'):
            row_text = row.get_text(' ', strip=True).lower()
            if not name_matches(row_text, player_name): continue
            cells = row.find_all('td')
            if len(cells) < 6: continue

            if is_avg and averages_stats is None:
                gp   = safe_float(cells, 2) or 1
                mins = safe_float(cells, 3)
                fgp  = pct(safe_float(cells, 4))
                tpp  = pct(safe_float(cells, 5))
                ftp  = pct(safe_float(cells, 6))
                reb  = safe_float(cells, 9)
                ast  = safe_float(cells, 10)
                stl  = safe_float(cells, 11)
                blk  = safe_float(cells, 12)
                pts  = safe_float(cells, 13)
                if pts > 0 or reb > 0:
                    print(f"Sidearm avg row: GP={gp} PTS={pts} REB={reb} FG%={fgp} MIN={mins}")
                    averages_stats = {
                        'games': int(gp), 'fgp': fgp, 'tpa': 0.0, 'tpp': tpp,
                        'ftp': ftp, 'reb': round(reb,1), 'pts': round(pts,1),
                        'ast': round(ast,1), 'stl': round(stl,1),
                        'blk': round(blk,1), 'tov': 0.0, 'min': round(mins,1)
                    }

            if is_overall:
                gp2 = safe_float(cells, 2) or 1
                tpa_raw = safe_float(cells, tpa_col) if tpa_col is not None else 0.0
                to_raw  = safe_float(cells, to_col)  if to_col  is not None else 0.0

                # If TO not found via header, scan last 10 columns for total TOs
                if to_raw == 0:
                    gp2_int = max(int(gp2), 1)
                    for ci in range(max(0, len(cells)-10), len(cells)):
                        v = safe_float(cells, ci)
                        # Plausible season total TOs: integer, between 5 and 8 per game
                        if 5 <= v <= gp2_int * 8 and abs(v - round(v)) < 0.01:
                            to_raw = v
                            print(f"TO total found at col {ci}: {v} -> {round(v/gp2,2)}/game")
                            break

                if tpa_raw > 0 or to_raw > 0:
                    overall_tpa = round(tpa_raw / gp2, 1)
                    overall_tov = round(to_raw  / gp2, 1)
                    print(f"Sidearm overall: 3PA/G={overall_tpa} TO/G={overall_tov}")

    if averages_stats:
        averages_stats['tpa'] = overall_tpa
        averages_stats['tov'] = overall_tov
        return averages_stats
    return None

# ─── PRESTOSPORTS PARSER ──────────────────────────────────────────────────────
def parse_presto(html, player_name):
    """
    Parse a PrestoSports stats page.
    Used for NAIA (naiastats.prestosports.com) and NJCAA (njcaastats.prestosports.com)
    and any D2/D3 school that uses PrestoSports.
    PrestoSports column order is consistent across ALL schools on the platform.
    """
    soup = BeautifulSoup(html, 'html.parser')

    for table in soup.find_all('table'):
        headers = [th.get_text(strip=True).upper() for th in table.find_all('th')]
        h_str = ' '.join(headers)
        if 'FG%' not in h_str or 'PTS' not in h_str: continue

        # Build a column index map from headers
        col = {}
        for i, h in enumerate(headers):
            col[h] = i

        for row in table.find_all('tr'):
            row_text = row.get_text(' ', strip=True)
            if not name_matches(row_text, player_name): continue
            cells = row.find_all('td')
            if len(cells) < 8: continue

            try:
                # Use header-based column lookup where possible
                def get(key, fallback_idx, divide_by_gp=False):
                    idx = col.get(key, fallback_idx)
                    val = safe_float(cells, idx)
                    return round(val / gp, 1) if divide_by_gp and val > gp else round(val, 1)

                gp = max(safe_float(cells, col.get('GP', 1)), 1)

                # PrestoSports standard layout
                mins_total = safe_float(cells, col.get('MIN', 3))
                mins = round(mins_total / gp, 1) if mins_total > 100 else round(mins_total, 1)

                fgp = pct(safe_float(cells, col.get('FG%', 6)))
                tpa_total = safe_float(cells, col.get('3PA', 8))
                tpa = round(tpa_total / gp, 1)
                tpp = pct(safe_float(cells, col.get('3P%', 9)))
                ftp = pct(safe_float(cells, col.get('FT%', 12)))
                reb = safe_float(cells, col.get('REB', 15))
                ast = safe_float(cells, col.get('AST', 16))
                to_total = safe_float(cells, col.get('TO', col.get('TOV', 17)))
                tov = round(to_total / gp, 1) if to_total > gp else round(to_total, 1)
                stl = safe_float(cells, col.get('STL', 18))
                blk = safe_float(cells, col.get('BLK', 19))
                pts = safe_float(cells, col.get('PTS', 20))

                if pts <= 0 and fgp <= 0: continue

                print(f"Presto: GP={gp} PTS={pts} REB={reb} TO/G={tov} 3PA/G={tpa}")
                return {
                    'games': int(gp), 'fgp': fgp, 'tpa': tpa, 'tpp': tpp,
                    'ftp': ftp, 'reb': round(reb,1), 'pts': round(pts,1),
                    'ast': round(ast,1), 'stl': round(stl,1),
                    'blk': round(blk,1), 'tov': tov, 'min': mins
                }
            except Exception as e:
                print(f"Presto parse error: {e}")
                continue
    return None

# ─── MAIN /search ENDPOINT ────────────────────────────────────────────────────
@app.route('/search', methods=['GET'])
def search():
    player   = request.args.get('player', '').strip()
    school   = request.args.get('school', '').strip()
    division = request.args.get('div',    '').strip().upper()
    season   = request.args.get('season', '2025-26').strip()

    if not player or not school:
        return jsonify({'error': 'player and school required'}), 400

    print(f"\n=== SEARCH: {player} @ {school} [{division}] {season} ===")

    # ── 1. D1 → ESPN API ──────────────────────────────────────────────────────
    if division == 'D1':
        stats, height, err = fetch_espn_stats(player, school, season)
        if stats:
            return jsonify({'success': True, 'stats': stats, 'height': height, 'source': 'espn'})
        print(f"ESPN failed ({err}), falling through to school site")
        # Fall through — some D1 schools might not be in ESPN_IDS yet

    # ── 2. NAIA → PrestoSports central site ───────────────────────────────────
    if division == 'NAIA':
        slug = NAIA_SLUGS.get(school)
        if not slug:
            for k, v in NAIA_SLUGS.items():
                if school.lower() in k.lower() or k.lower() in school.lower():
                    slug = v; break
        if slug:
            for s in dedup([season, '2025-26', '2024-25']):
                url = f"https://naiastats.prestosports.com/sports/mbkb/{s}/teams/{slug}/players"
                try:
                    resp = requests.get(url, headers=HEADERS, timeout=10)
                    if resp.status_code == 200:
                        stats = parse_presto(resp.text, player)
                        if stats:
                            return jsonify({'success': True, 'stats': stats, 'height': None, 'source': 'presto_naia'})
                except Exception as e:
                    print(f"NAIA error: {e}")
        # If slug not found or presto failed, fall through to domain-based lookup

    # ── 3. NJCAA → PrestoSports central site ──────────────────────────────────
    if division in ['JUCO', 'NJCAA']:
        slug = NJCAA_SLUGS.get(school)
        if not slug:
            for k, v in NJCAA_SLUGS.items():
                if school.lower() in k.lower() or k.lower() in school.lower():
                    slug = v; break
        if slug:
            for s in dedup([season, '2025-26', '2024-25']):
                url = f"https://njcaastats.prestosports.com/sports/mbkb/{s}/teams/{slug}/players"
                try:
                    resp = requests.get(url, headers=HEADERS, timeout=10)
                    if resp.status_code == 200:
                        stats = parse_presto(resp.text, player)
                        if stats:
                            return jsonify({'success': True, 'stats': stats, 'height': None, 'source': 'presto_njcaa'})
                except Exception as e:
                    print(f"NJCAA error: {e}")
            return jsonify({'success': False, 'error': f"Could not find {player} on NJCAA stats"}), 404

    # ── 4. D2/D3/NAIA via school domain — auto-detect Sidearm or PrestoSports ─
    domain = NCAA_DOMAINS.get(school)
    if not domain:
        for k, v in NCAA_DOMAINS.items():
            if school.lower() in k.lower() or k.lower() in school.lower():
                domain = v; break

    if not domain:
        return jsonify({'success': False, 'error': f"School '{school}' not in database yet. Contact support to add it."}), 404

    for s in dedup([season, '2025-26', '2024-25']):
        for url in [
            f"https://{domain}/sports/mens-basketball/stats/{s}",
            f"https://{domain}/sports/mens-basketball/stats",
            f"https://{domain}/sports/mbkb/stats/{s}",
            f"https://{domain}/sports/mbkb/stats",
        ]:
            try:
                resp = requests.get(url, headers=HEADERS, timeout=12)
                if resp.status_code != 200: continue

                platform = detect_platform(resp.text)
                print(f"URL: {url} | Platform: {platform}")

                # Try platform-specific parser, then fall back to the other
                stats = None
                if platform == 'sidearm':
                    stats = parse_sidearm(resp.text, player)
                    if not stats: stats = parse_presto(resp.text, player)
                elif platform == 'presto':
                    stats = parse_presto(resp.text, player)
                    if not stats: stats = parse_sidearm(resp.text, player)
                else:
                    # Unknown — try both
                    stats = parse_sidearm(resp.text, player)
                    if not stats: stats = parse_presto(resp.text, player)

                if stats:
                    height = fetch_height_from_roster(domain, player)
                    return jsonify({'success': True, 'stats': stats, 'height': height, 'source': platform})

            except Exception as e:
                print(f"Error {url}: {e}")
                continue

    return jsonify({'success': False, 'error': f"Could not find stats for {player} at {school}. Stats may not be posted yet."}), 404


# ─── /roster ENDPOINT ─────────────────────────────────────────────────────────
@app.route('/roster', methods=['GET'])
def roster():
    school  = request.args.get('school', '').strip()
    season  = request.args.get('season', '2025-26').strip()

    if not school:
        return jsonify({'error': 'school required'}), 400

    domain = NCAA_DOMAINS.get(school)
    if not domain:
        for k, v in NCAA_DOMAINS.items():
            if school.lower() in k.lower() or k.lower() in school.lower():
                domain = v; break
    if not domain:
        return jsonify({'success': False, 'error': f"School '{school}' not in database yet"}), 404

    for s in dedup([season, '2025-26', '2024-25']):
        for url in [
            f"https://{domain}/sports/mens-basketball/stats/{s}",
            f"https://{domain}/sports/mens-basketball/stats",
        ]:
            try:
                resp = requests.get(url, headers=HEADERS, timeout=12)
                if resp.status_code != 200: continue
                platform = detect_platform(resp.text)
                players = parse_roster(resp.text, platform)
                if players:
                    return jsonify({'success': True, 'school': school, 'players': players, 'season': s, 'platform': platform})
            except Exception as e:
                print(f"Roster error: {e}")

    return jsonify({'success': False, 'error': f"Could not load roster for {school}"}), 404


def parse_roster(html, platform):
    """Parse all players from a stats page for the roster view."""
    soup = BeautifulSoup(html, 'html.parser')
    players = []
    overall_data = {}  # name -> {tpa, tov}

    # First pass: get totals from overall table for 3PA and TO
    for table in soup.find_all('table'):
        headers = [th.get_text(strip=True).upper() for th in table.find_all('th')]
        h_str = ' '.join(headers)
        is_overall = 'FGM' in h_str and ('3PTA' in h_str or '3PA' in h_str)
        if not is_overall: continue

        tpa_col = next((i for i,h in enumerate(headers) if h in ['3PTA','3PA']), None)
        to_col  = next((i for i,h in enumerate(headers) if h in ['TO','TOV','TURNOVERS','T/O']), None)

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) < 8: continue
            name_raw = cells[1].get_text(strip=True) if len(cells) > 1 else ''
            name = re.sub(r'^\d+\s*', '', name_raw).strip()
            dup_match2 = re.match(r'^(.+?)\d+$', name)
            if dup_match2: name = dup_match2.group(1).strip()
            if ',' in name:
                parts = name.split(',', 1)
                name = parts[1].strip() + ' ' + parts[0].strip()
            if not name or len(name) < 3: continue
            gp = safe_float(cells, 2) or 1
            tpa_raw = safe_float(cells, tpa_col) if tpa_col else 0
            to_raw = safe_float(cells, to_col) if to_col else 0
            # Scan for TO if not found
            if to_raw == 0:
                for ci in range(max(0, len(cells)-10), len(cells)):
                    v = safe_float(cells, ci)
                    if 5 <= v <= gp * 8 and abs(v - round(v)) < 0.01:
                        to_raw = v; break
            overall_data[name.lower()] = {
                'tpa': round(tpa_raw/gp, 1),
                'tov': round(to_raw/gp, 1)
            }
        break

    # Second pass: get per-game stats from averages table
    for table in soup.find_all('table'):
        headers = [th.get_text(strip=True).upper() for th in table.find_all('th')]
        h_str = ' '.join(headers)
        is_avg = 'FG%' in h_str and 'REB' in h_str and 'FGM' not in h_str and 'PTS' in h_str
        if not is_avg: continue

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) < 8: continue
            name_raw = cells[1].get_text(strip=True) if len(cells) > 1 else ''
            name = re.sub(r'^\d+\s*', '', name_raw).strip()
            # Fix duplicate: "Richardson, Isaac23Richardson, Isaac" -> "Isaac Richardson"
            dup = re.match(r'^(.+?)\d+\1$', name)
            if dup: name = dup.group(1).strip()
            # Convert "Last, First" to "First Last"
            if ',' in name:
                parts = name.split(',', 1)
                name = parts[1].strip() + ' ' + parts[0].strip()
            if not name or name in ['Total','Opponents','Team'] or len(name) < 3: continue
            try:
                gp   = safe_float(cells, 2) or 1
                mins = safe_float(cells, 3)
                fgp  = pct(safe_float(cells, 4))
                tpp  = pct(safe_float(cells, 5))
                ftp  = pct(safe_float(cells, 6))
                reb  = safe_float(cells, 9)
                ast  = safe_float(cells, 10)
                stl  = safe_float(cells, 11)
                blk  = safe_float(cells, 12)
                pts  = safe_float(cells, 13)
                if mins < 5 or gp < 3: continue
                extra = overall_data.get(name.lower(), {'tpa': 0.0, 'tov': 0.0})
                players.append({
                    'name': name, 'games': int(gp),
                    'fgp': fgp, 'tpa': extra['tpa'], 'tpp': tpp, 'ftp': ftp,
                    'reb': round(reb,1), 'pts': round(pts,1),
                    'ast': round(ast,1), 'stl': round(stl,1),
                    'blk': round(blk,1), 'tov': extra['tov'],
                    'min': round(mins,1), 'height': 72
                })
            except:
                continue
        if players: break

    return sorted(players, key=lambda x: x['min'], reverse=True)


# ─── HEALTH CHECK ─────────────────────────────────────────────────────────────
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'version': '3.0', 'systems': ['espn_d1', 'sidearm', 'presto_naia', 'presto_njcaa']})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
