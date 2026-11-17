# gretil-corrected

Reproducible build of the Pali Text Society (PTS) editions of the Pali canon from
[GRETIL](https://gretil.sub.uni-goettingen.de/), with proofreading corrections marked in the text.

    python3 build.py            # 1. download GRETIL  2. read corrections.json  3. write corrected/*.htm
    python3 build.py --verify   # only check the downloaded files against the expected checksums

Requirements: Python 3.9+ and git. No other dependency. Download size: about 130 MB.

## How it works

1. **Download.** `build.py` fetches one pinned commit of
   [INDOLOGY/GRETIL-mirror](https://github.com/INDOLOGY/GRETIL-mirror) (only the Pali folders).
2. **Verify.** The SHA-256 of each GRETIL file must equal the one recorded in `corrections.json`;
   otherwise the build stops, because the corrections were made on exactly those files.
3. **Correct.** Each correction replaces the text GRETIL has with the text the printed book prints
   (checked against scans of the PTS edition). A correction that does not fit exactly the stated
   number of times stops the build; nothing is applied halfway.
4. **Write.** One HTML file per GRETIL file in `corrected/` (also committed here). GRETIL's own opening (title, notice,
   licence, terms of use) is kept unchanged. Red underline: an erratum GRETIL prints between braces,
   kept as printed. Blue underline: a correction from `corrections.json`; hovering shows its source,
   approval date, what GRETIL had and what the book prints.

`corrections.json` holds the checksums, the corrections and eight Saṃyutta II pages that GRETIL's
file lacks (read from the scan and reviewed). The GRETIL files themselves are never modified.

## Scope and limits

- **The critical apparatus (footnotes and variant readings) has NOT been proofread.** The corrections
  apply to the main text only.
- **Included:** every GRETIL volume of the PTS editions that the foureditions review service does not
  block: 43 volumes (Dīgha, Majjhima, Saṃyutta, Aṅguttara, Vinaya, Khuddakapāṭha, Dhammapada, Udāna,
  Itivuttaka, Sutta Nipāta, Theragāthā and Therīgāthā, Jātaka, Mahāniddesa and Cūḷaniddesa,
  Paṭisambhidāmagga, Milindapañha, Dhammasaṅgaṇī, Vibhaṅga, Dhātukathā, Puggalapaññatti,
  Kathāvatthu). A volume without corrections is rebuilt as GRETIL has it, with the licence and the notices.
- **Left out because the review service blocks them** (no compatible scan of the printed edition to
  check against): Vimānavatthu, Petavatthu, Apadāna, Buddhavaṃsa, Cariyāpiṭaka, Yamaka and Paṭṭhāna.
- **Nettippakaraṇa and Peṭakopadesa:** the foureditions project also works on them, but GRETIL does not
  carry their text, so they cannot be part of this build. They are mentioned here only for completeness.
- **The Sutta Nipāta, Theragāthā and Therīgāthā** were proofread directly in the GRETIL file. Their
  differences from the mirror's file are written in `corrections.json` as ordinary corrections
  (source label: "Hand-corrected copy of the GRETIL file"), so they are reproducible from the mirror too.
- The proofreading is not finished for every book.
- Corrections are by Jorge Contreras (github.com/jorgecaa), from the foureditions project.

## Licence

The GRETIL texts are © Pali Text Society and Dhammakaya Foundation, 2015, under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); the files in `corrected/` (also committed here) are
derivatives and carry the same licence and notice.
