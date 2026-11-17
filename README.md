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
4. **Write.** One HTML file per GRETIL file in `corrected/`. GRETIL's own opening (title, notice,
   licence, terms of use) is kept unchanged. Red underline: an erratum GRETIL prints between braces,
   kept as printed. Blue underline: a correction from `corrections.json`; hovering shows its source,
   approval date, what GRETIL had and what the book prints.

`corrections.json` holds the checksums, the corrections and eight Saṃyutta II pages that GRETIL's
file lacks (read from the scan and reviewed). The GRETIL files themselves are never modified.

## Scope and limits

- **The critical apparatus (footnotes and variant readings) has NOT been proofread.** The corrections
  apply to the main text only.
- **Not included, because no compatible scan of the printed edition is available to check against:**
  Theragāthā and Therīgāthā, Vimānavatthu, Petavatthu, Apadāna, Buddhavaṃsa, Cariyāpiṭaka,
  Mahāniddesa and Cūḷaniddesa, Paṭisambhidāmagga, Yamaka, Paṭṭhāna (Dukapaṭṭhāna, Tikapaṭṭhāna).
- **Not included, because its source is not GRETIL's file:** the Sutta Nipāta (the proofread copy
  started from an already edited version, so it cannot be rebuilt from the GRETIL mirror).
- Dhammapada, Jātaka and Vinaya are included although a few pages of their scans are missing; those
  pages cannot be verified.
- The proofreading is not finished for every book.
- Corrections are by Jorge Contreras (github.com/jorgecaa), from the foureditions project.

## Licence

The GRETIL texts are © Pali Text Society and Dhammakaya Foundation, 2015, under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); the files in `corrected/` are
derivatives and carry the same licence and notice.
