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
   between braces, kept as printed. Green underline: a correction from `corrections.json`; hovering
   (or tapping) shows its source, its approval date when recorded, what GRETIL had and what the book prints.

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
| `LICENSE` | Licence notice (CC BY-SA 4.0; the scope of the drafts in `transcriptions/` is stated apart). |
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
| Cone's Dictionary of Pāli (entry marked as wrong reading), approved by hand | 1,023 |
| Hand-corrected copy of the GRETIL file, checked against the scan of the PTS edition | 886 |
| Revised edition of the Saṃyutta, vol. IV (apparatus) | 608 |
| Word Index to the Pāli Tipiṭaka, compared with the copy | 252 |
| Literal reading recorded during review | 135 |
| PTS word index, compared with the copy | 71 |
| Character-level repair (characters layer) | 28 |
| Transcribed from the scan and approved by hand | 24 |
| Corrections published by the PTS (2004) | 14 |
| Answer given by hand during review | 7 |
| Scan of the PTS edition, checked word by word on 2026-10-11 | 6 |
| Corrections published for Majjhima I (W. Pruitt) | 4 |
| Precision study, confirmed against the scan | 1 |

## Reading the pages

- Red underline: an erratum GRETIL prints between braces { }, kept as printed.
- Green underline: a correction (hover or tap for its source). Only the words that change are underlined:
  a line-break hyphen or a neighbouring word that a correction repeats as context is left unmarked.
- Each page shows line numbers in the left margin (1, 5, 10, 15 …), counting only the lines of the text, not
  the running head nor the apparatus. They are drawn by the style sheet and are not part of the text.
- The pages are set in Noto Sans, loaded from Google Fonts; without a connection the browser's default
  sans-serif font is used.
- Note calls are superscript numbers and the apparatus is shown in blue (GRETIL shows both in red). On the eight Saṃyutta II pages read from the
  scan and on three pages GRETIL's markup does not let be read reliably (SN II 60 and 129, Nidd I 161), the
  digits glued to the end of a word are taken as the calls.
- A correction that only deletes text leaves no mark in the HTML; it is still listed in `corrections.json`.

## Volumes

| Volume | File | Pages | Corrections |
|---|---|---:|---:|
| DN I | [`dighn1ou.htm`](corrected/dighn1ou.htm) | 253 | 98 |
| DN II | [`dighn2ou.htm`](corrected/dighn2ou.htm) | 358 | 113 |
| DN III | [`dighn3ou.htm`](corrected/dighn3ou.htm) | 293 | 137 |
| MN I | [`majjn1ou.htm`](corrected/majjn1ou.htm) | 524 | 151 |
| MN II | [`majjn2ou.htm`](corrected/majjn2ou.htm) | 266 | 79 |
| MN III | [`majjn3ou.htm`](corrected/majjn3ou.htm) | 302 | 164 |
| SN I | [`samyu1ou.htm`](corrected/samyu1ou.htm) | 240 | 198 |
| SN II | [`samyu2ou.htm`](corrected/samyu2ou.htm) | 279 | 96 |
| SN III | [`samyu3ou.htm`](corrected/samyu3ou.htm) | 279 | 60 |
| SN IV | [`samyu4ou.htm`](corrected/samyu4ou.htm) | 403 | 736 |
| SN V | [`samyu5ou.htm`](corrected/samyu5ou.htm) | 478 | 106 |
| AN I | [`angut1ou.htm`](corrected/angut1ou.htm) | 304 | 84 |
| AN II | [`angut2ou.htm`](corrected/angut2ou.htm) | 257 | 82 |
| AN III | [`angut3ou.htm`](corrected/angut3ou.htm) | 452 | 37 |
| AN IV | [`angut4ou.htm`](corrected/angut4ou.htm) | 466 | 67 |
| AN V | [`angut5ou.htm`](corrected/angut5ou.htm) | 361 | 28 |
| Sn | [`sutnipou.htm`](corrected/sutnipou.htm) | 223 | 827 |
| Th & Th | [`theragou.htm`](corrected/theragou.htm) | 115 | 63 |
|  | [`therigou.htm`](corrected/therigou.htm) | 52 |  |
| Dhp | [`dhampdou.htm`](corrected/dhampdou.htm) | 120 | 0 |
| Khp | [`khudp_ou.htm`](corrected/khudp_ou.htm) | 9 | 0 |
| Ud | [`udana_ou.htm`](corrected/udana_ou.htm) | 94 | 7 |
| It | [`itivutou.htm`](corrected/itivutou.htm) | 124 | 0 |
| Ja I | [`jatak1ou.htm`](corrected/jatak1ou.htm) | 511 | 86 |
| Ja II | [`jatak2ou.htm`](corrected/jatak2ou.htm) | 451 | 69 |
| Ja III | [`jatak3ou.htm`](corrected/jatak3ou.htm) | 543 | 111 |
| Ja IV | [`jatak4ou.htm`](corrected/jatak4ou.htm) | 499 | 125 |
| Ja V | [`jatak5ou.htm`](corrected/jatak5ou.htm) | 511 | 222 |
| Ja VI | [`jatak6ou.htm`](corrected/jatak6ou.htm) | 596 | 181 |
| Nidd I | [`nidde1ou.htm`](corrected/nidde1ou.htm) | 509 | 2 |
| Nidd II | [`nidde2ou.htm`](corrected/nidde2ou.htm) | 72 | 0 |
| Patis I | [`patis1ou.htm`](corrected/patis1ou.htm) | 196 | 73 |
| Patis II | [`patis2ou.htm`](corrected/patis2ou.htm) | 246 | 38 |
| Mil | [`milindou.htm`](corrected/milindou.htm) | 420 | 0 |
| Vin I | [`vin1maou.htm`](corrected/vin1maou.htm) | 360 | 0 |
| Vin II | [`vin2cuou.htm`](corrected/vin2cuou.htm) | 308 | 0 |
| Vin III | [`vin3s1ou.htm`](corrected/vin3s1ou.htm) | 266 | 1 |
| Vin IV | [`vin4s2ou.htm`](corrected/vin4s2ou.htm) | 351 | 0 |
| Vin V | [`vin5paou.htm`](corrected/vin5paou.htm) | 226 | 0 |
| Dhs | [`dhamsgou.htm`](corrected/dhamsgou.htm) | 264 | 1 |
| Vibh | [`vibhanou.htm`](corrected/vibhanou.htm) | 436 | 0 |
| Dhātuk | [`dhatukou.htm`](corrected/dhatukou.htm) | 113 | 0 |
| Pp | [`pugpan_ou.htm`](corrected/pugpan_ou.htm) | 74 | 13 |
| Kv | [`kathavou.htm`](corrected/kathavou.htm) | 628 | 136 |

Page counts are those of each built file; corrections are counted per volume.

## Scope and limits

- **The critical apparatus (footnotes and variant readings) has NOT been proofread.** The corrections
  apply to the main text only, and every built file says so at the top of the page. The one exception
  is the Sutta Nipāta, whose footnotes were proofread together with its text; its file carries no such warning.
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

The two files in `transcriptions/` are not derived from GRETIL (they are drafts transcribed from printed
PTS editions); their rights have not been assessed. See `LICENSE`.
