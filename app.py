from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

NCAA_TEAM_IDS = {
    "Wisconsin-Platteville": {"id": "457", "div": "D3"},
    "Baldwin Wallace": {"id": "30006", "div": "D3"},
    "Gonzaga": {"id": "177", "div": "D1"},
    "Duke": {"id": "150", "div": "D1"},
    "Kansas": {"id": "198", "div": "D1"},
    "Kentucky": {"id": "202", "div": "D1"},
    "Northwest Missouri State": {"id": "505", "div": "D2"},
}

def search_ncaa_player(player_name, school_name):
    try:
        search_url = f"https://stats.ncaa.org/players/search?utf8=%E2%9C%93&player_search_name={player_name.replace(' ', '+')}&player_school_name=&sport_year_ctl_id=15860&division=&stats_player_seq=-100"
        resp = requests.get(search_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", {"id": "player_search_results"})
        if not table:
            return None
        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue
            name_cell = cols[0].get_text(strip=True)
            school_cell = cols[2].get_text(strip=True)
            if school_name.lower() in school_cell.lower():
                link = cols[0].find("a")
                if link and link.get("href"):
                    player_id = re.search(r'/players/(\d+)', link["href"])
                    if player_id:
                        return player_id.group(1)
        return None
    except Exception as e:
        print(f"Search error: {e}")
        return None

def get_player_stats(player_id):
    try:
        url = f"https://stats.ncaa.org/players/{player_id}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        tables = soup.find_all("table")
        stats = {}
        for table in tables:
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if not cols:
                    continue
                label = cols[0].get_text(strip=True).lower()
                if "total" in label or "career" in label:
                    row_data = {}
                    for i, col in enumerate(cols):
                        if i < len(headers):
                            row_data[headers[i]] = col.get_text(strip=True)
                    stats = row_data
                    break
        if not stats:
            return None

        def safe_float(val, default=0.0):
            try:
                return float(str(val).replace("%","").strip())
            except:
                return default

        g  = safe_float(stats.get("G", 1)) or 1
        fg_pct  = safe_float(stats.get("FG%", 0))
        tpa     = safe_float(stats.get("3FGA", 0)) / g
        tp_pct  = safe_float(stats.get("3FG%", 0))
        ft_pct  = safe_float(stats.get("FT%", 0))
        reb     = safe_float(stats.get("Reb/G", stats.get("REB", 0))) 
        if reb > 20:
            reb = reb / g
        pts     = safe_float(stats.get("Pts/G", stats.get("PTS", 0)))
        if pts > 30:
            pts = pts / g
        ast     = safe_float(stats.get("Ast/G", stats.get("AST", 0)))
        if ast > 15:
            ast = ast / g
        stl     = safe_float(stats.get("Stl/G", stats.get("STL", 0)))
        if stl > 10:
            stl = stl / g
        blk     = safe_float(stats.get("Blk/G", stats.get("BLK", 0)))
        if blk > 8:
            blk = blk / g
        tov     = safe_float(stats.get("TO/G", stats.get("TO", 0)))
        if tov > 10:
            tov = tov / g
        mins    = safe_float(stats.get("Min/G", stats.get("MIN", 0)))
        if mins > 40:
            mins = mins / g

        return {
            "fgp": round(fg_pct, 1),
            "tpa": round(tpa, 1),
            "tpp": round(tp_pct, 1),
            "ftp": round(ft_pct, 1),
            "reb": round(reb, 1),
            "pts": round(pts, 1),
            "ast": round(ast, 1),
            "stl": round(stl, 1),
            "blk": round(blk, 1),
            "tov": round(tov, 1),
            "min": round(mins, 1),
            "games": int(g)
        }
    except Exception as e:
        print(f"Stats error: {e}")
        return None

@app.route("/search", methods=["GET"])
def search():
    player = request.args.get("player", "")
    school = request.args.get("school", "")
    if not player or not school:
        return jsonify({"error": "player and school required"}), 400
    player_id = search_ncaa_player(player, school)
    if not player_id:
        return jsonify({"error": "Player not found", "player": player, "school": school}), 404
    stats = get_player_stats(player_id)
    if not stats:
        return jsonify({"error": "Could not retrieve stats"}), 500
    return jsonify({"success": True, "player": player, "school": school, "stats": stats})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "TransferIQ backend running"})

if __name__ == "__main__":
    app.run(debug=True)
