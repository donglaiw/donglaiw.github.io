---
name: add-paper
description: >
  Add a new publication entry to index.html on Donglai Wei's homepage. Downloads the
  paper PDF into paper/ with the canonical filename, then inserts a publication chunk
  in the right year block of index.html using teaser/todo.png as the placeholder image.
  Trigger when the user says "add a paper", "add this paper to index.html", "add publication",
  or invokes /add-paper. Does NOT read the paper PDF — relies on metadata supplied by the
  user or scraped from the landing page.
---

# add-paper

Add a new publication to `index.html`. Two artifacts: a PDF in `paper/` and a `<tr>` chunk in the publications table.

## Inputs needed

Before doing anything, you must know:

1. **Paper URL** — either a direct PDF URL or a landing page (arXiv, bioRxiv, journal). Provided by the user.
2. **Title** — full paper title.
3. **Author list** — comma-separated, in publication order. Wrap `Donglai Wei` in `<b>...</b>`. If the user did not give the list, fetch the landing page with WebFetch and extract it. Do **not** open the PDF.
4. **Venue + year** — e.g. `bioRxiv 2026`, `Nature 2026`, `MICCAI 2025`. Year drives placement in `index.html`.
5. **Short name** — 1–2 word stem for the filename, e.g. `hydra`, `cytotape`, `trisam`. Ask the user if not obvious.
6. **Topic class** — one of `topic_sci` (neuroscience/discovery, default for biology papers), `topic_data` (dataset/benchmark), or no class (general AI). Match the surrounding entries' style for the year block if unsure.

If any of (2)–(6) are missing and cannot be inferred, ask the user with **one** consolidated AskUserQuestion before proceeding. Do not invent author lists.

## Step 1 — download the PDF

Filename convention: `paper/<year>_<venue>_<shortname>.pdf` where `<venue>` is a short lowercase tag matching existing files (`nature`, `cb` for Current Biology, `biorxiv`, `arxiv`, `tmi`, `jbhi`, `miccai`, `cvpr`, `eccv`, `iccv`, `nips`/`neurips`, `iclr`, `icml`, `media` for MedIA, `pnas`, `science`, `sciadv`, `nc` for Nature Comm, `nm` for Nature Methods). Glob `paper/<year>_*` first to mirror an existing tag for the same venue rather than guessing a new one.

Download with `curl`. bioRxiv and many journals 403 the default curl UA — always use a browser UA:

```bash
curl -sSL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  -o paper/<year>_<venue>_<shortname>.pdf "<pdf_url>"
```

For arXiv abstracts, transform `arxiv.org/abs/XXXX.YYYYY` → `arxiv.org/pdf/XXXX.YYYYY.pdf`.
For bioRxiv landing pages, append `.full.pdf` to the version URL.

After download, verify the file is a real PDF and not an HTML error page:

```bash
file paper/<year>_<venue>_<shortname>.pdf
ls -la paper/<year>_<venue>_<shortname>.pdf
```

The output must say `PDF document` and the size must be more than ~50 KB. If not, stop and report to the user — do not insert a broken link.

## Step 2 — insert the chunk in `index.html`

Locate the year block. Each year is introduced by:

```html
<tr>
    <td>
        <font size=5><b><i>YYYY</i></b>
    </td>
</tr>
<tr>
    <td height=5px></td>
</tr>
<tr>
    <td height=15px></td>
</tr>
```

Insert the new entry as the **first** entry of the matching year (just after that header trio of `<tr>`s). If the year does not yet exist, add the year header trio above the most recent existing year (years are listed newest-first).

Template (use `teaser/todo.png` as placeholder; the user will swap it later):

```html
<tr>
    <td width=30%><img height=140 src="teaser/todo.png" /></td>
    <td class="<topic_class>">
        <h3><a href="<paper_url>"><title></a></h3>
        <h4><authors with <b>Donglai Wei</b> bolded><br />
            <em><venue> <year></em><br><span class="links">
            </span>
        </h4>
    </td>
</tr>
<tr>
    <td height=15px></td>
</tr>
```

Notes:
- `<topic_class>` is one of `topic_sci`, `topic_data`, or omit `class="..."` entirely for general AI papers — match neighbors in the same year.
- The trailing spacer `<tr><td height=15px></td></tr>` separates entries; keep it.
- Use the Edit tool with enough surrounding context to make the `old_string` unique (the year header trio is unique per year).
- Do not include `[Code]` / `[Data]` / `[Website]` links unless the user supplied them.

## Step 3 — confirm

Report to the user:

- The PDF path that was created and its size.
- The year block where the entry was inserted.
- A reminder that `teaser/todo.png` is a placeholder and a real teaser image should be added at `teaser/<year>_<venue>_<shortname>.png` later.

Do not commit. The user will review and commit themselves.

## What this skill does NOT do

- Does not read or parse the PDF content.
- Does not fetch or generate a teaser image.
- Does not edit the "Research Highlights" section at the top of `index.html`.
- Does not git add / commit / push.
