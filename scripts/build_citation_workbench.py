from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
DATA_SOURCE = ROOT / "data-source"
PACKETS_DIR = ROOT / "packets"
EXPORTS_DIR = ROOT / "exports"
SITE_URL = "https://mahmood726-cyber.github.io/citation-workbench/"
REPO_URL = "https://github.com/mahmood726-cyber/citation-workbench"
STEWARD = "Tahir Heart Institute"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def quote_yaml(text: str) -> str:
    value = compact(text).replace("\\", "\\\\").replace('"', '\\"')
    return f"\"{value}\""


def bibtex_escape(text: str) -> str:
    return compact(text).replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")


def publication_year(record: dict) -> int:
    match = re.search(r"(19|20)\d{2}", compact(record.get("lastTouch", "")))
    if match:
        return int(match.group(0))
    match = re.search(r"(19|20)\d{2}", compact(record.get("generatedAt", "")))
    if match:
        return int(match.group(0))
    return 2026


def release_date(record: dict) -> str:
    value = compact(record.get("lastTouch", ""))
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return value
    generated = compact(record.get("generatedAt", ""))
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}.*", generated):
        return generated[:10]
    return "2026-03-30"


def resource_type_general(record_type: str, tier: str) -> str:
    value = compact(record_type).lower()
    if "dataset" in value:
        return "Dataset"
    if tier == "Tier 8" or "course" in value or "educational" in value:
        return "Text"
    if "model" in value:
        return "Model"
    if any(token in value for token in ("app", "site", "pipeline", "package", "dashboard", "html")):
        return "Software"
    if "project" in value:
        return "Project"
    return "Other"


def cff_type(resource_type: str) -> str:
    return {
        "Dataset": "dataset",
        "Text": "generic",
        "Model": "software",
        "Software": "software",
        "Project": "generic",
        "Other": "generic",
    }[resource_type]


def citeproc_type(resource_type: str) -> str:
    return {
        "Dataset": "dataset",
        "Text": "report",
        "Model": "software",
        "Software": "software",
        "Project": "webpage",
        "Other": "webpage",
    }[resource_type]


def readiness_score(record: dict) -> tuple[int, list[str]]:
    reasons = []
    score = 0
    if record["name"]:
        score += 10
        reasons.append("Title preserved (+10)")
    if record["recordUrl"]:
        score += 10
        reasons.append("Public landing page available (+10)")
    if STEWARD:
        score += 10
        reasons.append("Institutional steward available (+10)")
    if record["resourceTypeGeneral"]:
        score += 10
        reasons.append("DataCite resource type mapped (+10)")
    if record["publicationYear"]:
        score += 10
        reasons.append("Publication year derivable (+10)")
    if record["resolvedStatus"] != "Needs triage":
        score += 15
        reasons.append("Lifecycle state resolved (+15)")
    if record["hasPaper"]:
        score += 10
        reasons.append("Paper evidence present (+10)")
    if record["hasProtocol"]:
        score += 10
        reasons.append("Protocol evidence present (+10)")
    if record["publishSignal"]:
        score += 10
        reasons.append("Public release signal present (+10)")
    if record["targetJournal"]:
        score += 5
        reasons.append("Journal target preserved (+5)")
    return score, reasons


def readiness_band(score: int) -> str:
    if score >= 80:
        return "high"
    if score >= 55:
        return "medium"
    return "low"


def primary_gap(record: dict) -> str:
    if record["resolvedStatus"] == "Needs triage":
        return "Resolve lifecycle status"
    if not record["publishSignal"]:
        return "Add public release signal"
    if not record["hasPaper"] or not record["hasProtocol"]:
        return "Add manuscript evidence"
    if not record["targetJournal"]:
        return "Preserve journal target"
    if record["fairTotal"] < 60:
        return "Raise maturity metadata"
    return "Maintain current packet"


def plain_citation(record: dict) -> str:
    return (
        f"{STEWARD} ({record['publicationYear']}). {record['name']} "
        f"[{record['resourceTypeGeneral']}]. {record['recordUrl']}"
    )


