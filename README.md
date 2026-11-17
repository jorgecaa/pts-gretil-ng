# pts-gretil-ng

Reproducible build of the Pali Text Society (PTS) editions of the Pali canon from
[GRETIL](https://gretil.sub.uni-goettingen.de/), with proofreading corrections marked in the text.

    python3 build.py            # 1. download GRETIL  2. read corrections.json  3. write corrected/*.htm
    python3 build.py --verify   # only check the downloaded files against the expected checksums

Requirements: Python 3.9+ and git. No other dependency. The download takes about 150 MB on disk
(folder `mirror/`, not committed); the build itself takes under a minute.

The build is deterministic: after `python3 build.py`, `git status` must show no change in `corrected/`.

## How it works

1. **Download.** `build.py` fetches one pinned commit of
   [INDOLOGY/GRETIL-mirror](https://github.com/INDOLOGY/GRETIL-mirror) (only the Pali folders).
2. **Verify.** The SHA-256 of each GRETIL file must equal the one recorded in `corrections.json`;
   otherwise the build stops, because the corrections were made on exactly those files.
3. **Correct.** Each correction replaces the text GRETIL has with the text the printed book prints.
   A correction that does not fit exactly the stated number of times stops the build; nothing is
   applied halfway.
4. **Write.** One HTML file per GRETIL file in `corrected/` (also committed here). GRETIL's own opening
   (title, notice, licence, terms of use) is kept unchanged. Red underline: an erratum GRETIL prints
   between braces, kept as printed. Blue underline: a correction from `corrections.json`; hovering
   shows its source, approval date, what GRETIL had and what the book prints.

`corrections.json` holds the pinned mirror commit, the checksums, the corrections and eight
Saṃyutta II pages (109-116) that GRETIL's file lacks; those pages were read from the scan and
reviewed, replace GRETIL's broken text whole, and carry no marks. The GRETIL files themselves are
never modified. `corrections.json` is exported from the corrections layer of the foureditions
project, where the review is done; it is data, not written by hand, and is updated from there.

## Files

| Path | What it is |
|---|---|
| `build.py` | The whole build: download, verify, correct, write. |
| `corrections.json` | Pinned mirror commit, checksums, corrections with their sources. |
| `transcriptions/` | Two HTML files: unreviewed draft transcriptions of the Nettippakaraṇa and Peṭakopadesa. Not built by `build.py`. |
| `corrected/` | The built files (44 HTML files, 43 volumes), committed for convenience. |

## Corrections and their sources

Manual proofreading corrections against the scans of the printed edition are marked in the text.
Each correction was approved by a person. Corrections derived from the Cone dictionary, Jackson's
revised Saṃyutta IV apparatus or word indices are identified by their source label (shown in the
popup of each marked word and in `corrections.json`).

4,191 corrections in total:

| Source label | Corrections |
|---|---|
| Sheet corrected by hand against the scan of the PTS edition | 1,132 |
| Cone's Dictionary of Pāli (entry marked as wrong reading), confirmed against the scan | 1,023 |
| Hand-corrected copy of the GRETIL file, checked against the scan of the PTS edition | 886 |
| Revised edition of the Saṃyutta, vol. IV (apparatus) | 608 |
| Word Index to the Pāli Tipiṭaka, compared with the copy | 252 |
| Literal reading recorded during review | 135 |
| PTS word index, compared with the copy | 71 |
| Character-level repair (characters layer) | 28 |
| Transcribed from the scan and approved by hand | 24 |
| Corrections published by the PTS (2004) | 14 |
| Answer given by hand during review | 7 |
| Earlier hand correction | 6 |
| Corrections published for Majjhima I (W. Pruitt) | 4 |
| Precision study, confirmed against the scan | 1 |

## Scope and limits

- **The critical apparatus (footnotes and variant readings) has NOT been proofread.** The corrections
  apply to the main text only, and every built file says so at the top of the page. The one exception
  is the Sutta Nipāta, whose footnotes were proofread together with its text; its file carries no such warning.
- A correction that only deletes text leaves no mark in the HTML; it is still listed in `corrections.json`.
- **Included:** every GRETIL volume of the PTS editions that the foureditions review service does not
  block: 43 volumes (Dīgha, Majjhima, Saṃyutta, Aṅguttara, Vinaya, Khuddakapāṭha, Dhammapada, Udāna,
  Itivuttaka, Sutta Nipāta, Theragāthā and Therīgāthā, Jātaka, Mahāniddesa and Cūḷaniddesa,
  Paṭisambhidāmagga, Milindapañha, Dhammasaṅgaṇī, Vibhaṅga, Dhātukathā, Puggalapaññatti,
  Kathāvatthu). A volume without corrections is rebuilt as GRETIL has it, with the licence and the notices.
- **Left out because the review service blocks them** (no compatible scan of the printed edition to
  check against): Vimānavatthu, Petavatthu, Apadāna, Buddhavaṃsa, Cariyāpiṭaka, Yamaka and Paṭṭhāna.
- **Nettippakaraṇa and Peṭakopadesa** are not in GRETIL, so they are not part of this build. The folder
  `transcriptions/` holds one HTML file for each, transcribed from the scans of the printed PTS editions.
  **They are unreviewed drafts**: no page has been proofread by a person; each file says so at the top.
- **The Sutta Nipāta, Theragāthā and Therīgāthā** were proofread directly in the GRETIL file. Their
  differences from the mirror's file are written in `corrections.json` as ordinary corrections
  (source label: "Hand-corrected copy of the GRETIL file"), so they are reproducible from the mirror too.
- The proofreading is not finished for every book.
- Corrections are by Jorge Contreras (github.com/jorgecaa), from the foureditions project.

## Licence

The GRETIL texts are © Pali Text Society and Dhammakaya Foundation, 2015, under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Everything in this repository (the
code, `corrections.json` and the built files in `corrected/`) is a derivative and is released under
the same licence, with the same notice.
