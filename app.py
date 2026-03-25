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

# ─── SCHOOL DOMAIN LOOKUP (NCAA D1/D2/D3) ────────────────────────────────────
# Format: "School Name": "domain.com"
NCAA_DOMAINS = {
    # D3 Ohio Athletic Conference (most relevant for BW)
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
    # D1 major programs
    "Gonzaga": "gozags.com",
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
    "Arizona": "arizonawildcats.com",
    "Arizona State": "thesundevils.com",
    "UCLA": "uclabruins.com",
    "USC": "usctrojans.com",
    "Oregon": "goducks.com",
    "Washington": "gohuskies.com",
    "Colorado": "cubuffs.com",
    "Utah": "utahutes.com",
    "Stanford": "gostanford.com",
    "California": "calbears.com",
    "Florida": "floridagators.com",
    "Florida State": "seminoles.com",
    "Miami (FL)": "hurricanesports.com",
    "North Carolina": "tarheelblue.com",
    "Duke": "goduke.com",
    "NC State": "gopack.com",
    "Virginia": "virginiasports.com",
    "Virginia Tech": "hokiesports.com",
    "Syracuse": "suathletics.com",
    "Pittsburgh": "pittsburghpanthers.com",
    "Louisville": "gocards.com",
    "Clemson": "clemsontigers.com",
    "Wake Forest": "wakeforestsports.com",
    "Georgia Tech": "ramblinwreck.com",
    "Notre Dame": "und.com",
    "Connecticut": "uconnhuskies.com",
    "Villanova": "villanovawildcats.com",
    "Creighton": "gocreighton.com",
    "Marquette": "muathletics.com",
    "Xavier": "goxavier.com",
    "Providence": "friars.com",
    "Seton Hall": "shupirates.com",
    "St. John's": "redstormsports.com",
    "Georgetown": "guhoyas.com",
    "DePaul": "depaulbluedemons.com",
    "Butler": "butlersports.com",
    "Houston": "uhcougars.com",
    "Baylor": "baylorbears.com",
    "Texas": "texassports.com",
    "Texas Tech": "texastech.com",
    "TCU": "gofrogs.com",
    "Oklahoma": "soonersports.com",
    "Oklahoma State": "okstate.com",
    "Kansas State": "kstatesports.com",
    "Iowa State": "cyclones.com",
    "West Virginia": "wvusports.com",
    "Cincinnati": "gobearcats.com",
    "UCF": "ucfknights.com",
    "South Florida": "gousfbulls.com",
    "Dayton": "daytonflyers.com",
    "Saint Louis": "slubillikens.com",
    "Richmond": "richmondspiders.com",
    "Davidson": "davidsonwildcats.com",
    "Rhode Island": "gorhody.com",
    "George Mason": "gomason.com",
    "VCU": "vcuathletics.com",
    "Saint Joseph's": "sjuhawks.com",
    "La Salle": "goexplorers.com",
    "Duquesne": "duquesnedukes.com",
    "Fordham": "fordhamsports.com",
    "George Washington": "gwsports.com",
    "Massachusetts": "umassmminutemen.com",
    "Memphis": "gotigersgo.com",
    "Wichita State": "goshockers.com",
    "Temple": "owlsports.com",
    "Tulsa": "tulsahurricane.com",
    "SMU": "smumustangs.com",
    "Gonzaga": "gozags.com",
    "BYU": "byucougars.com",
    "Saint Mary's": "smcgaels.com",
    "San Diego": "usdtoreros.com",
    "San Francisco": "usfcadons.com",
    "Pacific": "pacifictigers.com",
    "Pepperdine": "pepperdinewaves.com",
    "Santa Clara": "santaclarabroncos.com",
    "Loyola Marymount": "lionssports.com",
    "Portland": "portlandpilots.com",
    "Murray State": "goracers.com",
    "Belmont": "belmontbruins.com",
    "Tennessee": "utsports.com",
    "Alabama": "rolltide.com",
    "Auburn": "auburntigers.com",
    "LSU": "lsusports.net",
    "Georgia": "georgiadogs.com",
    "Mississippi State": "hailstate.com",
    "Ole Miss": "olemisssports.com",
    "Arkansas": "arkansasrazorbacks.com",
    "Missouri": "mutigers.com",
    "South Carolina": "gamecocksonline.com",
    "Vanderbilt": "vucommodores.com",
    "Texas A&M": "12thman.com",
    "Mississippi Valley State": "mvsu.edu",
}

# ─── NAIA TEAM SLUG LOOKUP ────────────────────────────────────────────────────
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
    "Loyola (NO)": "loyolano",
    "LSU-Alexandria": "lsua",
    "Marian (IN)": "marianian",
    "Masters": "mastersca",
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
    "Point": "pointga",
    "Robert Morris (IL)": "robertmorrisil",
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

