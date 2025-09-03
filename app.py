from flask import Flask, request, render_template_string, send_from_directory
import re
import json
import pandas as pd
import requests
from pathlib import Path

app = Flask(__name__)

# Carpeta on guardarem els Excel generats
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

HTML_BASE = """
<!doctype html>
<html lang="ca">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Extractor de telèfons — Páginas Amarillas</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 2rem; background: #f6f6f6; }
      .card { background: #fff; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.1); margin-bottom: 2rem; }
      h1 { font-size: 1.5rem; margin-bottom: 1rem; }
      form { display: flex; gap: 1rem; flex-wrap: wrap; }
      input[type="text"], input[type="number"] { flex: 1; padding: 0.5rem; border: 1px solid #ccc; border-radius: 8px; }
      button { padding: 0.6rem 1.2rem; border: none; border-radius: 8px; background: #0a66c2; color: white; cursor: pointer; }
      table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
      th, td { border: 1px solid #ddd; padding: 0.5rem; }
      th { background: #f0f0f0; }
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Extractor de telèfons — Páginas Amarillas</h1>
      <form method="POST" action="/scrape">
        <input type="text" name="sector" placeholder="Sector (p.ex. inmobiliarias)" value="{{ sector or '' }}" required />
        <input type="text" name="provincia" placeholder="Província (p.ex. valencia)" value="{{ provincia or '' }}" required />
        <input type="number" name="pagines" placeholder="Núm. de pàgines" value="{{ pagines or 1 }}" min="1" />
        <button type="submit">Cerca</button>
      </form>
    </div>

    {% if error %}
      <div class="card" style="color:red;">Error: {{ error }}</div>
    {% endif %}

    {% if results %}
      <div class="card">
        <p>S'han extret {{ results|length }} empreses.</p>
        <a href="{{ download_path }}">Descarregar Excel</a>
        <table>
          <thead><tr><th>Nom empresa</th><th>Telèfon</th></tr></thead>
          <tbody>
            {% for r in results %}
              <tr><td>{{ r['Nom empresa'] }}</td><td>{{ r['Telèfon'] }}</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    {% endif %}
  </body>
</html>
"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
}

POIS_REGEX = re.compile(r'PAOL\\.mapaPois\\.addPois\\s*\\(\\s*(\\[.*?\\])\\s*\\);', re.S)


def slugify(value: str) -> str:
    value = value.lower()
    return re.sub(r"[^a-z0-9_-]+", "-", value).strip("-")


def scrape_page(sector: str, provincia: str, pagina: int):
    url = f"https://www.paginasamarillas.es/a/{sector}/{provincia}/{pagina}"
    response = requests.get(url, headers=HEADERS, timeout=30)
    html = response.text

    m = re.search(r'PAOL\.mapaPois\.addPois\s*\(\s*(\[.*?])\s*\);', html, re.S)
    if not m:
        return []

    pois_json = m.group(1)
    pois = json.loads(pois_json)

    rows = []
    for poi in pois:
        name = poi.get("name")
        phone = poi.get("phone")
        if name and phone:
            rows.append({"Nom empresa": name, "Telèfon": phone})
    return rows


def scrape(sector: str, provincia: str, pagines: int):
    all_rows = []
    for p in range(1, pagines + 1):
        rows = scrape_page(sector, provincia, p)
        if not rows:
            break
        all_rows.extend(rows)
    df = pd.DataFrame(all_rows).drop_duplicates().reset_index(drop=True)
    return df


@app.route("/")
def index():
    return render_template_string(HTML_BASE, sector="", provincia="", pagines=1)


@app.route("/scrape", methods=["POST"])
def do_scrape():
    sector = request.form.get("sector", "").strip()
    provincia = request.form.get("provincia", "").strip()
    try:
        pagines = int(request.form.get("pagines", "1").strip())
    except ValueError:
        pagines = 1

    try:
        df = scrape(sector, provincia, pagines)
        results = df.to_dict(orient="records")

        fname = f"telefonos_{slugify(sector)}_{slugify(provincia)}.xlsx"
        fpath = EXPORT_DIR / fname
        df.to_excel(fpath, index=False)

        return render_template_string(
            HTML_BASE,
            sector=sector,
            provincia=provincia,
            pagines=pagines,
            results=results,
            download_path=f"/files/{fname}",
            error=None,
        )
    except Exception as e:
        return render_template_string(
            HTML_BASE,
            sector=sector,
            provincia=provincia,
            pagines=pagines,
            results=None,
            download_path=None,
            error=str(e),
        )


@app.route("/files/<path:filename>")
def download_file(filename):
    safe_path = (EXPORT_DIR / filename).resolve()
    if not str(safe_path).startswith(str(EXPORT_DIR.resolve())):
        return "No autoritzat", 403
    if not safe_path.exists():
        return "Fitxer no trobat", 404
    return send_from_directory(EXPORT_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)