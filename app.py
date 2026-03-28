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
}

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
    "Washburn": "washburnichabods.com",
    "Northwest Missouri State": "nwmobearcat.com",
    "Ferris State": "ferrissports.com",
    "Grand Valley State": "gvsulakers.com",
    "Duke": "goduke.com",
    "Kansas": "kuathletics.com",
    "Kentucky": "ukathletics.com",
    "Iowa": "hawkeyesports.com",
    "Ohio State": "ohiostatebuckeyes.com",
    "Michigan": "mgoblue.com",
    "Indiana": "iuhoosiers.com",
    "Purdue": "purduesports.com",
    "Wisconsin": "uwbadgers.com",
    "Michigan State": "msuspartans.com",
    "Illinois": "fightingillini.com",
    "Minnesota": "gophersports.com",
    "Northwestern": "nusports.com",
    "Nebraska": "huskers.com",
    "Penn State": "gopsusports.com",
    "Maryland": "umterps.com",
    "Rutgers": "scarletknights.com",
    "Gonzaga": "gozags.com",
    "Arizona": "arizonawildcats.com",
    "UCLA": "uclabruins.com",
    "USC": "usctrojans.com",
    "Oregon": "goducks.com",
    "Washington": "gohuskies.com",
    "Colorado": "cubuffs.com",
    "Utah": "utahutes.com",
    "Stanford": "gostanford.com",
    "Florida": "floridagators.com",
    "Florida State": "seminoles.com",
    "North Carolina": "tarheelblue.com",
    "Virginia": "virginiasports.com",
    "Virginia Tech": "hokiesports.com",
    "Syracuse": "suathletics.com",
    "Pittsburgh": "pittsburghpanthers.com",
    "Louisville": "gocards.com",
    "Notre Dame": "und.com",
    "Connecticut": "uconnhuskies.com",
    "Villanova": "villanovawildcats.com",
    "Creighton": "gocreighton.com",
    "Marquette": "muathletics.com",
    "Xavier": "goxavier.com",
    "Butler": "butlersports.com",
    "Houston": "uhcougars.com",
    "Baylor": "baylorbears.com",
    "Texas": "texassports.com",
    "Texas Tech": "texastech.com",
    "Kansas State": "kstatesports.com",
    "Iowa State": "cyclones.com",
    "West Virginia": "wvusports.com",
    "Tennessee": "utsports.com",
    "Alabama": "rolltide.com",
    "Auburn": "auburntigers.com",
    "LSU": "lsusports.net",
    "Georgia": "georgiadogs.com",
    "Mississippi State": "hailstate.com",
    "Ole Miss": "olemisssports.com",
    "Arkansas": "arkansasrazorbacks.com",
    "Missouri": "mutigers.com",
    "Vanderbilt": "vucommodores.com",
    "Texas A&M": "12thman.com",
    "BYU": "byucougars.com",
    "Dayton": "daytonflyers.com",
    "VCU": "vcuathletics.com",
    "Murray State": "goracers.com",
}

NAIA_SLUGS = {
    "Benedictine (KS)": "benedictineks",
    "College of Idaho": "collegeofidaho",
    "Cornerstone": "cornerstonemi",
    "Doane": "doanene",
    "Friends": "friendsks",
    "Georgetown (KY)": "georgetownky",
    "Grand View": "grandviewia",
    "Indiana Wesleyan": "indianawesleyan",
    "Keiser": "keiserfl",
    "Lewis-Clark State": "lewisclarkstate",
    "Life": "life",
    "Lindsey Wilson": "lindseywilson",
    "LSU-Alexandria": "lsua",
    "Marian (IN)": "marianian",
    "McKendree": "mckendree",
    "MidAmerica Nazarene": "midamericanazarene",
    "Mobile": "mobileal",
    "Morningside": "morningsideia",
    "Mount Mercy": "mountmercyia",
    "Northwestern (IA)": "northwesternia",
    "Oklahoma Wesleyan": "oklahomawesleyan",
    "Oregon Tech": "oregontech",
    "Our Lady of the Lake": "ollu",
    "Peru State": "perustate",
    "Rocky Mountain": "rockymountainmt",
    "Saint Ambrose": "saintambrose",
    "Science & Arts (OK)": "scienceartsok",
    "Siena Heights": "sienaheights",
    "Southern Oregon": "southernoregon",
    "Southwestern (KS)": "southwesternks",
    "Tabor": "taborks",
    "Taylor": "taylorin",
    "Thomas More (KY)": "thomasmorekentucky",
    "Trevecca Nazarene": "treveccanazarene",
    "Union (TN)": "uniontn",
    "Valley City State": "valleycitystate",
    "Viterbo": "viterbowi",
    "Wayland Baptist": "waylandbaptist",
    "William Penn": "williampenn",
}