# ─── NJCAA TEAM SLUG LOOKUP ───────────────────────────────────────────────────
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
    "Collin County Community College": "collincountycommunitycollege",
    "Connors State": "connorsstatecollege",
    "Copiah-Lincoln CC": "copiahlincolncommunitycollege",
    "Cowley College": "cowleycountycommunitycollege",
    "Dodge City CC": "dodgecitycommunitycollege",
    "Eastern Arizona": "easternarizonacollege",
    "Fort Scott CC": "fortscottcc",
    "Garden City CC": "gardencitycommunitycollege",
    "Gulf Coast State": "gulfcoaststatecollege",
    "Highland CC": "highlandcommunitycollegeillinois",
    "Hillsborough CC": "hillsboroughcommunitycollege",
    "Holmes CC": "holmescommunitycollege",
    "Howard College": "howardcollege",
    "Hutchinson CC": "hutchinsoncommunitycollege",
    "Independence CC": "independencecommunitycollege",
    "Indian Hills CC": "indianhillscommunitycollege",
    "Iowa Central CC": "marshalltowncc",
    "Iowa Western CC": "iowawesterncc",
    "John A. Logan College": "johnalogancollege",
    "Johnson County CC": "johnsoncountycc",
    "Jones College": "jonescollege",
    "Kilgore College": "kilgorecollege",
    "Lake Land College": "lakelandcollege",
    "Laramie County CC": "laramiecountycommunitycollege",
    "McLennan CC": "mclennancommunitycollege",
    "Meridian CC": "meridiancommunitycollege",
    "Mesa CC": "mesacc",
    "Mineral Area College": "mineralareacollege",
    "Mississippi Delta CC": "mississippideltacommunitycollege",
    "Moberly Area CC": "moberlyareacommunitycollege",
    "Monroe CC": "monroecc",
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
    "Southwest Mississippi CC": "southwestmississippicommunitycollege",
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

