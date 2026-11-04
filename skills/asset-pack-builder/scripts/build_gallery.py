#!/usr/bin/env python3
"""Build gallery.html, a browsable 3D preview of a pack, from manifest.json.

    python3 build_gallery.py art/dungeon/manifest.json
    cd art/dungeon && python3 -m http.server 8000   # then open http://localhost:8000/gallery.html

Views:
    gallery.html            cards with name, id, category, variants, concept image
    gallery.html?sheet=1    tight auto-rotating grid with no text, for screenshots or screen recordings

Uses local files when present (serve the folder over http, because browsers block file:// GLBs),
otherwise the public Sloyd URLs. Standard library only.
"""

from __future__ import annotations

import html
import json
import os
import sys

VIEWER = "https://ajax.googleapis.com/ajax/libs/model-viewer/4.1.0/model-viewer.min.js"


def src(job: dict, base: str) -> str | None:
    if not job or job.get("status") not in ("success", "completed"):
        return None
    f = job.get("file")
    if f and os.path.isfile(os.path.join(base, f)):
        return f.replace(os.sep, "/")
    return job.get("url")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    path = sys.argv[1]
    base = os.path.dirname(os.path.abspath(path))
    with open(path, encoding="utf-8") as fh:
        man = json.load(fh)

    cards = []
    for a in man["assets"]:
        jobs = a.get("jobs", {})
        model = src(jobs.get("model"), base)
        if not model:
            continue
        concept = src(jobs.get("concept") or jobs.get("upload"), base)
        variants = [("base", model)]
        for key, job in jobs.items():
            if key.startswith("variant:") and src(job, base):
                variants.append((key.split(":", 1)[1], src(job, base)))
        if src(jobs.get("split"), base):
            variants.append(("parts", src(jobs["split"], base)))
        buttons = "".join(
            f'<button data-src="{html.escape(s)}"{" class=on" if i == 0 else ""}>{html.escape(n)}</button>'
            for i, (n, s) in enumerate(variants)
        ) if len(variants) > 1 else ""
        poster = f' poster="{html.escape(concept)}"' if concept else ""
        thumb = f'<img src="{html.escape(concept)}" alt="concept">' if concept else ""
        cards.append(f"""
<figure class="card">
  <model-viewer src="{html.escape(model)}"{poster} camera-controls auto-rotate rotation-per-second="20deg"
    interaction-prompt="none" shadow-intensity="0.8" exposure="1.05" environment-image="neutral" loading="lazy"></model-viewer>
  <figcaption>
    <div class="row"><strong>{html.escape(a.get('name', a['id']))}</strong>{thumb}</div>
    <code>{html.escape(a['id'])}</code> <span>{html.escape(a.get('category', ''))}</span>
    <div class="vars">{buttons}</div>
  </figcaption>
</figure>""")

    t = man.get("totals", {})
    title = html.escape(man.get("title", man.get("pack", "Asset pack")))
    meta = (f"{len(cards)} models &middot; style <code>{html.escape(str(man.get('genStyleId')))}</code> &middot; "
            f"{html.escape(str(man.get('topology')))} &middot; {html.escape(str(man.get('textureResolution')))} textures"
            f" &middot; ~{t.get('creditsSpentEstimate', 0)} credits")
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<script type="module" src="{VIEWER}"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
<style>
:root {{ --bg:#0b1833; --card:#12234a; --ink:#e8eefc; --muted:#8fa3c8; --accent:#03f584; }}
* {{ box-sizing:border-box }}
body {{ margin:0; background:var(--bg); color:var(--ink); font-family:Poppins,system-ui,sans-serif }}
header {{ padding:28px 32px 8px }} h1 {{ margin:0 0 6px; font-weight:600 }} .meta {{ color:var(--muted) }}
main {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr)); gap:16px; padding:24px 32px 48px }}
.card {{ margin:0; background:var(--card); border-radius:16px; overflow:hidden }}
model-viewer {{ width:100%; height:240px; background:radial-gradient(circle at 50% 40%,#1c3266,#12234a) }}
figcaption {{ padding:10px 14px 14px; font-size:13px }} .row {{ display:flex; justify-content:space-between; align-items:center }}
figcaption img {{ width:36px; height:36px; border-radius:6px; object-fit:cover }}
code {{ color:var(--accent); font-size:12px }} figcaption span {{ color:var(--muted); margin-left:6px }}
.vars button {{ margin:8px 6px 0 0; padding:4px 10px; border-radius:38px; border:1px solid #2b4580; background:none; color:var(--ink); font:inherit; cursor:pointer }}
.vars button.on {{ background:linear-gradient(63deg,#45bcff 19%,#03f584 100%); color:#021225; border-color:transparent }}
footer {{ color:var(--muted); padding:0 32px 32px; font-size:13px }}
body.sheet header, body.sheet footer, body.sheet figcaption {{ display:none }}
body.sheet main {{ grid-template-columns:repeat(8,1fr); gap:6px; padding:6px }}
body.sheet model-viewer {{ height:12.5vw }} body.sheet .card {{ border-radius:10px }}
</style></head>
<body>
<header><h1>{title}</h1><div class="meta">{meta}</div></header>
<main>{''.join(cards)}</main>
<footer>Generated with the Game Art Department skills and the Sloyd API. Drag to orbit.</footer>
<script>
if (new URLSearchParams(location.search).get('sheet')) document.body.classList.add('sheet');
document.querySelectorAll('.vars').forEach(v => v.addEventListener('click', e => {{
  const b = e.target.closest('button'); if (!b) return;
  v.querySelectorAll('button').forEach(x => x.classList.toggle('on', x === b));
  v.closest('.card').querySelector('model-viewer').src = b.dataset.src;
}}));
</script>
</body></html>
"""
    out = os.path.join(base, "gallery.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"{out} ({len(cards)} models)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
