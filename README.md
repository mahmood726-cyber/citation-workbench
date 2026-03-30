# CitationWorkbench

CitationWorkbench is a standalone citation-readiness layer for the C-drive research portfolio.

## Why this exists

The portfolio now has registry, FAIR, operations, drive telemetry, and public catalog layers, but it still lacked one reproducible surface that turns those records into citation packets and DOI-ready metadata drafts.

## What it does

- reuses bundled `PortfolioCatalog` records as canonical public landing pages
- generates one citation packet for every indexed project
- exports CFF, DataCite draft JSON, CiteProc JSON, and BibTeX
- scores citation readiness across the indexed portfolio
- ships a static GitHub Pages dashboard and E156 bundle

## Outputs

- `citation-readiness.json` - scored per-project citation readiness model
- `packet-index.json` - lookup table for generated packet files
- `datacite-drafts.json` - aggregated DataCite-style draft metadata
- `citeproc-items.json` - aggregated CiteProc/CSL JSON items
- `exports/` - generated CFF, DataCite, CSL, and BibTeX files
- `packets/` - generated packet landing pages
- `data.json` and `data.js` - dashboard payloads
- `CITATION.cff` - citation file for CitationWorkbench itself
- `e156-submission/` - paper, protocol, metadata, and reader page

## Rebuild

Run:

`python C:\Users\user\CitationWorkbench\scripts\build_citation_workbench.py`

## Scope note

This project prepares citation metadata and draft DOI-facing records. It does not register DOIs, prove authorship for every collaborative project, or replace project-specific release policies.