# ─── PARSE PRESTO SPORTS LINEUP PAGE ─────────────────────────────────────────
def parse_presto_lineup(html, player_name):
    """Parse a PrestoSports ?view=lineup page and find a player by name."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Find all rows in the stats table
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if not cells:
                continue
            row_text = row.get_text(" ", strip=True).lower()
            name_parts = player_name.lower().split()
            # Match if first or last name appears in row
            if any(part in row_text for part in name_parts if len(part) > 2):
                return extract_presto_stats(cells, row)
    return None

def extract_presto_stats(cells, row):
    """Extract per-game stats from a PrestoSports table row."""
    def safe(idx, default=0.0):
        try:
            val = cells[idx].get_text(strip=True).replace('%','').replace('-','0')
            return float(val)
        except:
            return default

    # PrestoSports lineup table column order:
    # Name, GP, GS, MIN, FGM, FGA, FG%, 3PM, 3PA, 3P%, FTM, FTA, FT%, 
    # OREB, DREB, REB, PF, AST, TO, BLK, STL, PTS
    try:
        gp   = safe(1) or 1
        mins = safe(3) / gp if safe(3) > 40 else safe(3)
        fgp  = safe(6) * 100 if safe(6) <= 1 else safe(6)
        tpa  = safe(8) / gp
        tpp  = safe(9) * 100 if safe(9) <= 1 else safe(9)
        ftm  = safe(10)
        fta  = safe(11)
        ftp  = safe(12) * 100 if safe(12) <= 1 else safe(12)
        reb  = safe(15) / gp
        ast  = safe(17) / gp
        tov  = safe(18) / gp
        blk  = safe(19) / gp
        stl  = safe(20) / gp
        pts  = safe(21) / gp

        if gp < 1: return None

        return {
            "fgp": round(fgp, 1),
            "tpa": round(tpa, 1),
            "tpp": round(tpp, 1),
            "ftp": round(ftp, 1),
            "reb": round(reb, 1),
            "pts": round(pts, 1),
            "ast": round(ast, 1),
            "stl": round(stl, 1),
            "blk": round(blk, 1),
            "tov": round(tov, 1),
            "min": round(mins, 1),
            "games": int(gp)
        }
    except Exception as e:
        print(f"Extract error: {e}")
        return None

# ─── FETCH FROM NJCAA ─────────────────────────────────────────────────────────
def fetch_njcaa(player_name, school_name):
    slug = NJCAA_SLUGS.get(school_name)
    if not slug:
        # Try fuzzy match
        school_lower = school_name.lower()
        for k, v in NJCAA_SLUGS.items():
            if k.lower() in school_lower or school_lower in k.lower():
                slug = v
                break
    if not slug:
        return None, "JUCO school not found in database"

    for div in ["div1", "div2", "div3"]:
        url = f"https://njcaastats.prestosports.com/sports/mbkb/2024-25/{div}/teams/{slug}?view=lineup"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                stats = parse_presto_lineup(resp.text, player_name)
                if stats:
                    return stats, None
        except Exception as e:
            print(f"NJCAA fetch error: {e}")
    return None, "Player not found on NJCAA stats"

# ─── FETCH FROM NAIA ──────────────────────────────────────────────────────────
def fetch_naia(player_name, school_name):
    slug = NAIA_SLUGS.get(school_name)
    if not slug:
        school_lower = school_name.lower().replace(" ", "").replace("-", "")
        for k, v in NAIA_SLUGS.items():
            if k.lower().replace(" ","") in school_lower or school_lower in k.lower().replace(" ",""):
                slug = v
                break
    if not slug:
        return None, "NAIA school not found in database"

    url = f"https://naiastats.prestosports.com/sports/mbkb/2024-25/teams/{slug}?view=lineup"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            stats = parse_presto_lineup(resp.text, player_name)
            if stats:
                return stats, None
    except Exception as e:
        print(f"NAIA fetch error: {e}")
    return None, "Player not found on NAIA stats"

# ─── FETCH FROM NCAA SCHOOL WEBSITE ──────────────────────────────────────────
def fetch_ncaa_school(player_name, school_name):
    domain = NCAA_DOMAINS.get(school_name)
    if not domain:
        # Try partial match
        for k, v in NCAA_DOMAINS.items():
            if school_name.lower() in k.lower() or k.lower() in school_name.lower():
                domain = v
                break
    if not domain:
        return None, "School website not found — enter stats manually"

    # Try current season stats page
    season = "2024-25"
    urls_to_try = [
        f"https://{domain}/sports/mens-basketball/stats/{season}",
        f"https://{domain}/sports/mens-basketball/stats",
        f"https://{domain}/sports/mbkb/stats/{season}",
        f"https://{domain}/sports/mbkb/{season}/stats",
    ]

    for url in urls_to_try:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                stats = parse_sidearm_stats(resp.text, player_name)
                if stats:
                    return stats, None
        except Exception as e:
            print(f"NCAA fetch error for {url}: {e}")
            continue

    return None, f"Stats page not found for {school_name} — enter stats manually"

def parse_sidearm_stats(html, player_name):
    """Parse a Sidearm Sports stats page for a specific player."""
    soup = BeautifulSoup(html, "html.parser")
    name_parts = player_name.lower().split()

    # Look for the player in any table
    tables = soup.find_all("table")
    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            row_text = row.get_text(" ", strip=True).lower()
            if any(part in row_text for part in name_parts if len(part) > 2):
                cells = row.find_all("td")
                if len(cells) >= 10:
                    stats = extract_sidearm_stats(cells)
                    if stats:
                        return stats
    return None

def extract_sidearm_stats(cells):
    """Extract stats from a Sidearm Sports table row."""
    def safe(idx, default=0.0):
        try:
            if idx >= len(cells): return default
            val = cells[idx].get_text(strip=True).replace('%','').replace('-','0').strip()
            return float(val) if val else default
        except:
            return default

    try:
        # Sidearm column order varies but typically:
        # Name, GP, GS, MIN/G, FG%, 3PA/G, 3PT%, FT%, REB/G, AST/G, TO/G, STL/G, BLK/G, PTS/G
        gp   = safe(1) or 1
        mins = safe(3)
        fgp  = safe(4) * 100 if safe(4) <= 1 else safe(4)
        tpa  = safe(5)
        tpp  = safe(6) * 100 if safe(6) <= 1 else safe(6)
        ftp  = safe(7) * 100 if safe(7) <= 1 else safe(7)
        reb  = safe(8)
        ast  = safe(9)
        tov  = safe(10)
        stl  = safe(11)
        blk  = safe(12)
        pts  = safe(13)

        if gp < 1 or pts == 0: return None

        return {
            "fgp": round(fgp, 1),
            "tpa": round(tpa, 1),
            "tpp": round(tpp, 1),
            "ftp": round(ftp, 1),
            "reb": round(reb, 1),
            "pts": round(pts, 1),
            "ast": round(ast, 1),
            "stl": round(stl, 1),
            "blk": round(blk, 1),
            "tov": round(tov, 1),
            "min": round(mins, 1),
            "games": int(gp)
        }
    except Exception as e:
        print(f"Sidearm extract error: {e}")
        return None

# ─── MAIN SEARCH ENDPOINT ─────────────────────────────────────────────────────
@app.route("/search", methods=["GET"])
def search():
    player = request.args.get("player", "").strip()
    school = request.args.get("school", "").strip()
    division = request.args.get("div", "").strip().upper()

    if not player or not school:
        return jsonify({"error": "player and school required"}), 400

    stats = None
    error = None

    if division == "JUCO":
        stats, error = fetch_njcaa(player, school)
    elif division == "NAIA":
        stats, error = fetch_naia(player, school)
    else:
        # NCAA D1, D2, D3
        stats, error = fetch_ncaa_school(player, school)

    if not stats:
        return jsonify({
            "error": error or "Player not found",
            "player": player,
            "school": school,
            "manual_entry": True
        }), 404

    return jsonify({
        "success": True,
        "player": player,
        "school": school,
        "stats": stats
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "TransferIQ backend running"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
