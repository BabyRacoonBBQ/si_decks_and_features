# Repository scope

- Maintain two parts: the StressThermal feature introduction and the StressThermal case library. They share `sinterconnect-catalog/`; `hybrid-bonding/hybrid-bonding.html` is the maintained companion presentation.
- Xiaodong's presentation (`芯片与封装仿真_HTML幻灯片.html`) is reference material reconstructed by OCR from screenshots. Do not rewrite it or the originals in `Resources/xiaodong-originals/` as part of routine maintenance. Verify transcribed claims against their sources before using them in maintained pages.
- Preserve existing page styles, unrelated content and development-status labels unless the user requests a change. Edit HTML by default; export PPTX only when requested. Avoid side notes and text-heavy slides.
- Keep real images, source credits, units and magnification information. Do not invent results, dimensions, benchmark timings or recovery claims.
- Distinguish retained historical output, current solver validation and GT-A comparison. A source archive or successful page build is not a new simulation.
- Keep case inputs, commands, solver identity evidence and required page resources. Do not delete case TDRs, archives, logs or scripts based only on their extension or size.
- `rea-review/`, `rea-feature-analysis.md`, `.report-runtime/` and `sinterconnect-catalog-backups/` are local material outside this repository's maintained scope.
- Before committing, run `python sinterconnect-catalog/check_catalog_links.py`. Visually check changed HTML interactions. Do not run solver or historical environment scripts merely to check webpage changes.
