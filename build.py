#!/usr/bin/env python3
"""Reads data/restaurants.csv and generates _site/index.html."""

import csv
import html
import json
import shutil
import time
import urllib.parse
import urllib.request
from pathlib import Path

CSV_PATH = Path("data/restaurants.csv")
OUTPUT_DIR = Path("docs")
OUTPUT_FILE = OUTPUT_DIR / "index.html"
CACHE_PATH = Path("data/coords_cache.json")


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text())
    return {}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, indent=2))


def geocode(name: str, cache: dict) -> dict | None:
    if name in cache:
        return cache[name]
    query = urllib.parse.quote_plus(f"{name} San Francisco CA")
    url = f"https://nominatim.openstreetmap.org/search?q={query}&format=json&limit=1"
    req = urllib.request.Request(url, headers={"User-Agent": "BAYby-Led-Weaning/1.0"})
    result = None
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.load(resp)
        if data:
            result = {"lat": float(data[0]["lat"]), "lng": float(data[0]["lon"])}
    except Exception as e:
        print(f"  Geocode failed for '{name}': {e}")
        return None  # Don't cache transient failures
    cache[name] = result
    time.sleep(1.1)
    return result


def yn_badge(label: str, value: str) -> str:
    is_yes = value.strip().lower() in ("yes", "y", "true", "1")
    cls = "badge-yes" if is_yes else "badge-no"
    icon = '<i class="fa-solid fa-check"></i>' if is_yes else '<i class="fa-solid fa-xmark"></i>'
    return f'<span class="badge {cls}">{icon} {label}</span>'


def maps_url(name: str) -> str:
    query = urllib.parse.quote_plus(f"{name} Bay Area CA")
    return f"https://www.google.com/maps/search/?api=1&query={query}"


def make_card(r: dict, idx: int) -> str:
    name = r["name"].strip()
    review = html.escape(r["review"].strip()).replace("\n", "<br>")
    url = maps_url(name)
    badges = ""
    if r["high_chairs"].strip():
        badges += yn_badge('<i class="fa-solid fa-chair"></i> High Chairs', r["high_chairs"])
    if r["inglesina_safe"].strip():
        badges += yn_badge('<i class="fa-solid fa-baby"></i> Inglesina Safe', r["inglesina_safe"])
    return f"""
    <article class="card" data-index="{idx}">
      <h2 class="card-title">
        <a href="{url}" target="_blank" rel="noopener">{html.escape(name)} <i class="fa-solid fa-location-dot pin"></i></a>
      </h2>
      <div class="badges">
        {badges}
      </div>
      <p class="review">{review}</p>
    </article>"""


PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data: https://*.tile.openstreetmap.org;" />
  <title>BAYby-Led Weaning</title>
  <link rel="stylesheet" href="vendor/fonts/fonts.css" />
  <link rel="stylesheet" href="vendor/fontawesome/all.min.css" />
  <link rel="stylesheet" href="vendor/leaflet/leaflet.css" />
  <style>
    :root {{
      --card: #fdfaff;
      --accent: #b8883a;
      --accent-light: #d4aa60;
      --yes-bg: #e8f0e0;
      --yes-fg: #4a7040;
      --no-bg: #f5e2e2;
      --no-fg: #9a5050;
      --charcoal: #1e1830;
      --muted: #c09858;
    }}

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    html, body {{ height: 100%; overflow: hidden; }}

    body {{
      background: linear-gradient(160deg, #3a96b8 0%, #a8dbb0 100%) fixed;
      background-attachment: fixed;
      color: var(--charcoal);
      font-family: 'Lora', Georgia, serif;
    }}

    /* ── Two-column layout: cards left, map right ── */
    .layout {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: auto 1fr;
      grid-template-areas: "header map" "cards map";
      height: 100vh;
    }}

    .layout > header {{ grid-area: header; }}

    .cards-col {{
      grid-area: cards;
      overflow-y: auto;
    }}

    .map-col {{
      grid-area: map;
      position: relative;
    }}

    #map {{ width: 100%; height: 100%; }}

    @media (max-width: 768px) {{
      html, body {{ overflow: visible; }}
      .layout {{
        grid-template-columns: 1fr;
        grid-template-areas: "header" "map" "cards";
        height: auto;
      }}
      .map-col {{ height: 280px; }}
      #map {{ height: 280px; }}
      .cards-col {{ height: auto; overflow-y: visible; }}
    }}

    /* ── Header ── */
    header {{
      padding: 3rem 2rem 2rem;
      text-align: center;
    }}

    header h1 {{
      font-family: 'Fraunces', Georgia, serif;
      font-size: clamp(2rem, 4vw, 3rem);
      font-weight: 900;
      font-style: italic;
      line-height: 1.05;
      letter-spacing: -0.02em;
      color: #ffffff;
    }}

    header h1 .bay {{ color: inherit; }}

    .header-sub {{
      font-family: 'Caveat', cursive;
      font-size: clamp(1rem, 2.5vw, 1.35rem);
      font-weight: 500;
      color: #ffffff;
      margin-top: 1rem;
      letter-spacing: 0.02em;
    }}

    .header-sub i {{ margin: 0 0.25em; }}

    .header-divider {{
      width: 48px;
      height: 2px;
      background: var(--accent);
      margin: 1.75rem auto 0;
      border-radius: 2px;
    }}

    /* ── Cards ── */
    main {{
      padding: 2rem 1.5rem 4rem;
      display: grid;
      gap: 1.5rem;
    }}

    .card {{
      background: var(--card);
      color: var(--charcoal);
      border-radius: 3px;
      padding: 1.75rem 2rem;
      border-left: 4px solid var(--accent);
      box-shadow: 0 2px 8px rgba(160,120,40,0.08), 0 8px 28px rgba(160,120,40,0.1);
      opacity: 0;
      transform: translateY(20px);
      animation: fadeUp 0.55s cubic-bezier(0.22, 1, 0.36, 1) forwards;
      transition: transform 0.2s ease, box-shadow 0.2s ease, border-left-color 0.15s ease;
    }}

    .card:hover, .card.highlighted {{
      transform: translateY(-4px);
      box-shadow: 0 4px 16px rgba(160,120,40,0.18), 0 16px 40px rgba(160,120,40,0.2);
      border-left-color: var(--accent-light);
    }}

    .card:nth-child(1)  {{ animation-delay: 0.08s; }}
    .card:nth-child(2)  {{ animation-delay: 0.18s; }}
    .card:nth-child(3)  {{ animation-delay: 0.28s; }}
    .card:nth-child(4)  {{ animation-delay: 0.38s; }}
    .card:nth-child(5)  {{ animation-delay: 0.48s; }}
    .card:nth-child(6)  {{ animation-delay: 0.58s; }}
    .card:nth-child(7)  {{ animation-delay: 0.68s; }}
    .card:nth-child(8)  {{ animation-delay: 0.78s; }}
    .card:nth-child(9)  {{ animation-delay: 0.88s; }}
    .card:nth-child(10) {{ animation-delay: 0.98s; }}

    @keyframes fadeUp {{
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .card-title {{
      font-family: 'Fraunces', Georgia, serif;
      font-size: 1.4rem;
      font-weight: 700;
      line-height: 1.2;
      margin-bottom: 0.75rem;
    }}

    .card-title a {{
      color: var(--charcoal);
      text-decoration: none;
      transition: color 0.15s;
    }}

    .card-title a:hover {{ color: var(--accent); }}

    .pin {{
      color: var(--accent);
      font-size: 0.75em;
      margin-left: 0.3em;
      opacity: 0.8;
    }}

    .badges {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem;
      margin-bottom: 0.9rem;
    }}

    .badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.3rem;
      padding: 0.2rem 0.7rem;
      border-radius: 2px;
      font-family: 'Fraunces', Georgia, serif;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.07em;
      text-transform: uppercase;
    }}

    .badge-yes {{ background: var(--yes-bg); color: var(--yes-fg); }}
    .badge-no  {{ background: var(--no-bg);  color: var(--no-fg); }}

    .review {{
      font-style: italic;
      font-size: 0.95rem;
      line-height: 1.8;
      color: #2a2040;
    }}

    /* ── Footer ── */
    footer {{
      text-align: center;
      padding: 1.5rem 1rem 2.5rem;
      font-family: 'Caveat', cursive;
      font-size: 1.05rem;
      color: #ffffff;
      font-size: 1.4rem;
    }}

    footer i {{ color: var(--accent); margin: 0 0.1em; }}
    .footer-contrib {{ display: block; margin-bottom: 0.5rem; font-size: 1.4rem; }}
    .footer-contrib a {{ color: var(--accent); text-decoration: underline; }}

    .leaflet-popup-content b {{ font-family: 'Fraunces', Georgia, serif; }}
  </style>