NJCAA_SLUGS = {
    "Allen County CC": "allencountycc",
    "Barton County CC": "bartoncommunitycollege",
    "Blinn College": "blinncollege",
    "Butler CC": "butlercommunitycollegeks",
    "Casper College": "caspercollege",
    "Central Arizona": "centralarizonacollege",
    "Chipola College": "chipolacollege",
    "Cloud County CC": "cloudcountycommunitycollege",
    "Cochise College": "cochisecollege",
    "Coffeyville CC": "coffeyvillecommunitycollege",
    "College of Southern Idaho": "collegeofsouthernidaho",
    "Connors State": "connorsstatecollege",
    "Copiah-Lincoln CC": "copiahlincolncommunitycollege",
    "Cowley College": "cowleycountycommunitycollege",
    "Dodge City CC": "dodgecitycommunitycollege",
    "Eastern Arizona": "easternarizonacollege",
    "Garden City CC": "gardencitycommunitycollege",
    "Gulf Coast State": "gulfcoaststatecollege",
    "Hillsborough CC": "hillsboroughcommunitycollege",
    "Holmes CC": "holmescommunitycollege",
    "Howard College": "howardcollege",
    "Hutchinson CC": "hutchinsoncommunitycollege",
    "Independence CC": "independencecommunitycollege",
    "Indian Hills CC": "indianhillscommunitycollege",
    "John A. Logan College": "johnalogancollege",
    "Kilgore College": "kilgorecollege",
    "Lake Land College": "lakelandcollege",
    "Laramie County CC": "laramiecountycommunitycollege",
    "Meridian CC": "meridiancommunitycollege",
    "Moberly Area CC": "moberlyareacommunitycollege",
    "Murray State College": "murraystatecollege",
    "Navarro College": "navarrocollege",
    "New Mexico JC": "newmexicojuniorcollege",
    "North Idaho College": "northidahocollege",
    "Northeast Mississippi CC": "northeastmississippicommunitycollege",
    "Northeastern Oklahoma A&M": "northeasternoklahomaamcollege",
    "Northwest Mississippi CC": "northwestmississippicommunitycollege",
    "Odessa College": "odessacollege",
    "Panola College": "panolacollege",
    "Paris Junior College": "parisjuniorcollege",
    "Pensacola State": "pensacolastatecollege",
    "Pratt CC": "prattcommunitycollege",
    "Ranger College": "rangercollege",
    "Salt Lake CC": "saltlakecommunitycollege",
    "Seward County CC": "sewardcountycommunitycollege",
    "South Plains College": "southplainscollege",
    "Temple College": "templecollege",
    "Three Rivers College": "threeriverscommunitycollegemo",
    "Trinity Valley CC": "trinityvalleycommunitycollege",
    "Tyler Junior College": "tylerjuniorcollege",
    "Vincennes": "vincennesuniversity",
    "Wallace State CC": "wallacestatecommunitycollegehancevil",
    "Weatherford College": "weatherfordcollege",
    "Western Nebraska CC": "westernnebraskacommunitycollege",
    "Western Texas College": "westerntexascollege",
    "Yavapai College": "yavapaicollege",
}

