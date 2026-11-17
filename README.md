# pts-gretil-ng

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24314138.svg)](https://doi.org/10.5281/zenodo.24314138)

Reproducible build of the Pali Text Society (PTS) editions of the Pali canon from
[GRETIL](https://gretil.sub.uni-goettingen.de/), with proofreading corrections marked in the text.

**Read online:** <https://jorgecaa.github.io/pts-gretil-ng/>. **Licence:** texts, data and built files
CC BY-SA 4.0; code CC0 1.0 (GitHub's sidebar shows only the first; see [Licence](#licence)).
**Cite:** [Citing](#citing).

    python3 build.py            # 1. download GRETIL  2. read corrections.json  3. write corrected/*.htm and index.html
    python3 build.py --verify   # only check the downloaded files against the expected checksums

Requirements: Python 3.9+ and git. No other dependency. The download takes about 150 MB on disk
(folder `mirror/`, not committed); the build itself takes under a minute.

The build is deterministic: after `python3 build.py`, `git status` must show no change in `corrected/`
nor in `index.html`. A GitHub Action (`.github/workflows/build.yml`) checks this on every push, with
Python 3.9 and 3.13.

**Reading online:** the pages are meant to be opened in a browser, where hovering over a marked word
shows its popup; GitHub's file view shows their source instead. They are published with GitHub Pages
at <https://jorgecaa.github.io/pts-gretil-ng/>.

## How it works

1. **Download.** `build.py` fetches one pinned commit of
   [INDOLOGY/GRETIL-mirror](https://github.com/INDOLOGY/GRETIL-mirror) (only the Pali folders).
2. **Verify.** The SHA-256 of each GRETIL file must equal the one recorded in `corrections.json`;
   otherwise the build stops, because the corrections were made on exactly those files.
3. **Correct.** Where GRETIL departs from the printed edition, the correction replaces GRETIL's text
   with the printed reading. Corrections of the edition itself published by the PTS (Cone, Jackson,
   Pruitt, the corrigenda printed in the volume), which mark a printed reading as wrong and give the reading to adopt, are applied too: the
   text gives the reading to adopt, and the popup on the words concerned gives the printed reading it
   replaces. In those places the text is no longer the printed edition.
   A correction that does not fit exactly the stated number of times stops the build; nothing is
   applied halfway.
4. **Write.** One HTML file per GRETIL file in `corrected/` (also committed here). GRETIL's own opening
   (notice, licence, terms of use) is kept unchanged; the title gains "(with approved corrections
   marked)". The marks are described under
   [Reading the pages](#reading-the-pages).

`corrections.json` holds the pinned mirror commit, the checksums, the corrections and eight
Saṃyutta II pages (109-116): GRETIL's file lacks pages 110-116 and cuts page 109 short. Those pages
were read from the scan by machine (OCR for 109-112, AI for 113-116), reviewed by hand, replace
GRETIL's text whole, and carry no marks. The GRETIL files themselves are
never modified. `corrections.json` is exported from the corrections layer of the foureditions
project, where the review is done; it is data, not written by hand, and is updated from there.

**The foureditions project is not public.** Its review records (the review sheets, the corrected copies,
the answers given during review) cannot be consulted. What can be checked from outside is each
correction in `corrections.json` (volume, page, GRETIL's reading, the printed reading, its source and
date) against a scan of the printed edition. The column «Public scan» in [Volumes](#volumes) says which
volumes have a scan published (see [Scans of the printed editions](#scans-of-the-printed-editions));
for the others, checking needs a copy of the printed edition.

## Files

| Path | What it is |
|---|---|
| `build.py` | The whole build: download, verify, correct, write. |
| `corrections.json` | Pinned mirror commit, checksums, corrections with their sources. |
| `LICENSE` | Full text of the licence of the texts, the data and this README (CC BY-SA 4.0); the code is CC0 1.0 (see [Licence](#licence)). |
| `NOTICE` | Licence notice: copyright of the GRETIL texts, what derives from them, credits. |
| `corrected/` | The built files (44 HTML files, 43 volumes), committed for convenience. Each keeps the name of its GRETIL file (`dighn1ou.htm`: Dīgha-nikāya I); [Volumes](#volumes) gives the volume of each. |
| `index.html` | Entry page with a link to every built file (written by `build.py`; the GitHub Pages home). |
| `CITATION.cff` | How to cite this repository (cite the release used: `corrections.json` changes between releases). |
| `CONTRIBUTING.md` | How to report an error. |
| `.github/ISSUE_TEMPLATE/` | The form for reporting an error in the text. |
| `.github/workflows/build.yml` | The check that the build reproduces the committed files. |

## Corrections and their sources

Each correction was approved by a person. Every correction in `corrections.json` has a `kind`:

- **transcription**: GRETIL departs from the printed edition; checked against the scan of the edition.
  Applied to the text.
- **notation**: GRETIL's signs written as the book prints them (`me^so` for `mêso`, `<…>` for `[…]` or
  `(…)`); the letters are the same. Applied.
- **emendation**: a correction of the edition itself, published by the PTS: M. Cone's Dictionary of
  Pāli (an entry that marks the printed reading as wrong), P. Jackson's revision of Saṃyutta IV, W. Pruitt's
  correction lists, the corrigenda printed in the volume itself. The authority declares the printed reading wrong and gives the reading to adopt.
  Applied: the text gives the reading to adopt, and the popup gives the printed reading it replaces and the
  authority. A correction taken from Cone also has `entry`: the article(s) of the Dictionary of Pāli that
  cite the passage, found mechanically from the passage cited and the forms of Cone's note. Where Cone
  gives more than one reading as correct, `alternatives` lists the others, with their editions.
- **wrong-reading**: not a correction. Cone marks the printed reading as wrong and gives no reading to
  adopt, or gives several naming no edition: the word is left as printed and marked (`gretil` and `book`
  are the same); `alternatives` lists the readings he proposes, if any.

**Cone's notes.** What is done with a note of the Dictionary of Pāli depends on what it says:

- it marks the printed reading as wrong and gives no reading to adopt: the text is not changed, and the
  word is marked as a wrong reading (purple dashed underline);
- it gives one reading to adopt: that reading replaces the printed one;
- it says explicitly that more than one reading is correct, naming the editions that read them: the
  text adopts the reading of Ce (the Sri Lankan edition), or failing it that of Be (the Burmese
  edition), or failing it that of Se (the Thai edition), always in that order; the popup gives the
  other readings with their editions;
- it gives more than one reading without naming the edition of any: the text is not changed; the word is
  marked as a wrong reading, and the popup gives the readings Cone proposes;
- it reports readings without saying whether they are correct: not applied.

Each note is applied as it stands; the notes are not compared with one another. Where two notes of
Cone's concern the same word and the text can carry only one reading, a note that gives a reading with
its editions prevails over one that does not, in the order Ce, Be, Se, and a note that cites only the
lemma does not replace the word as printed.

Not marked: a wrong reading is marked only where its word stands once on the page, or once on the line
Cone cites. 66 are not marked: 58 whose form, as recorded in the review, is not a whole word on the page
(split at the end of a line, cited as a lemma or as a member of a compound), 2 with more than one site
on the cited line, and 6 on a word that a correction from another of Cone's notes writes. Notes whose
site was not found on the page, and readings Cone gives with his mark of doubtful quantity (˘), are not
applied.

4,251 corrections and 174 marked wrong readings in total:

| Kind | Source label (evidence or authority) | Corrections |
|---|---|---:|
| transcription | Review sheet, checked by hand against the scan of the PTS edition | 961 |
| transcription | Copy of the GRETIL file corrected by hand, checked against the scan of the PTS edition | 886 |
| transcription | Flagged by the Word Index to the Pāli Tipiṭaka (Ousaka 2019), checked by hand against the scan of the PTS edition | 252 |
| transcription | Printed reading, checked by hand against the scan of the PTS edition | 134 |
| transcription | Flagged by the PTS word index (Ousaka, Pruitt and Jackson 2019), checked by hand against the scan of the PTS edition | 71 |
| transcription | Read on the scan of the PTS edition by machine; checked and approved by hand | 24 |
| transcription | Answer during review, checked by hand against the scan of the PTS edition | 44 |
| transcription | Earlier correction, checked by hand word by word against the scan of the PTS edition on 2026-10-11 | 6 |
| transcription | Precision sample, checked by hand against the scan of the PTS edition | 1 |
| notation | Notation only: GRETIL's signs (^ for a circumflex, <…> for brackets or parentheses) written as the book prints them; same letters | 28 |
| emendation | M. Cone, A Dictionary of Pāli (entry marked as a wrong reading of the PTS edition) | 1,163 |
| emendation | L. Feer, Saṃyutta-nikāya IV, revised by P. Jackson (PTS, 2014) | 609 |
| emendation | W. Pruitt, Corrections for the 2004 reprint of Majjhima-nikāya II (PTS, 2008) | 14 |
| emendation | W. Pruitt, M I corrections (PTS, 2009) | 4 |
| emendation | Corrigenda printed in the PTS edition itself | 54 |
| wrong-reading | M. Cone, A Dictionary of Pāli (entry marked as a wrong reading of the PTS edition) | 174 |

## Reading the pages

- Red underline: an erratum already corrected in GRETIL. GRETIL puts its correction in braces { } in
  place of the printed reading, which it does not give (e.g. MN I 4: the book prints «maññi», GRETIL
  «{maññī}»). The content between braces is kept as in GRETIL (unchanged by the proofreading, except
  for notation).
- Green underline: GRETIL departs from the printed edition; the text gives the printed reading.
- Orange dotted underline: the PTS has published a correction of the edition here (Cone, Jackson,
  Pruitt, or the corrigenda of the volume), marking the printed reading as wrong; applied: the text gives the reading the authority adopts,
  and the popup the printed reading it replaces. Where Cone gives more than one reading as correct, the
  popup also gives the others with their editions: `from «cilīmaṃ» corrected by DOP (see s.v. cilīmaṃ) |
  Cone also gives «vilimaṃsaṃ» (Be, Se); the text follows Ce, then Be, then Se`.
- Purple dashed underline: Cone marks the printed reading as wrong and gives no reading to adopt (or
  gives several, naming no edition); the word is left as printed: `«uppajjaṃ» marked as a wrong reading
  by DOP (see s.v. uppajjati) | Cone proposes «upapajja» or «upapajjaṃ», naming no edition`.
- Hover over (or tap) a marked word: the popup gives the reading the text replaced and who corrected it:
  `from «ratheni» (GRETIL) corrected by the PTS ed. (scan)` (green: checked on the scan of the PTS
  edition), `from «sattattāya» corrected by DOP (see s.v. pariṇamati)` or
  `from «Pāgagginā» corrected by Jackson, SN IV (2014)` (orange). «DOP»: M. Cone, *A Dictionary of
  Pāli*. «s.v.»: the article of Cone's
  Dictionary of Pāli where the reading is marked as wrong; when Cone cites the passage in more than one
  article, all are given. The full citation of each source, the kind of evidence and the date of each
  correction are in `corrections.json` (see «Corrections and their sources»).
  Only the words that change are underlined: a line-break hyphen or a neighbouring word that a
  correction repeats as context is left unmarked.
- Each page of the printed edition can be linked to: add `#p` and its number to the address of the
  volume (DN I, page 45: `https://jorgecaa.github.io/pts-gretil-ng/corrected/dighn1ou.htm#p45`). The top of
  every volume links back to the list of volumes and to this repository.
- Each page shows line numbers in the left margin (1, 5, 10, 15 …), counting only the lines of the text, not
  the running head nor the apparatus. They are drawn by the style sheet and are not part of the text.
- The pages are set in Noto Sans, loaded from Google Fonts; without a connection the browser's default
  sans-serif font is used.
- Note calls are superscript numbers and the apparatus is shown in blue (GRETIL shows both in red). On the eight Saṃyutta II pages read from the
  scan and on three pages GRETIL's markup does not let be read reliably (SN II 60 and 129, Nidd I 161), the
  digits glued to the end of a word are taken as the calls.
- A correction that only deletes text is marked on the word next to the deleted words. Corrections of a
  running head or of the apparatus are marked too; the content between braces is marked only in the body.

## Volumes

Proofreading corrections: transcription and notation corrections, where GRETIL departs from the printed
edition. PTS corrections of the edition: corrections published by the PTS (Cone, Jackson, Pruitt, the corrigenda of the volume) of
readings the printed edition gets wrong. Both are applied to the text. The two columns do not overlap:
each correction is counted once. Of the 634 PTS corrections of SN IV, 609 come from P. Jackson's revision
of that volume (2014).
Wrong readings marked (DOP): printed readings Cone marks as wrong without giving a reading to adopt;
the word is left as printed, so they are not corrections and are not counted in the other columns.

Every volume listed with a file was reviewed in the foureditions review service. The counts give the
corrections approved so far. A volume with 0 proofreading corrections has no approved correction yet; this
does not mean it was proofread in full and found free of errors, since the proofreading is not finished
for every book (see «Scope and limits»). Ja I carries only PTS corrections of the edition.

Public scan: "yes" when the scan of the printed edition used for proofreading is published at the
Internet Archive (see «Scans of the printed editions»); otherwise the scan used is not published.

Struck through, at the end: the books the review service leaves out, which are not built. A review needs
a scan of the same printed edition that GRETIL transcribes; six of these books have none usable, and the
Yamaka is excluded:

- **Vimānavatthu and Petavatthu, Buddhavaṃsa and Cariyāpiṭaka**: GRETIL gives the later PTS editions by
  N. A. Jayawickrama (1977 and 1974); the scans at hand are of the earlier editions (Gooneratne 1886,
  Minayeff 1888, Morris 1882), a different text.
- **Apadāna**: the scan at hand was withdrawn, because its images lose the diacritics.
- **Paṭṭhāna**: no scan of the PTS edition is at hand.
- **Yamaka**: its PTS edition is excluded from the review because of its many abbreviations.

| Volume | File | Pages | Proofreading corrections | PTS corrections of the edition | Wrong readings marked (DOP) | Public scan |
|---|---|---:|---:|---:|---:|---|
| DN I | [`dighn1ou.htm`](corrected/dighn1ou.htm) | 253 | 35 | 81 | 2 |  |
| DN II | [`dighn2ou.htm`](corrected/dighn2ou.htm) | 358 | 81 | 41 | 5 |  |
| DN III | [`dighn3ou.htm`](corrected/dighn3ou.htm) | 293 | 98 | 40 | 7 |  |
| MN I | [`majjn1ou.htm`](corrected/majjn1ou.htm) | 524 | 133 | 19 | 0 | yes |
| MN II | [`majjn2ou.htm`](corrected/majjn2ou.htm) | 266 | 36 | 43 | 4 |  |
| MN III | [`majjn3ou.htm`](corrected/majjn3ou.htm) | 302 | 128 | 35 | 3 |  |
| SN I | [`samyu1ou.htm`](corrected/samyu1ou.htm) | 240 | 141 | 57 | 4 |  |
| SN II | [`samyu2ou.htm`](corrected/samyu2ou.htm) | 279 | 78 | 18 | 2 | yes |
| SN III | [`samyu3ou.htm`](corrected/samyu3ou.htm) | 279 | 42 | 18 | 1 | yes |
| SN IV | [`samyu4ou.htm`](corrected/samyu4ou.htm) | 403 | 102 | 634 | 1 | yes |
| SN V | [`samyu5ou.htm`](corrected/samyu5ou.htm) | 478 | 76 | 30 | 5 | yes |
| AN I | [`angut1ou.htm`](corrected/angut1ou.htm) | 304 | 61 | 23 | 1 | yes |
| AN II | [`angut2ou.htm`](corrected/angut2ou.htm) | 257 | 51 | 31 | 3 | yes |
| AN III | [`angut3ou.htm`](corrected/angut3ou.htm) | 452 | 22 | 13 | 5 | yes |
| AN IV | [`angut4ou.htm`](corrected/angut4ou.htm) | 466 | 46 | 21 | 4 | yes |
| AN V | [`angut5ou.htm`](corrected/angut5ou.htm) | 361 | 23 | 5 | 2 | yes |
| Sn | [`sutnipou.htm`](corrected/sutnipou.htm) | 223 | 827 | 0 | 0 |  |
| Th | [`theragou.htm`](corrected/theragou.htm) | 115 | 31 | 0 | 0 | yes |
| Thī | [`therigou.htm`](corrected/therigou.htm) | 52 | 32 | 0 | 0 | yes |
| Dhp | [`dhampdou.htm`](corrected/dhampdou.htm) | 120 | 8 | 0 | 0 |  |
| Khp | [`khudp_ou.htm`](corrected/khudp_ou.htm) | 9 | 0 | 0 | 0 |  |
| Ud | [`udana_ou.htm`](corrected/udana_ou.htm) | 94 | 7 | 0 | 0 |  |
| It | [`itivutou.htm`](corrected/itivutou.htm) | 124 | 0 | 0 | 0 | yes |
| Ja I | [`jatak1ou.htm`](corrected/jatak1ou.htm) | 511 | 0 | 86 | 14 |  |
| Ja II | [`jatak2ou.htm`](corrected/jatak2ou.htm) | 451 | 1 | 68 | 15 | yes |
| Ja III | [`jatak3ou.htm`](corrected/jatak3ou.htm) | 543 | 5 | 105 | 12 |  |
| Ja IV | [`jatak4ou.htm`](corrected/jatak4ou.htm) | 499 | 19 | 106 | 20 | yes |
| Ja V | [`jatak5ou.htm`](corrected/jatak5ou.htm) | 511 | 24 | 196 | 34 | yes |
| Ja VI | [`jatak6ou.htm`](corrected/jatak6ou.htm) | 596 | 7 | 174 | 30 | yes |
| Nidd I | [`nidde1ou.htm`](corrected/nidde1ou.htm) | 509 | 2 | 0 | 0 |  |
| Nidd II | [`nidde2ou.htm`](corrected/nidde2ou.htm) | 72 | 0 | 0 | 0 |  |
| Patis I | [`patis1ou.htm`](corrected/patis1ou.htm) | 196 | 73 | 0 | 0 |  |
| Patis II | [`patis2ou.htm`](corrected/patis2ou.htm) | 246 | 38 | 0 | 0 |  |
| Mil | [`milindou.htm`](corrected/milindou.htm) | 420 | 0 | 0 | 0 | yes |
| Vin I | [`vin1maou.htm`](corrected/vin1maou.htm) | 360 | 8 | 0 | 0 |  |
| Vin II | [`vin2cuou.htm`](corrected/vin2cuou.htm) | 308 | 14 | 0 | 0 | yes |
| Vin III | [`vin3s1ou.htm`](corrected/vin3s1ou.htm) | 266 | 7 | 0 | 0 | yes |
| Vin IV | [`vin4s2ou.htm`](corrected/vin4s2ou.htm) | 351 | 1 | 0 | 0 |  |
| Vin V | [`vin5paou.htm`](corrected/vin5paou.htm) | 226 | 0 | 0 | 0 | yes |
| Dhs | [`dhamsgou.htm`](corrected/dhamsgou.htm) | 264 | 1 | 0 | 0 |  |
| Vibh | [`vibhanou.htm`](corrected/vibhanou.htm) | 436 | 0 | 0 | 0 |  |
| Dhātuk | [`dhatukou.htm`](corrected/dhatukou.htm) | 113 | 0 | 0 | 0 |  |
| Pp | [`pugpan_ou.htm`](corrected/pugpan_ou.htm) | 74 | 13 | 0 | 0 | yes |
| Kv | [`kathavou.htm`](corrected/kathavou.htm) | 628 | 136 | 0 | 0 |  |
| ~~Vimānavatthu~~ | not reviewed: no compatible scan of the printed PTS edition |  |  |  |  |  |
| ~~Petavatthu~~ | not reviewed: no compatible scan of the printed PTS edition |  |  |  |  |  |
| ~~Apadāna~~ | not reviewed: no compatible scan of the printed PTS edition |  |  |  |  |  |
| ~~Buddhavaṃsa~~ | not reviewed: no compatible scan of the printed PTS edition |  |  |  |  |  |
| ~~Cariyāpiṭaka~~ | not reviewed: no compatible scan of the printed PTS edition |  |  |  |  |  |
| ~~Yamaka~~ | not reviewed: the review service excludes its PTS edition (too many abbreviations) |  |  |  |  |  |
| ~~Paṭṭhāna~~ | not reviewed: no compatible scan of the printed PTS edition |  |  |  |  |  |

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
- **Left out because the review service blocks them**: Vimānavatthu, Petavatthu, Apadāna, Buddhavaṃsa,
  Cariyāpiṭaka and Paṭṭhāna (no compatible scan of the printed edition to check against), and Yamaka (its
  PTS edition is excluded from the review: too many abbreviations). They are listed struck through in «Volumes».
- **Nettippakaraṇa and Peṭakopadesa**: GRETIL has them only in the Sinhala edition (input by the Sri Lanka
  Tripitaka Project, with the PTS page numbers), not in the PTS edition, so they are not part of this build.
- **The Sutta Nipāta, Theragāthā and Therīgāthā** were proofread directly in the GRETIL file. Their
  differences from the mirror's file are written in `corrections.json` as ordinary corrections
  (source label: "Copy of the GRETIL file corrected by hand, checked against the scan of the PTS edition"),
  so they are reproducible from the mirror too. The Sutta Nipāta was checked against the scan, apparatus
  included. The Theragāthā and Therīgāthā were checked against the scan of the first printing
  (Oldenberg and Pischel, 1883), while GRETIL follows the second edition (1966); their pagination was found
  equal on the nine pages compared.
- The proofreading is not finished for every book.
- Proofreading and approval of the corrections: Jorge Contreras (github.com/jorgecaa), foureditions project.
  24 corrections and the eight Saṃyutta II pages were read on the scan by machine and checked by hand.
  The PTS corrections of the edition are those of the authorities cited (Cone, Jackson, Pruitt, the corrigenda of the volume), applied as
  they publish them.
- The proofreader is not a philologist. The corrections are mechanical: each one restores what the printed PTS edition prints, read on its scan, or applies a correction published by the authority cited. No reading was chosen on text-critical grounds, and no emendation is the proofreader's own; applying a correction of the PTS does not mean the proofreader has judged it.

## Scans of the printed editions

The scans used for proofreading that are in the public domain worldwide (published more than 95 years
ago, every named editor dead for more than 100 years) are at the Internet Archive:
<https://archive.org/details/pts-gretil-ng-public-domain-scans>. These are 23 volumes: AN I–V, MN I,
SN II–V, Ja II, IV, V and VI, Vin II, III and V, Thag, Thig, It, Mil, Pp and Nett. Its `MANIFEST.txt` gives each
volume's editor, the editor's year of death with a source, and a SHA-256 checksum. The other scans used
are not published here.

## Licence

The GRETIL texts are © Pali Text Society and Dhammakaya Foundation, 2015, under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). `corrections.json` and the built
files in `corrected/` derive from those texts and are released under the same licence, with the same
notice. This README contains no GRETIL text and is released under the same licence.

The code, `build.py` and the check in `.github/workflows/build.yml`, contains no GRETIL text and is
dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/):
it can be copied, changed and reused for any purpose, without asking and without attribution.

The full text of CC BY-SA 4.0 is in `LICENSE`; the notice (copyright, what derives from the GRETIL texts,
credits) is in `NOTICE`.

## Citing

Cite the release you used, by its version (and its DOI, when one is given), together with the printed
PTS edition (volume and page): `corrections.json` changes between releases, so the text at a later
release may differ. `CITATION.cff` gives the details; GitHub shows them under «Cite this repository».

The releases are archived at Zenodo:

- all versions (resolves to the latest release): [10.5281/zenodo.24314138](https://doi.org/10.5281/zenodo.24314138);
- version 2.3.1: [10.5281/zenodo.24322869](https://doi.org/10.5281/zenodo.24322869) (same text as 2.3.0;
  links back from every volume, page anchors, explanations on the index);
- version 2.3.0: [10.5281/zenodo.24322444](https://doi.org/10.5281/zenodo.24322444) (corrigenda of the
  Dīgha volumes applied; footnotes corrected);
- version 2.2.1: [10.5281/zenodo.24320118](https://doi.org/10.5281/zenodo.24320118) (same text as 2.0.0;
  DOP article of the note answered in review, popup on braces);
- version 2.2.0: [10.5281/zenodo.24318371](https://doi.org/10.5281/zenodo.24318371) (same text as 2.0.0;
  146 corrections attributed to Cone's DOP instead of the scan);
- version 2.1.0: [10.5281/zenodo.24316048](https://doi.org/10.5281/zenodo.24316048) (same text as 2.0.0;
  short popups, DOP articles);
- version 2.0.0: [10.5281/zenodo.24315419](https://doi.org/10.5281/zenodo.24315419);
- version 1.0.0: [10.5281/zenodo.24314139](https://doi.org/10.5281/zenodo.24314139). In this version the
  corrections of the edition published by the PTS were marked but not applied.
