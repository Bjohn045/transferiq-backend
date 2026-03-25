from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def search_player_sports_ref(player_name, school_name):
    try:
        parts = player_name.strip().split()
        if len(parts) < 2:
            return None
        last = parts[-1].lower()
        first_initial = parts[0][0].lower()
        search_url = f"https://www.sports-reference.com/cbb/search/search.fcgi?search={requests.utils.quote(player_name)}"
        resp = requests.get(search_url, headers=HEADERS, timeout=10, allow_redirects=True)
        if "players" in resp.url and "/cbb/players/" in resp.url:
            return resp.url
        soup = BeautifulSoup(resp.text, "html.parser")
        results = soup.find_all("div", {"class": "search-item"})
        for r in results:
            link = r.find("a")
            text = r.get_text(" ", strip=True).lower()
            if link and school_name.split()[0].lower() in text:
                href = link.get("href", "")
                if "/cbb/players/" in href:
                    return "https://www.sports-reference.com" + href
        if results:
            link = results[0].find("a")
            if link and "/cbb/players/" in link.get("href",""):
                return "https://www.sports-reference.com" + link["href"]
        return None
    except Exception as e:
        print(f"Search error: {e}")
        return None

def get_stats_from_player_page(url, school_name):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        table = soup.find("table", {"id": "players_per_game"})
        if not table:
            table = soup.find("table", {"id": "per_game"})
        if not table:
            tables = soup.find_all("table")
            for t in tables:
                if "FG%" in t.get_text():
                    table = t
                    break
        if not table:
            return None
        rows = table.find("tbody").find_all("tr")
        target_row = None
        for row in rows:
            if row.get("class") and "thead" in row.get("class"):
                continue
            school_td = row.find("td", {"data-stat": "school_name"})
            if school_td and school_name.split()[0].lower() in school_td.get_text(strip=True).lower():
                target_row = row
        if not target_row and rows:
            for row in reversed(rows):
                if row.get("class") and "thead" in row.get("class"):
                    continue
                tds = row.find_all("td")
                if len(tds) > 5:
                    target_row = row
                    break
        if not target_row:
            return None

        def cell(stat):
            td = target_row.find("td", {"data-stat": stat})
            if td:
                val = td.get_text(strip=True).replace("%","")
                try: return float(val)
                except: return 0.0
            return 0.0

        g = cell("g") or 1
        fg_pct  = cell("fg_pct") * 100 if cell("fg_pct") <= 1 else cell("fg_pct")
        tpa     = cell("fg3a_per_g")
        tp_pct  = cell("fg3_pct") * 100 if cell("fg3_pct") <= 1 else cell("fg3_pct")
        ft_pct  = cell("ft_pct") * 100 if cell("ft_pct") <= 1 else cell("ft_pct")
        reb     = cell("trb_per_g")
        pts     = cell("pts_per_g")
        ast     = cell("ast_per_g")
        stl     = cell("stl_per_g")
        blk     = cell("blk_per_g")
        tov     = cell("tov_per_g")
        mins    = cell("mp_per_g")

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
        print(f"Stats page error: {e}")
        return None

@app.route("/search", methods=["GET"])
def search():
    player = request.args.get("player", "").strip()
    school = request.args.get("school", "").strip()
    if not player or not school:
        return jsonify({"error": "player and school required"}), 400
    player_url = search_player_sports_ref(player, school)
    if not player_url:
        return jsonify({"error": "Player not found", "player": player, "school": school}), 404
    stats = get_stats_from_player_page(player_url, school)
    if not stats:
        return jsonify({"error": "Could not retrieve stats", "url": player_url}), 500
    return jsonify({"success": True, "player": player, "school": school, "stats": stats})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "TransferIQ backend running"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