def make_cff(record: dict) -> str:
    keywords = "\n".join(f"  - {quote_yaml(keyword)}" for keyword in record["keywords"])
    lines = [
        "cff-version: 1.2.0",
        f"message: {quote_yaml('If you use this project record, please cite it using the metadata below.')}",
        f"title: {quote_yaml(record['name'])}",
        f"type: {record['cffType']}",
        "authors:",
        f"  - name: {quote_yaml(STEWARD)}",
        f"abstract: {quote_yaml(record['description'])}",
        f"date-released: {record['releaseDate']}",
        f"url: {quote_yaml(record['recordUrl'])}",
        f"repository-code: {quote_yaml(REPO_URL)}",
        f"license: {quote_yaml('NOASSERTION')}",
        "keywords:",
        keywords,
    ]
    return "\n".join(lines) + "\n"


def make_datacite(record: dict) -> dict:
    return {
        "schemaVersion": "http://datacite.org/schema/kernel-4",
        "creators": [{"name": STEWARD, "nameType": "Organizational"}],
        "titles": [{"title": record["name"]}],
        "publisher": STEWARD,
        "publicationYear": str(record["publicationYear"]),
        "types": {
            "resourceTypeGeneral": record["resourceTypeGeneral"],
            "resourceType": record["recordType"],
        },
        "url": record["recordUrl"],
        "subjects": [{"subject": keyword} for keyword in record["keywords"]],
        "descriptions": [{"description": record["description"], "descriptionType": "Abstract"}],
        "version": "draft-citation-packet",
        "rightsList": [{"rights": "No license asserted in the portfolio snapshot"}],
    }


def make_csl(record: dict) -> dict:
    return {
        "id": record["slug"],
        "type": record["citeprocType"],
        "title": record["name"],
        "author": [{"literal": STEWARD}],
        "issued": {"date-parts": [[record["publicationYear"]]]},
        "URL": record["recordUrl"],
        "abstract": record["description"],
        "publisher": STEWARD,
        "container-title": "PortfolioCatalog",
        "genre": record["recordType"],
        "keyword": ", ".join(record["keywords"]),
    }


def make_bibtex(record: dict) -> str:
    note = bibtex_escape(f"Type: {record['recordType']}; Status: {record['resolvedStatus']}")
    return (
        f"@misc{{{record['slug']},\n"
        f"  author = {{{{{bibtex_escape(STEWARD)}}}}},\n"
        f"  title = {{{bibtex_escape(record['name'])}}},\n"
        f"  year = {{{record['publicationYear']}}},\n"
        f"  note = {{{note}}},\n"
        f"  url = {{{record['recordUrl']}}}\n"
        f"}}\n"
    )


