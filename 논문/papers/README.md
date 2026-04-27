# Reference Papers Folder Guide

## Folder Structure

```text
reference-paper-root/
├── 0.55 High-NA EUV reference paper list.txt
├── high_na_euv_paper_search_handoff.md
└── papers/
    ├── INDEX.md
    ├── README.md
    ├── 01_stochastic_effects_LWR.md
    ├── 02_SHARP_actinic_microscope.md
    ├── ...
    └── 21_statistics_EUV_nanopatterns.md
```

## Reading Order

1. Start with `INDEX.md` for the 21-paper overview, topic groups, phase mapping,
   and the recommended MVP paper set.
2. Open the individual paper notes for metadata and project-specific
   implementation points.
3. PDF files were not downloaded automatically because external network access
   is restricted in the current environment. Use the link, DOI, or PDF URL
   fields in each note to download papers manually in a browser.
4. The open-access papers marked in `INDEX.md` can be downloaded immediately.

## Individual Paper Note Template

Each paper note follows this structure:

- Link, DOI, and PDF URL.
- Year, authors, conference, or journal.
- Topic, priority, and PDF status.
- Core problem.
- Model or algorithm used.
- Key formula or result.
- Project application points with phase mapping.
- Implementation difficulty: Low, Medium, or High.
- Notes.

## Next Actions

- [ ] Download open-access PDFs and store them in a `papers/pdfs/` subfolder.
- [ ] Read the MVP papers, especially #19, #9, and #12.
- [ ] Add the most important formulas to the relevant paper-note sections.
- [ ] Download paywalled papers through an institutional library when available.
- [ ] Verify the mapping for paper #13.