def name_matches(row_text, player_name):
    """Require BOTH first AND last name in the row."""
    parts = player_name.lower().split()
    if len(parts) >= 2:
        return all(part in row_text for part in parts if len(part) > 1)
    return parts[0] in row_text if parts else False

def safe_float(cells, idx, default=0.0):
    try:
        if idx >= len(cells): return default
        val = cells[idx].get_text(strip=True).replace('%','').strip()
        if val in ['-', '', '--', 'N/A']: return default
        return float(val)
    except:
        return default

def pct(val):
    return round(val * 100, 1) if 0 < val <= 1.0 else round(val, 1)

def feet_inches_to_inches(text):
    """Convert height string like 6'3\" or 6-3 to inches."""
    try:
        text = text.strip().replace('"','').replace('\u2019',"'").replace('\u2018',"'")
        if "'" in text:
            parts = text.split("'")
            feet = int(parts[0].strip())
            inches = int(parts[1].strip()) if parts[1].strip() else 0
            return feet * 12 + inches
        if '-' in text and len(text) < 6:
            parts = text.split('-')
            return int(parts[0]) * 12 + int(parts[1])
    except:
        pass
    return None

def fetch_height_from_roster(domain, player_name):
    """Try to get player height from the school roster page."""
    urls = [
        f"https://{domain}/sports/mens-basketball/roster",
        f"https://{domain}/sports/mbkb/roster",
    ]
    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code != 200: continue
            soup = BeautifulSoup(resp.text, "html.parser")
            # Look for player name on roster page
            parts = player_name.lower().split()
            # Find all text blocks that contain the player name
            for tag in soup.find_all(['tr','div','li','article']):
                tag_text = tag.get_text(" ", strip=True).lower()
                if not name_matches(tag_text, player_name): continue
                # Look for height pattern in surrounding text
                full_text = tag.get_text(" ", strip=True)
                # Match patterns like 6'3", 6-3, 6 ft 3
                height_match = re.search(r"(\d)'(\d{1,2})", full_text)
                if height_match:
                    feet = int(height_match.group(1))
                    inches = int(height_match.group(2))
                    total = feet * 12 + inches
                    if 60 <= total <= 96:  # sanity check 5'0" to 8'0"
                        print(f"Height found: {feet}'{inches}\" = {total} inches")
                        return total
        except Exception as e:
            print(f"Height fetch error: {e}")
    return None

def parse_sidearm_page(html, player_name):
    """Parse Sidearm Sports stats page targeting the Player Averages table."""
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    averages_stats = None
    overall_tpa = 0.0
    overall_tov = 0.0

    for table in tables:
        headers = [th.get_text(strip=True).upper() for th in table.find_all("th")]
        headers_upper = " ".join(headers)
        is_averages = ("FG%" in headers_upper and "REB" in headers_upper and
                       "FGM" not in headers_upper and "FGA" not in headers_upper and
                       "PTS" in headers_upper)
        is_overall = ("FGM" in headers_upper and ("3PTA" in headers_upper or "3PA" in headers_upper))

        # Find column indices dynamically from headers
        tpa_col = next((i for i,h in enumerate(headers) if h in ["3PTA","3PA"]), None)
        to_col  = next((i for i,h in enumerate(headers) if h in ["TO","TOV","TURNOVERS","T/O"]), None)

        for row in table.find_all("tr"):
            row_text = row.get_text(" ", strip=True).lower()
            if not name_matches(row_text, player_name): continue
            cells = row.find_all("td")
            if len(cells) < 6: continue

            if is_averages and averages_stats is None:
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
                    print(f"Averages: GP={gp} PTS={pts} REB={reb} FG%={fgp} MIN={mins}")
                    averages_stats = {
                        "fgp": fgp, "tpa": 0.0, "tpp": tpp, "ftp": ftp,
                        "reb": round(reb,1), "pts": round(pts,1),
                        "ast": round(ast,1), "stl": round(stl,1),
                        "blk": round(blk,1), "tov": 0.0,
                        "min": round(mins,1), "games": int(gp)
                    }

            if is_overall and tpa_col is not None:
                gp2 = safe_float(cells, 2) or 1
                tpa_raw = safe_float(cells, tpa_col)
                to_raw  = safe_float(cells, to_col) if to_col else 0.0
                if tpa_raw > 0:
                    overall_tpa = round(tpa_raw / gp2, 1)
                    overall_tov = round(to_raw  / gp2, 1)
                    print(f"Overall: 3PA/G={overall_tpa} TO/G={overall_tov} (cols {tpa_col},{to_col})")

    if averages_stats:
        averages_stats["tpa"] = overall_tpa
        averages_stats["tov"] = overall_tov
        return averages_stats
    return None