def packet_page(record: dict) -> str:
    download_links = [
        ("CFF", f"../exports/cff/{record['slug']}.cff", "Citation File Format packet"),
        ("DataCite", f"../exports/datacite/{record['slug']}.json", "Draft DOI-facing metadata"),
        ("CiteProc", f"../exports/csl/{record['slug']}.json", "CSL JSON citation item"),
        ("BibTeX", f"../exports/bibtex/{record['slug']}.bib", "Portable citation snippet"),
        ("PortfolioCatalog", record["recordUrl"], "Canonical public landing page"),
    ]
    links_html = "".join(
        f"<a class=\"download-link\" href=\"{escape(href)}\"><strong>{escape(title)}</strong><span>{escape(text)}</span></a>"
        for title, href, text in download_links
    )
    facts = [
        ("Citation readiness", str(record["citationReadinessScore"])),
        ("Readiness band", record["readinessBand"]),
        ("Resource type", record["resourceTypeGeneral"]),
        ("Publication year", str(record["publicationYear"])),
        ("Resolved status", record["resolvedStatus"]),
        ("Primary gap", record["primaryGap"]),
    ]
    facts_html = "".join(
        f"<article class=\"fact-card\"><span>{escape(label)}</span><strong>{escape(value)}</strong></article>"
        for label, value in facts
    )
    evidence = [
        f"Paper evidence: {'Yes' if record['hasPaper'] else 'No'}",
        f"Protocol evidence: {'Yes' if record['hasProtocol'] else 'No'}",
        f"Public release signal: {'Yes' if record['publishSignal'] else 'No'}",
        f"Journal target: {record['targetJournal'] or 'Not preserved'}",
        f"Lifecycle resolution source: {record['resolutionSource']}",
        f"Portfolio tier: {record['tier']}",
    ]
    evidence_html = "".join(f"<li>{escape(item)}</li>" for item in evidence)
    reason_html = "".join(f"<li>{escape(item)}</li>" for item in record["reasons"])
    keyword_html = "".join(f"<span class=\"pill\">{escape(keyword)}</span>" for keyword in record["keywords"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(record['name'])} | CitationWorkbench</title>
  <meta name="description" content="{escape(record['description'])}">
  <link rel="stylesheet" href="../styles.css">
</head>
<body>
  <div class="packet-shell">
    <header class="hero packet-header">
      <div>
        <p class="eyebrow">Citation Packet</p>
        <h1 class="packet-title">{escape(record['name'])}</h1>
        <p class="hero-text">{escape(record['plainCitation'])}</p>
        <div class="pill-row">
          <span class="pill {escape(record['readinessBand'])}">{escape(record['readinessBand'])} readiness</span>
          <span class="pill">{escape(record['resourceTypeGeneral'])}</span>
          <span class="pill">{escape(record['tier'])}</span>
          <span class="pill">{escape(record['resolvedStatus'])}</span>
        </div>
      </div>
      <div class="download-grid">{links_html}</div>
    </header>

    <main class="packet-grid">
      <section class="panel">
        <div class="section-head"><p class="eyebrow">Facts</p><h2>Packet Summary</h2></div>
        <div class="fact-grid">{facts_html}</div>
      </section>

      <section class="panel">
        <div class="section-head"><p class="eyebrow">Evidence</p><h2>Citation Signals</h2></div>
        <ul class="fact-list">{evidence_html}</ul>
      </section>

      <section class="panel">
        <div class="section-head"><p class="eyebrow">Reasons</p><h2>Why This Score</h2></div>
        <ul class="fact-list">{reason_html}</ul>
      </section>

      <section class="panel">
        <div class="section-head"><p class="eyebrow">Keywords</p><h2>Discovery Terms</h2></div>
        <div class="pill-row">{keyword_html}</div>
      </section>

      <section class="panel panel-wide">
        <div class="section-head"><p class="eyebrow">BibTeX</p><h2>Portable Citation</h2></div>
        <div class="code-panel"><pre>{escape(record['bibtex'])}</pre></div>
      </section>
    </main>

    <footer class="panel">
      <div class="footer-links">
        <a class="mini-link" href="../index.html"><strong>Back to dashboard</strong><span>Return to CitationWorkbench.</span></a>
        <a class="mini-link" href="../packet-index.json"><strong>Packet index</strong><span>Machine-readable lookup table.</span></a>
      </div>
    </footer>
  </div>
</body>
</html>
"""


def main() -> None:
    snapshot = load_json(DATA_SOURCE / "catalog-records.snapshot.json")
    PACKETS_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in PACKETS_DIR.glob("*.html"):
        old_file.unlink()
    for subdir, pattern in [
        (EXPORTS_DIR / "cff", "*.cff"),
        (EXPORTS_DIR / "datacite", "*.json"),
        (EXPORTS_DIR / "csl", "*.json"),
        (EXPORTS_DIR / "bibtex", "*.bib"),
    ]:
        subdir.mkdir(parents=True, exist_ok=True)
        for old_file in subdir.glob(pattern):
            old_file.unlink()

    records = []
    packet_index = []
    datacite_items = []
    csl_items = []
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    for source in snapshot["records"]:
        resource = resource_type_general(source["type"], source["tier"])
        record = {
            "id": source["id"],
            "name": source["name"],
            "slug": source["slug"],
            "tier": source["tier"],
            "tierName": source["tierName"],
            "recordType": source["type"],
            "recordUrl": source["recordUrl"],
            "resolvedStatus": compact(source["resolvedStatus"]),
            "resolutionSource": compact(source["resolutionSource"]),
            "targetJournal": compact(source.get("targetJournal", "")),
            "description": compact(source["description"]),
            "keywords": list(source["keywords"]),
            "publishSignal": bool(source["publishSignal"]),
            "hasPaper": bool(source["hasPaper"]),
            "hasProtocol": bool(source["hasProtocol"]),
            "fairTotal": int(source["fairTotal"]),
            "publicationYear": publication_year(source),
            "releaseDate": release_date(source),
            "resourceTypeGeneral": resource,
            "cffType": cff_type(resource),
            "citeprocType": citeproc_type(resource),
            "generatedAt": generated_at,
        }
        score, reasons = readiness_score(record)
        record["citationReadinessScore"] = score
        record["readinessBand"] = readiness_band(score)
        record["primaryGap"] = primary_gap(record)
        record["plainCitation"] = plain_citation(record)
        record["reasons"] = reasons
        record["datacite"] = make_datacite(record)
        record["csl"] = make_csl(record)
        record["bibtex"] = make_bibtex(record)
        record["cff"] = make_cff(record)

        cff_path = f"exports/cff/{record['slug']}.cff"
        datacite_path = f"exports/datacite/{record['slug']}.json"
        csl_path = f"exports/csl/{record['slug']}.json"
        bibtex_path = f"exports/bibtex/{record['slug']}.bib"
        packet_path = f"packets/{record['slug']}.html"

        write_text(ROOT / cff_path, record["cff"])
        write_json(ROOT / datacite_path, record["datacite"])
        write_json(ROOT / csl_path, record["csl"])
        write_text(ROOT / bibtex_path, record["bibtex"])
        write_text(ROOT / packet_path, packet_page(record))

        packet_index.append(
            {
                "id": record["id"],
                "name": record["name"],
                "slug": record["slug"],
                "packetPage": SITE_URL + packet_path,
                "cff": SITE_URL + cff_path,
                "datacite": SITE_URL + datacite_path,
                "csl": SITE_URL + csl_path,
                "bibtex": SITE_URL + bibtex_path,
                "recordUrl": record["recordUrl"],
            }
        )
        datacite_items.append(record["datacite"])
        csl_items.append(record["csl"])
        records.append(record)

    records.sort(key=lambda item: (-item["citationReadinessScore"], item["name"].lower(), item["id"]))
    tracked = len(records)
    high = sum(item["citationReadinessScore"] >= 80 for item in records)
    medium_or_high = sum(item["citationReadinessScore"] >= 55 for item in records)
    datacite_core = sum(
        bool(item["name"] and item["recordUrl"] and item["publicationYear"] and item["resourceTypeGeneral"])
        for item in records
    )
    paper_backed = sum(item["hasPaper"] for item in records)
    journal_linked = sum(bool(item["targetJournal"]) for item in records)
    release_ready = sum(
        item["resolvedStatus"] != "Needs triage" and item["publishSignal"] and item["hasPaper"] and item["hasProtocol"]
        for item in records
    )

    gap_counter = Counter()
    type_groups = defaultdict(list)
    tier_groups = defaultdict(list)
    for item in records:
        type_groups[item["resourceTypeGeneral"]].append(item)
        tier_groups[item["tier"]].append(item)
        if item["resolvedStatus"] == "Needs triage":
            gap_counter["Needs resolved lifecycle status"] += 1
        if not item["publishSignal"]:
            gap_counter["Needs public release signal"] += 1
        if not item["hasPaper"] or not item["hasProtocol"]:
            gap_counter["Needs manuscript evidence"] += 1
        if not item["targetJournal"]:
            gap_counter["Needs preserved journal target"] += 1
        if item["fairTotal"] < 60:
            gap_counter["Needs stronger maturity metadata"] += 1

    resource_types = [
        {
            "resourceTypeGeneral": key,
            "count": len(items),
            "highReadiness": sum(item["citationReadinessScore"] >= 80 for item in items),
        }
        for key, items in sorted(type_groups.items(), key=lambda pair: (-len(pair[1]), pair[0]))
    ]

    tier_summary = [
        {
            "tier": key,
            "count": len(items),
            "meanScore": round(mean(item["citationReadinessScore"] for item in items), 1),
            "highReadiness": sum(item["citationReadinessScore"] >= 80 for item in items),
        }
        for key, items in tier_groups.items()
    ]
    tier_summary.sort(key=lambda item: (-item["meanScore"], item["tier"]))

    data = {
        "project": {
            "name": "CitationWorkbench",
            "version": "0.1.0",
            "generatedAt": generated_at,
            "designBasis": [
                "PortfolioCatalog landing pages reused as canonical citation URLs",
                "CFF, DataCite draft, CiteProc JSON, and BibTeX packet generation",
                "Snapshot-first citation readiness model over the indexed portfolio",
            ],
            "links": {
                "repo": REPO_URL,
                "site": SITE_URL,
                "packetIndex": SITE_URL + "packet-index.json",
                "dataciteDrafts": SITE_URL + "datacite-drafts.json",
                "cslItems": SITE_URL + "citeproc-items.json",
                "e156": SITE_URL + "e156-submission/",
            },
        },
        "metrics": {
            "trackedProjects": tracked,
            "cffPackets": tracked,
            "dataciteDrafts": tracked,
            "cslItems": tracked,
            "bibtexItems": tracked,
            "highCitationReadinessCount": high,
            "highCitationReadinessPercent": round(high / tracked * 100, 1),
            "mediumOrHighCount": medium_or_high,
            "mediumOrHighPercent": round(medium_or_high / tracked * 100, 1),
            "dataciteCoreReadyCount": datacite_core,
            "dataciteCoreReadyPercent": round(datacite_core / tracked * 100, 1),
            "paperBackedCount": paper_backed,
            "paperBackedPercent": round(paper_backed / tracked * 100, 1),
            "journalLinkedCount": journal_linked,
            "journalLinkedPercent": round(journal_linked / tracked * 100, 1),
            "releaseReadyCount": release_ready,
            "releaseReadyPercent": round(release_ready / tracked * 100, 1),
            "meanCitationReadiness": round(mean(item["citationReadinessScore"] for item in records), 1),
        },
        "gapBreakdown": [{"label": key, "count": value} for key, value in gap_counter.most_common()],
        "resourceTypes": resource_types,
        "tiers": tier_summary,
        "projects": records,
    }

    readiness = {
        "project": "CitationWorkbench",
        "generatedAt": generated_at,
        "overview": data["metrics"],
        "projects": records,
    }

    sitemap_lines = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">",
        f"  <url><loc>{SITE_URL}</loc><lastmod>{generated_at}</lastmod></url>",
        f"  <url><loc>{SITE_URL}e156-submission/</loc><lastmod>{generated_at}</lastmod></url>",
        f"  <url><loc>{SITE_URL}e156-submission/assets/dashboard.html</loc><lastmod>{generated_at}</lastmod></url>",
    ]
    for item in packet_index:
        sitemap_lines.append(f"  <url><loc>{item['packetPage']}</loc><lastmod>{generated_at}</lastmod></url>")
    sitemap_lines.append("</urlset>")

    write_json(ROOT / "citation-readiness.json", readiness)
    write_json(ROOT / "packet-index.json", {"generatedAt": generated_at, "packets": packet_index})
    write_json(ROOT / "datacite-drafts.json", {"generatedAt": generated_at, "items": datacite_items})
    write_json(ROOT / "citeproc-items.json", {"generatedAt": generated_at, "items": csl_items})
    write_json(ROOT / "data.json", data)
    write_text(ROOT / "data.js", "window.CITATION_WORKBENCH_DATA = " + json.dumps(data, indent=2) + ";\n")
    write_text(ROOT / "sitemap.xml", "\n".join(sitemap_lines) + "\n")

    print(
        "Built CitationWorkbench "
        f"({tracked} packets, {data['metrics']['highCitationReadinessPercent']:.1f}% high readiness, "
        f"{data['metrics']['releaseReadyPercent']:.1f}% release-ready)."
    )


if __name__ == "__main__":
    main()
