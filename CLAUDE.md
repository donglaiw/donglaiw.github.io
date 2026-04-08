# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

This is Donglai Wei's personal academic homepage, served as a static site via GitHub Pages from `donglaiw.github.io`. There is no build system, no package manager, and no tests — files are served directly. Editing HTML is the primary form of work.

## Architecture

- `index.html` (~2000 lines) is the entire homepage. It is hand-edited XHTML with inline `<style>` and inline `<table>`-based layout. Almost every change to the site is a localized edit somewhere in this file.
- `css/style.css` and `css/reset-fonts-grids-tabs.css` provide site-wide styles. Most paper-list styling, however, lives in inline `<style>` near the top of `index.html` (e.g. `.paper-tag`, `.ns-tag`, `.data-tag`, `.casual-tag` color tags used by the publication entries).
- `paper/` holds PDFs of publications. Filenames follow the convention `YYYY_<venue>_<shortname>.pdf` (e.g. `2025_cb_hydra.pdf`, `2026_nature_cytotape.pdf`). Supplementary files use the `_supp` suffix.
- `teaser/` holds teaser images for publications, named to match the paper (e.g. `2026_nature_cytotape.png`). When adding a new publication entry to `index.html`, drop the PDF in `paper/` and the teaser image in `teaser/` using the same `YYYY_<venue>_<shortname>` stem.
- `bio/` holds profile and biography photos; `lab/` holds group-member photos.
- `proj/{learnAoT,mneuron,youMVOS}/` are self-contained per-project mini-sites with their own `index.html`.
- `demo/` holds video files (mp4/mov/avi) referenced from project pages.
- `js/` contains vendored third-party libraries (jQuery 1.8.3, jwplayer, swfobject, ddaccordion). Do not assume modern JS tooling.
- `page/index.html` is a meta-refresh redirect to an external project page (`connectomics-bazaar.github.io/proj/mitoEM/`).
- `tmp/` is gitignored scratch space.

## Publication entries

The `Publications` section of `index.html` is a single large `<table class='pub'>` grouped by year. Each entry follows a fixed pattern: a `<tr>` with a teaser `<img>` from `teaser/`, a `<td>` whose class encodes the topic color (`topic_sci`, `topic_data`, etc.), an `<h3>` linking the title, an `<h4>` author list with `<b>Donglai Wei</b>` bolded, the venue in `<em>`, and a `<span class="links">` with `[Code]`, `[Data]`, `[Website]`, etc. When adding a new paper, copy the nearest existing entry as a template rather than writing markup from scratch — spacing rows (`<tr><td height=15px></td></tr>`) between entries are load-bearing for visual layout.

The "Research Highlights" section near the top uses four colored tag classes that correspond to the publication-section topic colors: `paper-tag` (AI, gray), `data-tag` (Dataset, blue), `ns-tag` (Neuroscience, yellow), `casual-tag` (Discovery, green). Keep new entries consistent with this color scheme.

## Local preview

There is no build step. To preview changes, open `index.html` directly in a browser, or serve the directory with any static server (e.g. `python3 -m http.server`) from the repo root. Deployment happens automatically via GitHub Pages on push to `master`.

## Conventions

- The site uses XHTML 1.0 Transitional with `<table>`-based layout and many inline attributes (`width`, `height`, `align`, `<font>`). Do not "modernize" this to semantic HTML/CSS unless explicitly asked — the existing structure is intentional and consistent across hundreds of entries.
- Author names link out to personal/lab pages; preserve existing links when editing entries.
- Alumni and historical content are often kept in HTML comments (`<!-- ... -->`) rather than deleted. Check commented blocks before assuming something is missing.