def parse_presto_lineup(html, player_name):
    """Parse PrestoSports ?view=lineup page."""
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if not cells: continue
            if not name_matches(row.get_text(" ", strip=True).lower(), player_name): continue
            gp  = safe_float(cells, 1) or 1
            fgp = pct(safe_float(cells, 6))
            tpp = pct(safe_float(cells, 9))
            ftp = pct(safe_float(cells, 12))
            mins = round(safe_float(cells, 3) / gp, 1)
            tpa  = round(safe_float(cells, 8) / gp, 1)
            reb  = round(safe_float(cells, 15) / gp, 1)
            ast  = round(safe_float(cells, 17) / gp, 1)
            tov  = round(safe_float(cells, 18) / gp, 1)
            blk  = round(safe_float(cells, 19) / gp, 1)
            stl  = round(safe_float(cells, 20) / gp, 1)
            pts  = round(safe_float(cells, 21) / gp, 1)
            if pts == 0 and reb == 0: continue
            print(f"Presto: GP={gp} PTS={pts} REB={reb} FG%={fgp}")
            return {"fgp":fgp,"tpa":tpa,"tpp":tpp,"ftp":ftp,"reb":reb,"pts":pts,
                    "ast":ast,"stl":stl,"blk":blk,"tov":tov,"min":mins,"games":int(gp)}
    return None

def fetch_njcaa(player_name, school_name):
    slug = NJCAA_SLUGS.get(school_name)
    if not slug:
        sl = school_name.lower()
        for k,v in NJCAA_SLUGS.items():
            if k.lower() in sl or sl in k.lower(): slug=v; break
    if not slug: return None, None, "JUCO school not in database"
    for div in ["div1","div2","div3"]:
        url = f"https://njcaastats.prestosports.com/sports/mbkb/2024-25/{div}/teams/{slug}?view=lineup"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                s = parse_presto_lineup(r.text, player_name)
                if s: return s, None, None
        except Exception as e: print(f"NJCAA: {e}")
    return None, None, "Player not found on NJCAA stats"

def fetch_naia(player_name, school_name):
    slug = NAIA_SLUGS.get(school_name)
    if not slug:
        sl = school_name.lower().replace(" ","")
        for k,v in NAIA_SLUGS.items():
            if k.lower().replace(" ","") in sl or sl in k.lower().replace(" ",""): slug=v; break
    if not slug: return None, None, "NAIA school not in database"
    url = f"https://naiastats.prestosports.com/sports/mbkb/2024-25/teams/{slug}?view=lineup"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            s = parse_presto_lineup(r.text, player_name)
            if s: return s, None, None
    except Exception as e: print(f"NAIA: {e}")
    return None, None, "Player not found on NAIA stats"