</head>
<body>
  <div class="layout">
    <header>
      <h1><span class="bay">BAY</span>by-Led Weaning</h1>
      <p class="header-sub">
        <i class="fa-solid fa-utensils"></i>
        Bay Area Restaurant Reviews by Tiny Foodies
        <i class="fa-solid fa-baby"></i>
      </p>
      <div class="header-divider"></div>
    </header>
    <div class="cards-col">
      <main>
{cards}
      </main>
      <footer>
        <span class="footer-contrib"> Want to add a restaurant? PRs welcome on <a href="https://github.com/diracdeltas/blw/blob/main/data/restaurants.csv" target="_blank" rel="noopener">GitHub</a></span>
      </footer>
    </div>
    <div class="map-col">
      <div id="map"></div>
    </div>
  </div>
  <script src="vendor/leaflet/leaflet.js"></script>
  <script src="app.js"></script>
</body>
</html>
"""


APP_JS_TEMPLATE = """\
var markers = {markers_json};
var map = L.map('map').setView([37.77, -122.45], 12);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  maxZoom: 19
}}).addTo(map);

var defaultStyle = {{ radius: 8,  fillColor: '#b8883a', color: '#fff', weight: 2,   opacity: 1, fillOpacity: 0.9 }};
var activeStyle  = {{ radius: 12, fillColor: '#e0aa50', color: '#fff', weight: 2.5, opacity: 1, fillOpacity: 1   }};

var cardsByIndex = {{}};
document.querySelectorAll('.card').forEach(function(card) {{
  cardsByIndex[parseInt(card.dataset.index)] = card;
}});

var circlesByIndex = {{}};
markers.forEach(function(m) {{
  var card = cardsByIndex[m.index];
  var circle = L.circleMarker([m.lat, m.lng], Object.assign({{}}, defaultStyle))
    .addTo(map)
    .bindPopup('<b>' + m.name + '</b>');

  circle.on('mouseover', function() {{
    circle.setStyle(activeStyle).openPopup();
    if (card) {{ card.classList.add('highlighted'); card.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }}); }}
  }});
  circle.on('mouseout', function() {{
    circle.setStyle(defaultStyle);
    if (card) card.classList.remove('highlighted');
  }});

  circlesByIndex[m.index] = circle;
}});

document.querySelectorAll('.card').forEach(function(card) {{
  var circle = circlesByIndex[parseInt(card.dataset.index)];
  if (!circle) return;
  card.addEventListener('mouseenter', function() {{ circle.setStyle(activeStyle); circle.openPopup(); map.panTo(circle.getLatLng()); }});
  card.addEventListener('mouseleave', function() {{ circle.setStyle(defaultStyle); circle.closePopup(); }});
}});
"""


def build():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        restaurants = list(csv.DictReader(f))

    if not restaurants:
        print("No restaurants found in CSV.")
        return

    cache = load_cache()
    markers = []
    card_parts = []
    for i, r in enumerate(restaurants):
        name = r["name"].strip()
        coords = geocode(name, cache)
        if coords:
            markers.append({"name": name, "lat": coords["lat"], "lng": coords["lng"], "index": i})
            print(f"  {name}: {coords['lat']:.4f}, {coords['lng']:.4f}")
        else:
            print(f"  {name}: no coordinates found")
        card_parts.append(make_card(r, i))
    save_cache(cache)

    OUTPUT_DIR.mkdir(exist_ok=True)
    shutil.copytree(Path("vendor"), OUTPUT_DIR / "vendor", dirs_exist_ok=True)
    cards_html = "".join(card_parts)
    OUTPUT_FILE.write_text(
        PAGE_TEMPLATE.format(cards=cards_html, markers_json=json.dumps(markers)),
        encoding="utf-8",
    )
    (OUTPUT_DIR / "app.js").write_text(
        APP_JS_TEMPLATE.format(markers_json=json.dumps(markers)),
        encoding="utf-8",
    )
    print(f"Built {OUTPUT_FILE} — {len(restaurants)} restaurant(s), {len(markers)} mapped.")


if __name__ == "__main__":
    build()
