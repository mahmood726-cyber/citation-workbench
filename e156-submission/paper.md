Mahmood Ahmad
Tahir Heart Institute
author@example.com

Paper: CitationWorkbench - Citation Packet Generation for the C Drive Portfolio

Can an internal research portfolio be converted into citation packets and DOI-facing metadata without hand-writing records one by one? We reused bundled PortfolioCatalog records, which exposed public landing pages for 134 indexed projects. CitationWorkbench v0.1 generated CFF, DataCite draft JSON, CiteProc JSON, and BibTeX for every project while scoring citation readiness from lifecycle, release, journal, and manuscript signals. High citation readiness reached 64.2 percent (86 of 134 projects), release-ready citation packets reached 50.7 percent (68 of 134), and DataCite core fields were derivable for all 134 records. Paper-backed coverage reached 68.7 percent, but only 4.5 percent preserved a target journal, making journal metadata the dominant citation gap rather than missing titles or URLs. This shifts the next portfolio task toward preserving venue targets, licensing, and authorship decisions instead of inventing more metadata shells. The packet factory improves citation hygiene, but it still produces draft metadata, does not register DOIs, and cannot prove authorship for collaborative work.

Outside Notes

Type: methods
Primary estimand: proportion of indexed projects reaching high citation readiness
App: CitationWorkbench v0.1
Code: repository root, scripts/build_citation_workbench.py, exports/, packet-index.json, and data-source/
Date: 2026-03-30
Validation: PASS
Protocol: e156-submission/protocol.md
