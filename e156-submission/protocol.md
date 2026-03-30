Mahmood Ahmad
Tahir Heart Institute
author@example.com

Protocol: CitationWorkbench - Portfolio Citation Packet Build

This protocol describes a snapshot-first citation study over the bundled `PortfolioCatalog` records for 134 indexed projects. The primary estimand is the proportion of indexed projects reaching high citation readiness, defined as a readiness score of at least 80/100 after combining public landing pages, steward metadata, typed resource mapping, lifecycle resolution, manuscript evidence, release signals, and preserved journal targets. Secondary outputs will report DataCite core-field coverage, release-ready packets, paper-backed coverage, journal-linked coverage, gap counts, tier summaries, and resource-type summaries. The build process will emit `citation-readiness.json`, `packet-index.json`, `datacite-drafts.json`, `citeproc-items.json`, `exports/`, `packets/`, `data.json`, and `data.js`. Generated packets will include CFF, DataCite-style JSON drafts, CiteProc JSON, and BibTeX. Anticipated limitations include draft-only metadata, heuristic authorship stewardship, missing license assertions, sparse journal preservation, and the fact that packet generation does not register DOIs or certify citation correctness for collaborative projects.

Outside Notes

Type: protocol
Primary estimand: proportion of indexed projects reaching high citation readiness
App: CitationWorkbench v0.1
Code: repository root, scripts/build_citation_workbench.py, exports/, packet-index.json, and data-source/
Date: 2026-03-30
Validation: DRAFT

References

1. DataCite. DataCite Metadata Schema Documentation. Accessed 2026-03-30.
2. Druskat S, Spaaks JH, Chue Hong N, et al. Citation File Format 1.2.0. Accessed 2026-03-30.
3. GitHub Docs. About CITATION files. Accessed 2026-03-30.

AI Disclosure

This protocol was drafted from versioned local artifacts and deterministic build logic. AI was used as a drafting and implementation assistant under author supervision, with the author retaining responsibility for scope, methods, and reporting choices.