def fetch_ncaa_school(player_name, school_name, season='2024-25'):
    domain = NCAA_DOMAINS.get(school_name)
    if not domain:
        for k,v in NCAA_DOMAINS.items():
            if school_name.lower() in k.lower() or k.lower() in school_name.lower():
                domain=v; break
    if not domain: return None, None, "School not in database — enter stats manually"

    # Try to fetch height from roster page simultaneously
    height_inches = fetch_height_from_roster(domain, player_name)

    season_url = f"https://{domain}/sports/mens-basketball/stats/{season}"
    fallback_url = f"https://{domain}/sports/mens-basketball/stats"

    # Try season-specific URL first
    for url in [season_url, fallback_url]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code == 200:
                s = parse_sidearm_page(r.text, player_name)
                if s:
                    # Verify we got the right season by checking games make sense
                    return s, height_inches, None
                elif url == season_url:
                    # Player not found in this specific season — stop here
                    return None, height_inches, f"{player_name} not found in {season} stats — they may not have played that season"
        except Exception as e:
            print(f"NCAA {url}: {e}")
            continue
    return None, height_inches, f"Could not load stats for {school_name} — enter manually"

@app.route("/roster", methods=["GET"])
def roster():
    school   = request.args.get("school","").strip()
    division = request.args.get("div","").strip().upper()
    season   = request.args.get("season","2024-25").strip()
    if not school:
        return jsonify({"error":"school required"}), 400

    domain = NCAA_DOMAINS.get(school)
    if not domain:
        for k,v in NCAA_DOMAINS.items():
            if school.lower() in k.lower() or k.lower() in school.lower():
                domain=v; break
    if not domain:
        return jsonify({"error":"School not in database — not supported yet","success":False}), 404

    for url in [
        f"https://{domain}/sports/mens-basketball/stats/{season}",
        f"https://{domain}/sports/mens-basketball/stats",
    ]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code == 200:
                players = parse_all_players(r.text)
                if players:
                    return jsonify({"success":True,"school":school,"players":players,"season":season})
        except Exception as e:
            print(f"Roster fetch error: {e}")

    return jsonify({"error":"Could not load roster","success":False}), 404

def parse_all_players(html):
    """Parse all players from a Sidearm averages table."""
    soup = BeautifulSoup(html, "html.parser")
    players = []
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True).upper() for th in table.find_all("th")]
        headers_str = " ".join(headers)
        is_averages = ("FG%" in headers_str and "REB" in headers_str and
                       "FGM" not in headers_str and "PTS" in headers_str)
        if not is_averages: continue
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) < 12: continue
            name_cell = cells[1].get_text(strip=True)
            if not name_cell or name_cell in ['Total','Opponents','Team']: continue
            # Clean name - remove jersey number prefix if present
            name = re.sub(r'^\d+\s*', '', name_cell).strip()
            if not name or len(name) < 3: continue
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
                if mins < 5 or gp < 3: continue  # skip walk-ons / minimal players
                players.append({
                    "name": name, "games": int(gp),
                    "fgp": fgp, "tpa": 0.0, "tpp": tpp, "ftp": ftp,
                    "reb": round(reb,1), "pts": round(pts,1),
                    "ast": round(ast,1), "stl": round(stl,1),
                    "blk": round(blk,1), "tov": 0.0,
                    "min": round(mins,1), "height": 72
                })
            except: continue
        if players: break
    # Sort by minutes per game descending
    return sorted(players, key=lambda x: x['min'], reverse=True)

@app.route("/search", methods=["GET"])
def search():
    player   = request.args.get("player","").strip()
    school   = request.args.get("school","").strip()
    division = request.args.get("div","").strip().upper()
    if not player or not school:
        return jsonify({"error":"player and school required"}), 400
    season = request.args.get("season", "2024-25").strip()
    if division == "JUCO":
        stats, height, error = fetch_njcaa(player, school)
    elif division == "NAIA":
        stats, height, error = fetch_naia(player, school)
    else:
        stats, height, error = fetch_ncaa_school(player, school, season)
    if not stats:
        return jsonify({"error":error or "Player not found","player":player,
                        "school":school,"manual_entry":True,"height":height}), 404
    return jsonify({"success":True,"player":player,"school":school,
                    "stats":stats,"height":height})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status":"ok","message":"TransferIQ backend running"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
