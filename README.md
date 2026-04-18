# BAYby-Led Weaning

BLW-friendly Bay Area restaurant reviews — a static site for families doing baby-led weaning.

## What it is

A single-page site listing restaurants with notes on high chair availability, Inglesina clip-on seat compatibility, and a short review. An interactive Leaflet map shows all locations; hovering a card highlights its marker and vice versa.

## Adding a restaurant

Edit [`data/restaurants.csv`](data/restaurants.csv). Columns:

| Column | Values |
|---|---|
| `name` | Restaurant name (used for geocoding and Google Maps link) |
| `high_chairs` | `Yes` / `No` / empty |
| `inglesina_safe` | `Yes` / `No` / empty |
| `review` | Free text |

## Building

```bash
python3 build.py
```

Outputs to `docs/`. Geocoding results are cached in `data/coords_cache.json` — commit the cache so builds are fast and reproducible. To override a coordinate (e.g. for a restaurant that geocodes incorrectly), edit the cache JSON directly.

## First-time setup

Vendor third-party assets before the first build (only needed once, or when upgrading library versions):

```bash
python3 vendor.py
```

This downloads Leaflet, Font Awesome, and the Google Fonts (Fraunces, Caveat, Lora) into `vendor/`. The build copies them into `_site/vendor/` automatically.

## Deploying

Build locally and commit `docs/` to the repo. In the GitHub Pages settings, set the source to the `docs` folder on the `main` branch.

## Third-party licenses

| Library | License |
|---|---|
| [Leaflet 1.9.4](https://leafletjs.com) | BSD 2-Clause |
| [Font Awesome 6.5.1 Free](https://fontawesome.com) | MIT (CSS), SIL OFL 1.1 (fonts), CC BY 4.0 (icons) |
| [Fraunces](https://github.com/undercasetype/Fraunces), [Caveat](https://github.com/googlefonts/caveat), [Lora](https://github.com/cyrealtype/Lora-Cyrillic) | SIL OFL 1.1 |
| Map tiles | © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors |
